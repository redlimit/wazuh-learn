# Journald log collection

Journald menyimpan log dalam format biner di `/var/log/journal/` dan menggantikan daemon syslog tradisional di banyak distribusi Linux. Agent Wazuh membaca journal lewat Logcollector.

## Konfigurasi default

Pengambilan journal sudah aktif secara default di `/var/ossec/etc/ossec.conf`:

```xml
<localfile>
  <location>journald</location>
  <log_format>journald</log_format>
</localfile>
```

Konfigurasi ini meneruskan seluruh log di journald ke Wazuh server.

Wazuh menyusun ulang entri journal menjadi format syslog supaya cocok dengan ruleset bawaan, memakai field berikut:

- `_HOSTNAME`
- `SYSLOG_IDENTIFIER`
- `MESSAGE`
- `SYSLOG_PID` atau `_PID` kalau tersedia

Hasilnya berbentuk:

```
$TIMESTAMP $_HOSTNAME $SYSLOG_IDENTIFIER[$PID]: $MESSAGE
```

## Filter

Mengambil seluruh journal menghasilkan banyak event yang tidak relevan. Filter mempersempitnya.

Hanya log dari satu systemd unit:

```xml
<localfile>
  <location>journald</location>
  <log_format>journald</log_format>
  <filter field="_SYSTEMD_UNIT">^ssh.service$</filter>
</localfile>
```

Hanya log dengan prioritas tertentu:

```xml
<localfile>
  <location>journald</location>
  <log_format>journald</log_format>
  <filter field="PRIORITY">^[0-3]$</filter>
</localfile>
```

Nilai `PRIORITY` mengikuti level syslog: 0 emergency sampai 7 debug. Filter di atas mengambil emergency sampai error saja.

Beberapa filter bisa dipasang dalam satu blok `<localfile>`:

```xml
<localfile>
  <location>journald</location>
  <log_format>journald</log_format>
  <filter field="_SYSTEMD_UNIT">^cron.service$</filter>
  <filter field="PRIORITY">[0-6]</filter>
</localfile>
```

Kalau sebuah log cocok dengan dua filter atau lebih di dalam satu blok, agent tetap mengirimnya satu kali saja.

## Catatan penting

Setelah konfigurasi berhasil diterapkan, Wazuh hanya mengumpulkan event journald yang terjadi sejak saat itu. Jangan menguji konfigurasi ini dengan log lama. Kalau anda memang butuh event yang tertinggal sejak Logcollector terakhir berhenti, matikan opsi `only-future-events`.

## Verifikasi

Picu event pada unit yang difilter, misalnya restart `ssh.service`, lalu bandingkan isi journal dengan alert yang muncul:

```
$ journalctl -u ssh.service -n 5
```

Di dashboard, buka Threat Hunting dan cari event dari agent tersebut.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/journald.html>
