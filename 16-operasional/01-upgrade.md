# Upgrade Wazuh

## Aturan kompatibilitas

Semua komponen pusat harus punya nomor versi yang identik, termasuk patch level. Wazuh manager harus selalu sama atau lebih baru dari Wazuh agent.

Wazuh indexer 4.14.10 secara khusus kompatibel dengan Filebeat-OSS 7.10.2.

Urutan upgrade: indexer, lalu server, lalu dashboard. Urutan ini sama untuk deployment all-in-one maupun multi-node cluster. Untuk all-in-one, semua command dijalankan di host yang sama; untuk multi-node, di node tempat komponen itu berada.

## Peringatan sebelum memulai

**Downgrade ke 4.11 atau lebih lama tidak mungkin.** Sejak 4.12.0 Wazuh memakai versi Apache Lucene yang lebih baru, dan Lucene tidak mendukung downgrade. Setelah naik ke 4.12.0 atau lebih baru, satu-satunya jalan kembali adalah instalasi ulang indexer. Buat index snapshot sebelum upgrade untuk menghindari kehilangan data.

**Sejak 4.14.1, field JSON bernama `user` dipetakan menjadi `dstuser` saat decoding.** Perubahan ini mempengaruhi dashboard custom, saved search, integrasi, dan script yang mengacu ke `data.user`. Periksa dan ubah semuanya menjadi `data.dstuser` sebelum upgrade, karena setelah upgrade keduanya tidak akan memberi error, hanya hasil kosong.

## Persiapan

Lakukan di setiap node indexer, server, dan dashboard.

Tambahkan repository Wazuh kalau sebelumnya dimatikan:

```
# apt-get update && apt-get install gnupg apt-transport-https curl
# curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
# echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
# apt-get update
```

Export saved object dari dashboard. Langkah ini menyelamatkan visualisasi dan dashboard custom kalau terjadi masalah: buka Dashboard management > Dashboards Management > Saved objects, pilih objek yang ingin diexport lalu klik Export, atau klik Export all objects.

Hentikan Filebeat dan dashboard di node tersebut:

```
# systemctl stop filebeat
# systemctl stop wazuh-dashboard
```

## Upgrade Wazuh indexer

Cluster indexer tetap melayani selama upgrade karena prosesnya rolling: node diperbarui satu per satu. Node dengan role `cluster_manager` di-upgrade paling akhir supaya konektivitas cluster terjaga.

Periksa role tiap node:

```
# curl -k -u <USERNAME> https://<WAZUH_INDEXER_IP_ADDRESS>:9200/_cat/nodes?v
```

Backup konfigurasi security indexer dari salah satu node:

```
# /usr/share/wazuh-indexer/bin/indexer-security-init.sh --options "-backup /etc/wazuh-indexer/opensearch-security -icl -nhnv"
```

Lalu di setiap node, satu per satu:

```
# systemctl stop wazuh-indexer
# cp /etc/wazuh-indexer/jvm.options /etc/wazuh-indexer/jvm.options.old
# apt-get install wazuh-indexer
```

Saat ditanya, pilih mengganti file `/etc/wazuh-indexer/jvm.options` dengan versi baru, lalu terapkan kembali pengaturan JVM custom anda dari file backup secara manual. Melewatkan langkah ini membuat setting heap size anda hilang, dan indexer berjalan dengan default yang mungkin tidak cukup.

```
# systemctl daemon-reload
# systemctl enable wazuh-indexer
# systemctl start wazuh-indexer
```

Setelah semua node indexer selesai, terapkan kembali konfigurasi security dari backup:

```
# /usr/share/wazuh-indexer/bin/indexer-security-init.sh
```

## Upgrade Wazuh server

```
# apt-get install wazuh-manager
# systemctl daemon-reload
# systemctl enable wazuh-manager
# systemctl start wazuh-manager
```

