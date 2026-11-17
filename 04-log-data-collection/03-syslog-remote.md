# Syslog remote di Wazuh server

Perangkat seperti firewall, switch, dan router tidak bisa dipasangi agent. Wazuh server bisa menerima log dari perangkat semacam itu lewat syslog.

## Konfigurasi

Tambahkan blok `<remote>` di dalam `<ossec_config>` pada `/var/ossec/etc/ossec.conf` di Wazuh server:

```xml
<remote>
  <connection>syslog</connection>
  <port>514</port>
  <protocol>tcp</protocol>
  <allowed-ips>192.168.2.0/24</allowed-ips>
  <local_ip>192.168.2.10</local_ip>
</remote>
```

Keterangan tiap tag:

- `<connection>`: jenis koneksi, bernilai `secure` untuk agent atau `syslog` untuk syslog remote.
- `<port>`: port yang didengarkan untuk pesan syslog.
- `<protocol>`: `tcp` atau `udp`.
- `<allowed-ips>`: IP address atau network range perangkat yang diizinkan mengirim.
- `<local_ip>`: IP address Wazuh server yang mendengarkan koneksi.

Tag `<allowed-ips>` bersifat wajib. Tanpa tag itu konfigurasi tidak aktif sama sekali, dan tidak ada error yang jelas untuk menjelaskannya.

Restart Wazuh manager:

```
# systemctl restart wazuh-manager
```

## Verifikasi

Pastikan server mendengarkan port yang dimaksud:

```
# ss -lntp | grep 514
```

Kirim pesan uji dari perangkat yang diizinkan:

```
$ logger -n <WAZUH_MANAGER_IP> -P 514 -T "uji syslog remote"
```

Kalau `<logall>` belum aktif, event yang tidak memicu rule tidak tersimpan. Untuk memastikan pesan benar-benar masuk, sementara aktifkan archive di Wazuh server lalu cek `/var/ossec/logs/archives/archives.log`.

## Alternatif

Kalau anda sudah punya central logging server seperti syslog-ng atau Logstash, memasang agent Wazuh di host tersebut sering lebih sederhana daripada mengarahkan setiap perangkat ke Wazuh server. Agent membaca file log yang sudah terkumpul di sana, dan anda mendapat semua kemampuan log collection biasa.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/syslog.html>
- <https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/remote.html>
