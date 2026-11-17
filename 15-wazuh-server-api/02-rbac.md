# RBAC Wazuh server API

RBAC mengatur siapa boleh melakukan apa lewat Wazuh server API. Tanpa pengaturan ini, setiap integrasi yang butuh membaca daftar agent harus memakai kredensial yang juga bisa merestart seluruh fleet.

## Empat komponen

**Users** adalah entitas yang mengirim request ke endpoint API.

**Roles** adalah kumpulan hak akses, yang dibentuk dari rules dan policies yang dikaitkan padanya.

**Rules** adalah kondisi yang menentukan kapan sebuah role berlaku.

**Policies** adalah izin spesifik yang menentukan aksi apa yang diperbolehkan terhadap resource apa.

Role diberikan ke user, bukan policy satu per satu. Dengan begitu, mengubah satu role langsung berlaku untuk semua user yang memakainya, dan anda tidak perlu menyentuh tiap user.

## Isi sebuah policy

Policy dibentuk dari tiga elemen: actions, resources, dan effect.

**Actions** adalah hirarki aksi yang bisa dilakukan user, ditulis sebagai `component:action`:

```
agent:restart
```

**Resources** adalah entitas yang menjadi sasaran aksi. Tipe resource sudah ditetapkan Wazuh.

**Effect** menentukan apakah kombinasi action dan resource itu diizinkan atau ditolak.

## Contoh pembagian role

Pembagian berikut adalah contoh penerapan prinsip privilege minimum:

Security analyst mendapat akses baca saja ke data monitoring dan laporan insiden. Mereka bisa menganalisis dan mengenali ancaman tanpa bisa mengubah konfigurasi atau data.

Security engineer mendapat izin baca, ubah, dan hapus terhadap policies, rules, dan konfigurasi sistem. Mereka bisa menyesuaikan policy keamanan, mengubah konfigurasi, dan memperbarui rules sebagai respons terhadap insiden.

Untuk integrasi otomatis, misalnya script yang mengambil daftar agent untuk laporan, buat user terpisah dengan role baca saja. Memakai user `wazuh` default untuk semua kebutuhan berarti setiap script memegang izin untuk merestart agent dan mengubah konfigurasi.

## Contoh lengkap: user baca saja untuk sekumpulan agent

Urutannya selalu sama: buat policy, buat role, kaitkan policy ke role, buat user, kaitkan role ke user.

Buat policy yang hanya mengizinkan membaca empat agent tertentu:

```
# curl -k -X POST "https://localhost:55000/security/policies?pretty=true" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"customer_x_agents","policy":{"actions":["agent:read"],"resources":["agent:id:001","agent:id:002","agent:id:003","agent:id:004"],"effect":"allow"}}'
```

Buat role:

```
# curl -k -X POST "https://localhost:55000/security/roles?pretty=true" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"team-alpha"}'
```

Kaitkan policy ke role. Ganti ID-nya dengan nilai dari jawaban dua command sebelumnya:

```
# curl -k -X POST "https://localhost:55000/security/roles/<ROLE_ID>/policies?policy_ids=<POLICY_ID>&pretty=true" \
  -H "Authorization: Bearer $TOKEN"
```

Buat user:

```
# curl -k -X POST "https://localhost:55000/security/users?pretty=true" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"alpha-member-1","password":"<PASSWORD>"}'
```

Kaitkan role ke user:

```
# curl -k -X POST "https://localhost:55000/security/users/<USER_ID>/roles?role_ids=<ROLE_ID>&pretty=true" \
  -H "Authorization: Bearer $TOKEN"
```

Untuk melihat ID yang sudah ada, pakai endpoint `GET`:

```
# curl -k -X GET "https://localhost:55000/security/users?pretty=true" -H "Authorization: Bearer $TOKEN"
# curl -k -X GET "https://localhost:55000/security/roles?pretty=true" -H "Authorization: Bearer $TOKEN"
# curl -k -X GET "https://localhost:55000/security/policies?pretty=true" -H "Authorization: Bearer $TOKEN"
```

## Ketika policy saling bertentangan

Sebuah role bisa memuat beberapa policy, dan policy itu bisa bertentangan: satu mengizinkan membaca agent 001, satu lagi menolaknya. Yang berlaku adalah policy yang ditambahkan paling akhir, yaitu yang muncul terakhir saat anda melihat daftar policy sebuah role lewat `GET /security/roles`.

Urutan itu bisa diatur dengan parameter `position` saat mengaitkan policy ke role:

```
# curl -k -X POST "https://localhost:55000/security/roles/<ROLE_ID>/policies?policy_ids=<POLICY_ID>&position=0&pretty=true" \
  -H "Authorization: Bearer $TOKEN"
```

Parameter yang sama tersedia saat mengaitkan role ke user.

## Verifikasi

Ambil token memakai user baru, lalu coba dua hal: satu endpoint yang seharusnya diizinkan, dan satu yang seharusnya ditolak.

```
# TOKEN_ALPHA=$(curl -u alpha-member-1:<PASSWORD> -k -X POST "https://localhost:55000/security/user/authenticate?raw=true")
# curl -k -X GET "https://localhost:55000/agents?pretty=true&limit=1" -H "Authorization: Bearer $TOKEN_ALPHA"
# curl -k -X PUT "https://localhost:55000/agents/002/restart?pretty=true" -H "Authorization: Bearer $TOKEN_ALPHA"
```

Request kedua harus dijawab HTTP 403. Kalau justru berhasil, role yang dikaitkan terlalu luas.

Menguji kedua arah seperti ini penting: role yang hanya diuji dengan request yang diizinkan tampak benar walaupun sebenarnya memberi akses penuh.

Untuk melihat policy final yang berlaku pada user yang tokennya sedang dipakai:

```
# curl -k -X GET "https://localhost:55000/security/users/me/policies?pretty=true" -H "Authorization: Bearer $TOKEN_ALPHA"
```

Endpoint ini menjawab pertanyaan yang sering membingungkan saat policy bertumpuk: bukan apa yang anda kaitkan, tapi apa yang akhirnya berlaku.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/api/rbac/how-it-works.html>
- <https://documentation.wazuh.com/current/user-manual/api/rbac/reference.html>
