# 🐧 Panduan Installasi di Ubuntu 22.04 LTS

Panduan lengkap installasi AI CCTV Security System di Ubuntu 22.04 LTS.

---

## 📋 Prasyarat

- Ubuntu 22.04 LTS (bisa fisik, VM, atau LXC container)
- Koneksi internet
- Akses root atau sudo
- Minimal RAM: 2GB (4GB recommended)
- Storage: 10GB free space

---

## 🚀 Langkah 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📦 Langkah 2: Install System Dependencies

```bash
# Install git, Python, dan build tools
sudo apt install -y git python3 python3-pip python3-dev build-essential cmake

# Install OpenCV dependencies
sudo apt install -y libopencv-dev python3-opencv

# Install additional dependencies
sudo apt install -y libsm6 libxext6 libxrender-dev libglib2.0-0
```

---

## 📥 Langkah 3: Clone Project dari GitHub

```bash
# Clone repository
git clone https://github.com/riftech22/riftech_ai_cam.git

# Masuk ke folder project
cd riftech_ai_cam
```

---

## 🔧 Langkah 4: Setup Python Virtual Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate
```

Setelah aktif, terminal akan menampilkan `(venv)` di depan prompt.

---

## 📚 Langkah 5: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies (ini akan memakan waktu 10-20 menit)
pip install -r requirements.txt
```

**Catatan**: Proses installasi akan:
- Download dan compile dlib (face recognition library) - ini yang paling lama
- Download YOLOv8n model (otomatis saat pertama kali run aplikasi)
- Install semua dependencies yang diperlukan

---

## ⚙️ Langkah 6: Konfigurasi Aplikasi

### 6.1 Copy File Konfigurasi

```bash
cp .env.example .env
```

### 6.2 Generate Secret Key

```bash
openssl rand -hex 32
```

Copy hasilnya (contoh: `a1b2c3d4e5f6...`) dan simpan untuk step selanjutnya.

### 6.3 Edit Konfigurasi

```bash
nano .env
```

Edit pengaturan berikut:

```bash
# =================== KAMERA ===================
# URL RTSP kamera CCTV Anda
# Format: rtsp://username:password@IP-KAMERA:554/stream
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream

# =================== TELEGRAM BOT ===================
# Token dari @BotFather di Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Chat ID dari @userinfobot di Telegram
TELEGRAM_CHAT_ID=123456789

# =================== WEB DASHBOARD ===================
# Username untuk login web dashboard
WEB_USERNAME=admin

# Password untuk login web dashboard (gunakan password yang kuat!)
WEB_PASSWORD=secure_password_123

# Secret Key untuk Flask (paste hasil dari openssl rand -hex 32)
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# =================== AI DETECTION SETTINGS ===================
# Process setiap N frame (lebih tinggi = lebih hemat CPU)
FRAME_PROCESS_INTERVAL=5

# Resize frame ke lebar X pixel (lebih kecil = lebih cepat)
FRAME_RESIZE_WIDTH=640

# Zoom factor untuk face detection
ZOOM_FACTOR=2

# Confidence threshold YOLOv8 (0.0-1.0)
CONFIDENCE_THRESHOLD=0.5

# =================== AUTO-DELETE SETTINGS ===================
# Hapus foto deteksi setelah X hari (0 = disable)
AUTO_DELETE_AFTER=7

# Check interval untuk cleanup (dalam detik, default 24 jam)
CLEANUP_CHECK_INTERVAL=86400

# =================== LOGGING ===================
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

**Cara mendapatkan Telegram Bot Token**:
1. Buka Telegram, cari bot **@BotFather**
2. Send command: `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Copy token yang diberikan

**Cara mendapatkan Telegram Chat ID**:
1. Buka Telegram, cari bot **@userinfobot**
2. Start bot dengan klik **Start**
3. Bot akan menampilkan **Id**: `123456789`
4. Copy ID tersebut

Save dan exit dengan `Ctrl+X`, lalu `Y`, lalu `Enter`.

---

## 🎬 Langkah 7: Jalankan Aplikasi

```bash
# Pastikan virtual environment aktif
source venv/bin/activate

# Jalankan aplikasi
python3 main.py
```

Aplikasi akan:
1. Download YOLOv8n model (otomatis, hanya sekali, file size ~6MB)
2. Koneksi ke RTSP camera
3. Mendeteksi orang dan wajah secara real-time
4. Mengirim notifikasi ke Telegram jika ada orang terdeteksi
5. Menjalankan web dashboard di port 5000

**Output yang diharapkan**:
```
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Connecting to RTSP stream...
INFO:     YOLOv8n model loaded successfully
INFO:     Camera connected successfully
INFO:     Starting detection...
```

