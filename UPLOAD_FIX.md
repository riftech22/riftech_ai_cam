# Fix Upload Error - Buat Folder Dulu di Server

## ❌ Error yang Terjadi

```
scp: dest open "/root/riftech_ai_cam/": Failure
scp: failed to upload file main.py to /root/riftech_ai_cam/
```

**Penyebab:** Folder `/root/riftech_ai_cam/` belum ada di server

---

## ✅ Solusi - Upload Langsung ke /root/ Lalu Rename

### Cara 1: Upload Langsung (Paling Mudah)

#### Di PC Anda:

```bash
# Upload ke /root/ dulu
scp main.py root@10.26.27.109:/root/
scp templates/login.html root@10.26.27.109:/root/
scp templates/dashboard.html root@10.26.27.109:/root/
```

#### Di Server (10.26.27.109):

```bash
# SSH ke server
ssh root@10.26.27.109

# Buat folder dan pindahkan file
mkdir -p /root/riftech_ai_cam/templates
mv /root/main.py /root/riftech_ai_cam/
mv /root/login.html /root/riftech_ai_cam/templates/
mv /root/dashboard.html /root/riftech_ai_cam/templates/

# Verifikasi
cd /root/riftech_ai_cam
ls -la
ls -la templates/
```

---

### Cara 2: Buat Folder di Server Dulu

#### Di Server (10.26.27.109):

```bash
# SSH ke server
ssh root@10.26.27.109

# Buat folder project
mkdir -p /root/riftech_ai_cam/templates
mkdir -p /root/riftech_ai_cam/known_faces
mkdir -p /root/riftech_ai_cam/uploads
mkdir -p /root/riftech_ai_cam/logs

# Verifikasi
ls -la /root/riftech_ai_cam
```

#### Di PC Anda (Setelah folder dibuat):

```bash
# Sekarang upload akan berhasil
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

---

### Cara 3: Gunakan FileZilla (Windows)

#### 1. Connect ke Server dengan FileZilla

```
Host: 10.26.27.109
Username: root
Password: password root Anda
Port: 22
```

#### 2. Buat Folder di Server

- Di panel kanan (Remote site):
  - Klik kanan di `/root/`
  - Pilih "Create directory"
  - Nama: `riftech_ai_cam`
  - Klik OK
  - Masuk ke folder `riftech_ai_cam`
  - Klik kanan -> "Create directory"
  - Nama: `templates`
  - Klik OK

#### 3. Upload Files

- Panel kiri (Local site): Buka `/home/riftech/projeck/riftech_ai_cam/`
- Drag & drop:
  - `main.py` ke `/root/riftech_ai_cam/`
  - `templates/login.html` ke `/root/riftech_ai_cam/templates/`
  - `templates/dashboard.html` ke `/root/riftech_ai_cam/templates/`

---

## ✅ Cek Upload Berhasil

### Di Server:

```bash
ssh root@10.26.27.109

# Cek folder
cd /root/riftech_ai_cam
ls -la

# Harusnya muncul:
# main.py
# templates/

# Cek templates
ls -la templates/

# Harusnya muncul:
# login.html
# dashboard.html
```

---

## 🚀 Setelah Upload Berhasil

Lanjutkan dengan instalasi lengkap:

### Di Server (10.26.27.109):

```bash
# SSH ke server (jika belum)
ssh root@10.26.27.109

# Verifikasi upload
cd /root/riftech_ai_cam
ls -la

# Lanjutkan instalasi
# (Copy command dari SERVICE_SIDE_INSTALL.md STEP 2-9)
```

---

## 📋 Summary - Cara Termudah

### Di PC Anda:

```bash
# Upload ke /root/ dulu (bypass error folder belum ada)
scp main.py root@10.26.27.109:/root/
scp templates/login.html root@10.26.27.109:/root/
scp templates/dashboard.html root@10.26.27.109:/root/
```

### Di Server:

```bash
ssh root@10.26.27.109

# Buat folder dan pindahkan file
mkdir -p /root/riftech_ai_cam/templates
mv /root/main.py /root/riftech_ai_cam/
mv /root/login.html /root/riftech_ai_cam/templates/
mv /root/dashboard.html /root/riftech_ai_cam/templates/

# Verifikasi
cd /root/riftech_ai_cam
ls -la
ls -la templates/
```

**Selesai! 🎉 File sudah di server dan siap untuk diinstall**

---

## 🔧 Cara Upload Lainnya

### Jika mau pakai FileZilla (GUI):

1. Connect ke 10.26.27.109
2. Buat folder `/root/riftech_ai_cam/templates/` di server
3. Drag & drop files dari PC ke server

### Jika mau pakai copy-paste (SSH):

```bash
ssh root@10.26.27.109

# Buat folder
mkdir -p /root/riftech_ai_cam/templates

# Buat main.py
cd /root/riftech_ai_cam
nano main.py
# Paste isi main.py dari PC
# Ctrl+X, Y, Enter

# Buat login.html
nano templates/login.html
# Paste isi login.html dari PC
# Ctrl+X, Y, Enter

# Buat dashboard.html
nano templates/dashboard.html
# Paste isi dashboard.html dari PC
# Ctrl+X, Y, Enter
```

**Catatan:** Copy-paste tidak direkomendasikan untuk file besar.

---

## 💡 Rekomendasi

**Gunakan Cara 1 (Upload ke /root/ lalu pindah)** - Paling mudah dan cepat!

```bash
# Di PC Anda:
scp main.py root@10.26.27.109:/root/
scp templates/login.html root@10.26.27.109:/root/
scp templates/dashboard.html root@10.26.27.109:/root/

# Di Server:
ssh root@10.26.27.109
mkdir -p /root/riftech_ai_cam/templates
mv /root/main.py /root/riftech_ai_cam/
mv /root/login.html /root/riftech_ai_cam/templates/
mv /root/dashboard.html /root/riftech_ai_cam/templates/
```

Setelah upload berhasil, lanjutkan dengan instalasi lengkap (SERVICE_SIDE_INSTALL.md).
