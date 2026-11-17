# System inventory: Syscollector dan IT Hygiene

Syscollector mengumpulkan inventory sistem dari endpoint: hardware, sistem operasi, network, paket terpasang, port, proses, user, group, service, dan browser extension. Data ini dipakai dua hal: menjawab pertanyaan inventory di dashboard, dan menyuplai modul Vulnerability Detection.

Modul ini aktif secara default di semua agent.

## Konfigurasi di agent

```xml
<!-- System inventory -->
<wodle name="syscollector">
  <disabled>no</disabled>
  <interval>1h</interval>
  <scan_on_start>yes</scan_on_start>
  <hardware>yes</hardware>
  <os>yes</os>
  <network>yes</network>
  <packages>yes</packages>
  <ports all="yes">yes</ports>
  <processes>yes</processes>
  <users>yes</users>
  <groups>yes</groups>
  <services>yes</services>
  <browser_extensions>yes</browser_extensions>

  <!-- Database synchronization settings -->
  <synchronization>
    <max_eps>10</max_eps>
  </synchronization>
</wodle>
```

| Tag | Default | Keterangan |
| --- | --- | --- |
| `disabled` | `no` | Mematikan modul |
| `interval` | `1h` | Jarak antar scan, diisi angka dengan suffix `s`, `m`, `h`, atau `d` |
| `scan_on_start` | `yes` | Memulai scan segera setelah service agent direstart |
| `hardware` | `yes` | Informasi hardware |
| `os` | `yes` | Informasi sistem operasi |
| `network` | `yes` | Interface dan konfigurasi network |
| `packages` | `yes` | Paket terpasang, menyuplai vulnerability detection |
| `ports all="yes"` | `yes` | Scan port. Atribut `all="yes"` memindai semua port, `all="no"` hanya port listening |
| `processes` | `yes` | Proses yang berjalan |
| `users` | `yes` | User account |
| `groups` | `yes` | Group user account |
| `services` | `yes` | Windows service dan systemd unit |
| `browser_extensions` | `yes` | Browser extension di Chrome, Firefox, Safari, dan lainnya |
| `max_eps` | `10` | Batas throughput pelaporan event per detik, 0 sampai 1000000 |

Atribut `all` pada `<ports>` punya perilaku khusus: file `ossec.conf` yang dipasang installer mengisi `all="yes"`, tapi kalau atribut itu dihilangkan, agent hanya memindai port listening.

Di Windows tersedia tambahan opsi `<hotfixes>` untuk mengumpulkan daftar patch terpasang.

Restart agent setelah mengubah konfigurasi. Kalau perubahan dikirim lewat centralized configuration, restart manual tidak diperlukan.

## Konfigurasi di Wazuh server

Modul Inventory Harvester di Wazuh manager memproses data inventory dan mengirimkannya ke Wazuh indexer lewat blok `<indexer>` yang sama dengan yang dipakai vulnerability detection. Blok itu aktif secara default; kalau hilang, lihat [chapter 07](../07-vulnerability-detection/01-cara-kerja-dan-konfigurasi.md) untuk cara menambahkannya beserta pengisian keystore.

## Yang baru di 4.14.0

Rilis 4.14.0 memperluas inventory dengan:

- Browser extensions, dengan model data terpadu untuk Windows, macOS, dan Linux. Berguna untuk audit extension yang terpasang di browser karyawan.
- Services, berupa inventory ternormalisasi untuk Windows service dan systemd unit, termasuk status dan tipe startup.
- Users dan groups, lintas platform dengan struktur data yang konsisten.

Ketiganya juga tersedia lewat endpoint Syscollector di Wazuh server API, dan muncul sebagai tab di modul IT Hygiene pada dashboard.

## Pertimbangan beban

Syscollector memindai seluruh paket, proses, dan port. Di endpoint dengan ribuan paket, scan ini tidak gratis. Yang bisa disesuaikan:

- Naikkan `<interval>` kalau inventory tidak perlu sesering satu jam.
- Matikan kategori yang tidak anda pakai. Jangan matikan `<packages>` kalau anda masih memakai vulnerability detection; itu memutus sumber datanya.
- Turunkan `<max_eps>` kalau agent membanjiri server saat sinkronisasi awal.

## Verifikasi

Di dashboard, buka modul IT Hygiene pada salah satu agent. Setiap tab harus terisi: System, Networks, Packages, Processes, Users & Groups, Services, dan Browser Extensions.

Lewat API:

```
# curl -k -X GET "https://<WAZUH_MANAGER_IP>:55000/syscollector/001/packages?pretty=true&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

Kalau tab kosong, picu scan dengan merestart agent, lalu tunggu sebentar. Scan pertama di endpoint besar bisa memakan waktu beberapa menit.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/system-inventory/configuration.html>
- <https://documentation.wazuh.com/current/user-manual/capabilities/system-inventory/available-inventory-fields.html>