---

## 🌐 Langkah 8: Access Web Dashboard

Buka browser dan akses:
```
http://IP-UBUNTU-ANDA:5000
```

Login dengan:
- Username: `WEB_USERNAME` dari `.env` (default: admin)
- Password: `WEB_PASSWORD` dari `.env`

Dashboard features:
- **Live Streaming**: Stream CCTV real-time
- **Gallery**: Lihat semua snapshot deteksi
- **Known Faces**: Daftar wajah yang dikenali
- **Settings**: Konfigurasi aplikasi

---

## 🔧 Langkah 9: Installasi sebagai Systemd Service (Opsional tapi Recommended)

Ini akan membuat aplikasi berjalan otomatis saat boot dan restart jika crash.

### 9.1 Buat Systemd Service File

```bash
sudo nano /etc/systemd/system/ai-cctv.service
```

Paste konfigurasi berikut (sesuaikan path dengan lokasi project Anda):

```ini
[Unit]
Description=AI CCTV Security System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/riftech_ai_cam
Environment="PATH=/root/riftech_ai_cam/venv/bin"
ExecStart=/root/riftech_ai_cam/venv/bin/python /root/riftech_ai_cam/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Catatan**: Jika Anda install di folder lain, sesuaikan:
- `WorkingDirectory`: path ke folder project
- `ExecStart`: path lengkap ke python di venv + path ke main.py

Save dan exit dengan `Ctrl+X`, lalu `Y`, lalu `Enter`.

### 9.2 Enable dan Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (run on boot)
sudo systemctl enable ai-cctv

# Start service
sudo systemctl start ai-cctv

# Cek status
sudo systemctl status ai-cctv
```

Output yang diharapkan:
```
● ai-cctv.service - AI CCTV Security System
   Loaded: loaded (/etc/systemd/system/ai-cctv.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2026-01-13 12:00:00 WITA; 5s ago
```

### 9.3 Commands Manajemen Service

```bash
# Stop service
sudo systemctl stop ai-cctv

# Start service
sudo systemctl start ai-cctv

# Restart service
sudo systemctl restart ai-cctv

# Cek status
sudo systemctl status ai-cctv

# Lihat logs real-time
sudo journalctl -u ai-cctv -f

# Lihat 100 baris log terakhir
sudo journalctl -u ai-cctv -n 100
```

---

## 🔒 Langkah 10: Firewall Configuration (Optional)

Jika Anda menggunakan firewall, buka port yang diperlukan:

```bash
# Jika menggunakan UFW
sudo ufw allow 5000/tcp

# Reload firewall
sudo ufw reload

# Cek status firewall
sudo ufw status
```

---

## ✅ Langkah 11: Verifikasi Installasi

### Checklist untuk memastikan semuanya berjalan dengan baik:

- [ ] Repository berhasil di-clone dari GitHub
- [ ] Virtual environment berhasil dibuat
- [ ] Semua dependencies berhasil diinstall (`pip list` untuk cek)
- [ ] File `.env` sudah dikonfigurasi dengan benar
- [ ] Aplikasi berhasil dijalankan (`python3 main.py`)
- [ ] Tidak ada error saat koneksi ke RTSP camera
- [ ] YOLOv8n model berhasil di-download dan diload
- [ ] Web dashboard bisa diakses di browser
- [ ] Login web dashboard berhasil
- [ ] Telegram bot aktif (test dengan kirim pesan ke bot)
- [ ] (Opsional) Systemd service berjalan dengan baik

---

## 🤖 Cara Menggunakan Telegram Bot

### Terima Notifikasi
Saat aplikasi mendeteksi orang, bot akan mengirim 2 foto:
1. Foto original (full frame)
2. Foto zoom (fokus pada wajah/orang yang terdeteksi)

### Self-Learning (Reply Nama)
- Reply foto notifikasi dengan nama orang
- Bot otomatis menambah foto ke `known_faces/` folder
- Deteksi berikutnya akan mengenali orang tersebut

### Manual Upload Training
- Kirim foto orang ke bot Telegram
- Sertakan caption: "Nama Orang"
- Bot otomatis mengekstrak wajah dan menyimpan untuk training

---

## 📊 Performance Tuning

Jika CPU usage terlalu tinggi, sesuaikan konfigurasi di `.env`:

```bash
# Untuk CPU usage lebih rendah
FRAME_PROCESS_INTERVAL=10  # Process setiap 10 frame (bukan 5)
FRAME_RESIZE_WIDTH=480     # Resize ke 480px (bukan 640)

# Untuk detection lebih cepat
FRAME_RESIZE_WIDTH=320     # Resize ke 320px (lebih cepat tapi kurang akurat)

# Untuk mengurangi false positives
CONFIDENCE_THRESHOLD=0.6   # Increase dari 0.5 ke 0.6
```

