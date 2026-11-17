# Enrollment agent dan troubleshooting

Enrollment adalah proses agent mendapatkan client key dari Wazuh server. Tanpa key itu, agent terpasang tapi tidak pernah muncul sebagai Active di dashboard.

Kalau agent dipasang dengan deployment variable `WAZUH_MANAGER`, enrollment sudah terjadi otomatis dan chapter ini hanya diperlukan untuk perbaikan.

## Enrollment lewat file konfigurasi agent

Cara ini dipakai saat agent dipasang tanpa deployment variable, misalnya instalasi Windows lewat GUI.

Edit file konfigurasi agent dan isi alamat manager:

```xml
<client>
  <server>
    <address><WAZUH_MANAGER_IP></address>
    <port>1514</port>
    <protocol>tcp</protocol>
  </server>
</client>
```

Dengan alamat ini, agent menghubungi server dan meminta client key secara otomatis.

Parameter enrollment tambahan bersifat opsional:

```xml
<client>
  <enrollment>
    <agent_name>web-01</agent_name>
    <groups>Linux,dbms</groups>
  </enrollment>
</client>
```

`<agent_name>` menentukan nama agent, default-nya hostname endpoint. `<groups>` menentukan group yang diikuti agent. Group harus sudah ada di server lebih dulu; enrollment gagal kalau group yang disebut belum dibuat.

Restart agent:

```
# systemctl restart wazuh-agent
```

Untuk sistem tanpa systemd:

```
# /var/ossec/bin/wazuh-control restart
```

## Cek dari sisi server

Daftar agent beserta statusnya:

```
# /var/ossec/bin/agent_control -l
```

Output menunjukkan ID, nama, IP, dan status tiap agent:

```
Wazuh agent_control. List of available agents:
   ID: 000, Name: wazuh-server (server), IP: 127.0.0.1, Active/Local
   ID: 001, Name: ubuntu-agent, IP: 10.0.0.5, Active
   ID: 002, Name: win-agent, IP: any, Never connected
```

Status `Never connected` berarti key sudah dibuat tapi agent belum pernah terhubung. Ini memisahkan masalah enrollment (port 1515) dari masalah koneksi (port 1514), dan menghemat banyak waktu debugging.

## Masalah yang sering muncul

**Agent tidak muncul di dashboard sama sekali.** Enrollment belum terjadi. Periksa agent bisa menjangkau port 1515, lalu cek `/var/ossec/logs/ossec.log` di endpoint untuk pesan dari `wazuh-agentd` seperti `Requesting a key from server`.

**Status Never connected.** Key sudah ada tapi koneksi ke 1514 gagal. Periksa firewall dan nilai `<address>`.

**Status Disconnected setelah sebelumnya Active.** Agent pernah jalan lalu berhenti berkomunikasi. Cek service agent dan jam sistem di kedua sisi.

**Agent sudah terhapus di dashboard tapi masih mengirim data.** Hapus `/var/ossec/etc/client.keys` di endpoint, lalu lakukan enrollment ulang.

**Nama agent duplikat.** Dua endpoint dengan hostname sama mendaftar sebagai nama yang sama. Gunakan `WAZUH_AGENT_NAME` atau `<agent_name>` yang eksplisit.

## Log yang perlu dibaca

| File | Isi |
| --- | --- |
| `/var/ossec/logs/ossec.log` (endpoint) | Log semua daemon agent, termasuk koneksi dan enrollment |
| `/var/ossec/logs/ossec.log` (server) | Log daemon server, termasuk `wazuh-authd` dan `wazuh-remoted` |
| `/var/ossec/etc/client.keys` (endpoint) | Client key hasil enrollment, kosong berarti belum ter-enroll |

## Referensi

- <https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/index.html>
- <https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/troubleshooting.html>
