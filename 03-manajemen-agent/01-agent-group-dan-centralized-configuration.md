# Agent group dan centralized configuration

Mengedit `ossec.conf` di setiap endpoint tidak bertahan lama begitu jumlah agent bertambah. Centralized configuration memindahkan konfigurasi ke server, dan agent group menentukan siapa menerima apa.

Setiap agent yang baru terhubung otomatis masuk group `default`.

## Membuat group

Lewat CLI di Wazuh server:

```
# /var/ossec/bin/agent_groups -a -g Linux -q
# /var/ossec/bin/agent_groups -a -g Windows -q
# /var/ossec/bin/agent_groups -a -g macOS -q
```

Flag `-a -g` menambah group, `-q` mematikan konfirmasi. Nama group hanya boleh berisi huruf, angka, titik, underscore, dan tanda hubung.

Lihat daftar group:

```
# /var/ossec/bin/agent_groups -l
```

```
Groups (5):
  Linux (0)
  Windows (0)
  default (2)
  macOS (0)
Unassigned agents: 0.
```

Lewat dashboard: Agents management > Groups, lalu Add new group.

Lewat Wazuh server API, dari Server management > Dev Tools:

```
POST /groups {"group_id": "Linux"}
```

## Memasukkan agent ke group

```
# /var/ossec/bin/agent_groups -a -i 002 -g dbms
```

Lewat API:

```
# curl -k -X PUT "https://<WAZUH_MANAGER_IP>:55000/agents/002/group/dbms?pretty=true" \
  -H "Authorization: Bearer $TOKEN"
```

Group harus dibuat dan dikonfigurasi sebelum agent dimasukkan ke dalamnya.

## File agent.conf

Setiap group punya satu file konfigurasi di server:

```
/var/ossec/etc/shared/<GROUP_NAME>/agent.conf
```

File ini kosong secara default. Isinya dikirim server ke semua agent dalam group tersebut.

Contoh `agent.conf` untuk group `Linux` yang menyalakan FIM realtime pada satu directory dan mengumpulkan satu file log:

```xml
<agent_config>
  <syscheck>
    <directories check_all="yes" report_changes="yes" realtime="yes">/etc</directories>
  </syscheck>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/auth.log</location>
  </localfile>
</agent_config>
```

Konfigurasi bisa dibatasi per sistem operasi dengan atribut `os`:

```xml
<agent_config os="Windows">
  <syscheck>
    <windows_registry>HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run</windows_registry>
  </syscheck>
</agent_config>
```

Setelah mengubah `agent.conf`, pastikan ownership file benar:

```
# chown wazuh:wazuh /var/ossec/etc/shared/Linux/agent.conf
```

## Urutan prioritas

Konfigurasi dari `agent.conf` menimpa konfigurasi lokal di `ossec.conf` agent. Kalau sebuah directory didefinisikan di kedua tempat, nilai dari centralized configuration yang dipakai.

Ini sering jadi sumber kebingungan: perubahan di `ossec.conf` endpoint tampak tidak berpengaruh, padahal sebenarnya ditimpa dari server. Kalau sebuah agent sudah masuk group dengan `agent.conf` terisi, edit `agent.conf`, bukan file lokalnya.

## Hot reload

Sejak Wazuh 4.14.0, agent Linux bisa menerapkan perubahan remote configuration tanpa memutus koneksi ke server. Semua daemon kecuali `wazuh-agentd` direstart saat reload.

## Verifikasi

Dijalankan dari Wazuh server, lihat group yang diikuti sebuah agent, status sinkronisasi file-nya, dan daftar file yang dibagikan ke sebuah group:

```
# /var/ossec/bin/agent_groups -s -i 002
# /var/ossec/bin/agent_groups -S -i 002
# /var/ossec/bin/agent_groups -c -g Linux
```

Command terakhir menampilkan daftar file beserta checksum-nya, termasuk `agent.conf` dan `merged.mg`.

Di endpoint, file yang diterima dari server tersimpan di `/var/ossec/etc/shared/`. Kalau `agent.conf` tidak muncul di sana beberapa menit setelah diubah, periksa log `ossec.log` di endpoint untuk pesan dari modul agent yang menangani shared configuration.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/agent/agent-management/grouping-agents.html>
- <https://documentation.wazuh.com/current/user-manual/reference/centralized-configuration.html>