**Expected Performance (Intel i5, no GPU)**:

| Konfigurasi | CPU Usage | Detection Speed |
|-------------|-----------|-----------------|
| 640px, Interval 5 | 40-60% | ~3-5 FPS |
| 640px, Interval 10 | 25-35% | ~2-3 FPS |
| 480px, Interval 5 | 30-45% | ~4-6 FPS |
| 480px, Interval 10 | 20-30% | ~2-4 FPS |

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: No module named 'dlib'

**Solusi**:
```bash
sudo apt install -y build-essential cmake
pip install dlib
```

### Error: RTSP Connection Failed

**Solusi**:
1. Test RTSP URL dengan VLC player:
   ```bash
   vlc rtsp://username:password@IP-KAMERA:554/stream
   ```
2. Pastikan kamera bisa diakses dari Ubuntu server:
   ```bash
   ping IP-KAMERA
   ```
3. Check firewall:
   ```bash
   sudo ufw status
   ```

### Error: High CPU Usage

**Solusi**: Edit `.env` dan sesuaikan:
```bash
FRAME_PROCESS_INTERVAL=10
FRAME_RESIZE_WIDTH=480
```

### Error: Telegram Bot Tidak Merespon

**Solusi**:
1. Pastikan bot token benar
2. Test bot dengan kirim pesan manual ke bot
3. Check logs: `sudo journalctl -u ai-cctv -f`

### Error: Web Dashboard Tidak Bisa Diakses

**Solusi**:
1. Pastikan aplikasi berjalan: `sudo systemctl status ai-cctv`
2. Check port 5000: `sudo netstat -tlnp | grep 5000`
3. Check firewall: `sudo ufw status`
4. Coba akses dengan: `curl http://localhost:5000`

### Error: YOLOv8n Model Not Found

**Solusi**: Model akan otomatis download saat pertama kali run. Jika gagal:
```bash
# Download manual
pip install ultralytics

# Download model
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## 🗄️ Backup dan Restore

### Backup Database
```bash
# Backup detections.db
cp detections.db backup/detections_$(date +%Y%m%d).db

# Backup known faces
tar -czf backup/known_faces_$(date +%Y%m%d).tar.gz known_faces/

# Backup configuration
cp .env backup/.env_$(date +%Y%m%d)
```

### Restore Database
```bash
# Stop service
sudo systemctl stop ai-cctv

# Restore database
cp backup/detections_20260113.db detections.db

# Restore known faces
tar -xzf backup/known_faces_20260113.tar.gz

# Start service
sudo systemctl start ai-cctv
```

---

## 📝 Maintenance

### Monitor Logs
```bash
# Jika dijalankan sebagai service
sudo journalctl -u ai-cctv -f

# Jika dijalankan manual
tail -f logs/app.log
```

### Update Project dari GitHub
```bash
cd riftech_ai_cam
source venv/bin/activate

# Stop service (jika menggunakan systemd)
sudo systemctl stop ai-cctv

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Start service
sudo systemctl start ai-cctv
```

### Cleanup Old Photos
Jika `AUTO_DELETE_AFTER` diaktifkan, aplikasi akan otomatis menghapus foto lama. Untuk manual cleanup:
```bash
# Hapus foto deteksi yang lebih dari 7 hari
find uploads/ -name "*.jpg" -mtime +7 -delete

# Hapus database entries yang sesuai
# (perlu manual edit database)
```

---

## 🔐 Security Best Practices

1. **Gunakan password yang kuat** untuk web dashboard
2. **Protect RTSP stream** dengan password yang kuat
3. **Generate secret key** yang aman: `openssl rand -hex 32`
4. **Batasi akses** - hanya buka port yang diperlukan
5. **Update system** secara berkala: `sudo apt update && sudo apt upgrade -y`
6. **Monitor logs** untuk aktivitas mencurigakan
7. **Backup data** secara berkala

---

## 📞 Support dan Bantuan

Jika mengalami masalah:

1. **Check logs**: `sudo journalctl -u ai-cctv -n 100`
2. **Check dependencies**: `pip list`
3. **Review configuration**: `nano .env`
4. **Test koneksi**: `vlc rtsp://URL-KAMERA`
5. **Review dokumentasi**: `cat README.md`

---

## 🎉 Selamat!

AI CCTV Security System Anda sudah siap digunakan di Ubuntu 22.04 LTS!

Project tersedia di: https://github.com/riftech22/riftech_ai_cam

---

**Built with ❤️ for home security**
