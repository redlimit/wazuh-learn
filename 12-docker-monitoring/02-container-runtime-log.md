# Container runtime log

Docker listener melaporkan aksi terhadap container: start, stop, pause, remove. Log dari aplikasi di dalam container adalah hal berbeda, dan untuk itu Logcollector yang bekerja.

Di Linux, runtime log container tersimpan di `/var/lib/docker/containers/<CONTAINER_ID>/<CONTAINER_ID>-json.log`.

## Konfigurasi agent

Tambahkan blok berikut ke `/var/ossec/etc/ossec.conf` di Docker server:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/lib/docker/containers/*/*-json.log</location>
</localfile>
```

Wildcard `*` dipakai karena nama directory dan file memuat container ID yang berubah setiap container dibuat. Tanpa wildcard, konfigurasi harus diperbarui setiap kali container baru jalan.

Restart agent:

```
# systemctl restart wazuh-agent
```

## Decoder untuk log web di dalam container

Docker membungkus setiap baris log container dalam JSON, sehingga log Apache atau nginx di dalamnya tidak langsung dikenali decoder web bawaan. Tambahkan decoder berikut ke `/var/ossec/etc/decoders/local_decoder.xml` di Wazuh server:

```xml
<decoder name="web-accesslog-docker">
  <parent>json</parent>
  <type>web-log</type>
  <use_own_name>true</use_own_name>
  <prematch offset="after_parent">^log":"\S+ \S+ \S+ \.*[\S+ \S\d+] \.*"\w+ \S+ HTTP\S+" \d+</prematch>
  <regex offset="after_parent">^log":"(\S+) \S+ \S+ \.*[\S+ \S\d+] \.*"(\w+) (\S+) HTTP\S+" (\d+)</regex>
  <order>srcip,protocol,url,id</order>
</decoder>

<decoder name="json">
  <parent>json</parent>
  <use_own_name>true</use_own_name>
  <plugin_decoder>JSON_Decoder</plugin_decoder>
</decoder>
```

Decoder pertama mengambil IP address sumber, HTTP method, URL, dan status code dari log yang sudah dibungkus JSON. Dengan `<type>web-log</type>`, event hasil decoding masuk ke rules web bawaan Wazuh, sehingga deteksi serangan web seperti SQL injection dan directory traversal langsung berlaku tanpa menulis rule baru.

Decoder `json` yang kedua adalah penadah: log container yang tidak memenuhi kriteria decoder pertama tetap didecode sebagai JSON biasa, bukan dibuang.

Uji decoder dengan `wazuh-logtest`, memakai satu baris asli dari file log container, lalu restart manager:

```
# /var/ossec/bin/wazuh-analysisd -t
# systemctl restart wazuh-manager
```

## Uji konfigurasi

Jalankan web container lalu kirim request yang memicu rule web bawaan:

```
# docker run -d --name web-test -p 8080:80 httpd
$ curl "http://localhost:8080/index.html?id=1' OR '1'='1"
```

Alert harus muncul di modul Threat Hunting dengan group `web` atau `attack`, tergantung rule yang cocok.

## Verifikasi

Pastikan Logcollector membaca file log container:

```
# grep -i "containers" /var/ossec/logs/ossec.log | tail -n 10
```

Kalau tidak ada baris `Analyzing file`, periksa permission directory `/var/lib/docker/containers`. Directory itu hanya bisa dibaca root secara default.

## Catatan

Log runtime hanya tersedia selama container dan log file-nya ada. Container yang dihapus dengan `docker rm` membawa serta log file-nya. Untuk menyimpan jejaknya, pakai logging driver yang mengirim log ke luar host, atau pastikan event sudah sampai ke Wazuh indexer sebelum container dihapus.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/container-security/use-cases.html>
