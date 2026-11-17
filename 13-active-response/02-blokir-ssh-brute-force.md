# Memblokir SSH brute force dengan Active Response

Use case ini memblokir IP address penyerang ketika rule 5763 (SSHD brute force trying to get access to the system) memicu. Script `firewall-drop` memakai iptables untuk melakukannya.

Lab yang dipakai: satu endpoint penyerang dengan SSH client, dan satu endpoint korban yang menjalankan SSH server serta Wazuh agent.

## Konfigurasi Wazuh server

Pastikan blok `<command>` berikut ada di `/var/ossec/etc/ossec.conf`. Blok ini biasanya sudah ada secara default:

```xml
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>
```

Tambahkan trigger-nya:

```xml
<ossec_config>
  <active-response>
    <disabled>no</disabled>
    <command>firewall-drop</command>
    <location>local</location>
    <rules_id>5763</rules_id>
    <timeout>180</timeout>
  </active-response>
</ossec_config>
```

`<location>local</location>` berarti script dijalankan di endpoint yang menghasilkan alert, yaitu korban. `<timeout>180</timeout>` memblokir IP penyerang selama 180 detik.

Restart manager:

```
$ sudo systemctl restart wazuh-manager
```

## Uji konfigurasi

Lakukan hanya di lab milik anda sendiri.

Pastikan jalur network antara penyerang dan korban terbuka:

```
$ ping <VICTIM_IP>
```

Pasang Hydra di endpoint penyerang:

```
$ sudo apt update && sudo apt install -y hydra
```

Buat file berisi beberapa password acak, lalu jalankan brute force:

```
$ sudo hydra -t 4 -l <VICTIM_USERNAME> -P <PASSWD_LIST.txt> <VICTIM_IP> ssh
```

Setelah serangan selesai, rule 5763 memicu dan bisa dilihat di dashboard.

Verifikasi blokir dengan ping dari penyerang, dalam rentang tiga menit setelah serangan:

```
$ ping <VICTIM_IP>
```

```
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
^C
--- 10.0.0.5 ping statistics ---
12 packets transmitted, 0 received, 100% packet loss, time 11000ms
```

Paket loss 100 persen menandakan active response berhasil. Setelah timeout berakhir, blokir dicabut otomatis dan ping kembali normal.

Cek juga langsung di endpoint korban:

```
$ sudo iptables -L INPUT -n --line-numbers
```

## Alert ketika active response berjalan

Endpoint Linux dan Unix mencatat aktivitas active response di `/var/ossec/logs/active-responses.log`, dan file itu sudah dipantau Wazuh secara default:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/ossec/logs/active-responses.log</location>
</localfile>
```

Alert yang muncul berasal dari rule 651, bagian dari file rule bawaan `/var/ossec/ruleset/rules/0015-ossec_rules.xml`.

Kalau anda membuat script active response sendiri, rule bawaan ini tidak akan mengenali output-nya. Tambahkan custom rule untuk menganalisis log yang dihasilkan script anda, seperti pada [chapter 09 bagian YARA](../09-malware-detection/03-yara.md).

## Risiko yang perlu dipertimbangkan

Memblokir IP address berdasarkan alert adalah aksi otomatis yang bisa dipakai menyerang anda sendiri. Penyerang yang memalsukan IP address sumber, atau sengaja memicu alert dari IP address yang anda butuhkan, bisa membuat Wazuh memblokir alamat penting. Sebelum memakai pola ini di produksi:

- Mulai dari rule ID yang spesifik, bukan dari `<level>` yang luas.
- Pakai `<timeout>` pendek, bukan blokir permanen.
- Pastikan IP address administrasi anda sendiri tidak ikut terblokir, misalnya dengan menambahkan pengecualian di firewall di atas rule yang dibuat Wazuh.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/active-response/ar-use-cases/blocking-ssh-brute-force.html>
