# Custom active response script

Script active response sendiri dipakai kalau script bawaan tidak cukup, misalnya untuk menonaktifkan akun di aplikasi internal, memanggil API firewall, atau mengumpulkan artefak saat alert muncul. Script bisa ditulis dalam bahasa apa pun yang bisa membaca stdin dan menulis stdout.

## Input yang diterima script

Wazuh mengirim seluruh alert ke script lewat stdin dalam format JSON:

```json
{
  "version": 1,
  "origin": {
    "name": "worker01",
    "module": "wazuh-execd"
  },
  "command": "add",
  "parameters": {
    "extra_args": [],
    "alert": {},
    "program": "/var/ossec/active-response/bin/firewall-drop"
  }
}
```

| Field | Isi |
| --- | --- |
| `command` | `add` saat aksi dijalankan, `delete` saat aksi dibatalkan |
| `parameters.extra_args` | Argumen dari tag `<extra_args>` di blok `<command>` |
| `parameters.alert` | Seluruh isi alert yang memicu active response |
| `parameters.program` | Path script yang dijalankan |

Letak field yang anda butuhkan berbeda antar jenis alert. Alert FIM menyimpan path file di `parameters.alert.syscheck.path`, sedangkan alert dari log web menyimpan IP address di `parameters.alert.data.srcip`. Periksa dulu bentuk alert aslinya di `/var/ossec/logs/alerts/alerts.json` sebelum menulis script.

## Stateless active response

Stateless berarti aksi sekali jalan, tanpa mekanisme pembatalan. Script hanya perlu:

1. Membaca stdin untuk mengambil pesan JSON.
2. Mem-parse pesan itu.
3. Memastikan field `command` bernilai `add`.
4. Mengambil informasi yang dibutuhkan dan menjalankan aksinya.

Contoh kerangka bash:

```bash
#!/bin/bash
# Contoh stateless active response

LOG_FILE="/var/ossec/logs/active-responses.log"

read INPUT_JSON
COMMAND=$(echo "$INPUT_JSON" | jq -r .command)
SRCIP=$(echo "$INPUT_JSON" | jq -r .parameters.alert.data.srcip)

if [ "$COMMAND" != "add" ]; then
    exit 0
fi

if [ -z "$SRCIP" ] || [ "$SRCIP" = "null" ]; then
    echo "$(date '+%Y/%m/%d %H:%M:%S') custom-ar: ERROR - srcip tidak ada di alert" >> "$LOG_FILE"
    exit 1
fi

# Aksi utama ditulis di sini
echo "$(date '+%Y/%m/%d %H:%M:%S') custom-ar: INFO - aksi dijalankan untuk $SRCIP" >> "$LOG_FILE"

exit 0
```

Untuk script stateless, blok `<command>` diisi `<timeout_allowed>no</timeout_allowed>`.

## Stateful active response

Stateful berarti aksi dibatalkan setelah jangka waktu tertentu. Protokolnya lebih panjang dari sekadar menangani `add` dan `delete`, dan ini sering dilewatkan saat menulis script sendiri. Urutan yang harus dilakukan script:

1. Membaca stdin untuk mengambil pesan JSON.
2. Mem-parse pesan itu.
3. Memeriksa field `command`. Nilai `add` berarti jalankan aksi utama, nilai `delete` berarti batalkan aksi itu.
4. Mengambil informasi untuk kontrol dan eksekusi. Script `firewall-drop`, misalnya, memakai nilai field `srcip` untuk memblokir dan membuka blokir.
5. Menyusun control message JSON berisi key yang diambil dari field alert, lalu menuliskannya ke stdout.
6. Menunggu jawaban lewat stdin, mem-parse-nya, dan memeriksa field `command` untuk memutuskan lanjut atau batal.

Control message yang dikirim script:

```json
{
  "version": 1,
  "origin": {
    "name": "program-name",
    "module": "active-response"
  },
  "command": "check_keys",
  "parameters": {
    "keys": ["10.0.0.1"]
  }
}
```

Jawaban yang diterima script:

```json
{
  "version": 1,
  "origin": {
    "name": "node01",
    "module": "wazuh-execd"
  },
  "command": "continue",
  "parameters": {}
}
```

Mekanisme ini mencegah aksi yang sama dijalankan dua kali: kalau aksi untuk key tersebut masih aktif dan belum timeout, jawabannya memerintahkan script membatalkan eksekusi.

Saat membaca stdin, script membaca sampai karakter newline. Saat menulis ke stdout, script harus menambahkan newline di akhir. Tanpa newline itu, eksekusi bisa berhenti dalam kondisi deadlock.

Karena protokol ini merepotkan ditulis dalam bash, dokumentasi resmi menyediakan template Python untuk stateful active response. Pakai template itu dan ubah tiga bagiannya: custom key untuk memilih field alert yang dipakai, custom action add untuk aksi utama, dan custom action delete untuk pembatalannya.

## Memasang script

Letakkan script di endpoint, lalu atur permission dan ownership:

```
$ sudo chmod 750 /var/ossec/active-response/bin/custom-ar.sh
$ sudo chown root:wazuh /var/ossec/active-response/bin/custom-ar.sh
```

Daftarkan command dan trigger-nya di `/var/ossec/etc/ossec.conf` pada Wazuh server:

```xml
<ossec_config>
  <command>
    <name>custom-ar</name>
    <executable>custom-ar.sh</executable>
    <timeout_allowed>no</timeout_allowed>
  </command>

  <active-response>
    <disabled>no</disabled>
    <command>custom-ar</command>
    <location>local</location>
    <rules_id>100300</rules_id>
  </active-response>
</ossec_config>
```

Restart manager:

```
$ sudo systemctl restart wazuh-manager
```

## Memberi alert dari output script

Log active response dipantau Wazuh, tapi rule bawaan hanya mengenali format script bawaan. Supaya output script anda menghasilkan alert, tambahkan decoder dan rule.

Decoder di `/var/ossec/etc/decoders/local_decoder.xml`:

```xml
<decoder name="custom_ar">
  <prematch>custom-ar:</prematch>
</decoder>

<decoder name="custom_ar1">
  <parent>custom_ar</parent>
  <regex>custom-ar: (\S+) - (\.*)</regex>
  <order>log_type, ar_message</order>
</decoder>
```

Rule di `/var/ossec/etc/rules/local_rules.xml`:

```xml
<group name="active_response,">
  <rule id="100400" level="0">
    <decoded_as>custom_ar</decoded_as>
    <description>Custom active response grouping rule</description>
  </rule>
  <rule id="100401" level="10">
    <if_sid>100400</if_sid>
    <match>custom-ar: ERROR</match>
    <description>Custom active response gagal: $(ar_message)</description>
  </rule>
</group>
```

Rule 100401 memberi alert ketika script anda gagal. Tanpa rule semacam ini, kegagalan active response hanya tertulis di log dan tidak ada yang tahu bahwa respons otomatis sudah berhenti bekerja.

## Verifikasi

Picu rule yang menjadi trigger, lalu periksa log:

```
$ sudo tail -n 20 /var/ossec/logs/active-responses.log
```

Untuk script stateful, pastikan script dipanggil dua kali: sekali dengan `add`, lalu dengan `delete` setelah timeout berakhir.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/active-response/custom-active-response-scripts.html>
