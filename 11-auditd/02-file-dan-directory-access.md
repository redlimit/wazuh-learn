# Memantau akses file dan directory dengan auditd

Use case ini memantau akses ke directory `/home` untuk write, read, execute, dan perubahan atribut.

Selesaikan dulu [persiapan di 01](01-persiapan-dan-cdb-audit-keys.md) sebelum melanjutkan.

## Audit rule di endpoint

```
# echo "-w /home -p w -k audit-wazuh-w" >> /etc/audit/audit.rules
# echo "-w /home -p a -k audit-wazuh-a" >> /etc/audit/audit.rules
# echo "-w /home -p r -k audit-wazuh-r" >> /etc/audit/audit.rules
# echo "-w /home -p x -k audit-wazuh-x" >> /etc/audit/audit.rules
```

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
```

Keempat permission sengaja dipisah menjadi empat rule, bukan digabung sebagai `-p warx`. Dengan dipisah, setiap rule punya key sendiri, dan key itulah yang membuat Wazuh bisa membedakan jenis akses saat analisis.

## Uji konfigurasi

Buat file baru:

```
$ touch /home/malware.py
```

Alert muncul dengan rule ID 80790. Di dashboard, buka Threat Hunting dan filter `rule.id:80790`.

Tulis ke file:

```
$ nano /home/malware.py
```

Filter `rule.id:80784`.

Ubah permission:

```
$ chmod u+x /home/malware.py
```

Filter `rule.id:80787`.

Jalankan file:

```
$ /home/malware.py
```

Filter `rule.id:(80784 or 80789)`.

Hapus file:

```
$ rm /home/malware.py
```

Filter `rule.id:80791`.

## Catatan

Memantau `read` pada directory yang sering dibaca menghasilkan event dalam jumlah sangat besar. Untuk lab ini `/home` masih wajar, tapi jangan terapkan `-p r` pada `/usr` atau `/var` di endpoint produksi tanpa memperhitungkan volumenya. Mulai dari `write` dan `attribute` saja, lalu tambahkan yang lain kalau memang dibutuhkan.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/system-calls-monitoring/use-cases/monitoring-file-and-directory-access.html>
