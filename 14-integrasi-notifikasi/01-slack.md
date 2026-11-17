# Integrasi Slack

Modul Integrator menghubungkan Wazuh dengan API eksternal dan alat alerting. Slack adalah integrasi bawaan, jadi tidak perlu menulis script.

## Konfigurasi

Aktifkan incoming webhook di Slack dan buat satu webhook untuk channel tujuan, lalu tambahkan blok berikut ke `/var/ossec/etc/ossec.conf` di Wazuh server:

```xml
<ossec_config>
  <integration>
    <name>slack</name>
    <hook_url><SLACK_WEBHOOK_URL></hook_url>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
```

Restart manager:

```
# systemctl restart wazuh-manager
```

## Filter

Tanpa filter, semua alert dikirim ke Slack. Di lingkungan dengan beberapa agent, itu berarti channel yang tidak terbaca lagi dalam satu hari. Pakai filter untuk membatasi:

```xml
<integration>
  <name>slack</name>
  <hook_url><SLACK_WEBHOOK_URL></hook_url>
  <level>10</level>
  <group>authentication_failures,attack</group>
  <alert_format>json</alert_format>
</integration>
```

| Tag | Isi |
| --- | --- |
| `<rule_id>` | Rule ID yang dikirim, beberapa ID dipisah koma |
| `<level>` | Level minimum. Alert dengan level itu atau lebih tinggi dikirim |
| `<group>` | Rule group, beberapa group dipisah koma |
| `<event_location>` | Menyaring berdasarkan asal event, menerima ekspresi sregex |
| `<options>` | Objek JSON untuk menambah atau menimpa field, sesuai referensi API tujuan |

Kalau `<rule_id>` dan `<group>` ditulis bersamaan, alert dikirim hanya kalau keduanya cocok. Periksa nama group dan rule ID dengan teliti: salah menuliskannya membuat alert yang anda harapkan tidak pernah terkirim, tanpa pesan error.

## Kustomisasi pesan

Tag `<options>` menerima objek JSON yang dikirim ke Slack, memakai field kustomisasi yang tersedia di Slack API, misalnya untuk mengubah nama pengirim atau ikon.

## Integrasi bawaan lainnya

| Nama | Yang dibutuhkan |
| --- | --- |
| `slack` | `hook_url` |
| `pagerduty` | `api_key` |
| `virustotal` | `api_key`, lihat [chapter 09](../09-malware-detection/02-integrasi-virustotal.md) |
| `shuffle` | `hook_url` |
| `maltiverse` | `hook_url` dan `api_key` |

Semuanya membutuhkan `<alert_format>json</alert_format>`.

Contoh PagerDuty:

```xml
<ossec_config>
  <integration>
    <name>pagerduty</name>
    <api_key><PAGERDUTY_API_KEY></api_key>
    <level>10</level>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
```

## Verifikasi

Aktifkan debug Integrator untuk melihat aktivitas integrasi:

```
# echo "integrator.debug=1" >> /var/ossec/etc/local_internal_options.conf
# systemctl restart wazuh-manager
# tail -f /var/ossec/logs/integrations.log
```

Lalu picu alert yang memenuhi filter anda, misalnya login SSH gagal berulang, dan amati pesan masuk ke channel Slack.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/manager/integration-with-external-apis.html>
