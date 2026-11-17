# Custom decoder

Decoder memecah satu baris log menjadi field yang bisa dipakai rules. Kalau log aplikasi anda belum dikenali ruleset bawaan, decoder adalah langkah pertama, bukan rules.

Semua pekerjaan di chapter ini dilakukan di Wazuh server.

## Struktur directory ruleset

```
/var/ossec/
  ├─ etc/
  │   ├─ decoders/
  │   │   └─ local_decoder.xml
  │   └─ rules/
  │       └─ local_rules.xml
  └─ ruleset/
      ├─ decoders/
      └─ rules/
```

Isi `/var/ossec/ruleset/` ditimpa setiap kali Wazuh di-upgrade. Jangan pernah menaruh perubahan anda di sana. Semua custom decoder dan rules masuk ke `/var/ossec/etc/`.

## Menambah decoder

Contoh log dari aplikasi bernama `example`:

```
Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100'
```

Tambahkan decoder berikut ke `/var/ossec/etc/decoders/local_decoder.xml`:

```xml
<decoder name="example">
  <program_name>^example</program_name>
</decoder>

<decoder name="example">
  <parent>example</parent>
  <regex>User '(\w+)' logged from '(\d+.\d+.\d+.\d+)'</regex>
  <order>dstuser, srcip</order>
</decoder>
```

Decoder pertama adalah parent, mencocokkan nama program. Decoder kedua mengambil nilai dari regex dan menamainya lewat `<order>`. Jumlah grup tangkap di `<regex>` harus sama dengan jumlah nama di `<order>`.

Nama field di `<order>` sebaiknya memakai nama standar Wazuh seperti `srcip`, `dstuser`, `url`, dan `status`, supaya rules bawaan serta dashboard ikut mengenalinya.

## Menguji dengan wazuh-logtest

```
# /var/ossec/bin/wazuh-logtest
```

Tempel satu baris log, lalu amati fase decoding:

```
**Phase 1: Completed pre-decoding.
	full event: 'Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100''
	timestamp: 'Dec 25 20:45:02'
	hostname: 'MyHost'
	program_name: 'example'

**Phase 2: Completed decoding.
	name: 'example'
	dstuser: 'admin'
	srcip: '192.168.1.100'
```

Untuk menguji decoder, cukup menyimpan file. Restart manager hanya dibutuhkan kalau anda ingin decoder itu benar-benar dipakai untuk menghasilkan alert.

## Mengubah decoder bawaan

Decoder bawaan kadang tidak mengenali format log yang sudah dimodifikasi di lingkungan anda. Jangan edit file di `/var/ossec/ruleset/decoders/`, karena perubahannya hilang saat upgrade. Prosedurnya:

Copy file decoder ke directory user:

```
# cp /var/ossec/ruleset/decoders/0310-ssh_decoders.xml /var/ossec/etc/decoders/
# chown wazuh:wazuh /var/ossec/etc/decoders/0310-ssh_decoders.xml
# chmod 660 /var/ossec/etc/decoders/0310-ssh_decoders.xml
```

Keluarkan file aslinya dari daftar yang dimuat, lewat `<decoder_exclude>` di `/var/ossec/etc/ossec.conf`:

```xml
<ruleset>
  <!-- Default ruleset -->
  <decoder_dir>ruleset/decoders</decoder_dir>
  <rule_dir>ruleset/rules</rule_dir>
  <rule_exclude>0215-policy_rules.xml</rule_exclude>
  <list>etc/lists/audit-keys</list>

  <!-- User-defined ruleset -->
  <decoder_dir>etc/decoders</decoder_dir>
  <rule_dir>etc/rules</rule_dir>
  <decoder_exclude>ruleset/decoders/0310-ssh_decoders.xml</decoder_exclude>
</ruleset>
```

Edit file salinan di `/var/ossec/etc/decoders/`, lalu restart manager:

```
# systemctl restart wazuh-manager
```

Konsekuensinya: file yang anda kecualikan tidak lagi menerima update dari Wazuh. Setiap upgrade, bandingkan versi baru decoder aslinya dengan salinan anda.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/ruleset/decoders/custom.html>
- <https://documentation.wazuh.com/current/user-manual/ruleset/index.html>
