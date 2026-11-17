# Instalasi agent macOS

Pilih paket sesuai arsitektur:

- Intel: `wazuh-agent-4.14.10-1.intel64.pkg`, untuk macOS Sierra ke atas.
- Apple silicon: `wazuh-agent-4.14.10-1.arm64.pkg`, untuk macOS Big Sur ke atas.

Semua command butuh akses root.

## Instalasi lewat CLI

Deployment variable di macOS dikirim lewat file `/tmp/wazuh_envs`, bukan sebagai prefix command seperti di Linux.

Intel:

```
# curl -O https://packages.wazuh.com/4.x/macos/wazuh-agent-4.14.10-1.intel64.pkg
# echo "WAZUH_MANAGER='<WAZUH_MANAGER_IP>'" > /tmp/wazuh_envs && sudo installer -pkg wazuh-agent-4.14.10-1.intel64.pkg -target /
```

Apple silicon:

```
# curl -O https://packages.wazuh.com/4.x/macos/wazuh-agent-4.14.10-1.arm64.pkg
# echo "WAZUH_MANAGER='<WAZUH_MANAGER_IP>'" > /tmp/wazuh_envs && sudo installer -pkg wazuh-agent-4.14.10-1.arm64.pkg -target /
```

## Nyalakan agent

```
# launchctl bootstrap system /Library/LaunchDaemons/com.wazuh.agent.plist
```

## Lokasi file

Semua file agent ada di `/Library/Ossec/`, dengan file konfigurasi utama `/Library/Ossec/etc/ossec.conf`.

Restart agent:

```
# /Library/Ossec/bin/wazuh-control restart
```

## Verifikasi

```
# /Library/Ossec/bin/wazuh-control status
# tail -n 20 /Library/Ossec/logs/ossec.log
```

## Catatan FIM di macOS

Default `<directories>` untuk FIM di agent macOS adalah `/private/etc,/usr/bin,/usr/sbin,/bin,/sbin`, bukan `/etc`, karena `/etc` di macOS hanya symbolic link ke `/private/etc`. Rule atau filter yang mencocokkan path `/etc/...` tidak akan kena di macOS.

## Referensi

- <https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-macos.html>
