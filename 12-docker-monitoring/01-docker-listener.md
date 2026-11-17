# Docker listener

Memantau Docker butuh dua lapis: host tempat Docker daemon berjalan, dan aktivitas container itu sendiri. Lapis pertama ditangani Wazuh agent biasa. Lapis kedua ditangani Docker listener.

## Langkah umum

1. Pasang Wazuh agent di Docker server. Agent ini mengamankan infrastruktur Docker dengan memantau host tempat daemon berjalan.
2. Aktifkan Docker listener untuk memantau aktivitas container. Listener berjalan di agent tersebut dan meneruskan log Docker ke Wazuh server.

## Dependency Python

Modul Docker listener butuh Python 3, kompatibel dengan versi 3.8 sampai 3.13. Versi yang lebih baru umumnya jalan tapi tidak dijamin.

Integrasi ini butuh library `docker` versi 7.1.0:

```
$ pip3 install docker==7.1.0 urllib3==1.26.20 requests==2.32.2
```

Untuk Python 3.11 dan 3.12 yang memakai externally managed environment:

```
$ pip3 install docker==7.1.0 urllib3==1.26.20 requests==2.32.2 --break-system-packages
```

Flag `--break-system-packages` mengubah environment Python sistem. Kalau anda tidak ingin itu terjadi, pasang dependency di virtual environment lalu ubah shebang pada `/var/ossec/wodles/docker/DockerListener` menjadi interpreter virtual environment tersebut:

```
#!</path/to/your/virtual/environment>/bin/python3
```

Dependency ini hanya perlu dipasang di agent. Wazuh manager sudah membawa semuanya.

## Konfigurasi agent

Tambahkan blok berikut ke `/var/ossec/etc/ossec.conf` di Docker server:

```xml
<wodle name="docker-listener">
  <disabled>no</disabled>
</wodle>
```

Restart agent:

```
# systemctl restart wazuh-agent
```

## Opsi konfigurasi

Opsi utama:

| Tag | Default | Keterangan |
| --- | --- | --- |
| `disabled` | `no` | Mematikan listener |
| `attempts` | `5` | Jumlah percobaan menjalankan listener kalau gagal |

Opsi penjadwalan:

| Tag | Default | Keterangan |
| --- | --- | --- |
| `run_on_start` | `yes` | Menjalankan listener segera setelah agent start |
| `interval` | `1m` | Jeda sebelum mencoba menjalankan listener lagi kalau gagal |
| `day` | tidak diisi | Tanggal dalam bulan, 1 sampai 31. Kalau diisi, `interval` harus kelipatan bulan |
| `wday` | tidak diisi | Hari dalam minggu, `sunday` sampai `saturday` atau singkatannya. Tidak bisa dipakai bersama `day` |
| `time` | tidak diisi | Jam dalam format `hh:mm` |

Contoh listener yang mencoba lima kali dengan jeda sepuluh menit dan tidak jalan saat agent start:

```xml
<wodle name="docker-listener">
  <interval>10m</interval>
  <attempts>5</attempts>
  <run_on_start>no</run_on_start>
  <disabled>no</disabled>
</wodle>
```

## Uji konfigurasi

Jalankan serangkaian aksi Docker di host:

```
# docker run -d --name test-container httpd
# docker pause test-container
# docker unpause test-container
# docker stop test-container
# docker rm test-container
# docker rmi httpd
```

Setiap aksi menghasilkan satu alert. Contoh alert ketika container dinyalakan:

```json
{
  "data": {
    "integration": "docker",
    "docker": {
      "Type": "container",
      "Action": "start",
      "Actor": {
        "Attributes": {
          "image": "httpd",
          "name": "test-container"
        },
        "ID": "d47511d28ebf226e6bebff7be58ba8b03cb62fba7686a877e565d837e3d438da"
      },
      "status": "start"
    }
  },
  "rule": {
    "level": 3,
    "description": "Docker: Container test-container started",
    "groups": ["docker"],
    "id": "87903"
  },
  "location": "Wazuh-Docker"
}
```

## Verifikasi

Di dashboard, buka modul Docker listener atau Threat Hunting dan cari event dengan group `docker`.

Kalau tidak ada event sama sekali, periksa listener benar-benar berjalan:

```
# grep -i docker /var/ossec/logs/ossec.log | tail -n 20
```

Penyebab paling sering adalah dependency Python yang belum terpasang, atau user yang menjalankan listener tidak punya akses ke Docker socket.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/container-security/monitoring-docker.html>
