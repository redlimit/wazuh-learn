# Instalasi all-in-one dengan installation assistant

Cara tercepat menyiapkan Wazuh server, indexer, dan dashboard di satu host. Jalankan sebagai root.

## Langkah instalasi

Download installation assistant dan jalankan dengan opsi `-a`:

```
# curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh && bash ./wazuh-install.sh -a
```

Proses ini memakan waktu beberapa menit. Assistant mengunduh paket, membuat sertifikat SSL, membuat password acak, lalu menyalakan ketiga komponen. Jangan hentikan di tengah jalan.

Instalasi berhasil kalau output diakhiri ringkasan seperti ini:

```
INFO: --- Summary ---
INFO: You can access the web interface https://<WAZUH_DASHBOARD_IP_ADDRESS>
    User: admin
    Password: <ADMIN_PASSWORD>
INFO: Installation finished.
```

## Mengambil seluruh password

Assistant membuat file `wazuh-install-files.tar` di directory tempat ia dijalankan. File itu berisi semua password user Wazuh indexer dan Wazuh server API:

```
# tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

Simpan file tar ini di tempat yang aman dan bisa diakses lagi. Kalau anda bekerja di `/tmp`, pindahkan segera: isi `/tmp` dibersihkan secara berkala dan tanpa file ini anda harus reset password secara manual.

## Akses dashboard

Buka `https://<WAZUH_DASHBOARD_IP_ADDRESS>` di browser, login dengan user `admin` dan password dari ringkasan instalasi.

Browser akan menampilkan peringatan bahwa sertifikat tidak diterbitkan otoritas terpercaya. Itu wajar, karena assistant membuat sertifikat self-signed. Terima sebagai exception untuk lab, atau pasang sertifikat dari CA terpercaya untuk produksi.

## Menonaktifkan repository Wazuh

Setelah instalasi selesai, Wazuh menyarankan mematikan repository supaya tidak ada upgrade tidak sengaja yang merusak environment. Upgrade komponen pusat harus direncanakan, bukan ikut terbawa `apt upgrade` rutin.

APT:

```
# sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list
# apt update
```

Yum atau DNF:

```
# sed -i "s/^enabled=1/enabled=0/" /etc/yum.repos.d/wazuh.repo
```

## Verifikasi

Cek status ketiga service:

```
# systemctl status wazuh-manager wazuh-indexer wazuh-dashboard
```

Cek indexer menjawab, masukkan password `admin` saat diminta:

```
# curl -k -u admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200
```

Output yang benar berisi `"cluster_name" : "wazuh-indexer-cluster"` dan `"number" : "7.10.2"` pada bagian version. Versi 7.10.2 di situ adalah versi engine indexer, bukan versi Wazuh.

## Uninstall

Jalankan assistant dengan opsi `-u` atau `--uninstall`:

```
# bash ./wazuh-install.sh -u
```

## Referensi

- <https://documentation.wazuh.com/current/quickstart.html>
