# Custom FIM rules

Rules bawaan memberi alert untuk setiap file yang ditambah, diubah, atau dihapus di directory yang dipantau. Custom FIM rules dipakai supaya file yang benar-benar penting mendapat level alert yang lebih tinggi daripada perubahan rutin.

## Field FIM pada alert

Decoder FIM memakai nama field yang berbeda dari nama field di alert. Rule ditulis memakai nama di kolom kiri, sedangkan yang anda lihat di dashboard adalah kolom kanan.

| Field FIM | Field alert | Isi |
| --- | --- | --- |
| `file` | `path` | Path file pada event ini |
| `size` | `size_after` | Ukuran file |
| `perm` | `perm_after`, `win_perm_after` | Permission file |
| `uid` | `uid_after` | User ID pemilik file |
| `gid` | `gid_after` | Group ID pemilik file |
| `uname` | `uname_after` | Nama user pemilik file |
| `gname` | `gname_after` | Nama group pemilik file |
| `md5` | `md5_after` | Hash MD5 setelah perubahan |
| `sha1` | `sha1_after` | Hash SHA-1 setelah perubahan |
| `sha256` | `sha256_after` | Hash SHA-256 setelah perubahan |
| `mtime` | `mtime_after` | Waktu perubahan file |
| `inode` | `inode_after` | Inode file |
| `changed_content` | `diff` | Isi perubahan yang dilaporkan |
| `changed_fields` | `changed_attributes` | Atribut yang berubah |
| `user_name` | `audit.user.name` | User yang memicu event, tersedia dengan who-data |
| `process_name` | `audit.process.name` | Nama proses yang memicu event, tersedia dengan who-data |
| `process_id` | `audit.process.id` | PID proses tersebut |
| `parent_name` | `audit.process.parent_name` | Nama proses parent |
| `audit_name` | `audit.login_user.name` | Nama user yang login ke sistem saat event terjadi |
| `tag` | `tag` | Tag custom pada event |

## Rule bawaan yang jadi pijakan

| Rule ID | Kejadian |
| --- | --- |
| 550 | File yang dipantau berubah |
| 553 | File yang dipantau dihapus |
| 554 | File ditambahkan ke directory yang dipantau |

Custom rule FIM hampir selalu memakai `<if_sid>` yang menunjuk ke salah satu dari ketiganya.

## Contoh: perubahan pada file kredensial

```xml
<group name="syscheck,">
  <rule id="100300" level="12">
    <if_sid>550</if_sid>
    <field name="file">/etc/shadow</field>
    <description>File /etc/shadow diubah</description>
    <mitre>
      <id>T1098</id>
    </mitre>
  </rule>
</group>
```

## Contoh: file baru di directory web yang dipantau

```xml
<group name="syscheck,">
  <rule id="100301" level="10">
    <if_sid>554</if_sid>
    <field name="file">/var/www/html/</field>
    <description>File baru di web root: $(file)</description>
  </rule>
</group>
```

Pola ini berguna untuk mendeteksi webshell yang ditanam lewat upload.

## Contoh: menyaring berdasarkan user

Dengan who-data aktif, rule bisa membedakan perubahan oleh proses deployment dari perubahan oleh user lain:

```xml
<group name="syscheck,">
  <rule id="100302" level="3">
    <if_sid>550</if_sid>
    <field name="file">/var/www/html/</field>
    <field name="user_name">deploy</field>
    <description>Perubahan web root oleh user deploy, diabaikan</description>
  </rule>
</group>
```

Rule dengan level 3 tetap tercatat tapi tidak menuntut perhatian. Untuk membungkam sama sekali, pakai level 0.

Rule yang lebih spesifik harus punya ID lebih besar daripada rule umum yang satu kelompok dengannya, karena Wazuh mengevaluasi rule dalam satu group secara berurutan.

## Menguji

Simpan rule, lalu uji syntax-nya sebelum restart:

```
# /var/ossec/bin/wazuh-analysisd -t
# systemctl restart wazuh-manager
```

Picu perubahan di endpoint dan periksa alert yang muncul memakai rule ID baru anda, bukan rule bawaan 550 atau 554. Kalau yang muncul masih rule bawaan, biasanya nilai `<field>` tidak cocok. Isi `<field>` dicocokkan sebagai regex tanpa anchor, jadi perilakunya seperti substring sampai anda menambahkan `^` atau `$` sendiri:

```xml
<field name="process_name">explorer.exe$</field>
```

Perhatikan juga trailing slash dan huruf besar kecil pada path.

## Referensi

- <https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/creating-custom-fim-rules.html>
