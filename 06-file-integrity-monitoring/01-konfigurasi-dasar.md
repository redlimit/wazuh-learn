# Konfigurasi dasar FIM

Modul FIM (`syscheck`) memantau pembuatan, perubahan, dan penghapusan file di Linux, Windows, dan macOS. Modul ini menyimpan checksum dan atribut file, lalu menghasilkan alert ketika ada selisih.

## Lokasi konfigurasi

FIM dikonfigurasi di sisi endpoint, atau dikirim lewat centralized configuration:

- Linux: `/var/ossec/etc/ossec.conf`
- Windows: `C:\Program Files (x86)\ossec-agent\ossec.conf`
- macOS: `/Library/Ossec/etc/ossec.conf`

Kalau sebuah directory didefinisikan di `agent.conf` dan di `ossec.conf` sekaligus, nilai dari centralized configuration yang menang.

## Konfigurasi minimum

```xml
<syscheck>
  <directories>/etc</directories>
  <directories>/var/www/html/config.php</directories>
</syscheck>
```

Restart agent:

```
# systemctl restart wazuh-agent
```

Untuk Windows `Restart-Service -Name wazuh`, untuk macOS `/Library/Ossec/bin/wazuh-control restart`.

## Atribut yang penting

```xml
<syscheck>
  <directories check_all="yes" report_changes="yes" realtime="yes">/etc</directories>
</syscheck>
```

| Atribut | Default | Fungsi |
| --- | --- | --- |
| `realtime` | `no` | Monitoring realtime lewat inotify di Linux dan mekanisme setara di Windows. Hanya bekerja untuk directory, bukan file tunggal |
| `whodata` | `no` | Mencatat siapa yang mengubah file, lihat [02-who-data.md](02-who-data.md) |
| `report_changes` | `no` | Melaporkan isi perubahan, terbatas untuk file teks |
| `diff_size_limit` | `50MB` | Batas ukuran file yang masih dilaporkan isi perubahannya |
| `check_all` | `yes` | Mengaktifkan semua pemeriksaan berawalan `check_`: ukuran, permission, owner, tanggal modifikasi, inode, dan hash |
| `check_sum` | `yes` | Memeriksa hash MD5, SHA-1, dan SHA-256 |

Satu baris `<directories>` menerima maksimal 64 path yang dipisah koma. Untuk lebih banyak path, pakai beberapa baris.

Wildcard `*` dan `?` bisa dipakai seperti di shell, misalnya `C:\Users\*\Downloads`. Wildcard dievaluasi ulang setiap scan terjadwal, bukan secara realtime.

Default `<directories>` di Linux adalah `/etc,/usr/bin,/usr/sbin,/bin,/sbin`. Di macOS default-nya `/private/etc,/usr/bin,/usr/sbin,/bin,/sbin`, karena `/etc` hanya symbolic link ke `/private/etc`.

## Mengecualikan file

Directory yang dipantau sering memuat file yang berubah terus dan tidak bernilai, misalnya cache atau file lock. Dua tag mengurangi kebisingan itu:

```xml
<syscheck>
  <directories check_all="yes" realtime="yes">/var/www/html</directories>
  <ignore>/var/www/html/cache</ignore>
  <ignore type="sregex">.log$|.tmp$</ignore>
  <nodiff>/var/www/html/.env</nodiff>
</syscheck>
```

`<ignore>` membuang event dari path tersebut. `<nodiff>` tetap memberi alert kalau file berubah, tapi tidak mengirim isi perubahannya. Pakai `<nodiff>` untuk file yang memuat kredensial, supaya isinya tidak berakhir di alert.

## Frekuensi scan

```xml
<syscheck>
  <frequency>43200</frequency>
  <scan_on_start>yes</scan_on_start>
</syscheck>
```

`<frequency>` dalam detik; 43200 berarti setiap 12 jam. `realtime` dan `whodata` tidak menggantikan scan terjadwal, karena scan terjadwal yang menangkap perubahan saat agent mati.

## Monitoring registry Windows

```xml
<syscheck>
  <windows_registry>HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run</windows_registry>
  <windows_registry arch="both">HKEY_LOCAL_MACHINE\Software\Classes\batfile</windows_registry>
</syscheck>
```

Atribut `arch="both"` memantau view 32-bit dan 64-bit sekaligus.

## Verifikasi

Buat perubahan di directory yang dipantau:

```
$ sudo touch /etc/uji-fim.conf
$ echo "uji" | sudo tee -a /etc/uji-fim.conf
$ sudo rm /etc/uji-fim.conf
```

Ketiga aksi itu harus memicu tiga alert berbeda: rule 554 untuk file ditambahkan, 550 untuk file diubah, dan 553 untuk file dihapus. Buka modul File Integrity Monitoring di dashboard untuk melihatnya.

Kalau tidak ada alert sama sekali, periksa modul FIM benar-benar jalan di endpoint:

```
# grep syscheck /var/ossec/logs/ossec.log | tail -n 20
```

## Catatan

Sejak Wazuh 4.13.0, FIM di Windows tidak mendukung UNC network path maupun mapped network drive. Hanya local file system yang dipantau.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/how-to-configure-fim.html>
- <https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/syscheck.html>
