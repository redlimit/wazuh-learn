# Who-data: mencatat siapa yang mengubah file

FIM biasa memberi tahu bahwa sebuah file berubah. Who-data menambahkan siapa yang mengubahnya, proses apa yang dipakai, dan user mana yang memulai aksinya. Untuk investigasi, selisih informasi ini besar.

## Mengaktifkan

Ganti atribut `realtime` dengan `whodata` pada directory yang ingin dipantau:

```xml
<syscheck>
  <directories check_all="yes" whodata="yes">/etc</directories>
</syscheck>
```

Restart agent:

```
# systemctl restart wazuh-agent
```

## Provider di Linux

Di Linux, who-data punya dua provider:

```xml
<syscheck>
  <whodata>
    <provider>audit</provider>
    <restart_audit>yes</restart_audit>
    <audit_key>auditkey1,auditkey2</audit_key>
    <startup_healthcheck>yes</startup_healthcheck>
    <queue_size>100000</queue_size>
  </whodata>
</syscheck>
```

| Tag | Default | Keterangan |
| --- | --- | --- |
| `provider` | `audit` | `audit` memakai Linux Audit, `ebpf` memakai eBPF |
| `restart_audit` | `yes` | Mengizinkan Wazuh merestart auditd setelah memasang plugin. Kalau diisi `no`, rule who-data tidak diterapkan otomatis |
| `audit_key` | kosong | Mengumpulkan event audit dari key yang sudah ada, berguna kalau auditd sudah dipakai keperluan lain |
| `startup_healthcheck` | `yes` | Memeriksa kesiapan who-data saat agent start |

Kalau `provider` diisi `ebpf` tapi health check gagal, misalnya pada kernel tanpa BPF ring buffer atau tanpa BTF, modul jatuh kembali ke mode `audit`. Jadi konfigurasi `ebpf` tidak akan membuat FIM berhenti bekerja, tapi juga tidak akan memberi tahu dengan keras bahwa ia tidak dipakai. Periksa `ossec.log` kalau anda butuh kepastian provider mana yang aktif.

Opsi `provider` hanya tersedia untuk endpoint Linux.

## Field yang ditambahkan

Who-data menambahkan field `audit` pada alert FIM:

| Field alert | Isi |
| --- | --- |
| `audit.user.id` dan `audit.user.name` | User yang memicu perubahan |
| `audit.group.id` dan `audit.group.name` | Group user tersebut |
| `audit.process.name` | Nama proses yang mengubah file |
| `audit.process.id` | PID proses tersebut |
| `audit.process.parent_name` | Nama proses parent |
| `audit.login_user.name` | User yang login ke sistem, berguna saat perubahan dilakukan lewat `sudo` |

Pasangan `audit.user.name` dan `audit.login_user.name` adalah yang paling sering menjawab pertanyaan sebenarnya: perubahan dilakukan sebagai root, tapi siapa yang login.

## Biaya

Who-data lebih mahal daripada `realtime`. Di mode `audit` ia menambah rule auditd dan memproses event audit, yang pada directory sibuk bisa menghasilkan banyak event. Pakai who-data pada directory yang memang penting, bukan pada seluruh file system.

## Verifikasi

```
$ sudo touch /etc/uji-whodata.conf
```

Alert FIM yang muncul di dashboard harus memuat bagian `audit` dengan nama user dan proses. Kalau bagian itu kosong sementara alert FIM tetap ada, who-data belum aktif: periksa auditd terpasang dan berjalan, lalu cek `ossec.log` untuk pesan dari `wazuh-syscheckd`.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/syscheck.html>
- <https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/advanced-settings.html>
