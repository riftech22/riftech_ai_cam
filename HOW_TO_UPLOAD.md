# Cara Upload Aplikasi ke Server (10.26.27.109)

## 📁 File yang Perlu Diupload

Dari folder `/home/riftech/projeck/riftech_ai_cam/` di PC Anda:

**Wajib:**
- ✅ `main.py` (aplikasi utama)
- ✅ `templates/login.html`
- ✅ `templates/dashboard.html`

**Opsional (tidak wajib karena bisa dibuat di server):**
- `requirements.txt` (bisa dibuat di server)
- `.env` (bisa dibuat di server)
- Script-script lainnya (bisa dibuat di server)

---

## 🚀 METODE 1: SCP (Linux/Mac - Paling Mudah)

### Di PC Anda (Terminal):

#### Upload main.py:
```bash
cd /home/riftech/projeck/riftech_ai_cam
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
```

#### Upload templates:
```bash
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

#### Upload semua sekaligus:
```bash
cd /home/riftech/projeck/riftech_ai_cam
scp main.py templates/login.html templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/
```

**Password yang diminta:** password root server Anda

---

## 🖥️ METODE 2: FileZilla/WinSCP (Windows - Paling Mudah)

### A. Install FileZilla:

1. Download: https://filezilla-project.org/download.php?type=client
2. Install di PC Anda

### B. Connect ke Server:

1. Buka FileZilla
2. Isi detail di top-right:

```
Host: 10.26.27.109
Username: root
Password: password root Anda
Port: 22
```

3. Klik "Quickconnect"

### C. Upload Files:

1. **Di panel kiri (Local site):**
   - Buka folder: `/home/riftech/projeck/riftech_ai_cam/`

2. **Di panel kanan (Remote site):**
   - Buka folder: `/root/riftech_ai_cam/`
   - Jika belum ada, buat folder `templates` di dalamnya

3. **Drag & Drop:**
   - Drag `main.py` dari kiri ke kanan (ke `/root/riftech_ai_cam/`)
   - Drag `templates/login.html` dari kiri ke kanan (ke `/root/riftech_ai_cam/templates/`)
   - Drag `templates/dashboard.html` dari kiri ke kanan (ke `/root/riftech_ai_cam/templates/`)

4. Tunggu sampai transfer selesai (status "Complete")

### D. Verifikasi:

1. Di panel kanan, refresh (klik kanan -> Refresh)
2. Pastikan file sudah muncul di server

---

## 📱 METODE 3: Cyberduck (Mac - GUI Alternative)

### A. Install Cyberduck:

1. Download: https://cyberduck.io/
2. Install di Mac Anda

### B. Connect ke Server:

1. Buka Cyberduck
2. Klik "Open Connection" (ikon + di kiri atas)
3. Pilih: SFTP (SSH File Transfer Protocol)
4. Isi:

```
Server: 10.26.27.109
Username: root
Password: password root Anda
```

5. Klik "Connect"

### C. Upload Files:

1. Navigasi ke `/root/riftech_ai_cam/` di server
2. Klik "Upload" (ikon panah ke atas)
3. Pilih file dari Mac Anda:
   - `main.py`
   - `templates/login.html`
   - `templates/dashboard.html`

4. Tunggu upload selesai

---

## 🔐 METODE 4: SFTP Command Line (Advanced)

### Di PC Anda:

```bash
# Connect ke server
sftp root@10.26.27.109

# Set local folder
lcd /home/riftech/projeck/riftech_ai_cam

# Set remote folder
cd /root/riftech_ai_cam

# Upload main.py
put main.py

# Upload templates
cd templates
put /home/riftech/projeck/riftech_ai_cam/templates/login.html
put /home/riftech/projeck/riftech_ai_cam/templates/dashboard.html

# Exit
exit
```

---

## 📝 METODE 5: Copy-Paste via SSH (Jika File Kecil)

### Di Server (10.26.27.109):

#### 1. Buat main.py:

```bash
cd /root/riftech_ai_cam
nano main.py
```

#### 2. Di PC Anda, buka main.py dan copy semua content

#### 3. Paste di server:
- Klik kanan di terminal server
- Pilih "Paste"
- Tekan: `Ctrl+X`, lalu `Y`, lalu `Enter`

#### 4. Ulangi untuk templates:

```bash
mkdir -p /root/riftech_ai_cam/templates
nano /root/riftech_ai_cam/templates/login.html
# Paste content
# Ctrl+X, Y, Enter

nano /root/riftech_ai_cam/templates/dashboard.html
# Paste content
# Ctrl+X, Y, Enter
```

**Catatan:** Metode ini TIDAK direkomendasikan untuk file besar seperti main.py karena bisa error saat paste.

---

## ✅ Cek Upload Berhasil

### Di Server (10.26.27.109):

```bash
ssh root@10.26.27.109

# Cek folder
cd /root/riftech_ai_cam
ls -la

# Harusnya muncul:
# main.py
# templates/ (folder)
```

```bash
# Cek templates
ls -la templates/

# Harusnya muncul:
# login.html
# dashboard.html
```

```bash
# Cek ukuran file
ls -lh main.py
ls -lh templates/

# main.py harusnya sekitar 20-30 KB
# templates/*.html harusnya sekitar 3-5 KB
```

---

## 🎯 Rekomendasi

### Jika Anda di Linux/Mac:
**Gunakan METODE 1 (SCP)** - Paling cepat dan mudah

```bash
cd /home/riftech/projeck/riftech_ai_cam
scp main.py templates/login.html templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/
```

### Jika Anda di Windows:
**Gunakan METODE 2 (FileZilla)** - Paling mudah dengan GUI

1. Download & install FileZilla
2. Connect ke 10.26.27.109
3. Drag & drop files

---

## 🚀 Setelah Upload Berhasil

Lanjutkan dengan instalasi di server:

### Di Server (10.26.27.109):

```bash
# SSH ke server
ssh root@10.26.27.109

# Verifikasi upload
cd /root/riftech_ai_cam
ls -la
ls -la templates/

# Lanjutkan dengan instalasi
# (Ikuti panduan di SERVICE_SIDE_INSTALL.md)
```

---

## 🔧 Troubleshooting

### Error "Connection refused"
```bash
# Cek server online
ping 10.26.27.109

# Cek SSH aktif
ssh root@10.26.27.109
```

### Error "Permission denied"
```bash
# Pastikan menggunakan user root
scp main.py root@10.26.27.109:/root/riftech_ai_cam/

# Atau beri permission di server
chmod +x /root/riftech_ai_cam/main.py
```

### File tidak muncul di server
```bash
# Cek folder target ada
ssh root@10.26.27.109
mkdir -p /root/riftech_ai_cam/templates

# Upload lagi
```

### FileZilla transfer gagal
1. Cek koneksi internet
2. Pastikan password root benar
3. Coba transfer file per file (bukan sekaligus)

---

## 📋 Summary - Cara Paling Mudah

### Di PC Anda:

```bash
cd /home/riftech/projeck/riftech_ai_cam

# Upload 3 file ini ke server
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

### Di Server:

```bash
# Verifikasi
cd /root/riftech_ai_cam
ls -la

# Lanjut instalasi (SERVICE_SIDE_INSTALL.md)
```

**Selesai! 🎉**

Sekarang file sudah di server dan siap untuk diinstall!
