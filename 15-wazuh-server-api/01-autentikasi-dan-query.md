# Wazuh server API: autentikasi dan query

Wazuh server API dipakai untuk mengelola agent, membaca konfigurasi, dan mengambil data inventory secara terprogram. Dashboard sendiri memakai API ini di belakang layar.

API terpasang otomatis dan berjalan sebagai bagian dari service Wazuh manager:

```
# systemctl start/status/stop/restart wazuh-manager
```

## API Console di dashboard

Cara tercepat mencoba API tanpa menyiapkan token:

1. Login ke dashboard dengan user yang punya privilege administrator, misalnya `admin`.
2. Buka Server management > Dev Tools.
3. Pilih HTTP method, tulis endpoint seperti `/agents` atau `/manager/info`, tambahkan query parameter seperti `?pretty=true&limit=10`, lalu klik tombol play.

Semua request dari console ini diautentikasi memakai session dashboard anda.

## Autentikasi lewat command line

Semua endpoint kecuali endpoint login membutuhkan JSON Web Token (JWT).

Ambil token dan simpan ke variable:

```
# TOKEN=$(curl -u <WAZUH_API_USER>:<WAZUH_API_PASSWORD> -k -X POST "https://localhost:55000/security/user/authenticate?raw=true")
```

Parameter `raw=true` membuat API mengembalikan token sebagai teks biasa, yang jauh lebih mudah dipakai di shell daripada JSON. Opsi `-k` dibutuhkan selama API masih memakai sertifikat self-signed.

Kredensial default API adalah `wazuh:wazuh` dan harus diganti setelah instalasi. Kalau Wazuh dipasang memakai installation assistant, user API-nya adalah `wazuh` dan password-nya bisa diambil dari file instalasi:

```
# tar -axf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt -O | grep -P "\'wazuh\'" -A 1
```

Pastikan token terbentuk:

```
# echo $TOKEN
```

Output berupa string panjang berisi tiga bagian yang dipisah titik. Kalau output kosong atau berisi pesan error, periksa kredensial dan konektivitas ke port 55000.

Uji request pertama:

```
# curl -k -X GET "https://localhost:55000/" -H "Authorization: Bearer $TOKEN"
```

Jawabannya berisi judul API, `api_version`, `revision`, informasi lisensi, hostname, dan timestamp. Nilai `api_version` mengikuti versi Wazuh yang anda pasang.

Token punya masa berlaku. Kalau request yang sebelumnya berhasil mulai menjawab 401, ambil token baru.

## Query yang sering dipakai

Daftar agent:

```
# curl -k -X GET "https://localhost:55000/agents?pretty=true&limit=20" -H "Authorization: Bearer $TOKEN"
```

Agent yang terputus:

```
# curl -k -X GET "https://localhost:55000/agents?status=disconnected&pretty=true" -H "Authorization: Bearer $TOKEN"
```

Informasi manager:

```
# curl -k -X GET "https://localhost:55000/manager/info?pretty=true" -H "Authorization: Bearer $TOKEN"
```

Paket terpasang di satu agent:

```
# curl -k -X GET "https://localhost:55000/syscollector/001/packages?pretty=true&limit=5" -H "Authorization: Bearer $TOKEN"
```

Membuat agent group:

```
# curl -k -X POST "https://localhost:55000/groups?pretty=true" \
  -H "Content-Type: application/json" \
  -d '{"group_id": "Linux"}' \
  -H "Authorization: Bearer $TOKEN"
```

Memasukkan agent ke group:

```
# curl -k -X PUT "https://localhost:55000/agents/002/group/Linux?pretty=true" -H "Authorization: Bearer $TOKEN"
```

Merestart satu agent:

```
# curl -k -X PUT "https://localhost:55000/agents/002/restart?pretty=true" -H "Authorization: Bearer $TOKEN"
```

## Query parameter umum

| Parameter | Fungsi |
| --- | --- |
| `pretty=true` | Output JSON yang dirapikan |
| `limit` dan `offset` | Paginasi hasil |
| `select` | Memilih field yang dikembalikan |
| `sort` | Mengurutkan hasil, awali nama field dengan `-` untuk urutan menurun |
| `q` | Query filter, misalnya `q=status=active` |
| `search` | Pencarian teks bebas |

Nilai `limit` punya batas maksimum dari sisi server. Untuk mengambil banyak data, lakukan paginasi dengan `offset`, jangan menaikkan `limit` sebesar-besarnya.

## Catatan untuk cluster

Pada deployment multi-node, jalankan request ke master node. Beberapa operasi, misalnya yang mengubah konfigurasi, hanya diterima di master.

## Verifikasi

Kalau request gagal, bedakan dulu penyebabnya:

| Gejala | Kemungkinan |
| --- | --- |
| Koneksi tertolak | Service `wazuh-manager` mati atau port 55000 diblokir |
| HTTP 401 | Token kedaluwarsa atau kredensial salah |
| HTTP 403 | Token sah tapi user tidak punya izin, lihat [02-rbac.md](02-rbac.md) |
| Error sertifikat | Sertifikat self-signed, tambahkan `-k` atau pasang CA yang dipercaya |

## Referensi

- <https://documentation.wazuh.com/current/user-manual/api/getting-started.html>
- <https://documentation.wazuh.com/current/user-manual/api/reference.html>
