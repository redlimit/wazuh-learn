# Security Configuration Assessment

SCA memeriksa konfigurasi endpoint terhadap policy berbasis benchmark, misalnya CIS. Hasilnya berupa daftar check yang lulus dan gagal, beserta cara memperbaikinya.

Agent sudah membawa policy yang sesuai dengan sistem operasinya sejak instalasi, jadi SCA biasanya sudah berjalan tanpa konfigurasi apa pun.

## Lokasi policy

Agent memindai setiap file `.yaml` atau `.yml` di directory ruleset-nya:

- Linux dan Unix: `/var/ossec/ruleset/sca`
- Windows: `C:\Program Files (x86)\ossec-agent\ruleset\sca`
- macOS: `/Library/Ossec/ruleset/sca`

Isi directory ini tidak dipertahankan saat instalasi atau update. Kalau anda ingin mengubah atau menambah policy, taruh di directory lain, jangan di sini.

## Mematikan policy

Cara paling sederhana adalah mengganti ekstensi file policy menjadi selain `.yaml` atau `.yml`.

Cara kedua lewat konfigurasi agent, dengan path relatif terhadap directory instalasi Wazuh:

```xml
<sca>
  <policies>
    <policy enabled="no">ruleset/sca/<POLICY_FILE_TO_DISABLE></policy>
  </policies>
</sca>
```

Untuk policy yang dikirim lewat centralized configuration, pakai path di `etc/shared` untuk Linux dan macOS:

```xml
<sca>
  <policies>
    <policy enabled="no">etc/shared/<POLICY_FILE_TO_DISABLE></policy>
  </policies>
</sca>
```

Atau di `shared\` untuk Windows:

```xml
<sca>
  <policies>
    <policy enabled="no">shared\<POLICY_FILE_TO_DISABLE></policy>
  </policies>
</sca>
```

Restart agent setelahnya.

## Mendistribusikan policy dari server

Wazuh server bisa mengirim file policy ke agent dalam sebuah group. Contoh berikut memakai group `default`.

Izinkan eksekusi command dalam policy SCA yang dikirim server, di sisi agent:

```
# echo "sca.remote_commands=1" >> /var/ossec/etc/local_internal_options.conf
```

Untuk Windows, tambahkan baris `sca.remote_commands=1` ke `C:\Program Files (x86)\ossec-agent\local_internal_options.conf`. Untuk macOS, ke `/Library/Ossec/etc/local_internal_options.conf`.

Opsi ini mati secara default sebagai langkah keamanan: menyalakannya berarti Wazuh server bisa mengeksekusi command di endpoint, sehingga server yang dikuasai penyerang menjadi jalan masuk ke seluruh fleet. Pertimbangkan dulu sebelum menyalakannya. Kalau anda bisa menempatkan file policy langsung di endpoint, misalnya lewat `scp` atau configuration management, remote command tidak perlu diaktifkan.

Letakkan file policy di group directory pada server dan atur ownership-nya:

```
# chown wazuh:wazuh /var/ossec/etc/shared/default/<NEW_POLICY_FILE>
```

Daftarkan policy di `agent.conf` group tersebut:

```xml
<agent_config os="Linux">
  <sca>
    <policies>
      <policy>etc/shared/<NEW_POLICY_FILE></policy>
    </policies>
  </sca>
</agent_config>

<agent_config os="Windows">
  <sca>
    <policies>
      <policy>shared\<NEW_POLICY_FILE></policy>
    </policies>
  </sca>
</agent_config>
```

Agent menyimpan semua file yang dikirim server di `etc/shared/` untuk Linux dan macOS, dan di `shared\` untuk Windows, tanpa memandang group asalnya. Karena itu path-nya ditulis relatif: directory instalasi berbeda antar sistem operasi.

Blok `<sca>` dari `agent.conf` digabungkan dengan blok `<sca>` di sisi agent, bukan menggantikannya.

## Verifikasi

Di dashboard, buka modul Configuration Assessment pada salah satu agent. Setiap policy menampilkan jumlah check yang lulus, gagal, dan tidak berlaku.

Dari CLI di endpoint:

```
# grep sca /var/ossec/logs/ossec.log | tail -n 20
```

Baris yang menyebut nama file policy menandakan policy itu dimuat. Kalau policy baru tidak muncul, periksa file sudah sampai di `etc/shared/` di endpoint dan nama file di `agent.conf` ditulis tepat.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/sec-config-assessment/how-to-configure.html>
- <https://documentation.wazuh.com/current/user-manual/capabilities/sec-config-assessment/available-sca-policies.html>
