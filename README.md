# wazuh-learn

Materi belajar Wazuh dalam bahasa Indonesia, disusun per chapter. Tiap chapter memuat konfigurasi, command, dan langkah verifikasi untuk satu kemampuan Wazuh.

Acuan: dokumentasi resmi Wazuh **4.14.10** (rilis 5 November 2026), dibaca pada 17 November 2026. Istilah teknis dibiarkan dalam bahasa Inggris (agent, indexer, dashboard, rules, decoder, active response, browser) supaya cocok dengan nama tag konfigurasi, output command, dan label di dashboard.

## Daftar chapter

| Chapter | Isi |
| --- | --- |
| [01 Pengenalan](01-pengenalan/) | Arsitektur, komponen, dan persiapan lab |
| [02 Instalasi](02-instalasi/) | Server all-in-one, step by step, agent Linux/Windows/macOS, enrollment |
| [03 Manajemen agent](03-manajemen-agent/) | Agent group, centralized configuration, listing, remove |
| [04 Log data collection](04-log-data-collection/) | File log, journald, syslog remote |
| [05 Decoder dan rules](05-decoder-dan-rules/) | Custom decoder, custom rules, wazuh-logtest |
| [06 File Integrity Monitoring](06-file-integrity-monitoring/) | Konfigurasi FIM, who-data, custom FIM rules |
| [07 Vulnerability detection](07-vulnerability-detection/) | Cara kerja, konfigurasi, mode offline |
| [08 Security Configuration Assessment](08-security-configuration-assessment/) | Enable/disable policy, distribusi policy |
| [09 Malware detection](09-malware-detection/) | CDB list, VirusTotal, YARA, Rootcheck |
| [10 System inventory](10-system-inventory/) | Syscollector dan IT Hygiene |
| [11 auditd](11-auditd/) | File access dan command yang dijalankan sebagai root |
| [12 Docker monitoring](12-docker-monitoring/) | Docker listener dan container runtime log |
| [13 Active response](13-active-response/) | Konfigurasi, blokir SSH brute force, custom script |
| [14 Integrasi notifikasi](14-integrasi-notifikasi/) | Slack dan Telegram |
| [15 Wazuh server API](15-wazuh-server-api/) | Autentikasi, query, RBAC |
| [16 Operasional](16-operasional/) | Upgrade, log, troubleshooting |

## Konvensi penulisan

Prompt di dalam code block menandakan hak akses yang dibutuhkan:

```
# command dijalankan sebagai root
$ command dijalankan sebagai user biasa
```

Nilai dalam tanda kurung sudut harus diganti, misalnya `<WAZUH_MANAGER_IP>`, `<ADMIN_PASSWORD>`, `<PATH_TO_MONITORED_DIRECTORY>`.

Path file konfigurasi berbeda per sistem operasi:

| Komponen | Path instalasi | File konfigurasi utama |
| --- | --- | --- |
| Wazuh server | `/var/ossec` | `/var/ossec/etc/ossec.conf` |
| Agent Linux/Unix | `/var/ossec` | `/var/ossec/etc/ossec.conf` |
| Agent Windows | `C:\Program Files (x86)\ossec-agent` | `C:\Program Files (x86)\ossec-agent\ossec.conf` |
| Agent macOS | `/Library/Ossec` | `/Library/Ossec/etc/ossec.conf` |

Setiap chapter ditutup dengan langkah verifikasi. Kalau langkah verifikasi tidak menghasilkan apa pun, konfigurasi belum jalan, dan jangan lanjut ke chapter berikutnya.

## Catatan versi

Wazuh 4.x memuat beberapa perubahan yang membuat tutorial lama tidak lagi akurat:

- Sejak 4.8.0 Vulnerability Detection memakai feed dari Wazuh CTI dan menyimpan hasil inventory di Wazuh indexer, bukan lagi modul `vulnerability-detector` dengan feed per-OS.
- Sejak 4.13.0 FIM dan log collection di Windows tidak lagi mendukung UNC path maupun mapped network drive.
- Sejak 4.14.0 inventory mencakup browser extensions, services, users, dan groups; agent Linux mendukung hot reload untuk remote configuration.
- Who-data FIM di Linux bisa memakai provider `ebpf` selain `audit`.

Kalau Wazuh sudah naik ke versi berikutnya, bandingkan dulu dengan dokumentasi resmi sebelum memakai command di repo ini.

## Sumber dan status pengujian

Seluruh command, tag konfigurasi, rule ID, dan nama field di repo ini diambil dari dokumentasi resmi <https://documentation.wazuh.com/current/> versi 4.14.10. Setiap chapter mencantumkan halaman sumbernya di bagian Referensi, supaya bisa dibandingkan sendiri.

Penjelasan, urutan langkah, catatan beban, dan catatan kesalahan umum ditulis sendiri, bukan terjemahan.

Yang sudah diuji: script integrasi Telegram di [14-integrasi-notifikasi/files/](14-integrasi-notifikasi/files/), dijalankan terhadap HTTP endpoint lokal untuk jalur sukses dan enam jalur gagal (argumen kurang, chat ID kosong, file alert hilang, file alert rusak, endpoint mati, dan jawaban HTTP 401).

Yang belum diuji ulang: command dan konfigurasi di chapter lain belum dijalankan ulang di lab saat materi ini disusun. Jalankan langkah verifikasi di akhir tiap chapter sebelum memakainya di lingkungan yang dipakai orang lain.
