# Integrasi Telegram

Telegram bukan integrasi bawaan Wazuh, jadi dibuat sebagai custom integration. Modul Integrator menjalankan script anda dan meneruskan alert kepadanya.

File script ada di [files/](files/).

## Kontrak script integrasi

Aturan yang harus dipenuhi script custom integration:

- Script diletakkan di `/var/ossec/integrations/` dengan nama yang sama dengan nilai `<name>` di blok `<integration>`.
- Nama integrasi custom harus diawali `custom-`.
- Script harus punya permission eksekusi dan dimiliki user root dengan group wazuh.
- Baris pertama script menyatakan interpreter-nya.
- Script menerima tiga argumen:

| Argumen | Isi |
| --- | --- |
| `sys.argv[1]` | Path file sementara berisi alert dalam format JSON, misalnya `/tmp/custom-telegram-1763000000-12345.alert` |
| `sys.argv[2]` | Nilai dari tag `<api_key>` |
| `sys.argv[3]` | Nilai dari tag `<hook_url>` |

Argumen yang tidak diisi di konfigurasi diterima script sebagai string kosong.

Untuk Telegram, dua argumen itu dipetakan sebagai berikut: `<hook_url>` menampung URL endpoint `sendMessage` milik bot, dan `<api_key>` menampung chat ID tujuan.

## Menyiapkan bot Telegram

Buat bot lewat BotFather di Telegram, lalu simpan token yang diberikan. Untuk mendapatkan chat ID, kirim satu pesan ke bot anda lalu jalankan:

```
$ curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates" | python3 -m json.tool
```

Nilai `result[].message.chat.id` pada output adalah chat ID yang dipakai. Untuk group, tambahkan bot ke group lalu kirim satu pesan di sana; chat ID group bernilai negatif.

## Memasang script

Copy kedua file dari [files/](files/) ke Wazuh server:

```
# cp custom-telegram /var/ossec/integrations/custom-telegram
# cp custom-telegram.py /var/ossec/integrations/custom-telegram.py
# chmod 750 /var/ossec/integrations/custom-telegram /var/ossec/integrations/custom-telegram.py
# chown root:wazuh /var/ossec/integrations/custom-telegram /var/ossec/integrations/custom-telegram.py
```

Dua file dipakai mengikuti pola integrasi bawaan Wazuh: satu wrapper shell yang dipanggil Integrator, dan satu file Python yang berisi logikanya. Wrapper memilih interpreter Python bawaan Wazuh di `framework/python/bin/python3` kalau tersedia, dan jatuh ke `python3` sistem kalau tidak.

Script Python hanya memakai standard library, jadi tidak ada paket tambahan yang perlu dipasang. Hasil eksekusi ditulis ke `/var/ossec/logs/integrations.log`; kalau file itu tidak bisa ditulis, pesan dialihkan ke stderr supaya tidak hilang.

Kedua file membaca environment variable `WAZUH_PATH` dan memakai `/var/ossec` kalau variable itu tidak diset. Ini berguna untuk menguji script di luar Wazuh server.

## Konfigurasi

Tambahkan ke `/var/ossec/etc/ossec.conf` di Wazuh server:

```xml
<ossec_config>
  <integration>
    <name>custom-telegram</name>
    <hook_url>https://api.telegram.org/bot<BOT_TOKEN>/sendMessage</hook_url>
    <api_key><CHAT_ID></api_key>
    <level>10</level>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
```

Sesuaikan `<level>` dengan kebutuhan. Tanpa filter, seluruh alert dikirim ke Telegram, dan rate limit Telegram akan menolak sebagian besarnya.

Restart manager:

```
# systemctl restart wazuh-manager
```

## Uji script secara langsung

Jangan menunggu alert sungguhan untuk menguji script. Buat file alert contoh lalu jalankan script dengan argumen yang sama seperti yang dipakai Integrator:

```
# cat > /tmp/uji.alert << 'ALERTEOF'
{"timestamp":"2026-11-17T10:00:00.000+0700","rule":{"level":10,"description":"Uji integrasi Telegram","id":"999999"},"agent":{"id":"001","name":"ubuntu-agent"},"location":"/var/log/auth.log","full_log":"baris log uji"}
ALERTEOF
# /var/ossec/integrations/custom-telegram /tmp/uji.alert "<CHAT_ID>" "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage"
```

Kalau pesan masuk ke Telegram, script dan kredensial sudah benar, dan masalah yang tersisa hanya ada di konfigurasi Integrator. Hapus file uji setelah selesai.

## Verifikasi lewat Integrator

```
# echo "integrator.debug=1" >> /var/ossec/etc/local_internal_options.conf
# systemctl restart wazuh-manager
# tail -f /var/ossec/logs/integrations.log
```

Picu alert yang memenuhi filter, lalu amati log. Kalau log menunjukkan script dipanggil tapi pesan tidak masuk, periksa jawaban dari Telegram API yang dicatat script. Kalau script tidak pernah dipanggil, filter di blok `<integration>` yang tidak kena.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/manager/integration-with-external-apis.html>
- <https://core.telegram.org/bots/api#sendmessage>
