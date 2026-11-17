# wazuh-logtest

`wazuh-logtest` menjalankan satu baris log melewati pipeline analisis Wazuh dan menunjukkan hasil setiap fase. Tool ini satu-satunya cara cepat memastikan decoder dan rule bekerja sebelum anda merestart manager.

```
# /var/ossec/bin/wazuh-logtest
```

Tool ini hanya memproses log satu baris, tanpa line break.

## Tiga fase

Output dibagi menjadi tiga fase yang memetakan pipeline analisis:

**Phase 1, pre-decoding.** Wazuh mengambil timestamp, hostname, dan `program_name` dari format syslog standar. Kalau `program_name` kosong padahal log anda memakai format syslog, decoder dengan `<program_name>` tidak akan pernah cocok.

**Phase 2, decoding.** Decoder dipilih dan field diekstrak. Kalau fase ini kosong, masalahnya di decoder, bukan rule.

**Phase 3, filtering (rules).** Rule dicocokkan, dan hasilnya menunjukkan ID, level, deskripsi, serta group.

Membaca output dari atas ke bawah menghemat waktu: tidak ada gunanya memperbaiki rule kalau fase 2 belum menghasilkan field.

## Contoh sesi

```
# /var/ossec/bin/wazuh-logtest
Starting wazuh-logtest
Type one log per line

Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100'

**Phase 1: Completed pre-decoding.
	full event: 'Dec 25 20:45:02 MyHost example[12345]: User 'admin' logged from '192.168.1.100''
	timestamp: 'Dec 25 20:45:02'
	hostname: 'MyHost'
	program_name: 'example'

**Phase 2: Completed decoding.
	name: 'example'
	dstuser: 'admin'
	srcip: '192.168.1.100'

**Phase 3: Completed filtering (rules).
	id: '100010'
	level: '0'
	description: 'User logged'
	groups: '['custom_rules_example']'
	firedtimes: '1'
```

## Opsi yang berguna

| Opsi | Fungsi |
| --- | --- |
| `-v` | Hasil verbose, opsi utama untuk menelusuri kenapa sebuah rule atau decoder tidak cocok |
| `-d` | Debug mode, mencetak output debug ke terminal |
| `-U <rule-id:alert-level:decoder-name>` | Keluar dengan exit status nol kalau hasil uji cocok dengan kriteria, berguna untuk script |
| `-l <location>` | Mengatur nilai location secara manual |
| `-q` | Eksekusi tanpa output tambahan |

Opsi `-U` membuat rule bisa diuji otomatis, misalnya sebagai bagian dari pipeline sebelum rules dipasang ke server produksi.

## Uji syntax seluruh ruleset

`wazuh-logtest` menguji satu log. Untuk memastikan seluruh file decoder dan rules bisa dimuat, uji konfigurasi `wazuh-analysisd`:

```
# /var/ossec/bin/wazuh-analysisd -t
```

Jalankan ini sebelum setiap restart manager. File rules yang cacat membuat `wazuh-analysisd` gagal start, dan yang berhenti bukan hanya rule yang salah, tapi seluruh analisis.

## Lewat dashboard

Fungsi yang sama tersedia di dashboard pada Tools > Ruleset test, berguna kalau anda tidak punya shell di Wazuh server.

## Konfigurasi logtest

Perilaku logtest diatur di blok `<rule_test>` pada `/var/ossec/etc/ossec.conf` di Wazuh server:

```xml
<rule_test>
  <enabled>yes</enabled>
  <threads>1</threads>
  <max_sessions>64</max_sessions>
  <session_timeout>15m</session_timeout>
</rule_test>
```

Setiap sesi logtest memuat set rules dan decoder-nya sendiri, dan punya counter `firedtimes` yang terus berjalan selama sesi itu hidup. Sesi yang menganggur lebih lama dari `session_timeout` ditutup. Di Wazuh cluster, master node yang memproses log uji.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/ruleset/testing.html>
