# Instalasi per komponen dengan config.yml

Cara ini memakai installation assistant yang sama, tapi memasang indexer, server, dan dashboard satu per satu. Pakai pendekatan ini kalau komponen dipisah ke beberapa host, atau kalau anda ingin melihat tahapannya.

Jalankan semua command sebagai root.

## Tahap 1: konfigurasi awal

Download assistant dan file konfigurasi:

```
# curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh
# curl -sO https://packages.wazuh.com/4.14/config.yml
```

Edit `config.yml` dan isi nama node serta IP address untuk setiap komponen. Untuk instalasi di satu host, isi IP address yang sama di ketiga bagian:

```yaml
nodes:
  # Wazuh indexer nodes
  indexer:
    - name: node-1
      ip: "10.0.0.2"
    #- name: node-2
    #  ip: "<indexer-node-ip>"

  # Wazuh server nodes
  # If there is more than one Wazuh server
  # node, each one must have a node_type
  server:
    - name: wazuh-1
      ip: "10.0.0.2"
    #- name: wazuh-2
    #  ip: "<wazuh-manager-ip>"
    #  node_type: worker

  # Wazuh dashboard nodes
  dashboard:
    - name: dashboard
      ip: "10.0.0.2"
```

Generate cluster key, sertifikat, dan password:

```
# bash wazuh-install.sh --generate-config-files
```

Hasilnya adalah `./wazuh-install-files.tar`. Kalau komponen dipasang di host berbeda, copy file ini ke semua host dengan `scp` sebelum melanjutkan. Tanpa file itu di working directory, tahap berikutnya gagal.

Password user `admin` bisa dibaca sekarang:

```
# tar -axf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt -O | grep -P "\'admin\'" -A 1
```

## Tahap 2: Wazuh indexer

Nama node harus sama dengan yang ditulis di `config.yml`:

```
# bash wazuh-install.sh --wazuh-indexer node-1
```

Ulangi di setiap node indexer kalau anda membangun cluster. Setelah semua node indexer terpasang, inisialisasi cluster satu kali saja, dari node mana pun:

```
# bash wazuh-install.sh --start-cluster
```

Verifikasi indexer sebelum lanjut:

```
# curl -k -u admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200
# curl -k -u admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200/_cat/nodes?v
```

Command kedua harus menampilkan semua node indexer. Kalau ada node yang tidak muncul, selesaikan dulu di tahap ini; server dan dashboard hanya akan memperbesar masalahnya.

## Tahap 3: Wazuh server

```
# bash wazuh-install.sh --wazuh-server wazuh-1
```

Kalau tidak ada pesan error, lanjut.

## Tahap 4: Wazuh dashboard

```
# bash wazuh-install.sh --wazuh-dashboard dashboard
```

Output berakhir dengan ringkasan berisi URL dan kredensial `admin`.

## Tahap 5: setelah instalasi

Cetak seluruh password yang dibuat assistant:

```
# tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

Matikan repository Wazuh di setiap host supaya tidak ada upgrade tidak sengaja:

```
# sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list
# apt update
```

## Catatan untuk endpoint yang dikeraskan

Kalau directory `/tmp` di host indexer dipasang dengan flag `noexec`, instalasi indexer butuh penyesuaian tambahan. Lihat bagian Wazuh indexer configuration on hardened endpoints di dokumentasi resmi.

## Referensi

- <https://documentation.wazuh.com/current/installation-guide/wazuh-indexer/installation-assistant.html>
- <https://documentation.wazuh.com/current/installation-guide/wazuh-server/installation-assistant.html>
- <https://documentation.wazuh.com/current/installation-guide/wazuh-dashboard/installation-assistant.html>
