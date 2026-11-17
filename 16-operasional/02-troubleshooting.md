# Troubleshooting dan log

Daftar tempat yang diperiksa ketika sesuatu tidak jalan, disusun berdasarkan komponen.

## Log penting

| Lokasi | Isi |
| --- | --- |
| `/var/ossec/logs/ossec.log` (server) | Semua daemon Wazuh server |
| `/var/ossec/logs/ossec.log` (agent) | Semua daemon agent, termasuk koneksi dan enrollment |
| `/var/ossec/logs/alerts/alerts.log` dan `alerts.json` | Alert yang dihasilkan |
| `/var/ossec/logs/archives/archives.log` dan `archives.json` | Semua event, hanya kalau `<logall>` aktif |
| `/var/ossec/logs/active-responses.log` | Hasil eksekusi active response |
| `/var/ossec/logs/integrations.log` | Aktivitas modul Integrator, hanya kalau debug aktif |
| `/var/log/filebeat/filebeat` | Pengiriman alert dari server ke indexer |
| `/var/log/wazuh-indexer/` | Log indexer |

## Status service

```
# systemctl status wazuh-manager wazuh-indexer wazuh-dashboard filebeat
# /var/ossec/bin/wazuh-control status
```

`wazuh-control status` memecah status per daemon, bukan hanya per service, dan itu penting: service bisa terlihat aktif padahal `wazuh-analysisd` di dalamnya mati.

## Alur diagnosis berdasarkan gejala

**Agent tidak muncul di dashboard.** Lihat [chapter 02 bagian enrollment](../02-instalasi/06-enrollment-dan-troubleshooting.md). Pisahkan masalah enrollment (port 1515) dari masalah koneksi (port 1514) lewat `agent_control -l`.

**Agent Active tapi tidak ada alert.** Modul pengumpul data di agent belum aktif, atau event tidak memicu rule apa pun. Cek `ossec.log` di agent untuk modul yang dimaksud, lalu uji satu event mentah dengan `wazuh-logtest` di server.

**Alert ada di `alerts.json` tapi tidak muncul di dashboard.** Masalahnya di jalur server ke indexer, bukan di deteksi. Periksa Filebeat:

```
# filebeat test output
# tail -n 50 /var/log/filebeat/filebeat
```

**Manager gagal start setelah mengubah rules.** Hampir selalu syntax error di decoder atau rules. Uji dulu, jangan langsung restart:

```
# /var/ossec/bin/wazuh-analysisd -t
```

**Dashboard tidak bisa diakses atau menampilkan error indexer.** Periksa indexer menjawab dan statusnya tidak `red`:

```
# curl -k -u admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200/_cluster/health?pretty
```

Status `red` berarti ada shard yang tidak tersedia. Penyebab paling sering di lab adalah disk penuh atau RAM tidak cukup.

**Perubahan konfigurasi di agent tidak berpengaruh.** Agent itu kemungkinan masuk group dengan `agent.conf` yang menimpa konfigurasi lokal. Centralized configuration selalu menang. Lihat [chapter 03](../03-manajemen-agent/01-agent-group-dan-centralized-configuration.md).

## Menyalakan debug

Debug per modul diatur di `local_internal_options.conf`, bukan di `ossec.conf`. Nilainya `1` atau `2`, semakin tinggi semakin rinci.

Di Wazuh server:

```
# echo "analysisd.debug=1" >> /var/ossec/etc/local_internal_options.conf
# echo "integrator.debug=1" >> /var/ossec/etc/local_internal_options.conf
# echo "remoted.debug=1" >> /var/ossec/etc/local_internal_options.conf
# systemctl restart wazuh-manager
```

Di agent:

```
# echo "agent.debug=1" >> /var/ossec/etc/local_internal_options.conf
# echo "syscheck.debug=1" >> /var/ossec/etc/local_internal_options.conf
# echo "logcollector.debug=1" >> /var/ossec/etc/local_internal_options.conf
# systemctl restart wazuh-agent
```

Matikan kembali debug setelah selesai. Log debug tumbuh cepat dan bisa mengisi disk, yang justru menimbulkan masalah baru.

## Memeriksa konfigurasi yang benar-benar aktif

Konfigurasi aktif bisa berbeda dari isi file konfigurasi, karena centralized configuration dan nilai default ikut berperan, dan karena perubahan file belum berlaku sampai agent direstart. Untuk melihat yang sebenarnya dipakai agent, gunakan Wazuh server API:

```
# curl -k -X GET "https://localhost:55000/agents/002/config/syscheck/syscheck?pretty=true" -H "Authorization: Bearer $TOKEN"
```

Format endpoint-nya `GET /agents/{agent_id}/config/{component}/{configuration}`. Kombinasi yang sering dipakai:

| component | configuration | Blok konfigurasi |
| --- | --- | --- |
| `syscheck` | `syscheck` | `<syscheck>` |
| `syscheck` | `rootcheck` | `<rootcheck>` |
| `logcollector` | `localfile` | `<localfile>` |
| `agent` | `client` | `<client>` |
| `agent` | `labels` | `<labels>` |
| `analysis` | `active_response` | `<active-response>` |
| `integrator` | `integration` | `<integration>` |

Di dashboard, informasi yang sama ada di Agents management > Summary, pilih agent lalu klik Configuration. Halaman itu juga menunjukkan apakah konfigurasi agent sudah tersinkron dengan pengaturan terbaru dari Wazuh manager. Untuk konfigurasi aktif Wazuh manager sendiri, buka Server management > Settings.

## Masalah kapasitas di lab

Tiga penyebab paling sering di lab kecil:

Disk penuh. Indexer berhenti menerima data dan status cluster menjadi `red`. Periksa `df -h` dan hapus index lama atau perbesar disk.

RAM tidak cukup. Indexer adalah yang paling rakus. Kalau indexer mati sendiri atau restart berulang, cek `dmesg` untuk pesan OOM killer.

Jam tidak sinkron. Alert muncul di rentang waktu yang salah dan terlihat seperti tidak ada alert sama sekali, karena dashboard memfilter berdasarkan waktu. Pastikan NTP aktif di server dan semua endpoint.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/reference/internal-options.html>
- <https://documentation.wazuh.com/current/user-manual/reference/daemons/index.html>
- <https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/troubleshooting.html>
