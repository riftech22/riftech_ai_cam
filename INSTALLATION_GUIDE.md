# Panduan Instalasi Lengkap dengan install.sh

## 🚀 Cara Paling Mudah - Satu Script Install!

Script `install.sh` akan melakukan SEMUA instalasi secara otomatis!

### Yang perlu Anda lakukan:

#### 1. Upload install.sh ke server

**Dari PC Anda:**
```bash
scp install.sh root@10.26.27.109:/root/
```

#### 2. SSH ke server

```bash
ssh root@10.26.27.109
```

#### 3. Jalankan script install

```bash
chmod +x install.sh
./install.sh
```

**Script akan otomatis:**
- ✅ Update system
- ✅ Install semua dependencies (15-30 menit)
- ✅ Install dlib dari source
- ✅ Setup Python virtual environment
- ✅ Install semua Python packages
- ✅ Download YOLOv8n model
- ✅ Buat semua folder dan konfigurasi
- ✅ Buat helper scripts (test_rtsp.py, start.sh, stop.sh)

**Total waktu: 15-30 menit**

#### 4. Upload file yang besar

Setelah script selesai, upload file-file ini ke `/root/riftech_ai_cam/`:

```bash
# Di PC Anda:
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

#### 5. Edit .env untuk Secret Key dan Password

```bash
cd /root/riftech_ai_cam
nano .env
```

Generate secret key:
```bash
openssl rand -hex 32
# Copy hasilnya
```

Edit .env:
```bash
# Ganti:
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
# SECRET_KEY=<hasil dari openssl>

# Ganti:
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password-here
# WEB_USERNAME=admin
# WEB_PASSWORD=password_anda_disini
```

Contoh lengkap:
```bash
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x
WEB_USERNAME=admin
WEB_PASSWORD=Kunci123!
```

#### 6. Test RTSP (Opsional tapi Recommended)

```bash
cd /root/riftech_ai_cam
source venv/bin/activate
python3 test_rtsp.py
```

Expected output:
```
✅ SUCCESS: Connected to camera
✅ SUCCESS: Successfully read 10 frames
```

#### 7. Jalankan Aplikasi

```bash
./start.sh
```

Atau:
```bash
source venv/bin/activate
python3 main.py
```

#### 8. Akses Web Dashboard

- URL: http://10.26.27.109:5000
- Login dengan admin / password_anda_disini

#### 9. (Opsional) Install sebagai Systemd Service

```bash
cp /root/riftech_ai_cam/ai-cctv.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-cctv
systemctl start ai-cctv
systemctl status ai-cctv
```

## 📋 Apa yang Diinstall oleh install.sh?

### System Dependencies
- build-essential
- cmake
- git
- wget
- curl
- python3
- python3-pip
- python3-dev
- python3-venv
- libopencv-dev
- python3-opencv
- libgtk-3-dev
- libboost-python-dev
- libboost-all-dev
- cpufrequtils
- htop
- vim
- unzip

### Python Libraries
- ultralytics==8.0.196 (YOLOv8)
- face-recognition==1.3.0
- opencv-python==4.8.1.78
- opencv-python-headless==4.8.1.78
- numpy==1.24.3
- Pillow==10.0.1
- Flask==3.0.0
- Flask-Login==0.6.3
- Werkzeug==3.0.1
- python-telegram-bot==20.7
- requests==2.31.0
- python-dotenv==1.0.0

### Tools & Models
- dlib (dari source, optimized untuk CPU)
- YOLOv8n model (yolov8n.pt)

### Scripts yang Dibuat
- test_rtsp.py - Test koneksi RTSP
- start.sh - Script untuk start aplikasi
- stop.sh - Script untuk stop aplikasi
- ai-cctv.service - Systemd service file

### Folders yang Dibuat
- /root/riftech_ai_cam/known_faces/
- /root/riftech_ai_cam/uploads/
- /root/riftech_ai_cam/logs/
- /root/riftech_ai_cam/templates/
- /root/riftech_ai_cam/static/
- /root/riftech_ai_cam/venv/

### Files yang Dibuat
- /root/riftech_ai_cam/requirements.txt
- /root/riftech_ai_cam/.env (sudah dengan RTSP + Telegram)

## 🎯 Summary - Cara Install Paling Mudah

```bash
# 1. Upload install.sh
scp install.sh root@10.26.27.109:/root/

# 2. SSH ke server
ssh root@10.26.27.109

# 3. Jalankan install (15-30 menit)
chmod +x install.sh
./install.sh

# 4. Upload file besar
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
scp templates/* root@10.26.27.109:/root/riftech_ai_cam/templates/

# 5. Edit .env
cd /root/riftech_ai_cam
nano .env
# Tambahkan SECRET_KEY, WEB_USERNAME, WEB_PASSWORD

# 6. Test RTSP
source venv/bin/activate
python3 test_rtsp.py

# 7. Jalankan aplikasi
./start.sh

# 8. Akses dashboard
# Browser: http://10.26.27.109:5000
```

## 🔧 Troubleshooting

### install.sh gagal
```bash
# Check permission
chmod +x install.sh

# Jalankan dengan bash
bash install.sh
```

### dlib install gagal
```bash
# Install dependencies manual
apt install -y build-essential cmake libboost-all-dev

# Coba lagi
cd /tmp
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_SSE2_INSTRUCTIONS=ON
cmake --build . --config Release
make install
```

### Python package install gagal
```bash
# Upgrade pip
pip3 install --upgrade pip

# Install manual
cd /root/riftech_ai_cam
source venv/bin/activate
pip install ultralytics
pip install face-recognition
pip install Flask
pip install python-telegram-bot
```

### Port 5000 sudah dipakai
```bash
# Kill process
pkill -f "python3 main.py"

# Atau ubah port di .env
WEB_PORT=5001
```

## ✅ Setelah Install Berhasil

### Test semua fungsi:

1. **Test RTSP**: `python3 test_rtsp.py`
2. **Test Web**: Buka http://10.26.27.109:5000
3. **Test Telegram**: Kirim pesan ke bot
4. **Test Detection**: Berdiri di depan kamera

### Monitor aplikasi:

```bash
# Cek logs
tail -f /var/log/syslog | grep ai-cctv

# Jika systemd service:
journalctl -u ai-cctv -f

# Monitor CPU
htop
```

### Start/Stop/Restart:

```bash
# Manual
./start.sh    # Start
./stop.sh     # Stop

# Systemd service
systemctl start ai-cctv     # Start
systemctl stop ai-cctv      # Stop
systemctl restart ai-cctv   # Restart
systemctl status ai-cctv    # Status
```

## 📚 Dokumentasi Lengkap

- **INSTALLATION_GUIDE.md** - Dokumentasi ini
- **SETUP_GUIDE.md** - Panduan detail Proxmox LXC
- **UPLOAD_INSTALL_GUIDE.md** - 4 metode upload
- **README.md** - Overview project

## 💡 Tips

1. **Jalankan install.sh di background jika SSH putus:**
   ```bash
   nohup ./install.sh > install.log 2>&1 &
   tail -f install.log
   ```

2. **Monitoring progress install:**
   - Script akan menampilkan progress setiap step
   - dlib install butuh waktu lama (10-20 menit)
   - Jangan panik jika terlihat "stuck" di step dlib

3. **Backup sebelum install:**
   - Backup data penting jika ada di server
   - Install script aman untuk fresh install

4. **Test RTSP dulu:**
   - Test dengan VLC player sebelum install
   - Pastikan kamera bisa diakses dari server

Script `install.sh` akan melakukan SEMUA instalasi otomatis! 🚀