Kalau `/var/ossec/etc/ossec.conf` pernah anda ubah, file itu tidak diganti oleh upgrade. Konsekuensinya, pengaturan untuk kemampuan baru harus anda tambahkan manual. Setelah upgrade besar, bandingkan `ossec.conf` anda dengan file `.rpmnew` atau contoh konfigurasi versi baru.

Upgrade dari 4.12.x atau lebih lama membutuhkan konfigurasi CDB list baru yang ditambahkan di versi setelahnya. Ikuti bagian Configuring CDB lists di dokumentasi resmi.

Periksa juga blok `<vulnerability-detection>` dan `<indexer>` masih sesuai, seperti dijelaskan di [chapter 07](../07-vulnerability-detection/01-cara-kerja-dan-konfigurasi.md).

## Upgrade Filebeat

```
# curl -s https://packages.wazuh.com/4.x/filebeat/wazuh-filebeat-0.5.tar.gz | sudo tar -xvz -C /usr/share/filebeat/module
# curl -so /etc/filebeat/wazuh-template.json https://raw.githubusercontent.com/wazuh/wazuh/v4.14.10/extensions/elasticsearch/7.x/wazuh-template.json
# chmod go+r /etc/filebeat/wazuh-template.json
# cp /etc/filebeat/filebeat.yml /etc/filebeat/filebeat.yml.old
# apt-get install filebeat
# cp /etc/filebeat/filebeat.yml.old /etc/filebeat/filebeat.yml
# systemctl enable filebeat
# systemctl start filebeat
```

Sesuaikan nomor versi di URL template dengan versi Wazuh yang anda pasang.

## Upgrade Wazuh dashboard

```
# cp /etc/wazuh-dashboard/opensearch_dashboards.yml /etc/wazuh-dashboard/opensearch_dashboards.yml.old
# apt-get install wazuh-dashboard
```

Saat ditanya, pilih mengganti `opensearch_dashboards.yml` dengan versi baru, lalu terapkan kembali perubahan konfigurasi anda secara manual. Pastikan nilai `server.ssl.key` dan `server.ssl.certificate` cocok dengan file di `/etc/wazuh-dashboard/certs/`.

```
# systemctl daemon-reload
# systemctl enable wazuh-dashboard
# systemctl start wazuh-dashboard
```

## Upgrade agent

Remote upgrade dari server, memakai paket WPK:

```
# /var/ossec/bin/agent_upgrade -l
# /var/ossec/bin/agent_upgrade -a 002
```

Beberapa agent sekaligus, ID dipisah spasi:

```
# /var/ossec/bin/agent_upgrade -a 003 004
```

Opsi yang tersedia:

| Opsi | Fungsi |
| --- | --- |
| `-l` | Daftar agent yang versinya tertinggal |
| `-a <IDs>` | Agent yang di-upgrade |
| `-v <VERSION>` | Versi tujuan, default versi terbaru |
| `-r <REPOSITORY>` | URL repository WPK sendiri |
| `-F` | Memaksa upgrade dengan melewati validasi versi |
| `-f <FILE>` | Memakai file WPK custom |

Upgrade lokal di endpoint Linux:

```
# apt-get update
# apt-get install wazuh-agent
```

Setelah selesai, matikan kembali repository supaya agent tidak terbawa upgrade berikutnya:

```
# sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
# apt-get update
```

## Verifikasi

```
# systemctl status wazuh-indexer wazuh-manager wazuh-dashboard filebeat
# curl -k -u admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200/_cat/nodes?v
# /var/ossec/bin/agent_control -l
```

Lalu login ke dashboard dan periksa alert baru masih masuk. Alert yang berhenti setelah upgrade biasanya berarti Filebeat tidak berjalan atau template-nya belum diperbarui.

## Referensi

- <https://documentation.wazuh.com/current/upgrade-guide/index.html>
- <https://documentation.wazuh.com/current/upgrade-guide/upgrading-central-components.html>
- <https://documentation.wazuh.com/current/upgrade-guide/wazuh-agent/linux.html>
