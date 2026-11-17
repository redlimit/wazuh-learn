# Konfigurasi Active Response

Active Response menjalankan script atau executable di endpoint ketika alert tertentu muncul. Konfigurasinya terbagi dua: definisi command dan trigger ada di Wazuh server, sedangkan script yang dieksekusi ada di endpoint.

## Blok command di Wazuh server

Blok `<command>` menentukan script apa yang dijalankan. Untuk script bawaan, blok ini sudah ada di `/var/ossec/etc/ossec.conf` dan tidak perlu ditambahkan. Untuk script sendiri, tambahkan di antara tag `<ossec_config>`:

```xml
<command>
  <name>host-deny</name>
  <executable>host-deny</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>
```

- `<name>`: nama command, dipakai sebagai acuan di blok `<active-response>`.
- `<executable>`: nama script atau executable. Ekstensi file tidak perlu ditulis kecuali ada beberapa script dengan nama sama.
- `<timeout_allowed>`: `yes` berarti aksinya dibatalkan setelah jangka waktu tertentu, yang disebut stateful active response.

Tag `<disabled>` wajib ada di setiap blok `<active-response>` dan harus diisi `yes` atau `no` secara eksplisit. Mengisi `<disabled>yes</disabled>` di agent mematikan active response untuk agent itu saja, sedangkan mengisinya di `ossec.conf` manager mematikan active response di manager dan di semua agent.

## Blok active-response di Wazuh server

Blok `<active-response>` menentukan kapan dan di mana command dijalankan:

```xml
<active-response>
  <disabled>no</disabled>
  <command>host-deny</command>
  <location>local</location>
  <level>7</level>
  <timeout>600</timeout>
</active-response>
```

Pemicunya bisa berupa rule ID, level alert, atau rule group:

| Tag | Isi |
| --- | --- |
| `<rules_id>` | Satu atau beberapa rule ID dipisah koma |
| `<level>` | Level alert minimum |
| `<rules_group>` | Nama rule group |

Nilai `<location>` menentukan di mana script berjalan:

| Nilai | Perilaku |
| --- | --- |
| `local` | Berjalan di endpoint yang menghasilkan alert |
| `server` | Berjalan di Wazuh server |
| `defined-agent` | Berjalan di agent tertentu, ID-nya ditulis di tag `<agent_id>` |
| `all` | Berjalan di semua agent |

Contoh `defined-agent`:

```xml
<ossec_config>
  <active-response>
    <disabled>no</disabled>
    <command>host-deny</command>
    <location>defined-agent</location>
    <agent_id>001</agent_id>
    <level>10</level>
    <timeout>180</timeout>
  </active-response>
</ossec_config>
```

Gunakan `all` dengan hati-hati. Konfigurasi yang salah dengan `location` bernilai `all` menjalankan aksi di seluruh fleet sekaligus, dan satu alert false positive bisa memblokir IP address yang anda butuhkan di semua endpoint.

`<timeout>` dalam detik, menentukan berapa lama aksi active response berlaku sebelum dibatalkan.

Restart manager:

```
$ sudo systemctl restart wazuh-manager
```

## Script bawaan

Untuk script bawaan, tidak ada konfigurasi tambahan di endpoint. Script untuk Linux dan Unix ada di `/var/ossec/active-response/bin`, untuk macOS di `/Library/Ossec/active-response/bin`.

| Script | Fungsi |
| --- | --- |
| `disable-account` | Mematikan sebuah user account |
| `firewall-drop` | Menambahkan IP address ke deny list iptables |
| `firewalld-drop` | Menambahkan IP address ke drop list firewalld, butuh firewalld terpasang |
| `host-deny` | Menambahkan IP address ke `/etc/hosts.deny` |
| `ip-customblock` | Blok custom yang mudah dimodifikasi |
| `ipfw` | Firewall drop untuk IPFW |
| `npf` | Firewall drop untuk NPF |
| `pf` | Firewall drop untuk PF |
| `route-null` | Mengarahkan IP address ke null route |
| `restart-wazuh` dan `restart.sh` | Merestart Wazuh agent atau manager |
| `wazuh-slack` | Mengirim notifikasi ke Slack, butuh hook URL lewat `extra_args` |
| `kaspersky` | Integrasi dengan Kaspersky Endpoint Security for Linux |

Untuk Windows, script ada di `C:\Program Files (x86)\ossec-agent\active-response\bin`:

| Script | Fungsi |
| --- | --- |
| `netsh.exe` | Memblokir IP address memakai netsh |
| `restart-wazuh.exe` | Merestart Wazuh agent |
| `route-null.exe` | Mengarahkan IP address ke null route |

## Script sendiri

Letakkan script di directory active response pada endpoint, lalu atur permission dan ownership.

Linux dan Unix:

```
$ sudo chmod 750 /var/ossec/active-response/bin/<CUSTOM_SCRIPT>
$ sudo chown root:wazuh /var/ossec/active-response/bin/<CUSTOM_SCRIPT>
```

macOS, dengan directory `/Library/Ossec/active-response/bin`. Untuk Windows, letakkan di `C:\Program Files (x86)\ossec-agent\active-response\bin`.

## Repeated offender

Untuk memperpanjang blokir pada penyerang yang kembali, tambahkan konfigurasi berikut di `ossec.conf` agent:

```xml
<active-response>
  <disabled>no</disabled>
  <repeated_offenders>30,60,120</repeated_offenders>
</active-response>
```

Nilainya dalam menit, berupa daftar timeout yang menaik dan maksimal lima entri. Blokir pertama memakai `<timeout>` biasa, pelanggaran berikutnya diblokir 30 menit, lalu 60, lalu 120. Ketika `repeated_offenders` dipakai, `<timeout>` hanya berlaku untuk pelanggaran pertama.

## Verifikasi

Hasil eksekusi script tercatat di:

- Linux: `/var/ossec/logs/active-responses.log`
- macOS: `/Library/Ossec/logs/active-responses.log`
- Windows: `C:\Program Files (x86)\ossec-agent\active-response\active-responses.log`

```
$ sudo tail -n 20 /var/ossec/logs/active-responses.log
```

File ini adalah tempat pertama yang diperiksa setiap kali active response tampak tidak jalan. Kalau file-nya kosong, trigger-nya yang belum kena. Kalau berisi pesan error, script-nya yang gagal.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/active-response/how-to-configure.html>
- <https://documentation.wazuh.com/current/user-manual/capabilities/active-response/default-active-response-scripts.html>
