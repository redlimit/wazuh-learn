# Persiapan lab

Materi ini ditulis untuk lab all-in-one: satu VM untuk komponen pusat Wazuh, dan beberapa VM endpoint untuk dipasangi agent.

## Sistem operasi komponen pusat

Komponen pusat Wazuh butuh prosesor Linux 64-bit (x86_64/AMD64 atau AARCH64/ARM64). Versi yang didukung:

- Amazon Linux 2, Amazon Linux 2023
- CentOS Stream 10
- Red Hat Enterprise Linux 7, 8, 9, 10
- Ubuntu 16.04, 18.04, 20.04, 22.04, 24.04

Lab di materi ini memakai Ubuntu 24.04.

## Hardware

Kebutuhan hardware bergantung pada jumlah endpoint, karena jumlah itu menentukan volume data yang dianalisis dan alert yang disimpan. Untuk deployment all-in-one dengan retensi 90 hari:

| Jumlah agent | CPU | RAM | Storage (90 hari) |
| --- | --- | --- | --- |
| 1-25 | 4 vCPU | 8 GiB | 50 GB |
| 26-50 | 8 vCPU | 8 GiB | 100 GB |
| 51-100 | 8 vCPU | 8 GiB | 200 GB |

Untuk lab belajar dengan 2-3 agent, 4 vCPU dan 8 GiB RAM sudah jalan. Indexer adalah komponen yang paling rakus RAM; kalau dashboard sering timeout atau indexer mati sendiri, RAM adalah tersangka pertama.

## Topologi lab yang dipakai di materi ini

| Host | Peran | Catatan |
| --- | --- | --- |
| `wazuh-server` | Wazuh server, indexer, dashboard | Ubuntu 24.04, 4 vCPU, 8 GiB |
| `ubuntu-agent` | Endpoint Linux | Target FIM, auditd, Docker, active response |
| `win-agent` | Endpoint Windows | Target FIM registry dan Event Channel |

Ganti nilai `<WAZUH_MANAGER_IP>` di seluruh materi dengan IP address host `wazuh-server`.

## Sebelum instalasi

Pastikan hal-hal berikut, karena tiga dari empat kegagalan instalasi di lab berasal dari sini:

1. Akses root tersedia di semua host.
2. Jam sistem sinkron. Selisih waktu antara agent dan server membuat alert sulit dikorelasikan dan bisa menolak sertifikat.
3. Port 1514/TCP, 1515/TCP, dan 443/TCP dari endpoint ke server tidak diblokir firewall.
4. Host server bisa menjangkau `packages.wazuh.com` dan `cti.wazuh.com` di port 443.
5. Disk untuk `/var` lega. Indexer menyimpan index di sini dan tidak akan sopan ketika penuh.

## Verifikasi konektivitas

Dari endpoint, cek jalur ke server sebelum memasang agent:

```
$ nc -zv <WAZUH_MANAGER_IP> 1514
$ nc -zv <WAZUH_MANAGER_IP> 1515
```

Kalau salah satu gagal, selesaikan dulu di level network. Agent yang tidak bisa menjangkau port 1515 akan terpasang tapi tidak pernah ter-enroll, dan gejalanya di dashboard terlihat seperti masalah lain.

## Referensi

- <https://documentation.wazuh.com/current/quickstart.html>
- <https://documentation.wazuh.com/current/installation-guide/index.html>
