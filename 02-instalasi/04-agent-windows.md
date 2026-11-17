# Instalasi agent Windows

Agent Windows mendukung Windows XP sampai versi terbaru, termasuk Windows 11 dan Windows Server 2025. Instalasi butuh hak administrator.

## Instalasi lewat CLI

Dengan CMD:

```
> curl.exe -so wazuh-agent-4.14.10-1.msi https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.10-1.msi
> msiexec.exe /i wazuh-agent-4.14.10-1.msi /q WAZUH_MANAGER="<WAZUH_MANAGER_IP>"
```

Dengan PowerShell:

```
> Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.10-1.msi -OutFile wazuh-agent-4.14.10-1.msi
> msiexec.exe /i wazuh-agent-4.14.10-1.msi /q WAZUH_MANAGER="<WAZUH_MANAGER_IP>"
```

Deployment variable lain ditulis setelah `WAZUH_MANAGER`, dipisahkan spasi:

```
> msiexec.exe /i wazuh-agent-4.14.10-1.msi /q WAZUH_MANAGER="<WAZUH_MANAGER_IP>" WAZUH_AGENT_NAME="win-01" WAZUH_AGENT_GROUP="Windows"
```

Nyalakan service:

```
> NET START WazuhSvc
```

Atau dengan PowerShell:

```
> Start-Service wazuhsvc
```

## Instalasi lewat GUI

Jalankan file MSI dan ikuti wizard. Untuk pilihan yang tidak anda kenali, pakai nilai default. Setelah terpasang, agent menyediakan GUI kecil untuk mengisi alamat manager, membuka log, dan start atau stop service.

Instalasi lewat GUI tidak melakukan enrollment. Daftarkan agent setelahnya, lihat [06-enrollment-dan-troubleshooting.md](06-enrollment-dan-troubleshooting.md).

## Lokasi file

Semua file agent ada di `C:\Program Files (x86)\ossec-agent`, dengan file konfigurasi utama `ossec.conf` di directory yang sama.

Restart agent setelah mengubah konfigurasi:

```
> Restart-Service -Name wazuh
```

## Verifikasi

```
> Get-Service WazuhSvc
> Get-Content "C:\Program Files (x86)\ossec-agent\ossec.log" -Tail 20
```

Lalu cek Agents management > Summary di dashboard.

## Catatan

Sejak Wazuh 4.13.0, FIM dan log collection di Windows tidak lagi mendukung UNC path seperti `\\server\share\file.log` maupun mapped network drive seperti `Z:\logs\file.log`. Path semacam itu diabaikan agent tanpa pesan error, jadi tidak ada alert dan tidak ada petunjuk penyebabnya. Hanya local file system yang didukung.

## Referensi

- <https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-windows.html>
