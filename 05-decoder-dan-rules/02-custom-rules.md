# Custom rules

Rules mencocokkan field hasil decoding dan menentukan level alert. Wazuh membawa lebih dari 3000 rules dan decoder bawaan; custom rules dipakai untuk hal yang spesifik di lingkungan anda.

## Aturan penomoran

Pakai ID antara 100000 dan 120000 untuk custom rules. Rentang di luar itu dipakai ruleset bawaan, dan tabrakan ID membuat salah satu rule diabaikan tanpa peringatan yang jelas.

Untuk perubahan kecil, tulis di `/var/ossec/etc/rules/local_rules.xml`. Untuk kumpulan rule yang besar, buat file baru di `/var/ossec/etc/rules/`.

## Menambah rule

Melanjutkan contoh decoder `example` dari chapter sebelumnya, tambahkan rule ke `/var/ossec/etc/rules/local_rules.xml`:

```xml
<group name="custom_rules_example,">
  <rule id="100010" level="0">
    <program_name>example</program_name>
    <description>User logged</description>
  </rule>
</group>
```

Uji dengan `wazuh-logtest`:

```
# /var/ossec/bin/wazuh-logtest
```

```
**Phase 3: Completed filtering (rules).
	id: '100010'
	level: '0'
	description: 'User logged'
	groups: '['custom_rules_example']'
	firedtimes: '1'
```

Restart manager supaya rule benar-benar menghasilkan alert:

```
# systemctl restart wazuh-manager
```

## Level alert

Level menentukan apakah alert ditulis dan seberapa penting. Level 0 berarti rule cocok tapi tidak menghasilkan alert, berguna sebagai rule pengelompokan atau untuk membungkam event yang berisik. Level 3 ke bawah umumnya informasi, level 7 ke atas perlu perhatian, level 12 ke atas biasanya serius.

Kalau anda bingung menentukan level, lihat level rule bawaan untuk kejadian sejenis dan pakai angka yang sebanding.

## Rule turunan

`<if_sid>` membuat rule hanya diperiksa setelah rule lain cocok. Pola ini dipakai hampir di semua custom rule yang berguna, karena membuat rule anda menumpang pada decoding yang sudah benar.

```xml
<group name="malware,">
  <rule id="110002" level="13">
    <if_sid>554, 550</if_sid>
    <list field="md5" lookup="match_key">etc/lists/malware-hashes</list>
    <description>File with known malware hash detected: $(file)</description>
    <mitre>
      <id>T1204.002</id>
    </mitre>
  </rule>
</group>
```

Rule 554 adalah file baru terdeteksi FIM, rule 550 adalah file berubah. Variable `$(file)` di `<description>` diganti nilai field aslinya saat alert dibuat.

Tag `<mitre>` memetakan rule ke teknik MITRE ATT&CK, dan membuat alert ikut muncul di modul MITRE ATT&CK pada dashboard.

## Menimpa rule bawaan

Untuk mengubah level atau isi rule bawaan, copy definisinya ke `/var/ossec/etc/rules/local_rules.xml` dan tambahkan atribut `overwrite="yes"`.

Contoh menaikkan level rule SSH 5710 dari 5 menjadi 10:

```xml
<group name="syslog,sshd,">
  <rule id="5710" level="10" overwrite="yes">
    <if_sid>5700</if_sid>
    <match>illegal user|invalid user</match>
    <description>sshd: Attempt to login using a non-existent user</description>
    <mitre>
      <id>T1110</id>
    </mitre>
  </rule>
</group>
```

Tag `<if_sid>`, `<if_group>`, `<if_level>`, `<if_matched_sid>`, dan `<if_matched_group>` tidak bisa ditimpa. Kalau ditulis di rule overwrite, tag itu diabaikan dan nilai aslinya dipertahankan.

Restart manager setelahnya.

## Verifikasi

Selain `wazuh-logtest`, periksa manager tidak menolak file rule anda:

```
# /var/ossec/bin/wazuh-analysisd -t
# tail -n 30 /var/ossec/logs/ossec.log
```

Kesalahan XML atau regex membuat `wazuh-analysisd` gagal start, dan seluruh analisis berhenti, bukan cuma rule yang salah. Selalu uji sebelum restart di lingkungan yang dipakai.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/ruleset/rules/custom.html>
- <https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/rules.html>
