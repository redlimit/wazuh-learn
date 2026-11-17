# Monitoring file log

Modul Logcollector membaca file log di endpoint dan meneruskan isinya ke Wazuh server untuk didecode dan dicocokkan dengan rules.

## Konfigurasi dasar

Tambahkan blok `<localfile>` di dalam `<ossec_config>` pada file konfigurasi agent:

```xml
<localfile>
  <location>/<FILE_PATH>/file.log</location>
  <log_format>syslog</log_format>
</localfile>
```

`<location>` adalah path lengkap file yang dipantau. `<log_format>` adalah format isi file.

Restart agent:

```
# systemctl restart wazuh-agent
```

Untuk Windows gunakan `Restart-Service -Name wazuh`, untuk macOS `/Library/Ossec/bin/wazuh-control restart`.

## Format log yang sering dipakai

| `log_format` | Untuk |
| --- | --- |
| `syslog` | Log teks satu baris per event, format paling umum |
| `json` | Log berformat JSON per baris |
| `apache` | Log Apache error dan access |
| `audit` | Output Linux Audit di `/var/log/audit/audit.log` |
| `journald` | Journal systemd, lihat [02-journald.md](02-journald.md) |
| `eventchannel` | Windows Event Channel |
| `command` dan `full_command` | Output sebuah command, lihat bagian bawah |
| `multi-line` | Event yang menempati beberapa baris |

## Contoh konfigurasi per endpoint

Log autentikasi dan web server di Ubuntu:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/auth.log</location>
</localfile>

<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/error.log</location>
</localfile>

<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/nginx/access.log</location>
</localfile>
```

Windows Event Channel:

```xml
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
</localfile>

<localfile>
  <location>Microsoft-Windows-Sysmon/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
```

## Log dengan nama berbasis tanggal

Logcollector mendukung format `strftime` di `<location>`, berguna untuk aplikasi yang membuat file baru setiap hari. Untuk file `file-26-11-17.log`:

```xml
<localfile>
  <location>/<FILE_PATH>/file-%y-%m-%d.log</location>
  <log_format>syslog</log_format>
</localfile>
```

## Wildcard

Wildcard dipakai saat nama file tidak bisa diprediksi, misalnya log container yang memakai container ID sebagai nama directory:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/lib/docker/containers/*/*-json.log</location>
</localfile>
```

## Output command sebagai log

Logcollector juga bisa menjalankan command secara berkala dan memperlakukan output-nya sebagai log. `command` memproses output baris per baris, `full_command` memperlakukan seluruh output sebagai satu event:

```xml
<localfile>
  <log_format>full_command</log_format>
  <command>df -P</command>
  <frequency>360</frequency>
</localfile>
```

`<frequency>` adalah jarak eksekusi dalam detik. Modul ini dibahas lebih lanjut sebagai Command monitoring di dokumentasi resmi.

## Verifikasi

Di endpoint, pastikan Logcollector benar-benar membaca file yang dimaksud:

```
# grep logcollector /var/ossec/logs/ossec.log | tail -n 20
```

Baris `Analyzing file: '/var/log/auth.log'` menandakan file sudah diambil. Kalau yang muncul `Unable to open file`, periksa ejaan path dan permission file tersebut.

Lalu picu satu event, misalnya login SSH yang gagal, dan cari alert-nya di dashboard pada modul Threat Hunting.

## Catatan Windows

Sejak Wazuh 4.13.0, log collection di Windows tidak mendukung file di UNC path atau mapped network drive. Konfigurasi semacam itu diabaikan tanpa pesan error.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/monitoring-log-files.html>
- <https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/localfile.html>
