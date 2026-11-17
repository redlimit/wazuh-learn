# Listing dan remove agent

## Listing

Dengan `agent_control`, menampilkan status koneksi:

```
# /var/ossec/bin/agent_control -l
```

```
Wazuh agent_control. List of available agents:
   ID: 000, Name: wazuh-server (server), IP: 127.0.0.1, Active/Local
   ID: 001, Name: ubuntu-agent, IP: 10.0.0.5, Active
   ID: 002, Name: win-agent, IP: any, Never connected
```

Dengan `manage_agents`, menampilkan agent yang terdaftar tanpa status:

```
# /var/ossec/bin/manage_agents -l
```

```
Available agents:
   ID: 001, Name: agent-ubuntu2, IP: any
   ID: 002, Name: agent-ubuntu1, IP: any
```

Lewat API:

```
# curl -k -X GET "https://<WAZUH_MANAGER_IP>:55000/agents?pretty=true&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## Remove agent

Secara interaktif:

```
# /var/ossec/bin/manage_agents
```

```
****************************************
* Wazuh v4.14.10 Agent manager.        *
* The following options are available: *
****************************************
   (A)dd an agent (A).
   (E)xtract key for an agent (E).
   (L)ist already added agents (L).
   (R)emove an agent (R).
   (Q)uit.
Choose your action: A,E,L,R or Q: r

Available agents:
   ID: 002, Name: Ubuntu, IP: any
Provide the ID of the agent to be removed (or '\q' to quit): 002
Confirm deleting it?(y/n): y
Agent '002' removed.
```

Langsung dengan ID agent:

```
# /var/ossec/bin/manage_agents -r <WAZUH_AGENT_ID>
```

Menghapus agent di server hanya mencabut key-nya. Agent di endpoint tetap jalan dan tetap mencoba menyambung. Kalau endpoint itu memang tidak dipakai lagi, hentikan dan uninstall agent di sana juga; kalau akan didaftarkan ulang, hapus `/var/ossec/etc/client.keys` di endpoint sebelum enrollment baru.

## Remote upgrade agent

Wazuh bisa meng-upgrade agent dari server memakai paket WPK, tanpa menyentuh endpoint:

```
# /var/ossec/bin/agent_upgrade -a <WAZUH_AGENT_ID>
```

Lihat daftar agent yang bisa di-upgrade:

```
# /var/ossec/bin/agent_upgrade -l
```

Remote upgrade butuh server bisa menjangkau `packages.wazuh.com` di port 443 untuk mengunduh paket WPK. Untuk upgrade lokal per sistem operasi, lihat [chapter 16](../16-operasional/01-upgrade.md).

## Referensi

- <https://documentation.wazuh.com/current/user-manual/agent/agent-management/listing/using-command-line.html>
- <https://documentation.wazuh.com/current/user-manual/agent/agent-management/remove-agents/remove.html>
- <https://documentation.wazuh.com/current/user-manual/agent/agent-management/remote-upgrading/index.html>
