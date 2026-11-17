# Instalasi agent Linux

Agent dipasang di endpoint yang dipantau dan mengirim data ke Wazuh manager lewat channel terenkripsi. Semua command di bawah butuh akses root.

## Tambahkan repository Wazuh

APT (Debian, Ubuntu):

```
# apt-get update && apt-get install gnupg apt-transport-https curl
# curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
# echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
# apt-get update
```

Yum atau DNF (RHEL, CentOS, Amazon Linux). Untuk RHEL 9 ke atas gunakan `priority=1`, untuk RHEL 8 ke bawah gunakan `protect=1`:

```
# rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH
# cat > /etc/yum.repos.d/wazuh.repo << REPOEOF
[wazuh]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=EL-\$releasever - Wazuh
baseurl=https://packages.wazuh.com/4.x/yum/
priority=1
REPOEOF
```

Nama delimiter heredoc di atas bebas; dokumentasi resmi memakai `EOF`.

## Pasang agent

Variable `WAZUH_MANAGER` diisi IP address atau hostname Wazuh manager. Variable ini dibaca saat instalasi untuk sekaligus melakukan enrollment, jadi jangan dilewat:

```
# WAZUH_MANAGER="<WAZUH_MANAGER_IP>" apt-get install wazuh-agent
```

Untuk Yum, DNF, atau Zypper, ganti package manager-nya:

```
# WAZUH_MANAGER="<WAZUH_MANAGER_IP>" yum install wazuh-agent
# WAZUH_MANAGER="<WAZUH_MANAGER_IP>" dnf install wazuh-agent
# WAZUH_MANAGER="<WAZUH_MANAGER_IP>" zypper install wazuh-agent
```

Deployment variable lain yang sering dipakai bersamaan:

| Variable | Fungsi |
| --- | --- |
| `WAZUH_AGENT_NAME` | Nama agent di dashboard, default-nya hostname endpoint |
| `WAZUH_AGENT_GROUP` | Group agent, harus sudah dibuat lebih dulu di server |
| `WAZUH_REGISTRATION_PASSWORD` | Password enrollment kalau authd memakai password |

Contoh dengan nama dan group:

```
# WAZUH_MANAGER="<WAZUH_MANAGER_IP>" WAZUH_AGENT_NAME="web-01" WAZUH_AGENT_GROUP="Linux" apt-get install wazuh-agent
```

Kalau seluruh deployment variable dihilangkan, agent terpasang tanpa ter-enroll dan harus didaftarkan manual. Lihat [06-enrollment-dan-troubleshooting.md](06-enrollment-dan-troubleshooting.md).

## Nyalakan service

```
# systemctl daemon-reload
# systemctl enable wazuh-agent
# systemctl start wazuh-agent
```

Pada sistem tanpa systemd:

```
# /var/ossec/bin/wazuh-control start
```

## Matikan repository

Agent tidak boleh lebih baru dari manager. Matikan repository supaya `apt upgrade` rutin tidak menaikkan versi agent melewati versi manager:

```
# sed -i "s/^deb /#deb/" /etc/apt/sources.list.d/wazuh.list
# apt-get update
```

Alternatifnya, tahan paketnya saja supaya masih bisa di-upgrade manual:

```
# echo "wazuh-agent hold" | dpkg --set-selections
```

## Verifikasi

Di endpoint:

```
# systemctl status wazuh-agent
# tail -n 20 /var/ossec/logs/ossec.log
```

Baris yang dicari adalah `Connected to the server`. Kalau yang berulang adalah `Unable to connect to any server`, periksa nilai `<address>` di `/var/ossec/etc/ossec.conf` dan jalur network ke port 1514.

Di dashboard, buka Agents management > Summary. Agent baru harus muncul dengan status Active.

## Referensi

- <https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-linux.html>
- <https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/deployment-variables/deployment-variables-linux.html>
