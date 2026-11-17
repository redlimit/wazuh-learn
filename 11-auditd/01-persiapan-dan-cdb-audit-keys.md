# auditd: persiapan dan CDB audit-keys

Linux Audit menghasilkan event untuk write, read, execute, perubahan atribut, dan system call. Wazuh membedakan jenis event itu lewat key yang anda beri pada audit rule, bukan lewat isi log, karena isi log audit terlalu seragam untuk dipisahkan rules dan decoder saja.

## CDB list audit-keys

Wazuh membawa CDB list bawaan yang memetakan key ke jenis event. Lihat isinya di Wazuh server:

```
# cat /var/ossec/etc/lists/audit-keys
```

```
audit-wazuh-w:write
audit-wazuh-r:read
audit-wazuh-a:attribute
audit-wazuh-x:execute
audit-wazuh-c:command
```

Format entri adalah `<KEY_NAME>:<VALUE>`, dengan `<KEY_NAME>` adalah string yang anda pakai di argumen `-k` pada audit rule, dan `<VALUE>` salah satu dari:

| Value | Untuk audit rule |
| --- | --- |
| `write` | File system rule dengan `-p w` |
| `read` | File system rule dengan `-p r` |
| `execute` | File system rule dengan `-p x` |
| `attribute` | File system rule dengan `-p a` |
| `command` | System call rule |

Menambahkan key sendiri:

```
# echo "<YOUR_KEY>:<VALUE>" >> /var/ossec/etc/lists/audit-keys
```

Restart manager setiap kali CDB list diubah:

```
# systemctl restart wazuh-manager
```

Rule bawaan untuk event audit ada di `/var/ossec/ruleset/rules/0365-auditd_rules.xml` pada Wazuh server.

## Konfigurasi endpoint

Pasang paket audit kalau belum ada:

```
# apt install -y auditd
```

Untuk RHEL dan turunannya, pakai `yum install -y auditd` atau `dnf install -y auditd`.

Kalau paket audit sudah terpasang sebelum Wazuh agent dipasang, konfigurasi berikut sudah ditambahkan otomatis oleh installer dan langkah di bawah tidak perlu dikerjakan.

Tambahkan blok berikut ke `/var/ossec/etc/ossec.conf` di agent supaya Wazuh membaca log audit:

```xml
<localfile>
  <log_format>audit</log_format>
  <location>/var/log/audit/audit.log</location>
</localfile>
```

Restart agent:

```
# systemctl restart wazuh-agent
```

Setelah itu, audit rule dibuat dengan `auditctl` atau lewat file rule audit. Dua use case berikutnya memakai pola ini.

## Verifikasi

```
# auditctl -s
# grep audit /var/ossec/logs/ossec.log | tail -n 10
```

Alert dari Linux Audit muncul di modul Threat Hunting pada dashboard.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/system-calls-monitoring/audit-configuration.html>
