# Arsitektur dan komponen Wazuh

Wazuh terdiri dari satu agent multi-platform dan tiga komponen pusat. Memahami pembagian tugas keempat komponen ini menentukan di mana sebuah konfigurasi harus ditulis, dan itu sumber kesalahan paling sering saat belajar Wazuh.

## Empat komponen

**Wazuh agent** dipasang di endpoint yang dipantau: laptop, desktop, server, cloud instance, atau virtual machine. Agent mengumpulkan log, inventory, dan event file system, lalu mengirimkannya ke server lewat channel terenkripsi. Agent tersedia untuk Linux, Windows, macOS, Solaris, AIX, dan HP-UX.

**Wazuh server** menganalisis data dari agent. Data melewati decoder untuk dipecah menjadi field, lalu dicocokkan dengan rules untuk menghasilkan alert. Server juga yang mengelola agent: mendaftarkan, mengirim konfigurasi, dan melakukan remote upgrade.

**Wazuh indexer** adalah search engine yang mengindeks dan menyimpan alert dari server. Komponen inilah yang membuat pencarian alert lama tetap cepat.

**Wazuh dashboard** adalah web interface untuk visualisasi dan analisis, sekaligus tempat mengelola konfigurasi dan memeriksa status agent.

Wazuh juga bisa memantau perangkat yang tidak bisa dipasangi agent, misalnya firewall, switch, dan router, lewat Syslog atau probing berkala via SSH.

## Alur data

```
endpoint (agent) --1514/tcp--> Wazuh server --Filebeat 9200/tcp--> Wazuh indexer
                                     ^                                   ^
                                     | 55000/tcp (server API)            | 9200/tcp
                                     +---------- Wazuh dashboard --------+
```

Agent mengirim event ke service agent connection di server. Server mendecode dan mencocokkan rules, lalu menulis alert ke `/var/ossec/logs/alerts/alerts.log` dan `alerts.json`. Filebeat membaca output itu dan meneruskannya ke indexer lewat TLS. Dashboard mengambil data alert dari indexer, dan mengambil status serta konfigurasi dari Wazuh server API.

Protokol pesan agent ke server memakai enkripsi AES secara default, 128 bit per block dengan key 256 bit. Blowfish tersedia sebagai opsi.

## Port default

| Komponen | Port | Protokol | Fungsi |
| --- | --- | --- | --- |
| Wazuh server | 1514 | TCP (default) | Agent connection service |
| Wazuh server | 1514 | UDP (opsional) | Agent connection service, mati secara default |
| Wazuh server | 1515 | TCP | Agent enrollment service |
| Wazuh server | 1516 | TCP | Wazuh cluster daemon |
| Wazuh server | 514 | UDP/TCP | Syslog collector, mati secara default |
| Wazuh server | 55000 | TCP | Wazuh server RESTful API |
| Wazuh indexer | 9200 | TCP | Indexer RESTful API |
| Wazuh indexer | 9300-9400 | TCP | Komunikasi cluster indexer |
| Wazuh dashboard | 443 | TCP | Web interface |

## Koneksi keluar yang dibutuhkan

| Sumber | Tujuan | Port | Keperluan |
| --- | --- | --- | --- |
| Wazuh server | `cti.wazuh.com` | 443/TCP | Update feed vulnerability detection dan update check |
| Wazuh server | `packages.wazuh.com` | 443/TCP | Paket WPK untuk remote upgrade agent |
| Semua komponen pusat | `packages.wazuh.com` | 443/TCP | Instalasi dan upgrade komponen pusat |

Kalau server tidak bisa menjangkau `cti.wazuh.com`, vulnerability detection tidak punya data CVE sama sekali. Untuk lingkungan tertutup, pakai mode offline di [chapter 07](../07-vulnerability-detection/02-mode-offline.md).

## Pilihan topologi

**All-in-one.** Server, indexer, dan dashboard di satu host. Ini yang dipakai di materi ini dan cukup untuk lab serta lingkungan kecil.

**Single-node.** Server, indexer, dan dashboard di host terpisah. Untuk lingkungan menengah yang butuh performa lebih tinggi.

**Multi-node.** Satu dashboard, beberapa node server (Wazuh server cluster), dan beberapa node indexer (Wazuh indexer cluster). Untuk event throughput besar atau kebutuhan high availability.

## Di mana konfigurasi ditulis

Pertanyaan ini muncul di hampir setiap chapter berikutnya, jadi hafalkan polanya:

- Konfigurasi yang mengumpulkan data dari endpoint (FIM, log collection, syscollector, Docker listener, SCA) ditulis di agent, atau dikirim ke agent lewat centralized configuration.
- Konfigurasi yang mengolah data (decoder, rules, CDB list, integration, vulnerability detection) ditulis di Wazuh server.
- Active response butuh keduanya: definisi command dan trigger di server, script yang dieksekusi ada di agent.

## Referensi

- <https://documentation.wazuh.com/current/getting-started/components/index.html>
- <https://documentation.wazuh.com/current/getting-started/architecture.html>
