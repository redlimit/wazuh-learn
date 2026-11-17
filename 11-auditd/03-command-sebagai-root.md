# Memantau command yang dijalankan sebagai root

Use case ini memantau semua command yang dieksekusi dengan privilege root.

Selesaikan dulu [persiapan di 01](01-persiapan-dan-cdb-audit-keys.md).

## Audit rule di endpoint

```
# echo "-a always,exit -F euid=0 -F arch=b64 -S execve -k audit-wazuh-c" >> /etc/audit/audit.rules
# echo "-a always,exit -F euid=0 -F arch=b32 -S execve -k audit-wazuh-c" >> /etc/audit/audit.rules
```

Arti tiap bagian:

- `-a always,exit`: event selalu dibuat, baik system call-nya berhasil maupun gagal.
- `-S execve`: hanya mencocokkan system call `execve`.
- `-F arch=b64` dan `-F arch=b32`: mencocokkan system call lewat interface 64-bit dan 32-bit. Sistem 64-bit bisa menjalankan program 32-bit, jadi kedua rule dibutuhkan untuk cakupan penuh.
- `-F euid=0`: hanya event dengan effective user ID 0, yaitu root.
- `-k audit-wazuh-c`: key yang menandai event ini sebagai system call rule di CDB list `audit-keys`.

Muat ulang rule:

```
# auditctl -R /etc/audit/audit.rules
# auditctl -l
```

```
-w /home -p w -k audit-wazuh-w
-w /home -p a -k audit-wazuh-a
-w /home -p r -k audit-wazuh-r
-w /home -p x -k audit-wazuh-x
-a always,exit -F arch=b64 -S execve -F euid=0 -F key=audit-wazuh-c
-a always,exit -F arch=b32 -S execve -F euid=0 -F key=audit-wazuh-c
```

## Uji konfigurasi

Sebagai user biasa dengan `sudo`:

```
$ sudo touch newfile.txt
```

Sebagai root:

```
# touch newfile2.txt
```

Alert muncul dengan rule ID 80792. Filter `rule.id:80792` di modul Threat Hunting.

## Membaca alert

Field `euid` menunjukkan aksi dijalankan dengan privilege root. Yang lebih berguna untuk investigasi adalah field `auid`, yang menunjukkan user mana yang login dan memulai rangkaian aksi tersebut.

Perbedaan itu penting: `euid=0` hanya memberi tahu bahwa sesuatu berjalan sebagai root, sedangkan `auid` menjawab siapa orangnya. Pada endpoint dengan beberapa administrator, `auid` adalah satu-satunya field yang memisahkan mereka.

## Catatan volume

Rule ini mencatat setiap `execve` oleh root, termasuk yang berasal dari cron, systemd, dan script maintenance. Di endpoint yang sibuk, volumenya besar. Kalau terlalu berisik, pertimbangkan mempersempitnya, misalnya hanya memantau `execve` dari shell interaktif, atau menyaring proses yang sudah diketahui lewat custom rule dengan level 0.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/system-calls-monitoring/use-cases/monitoring-commands-run-as-root.html>
