# Cara Upload dan Install di Ubuntu 22

## 📦 Metode 1: SCP (Paling Mudah dari PC Anda)

### Jika Anda punya akses dari PC Anda:

```bash
# 1. Di PC Anda, masuk ke folder project
cd /path/to/riftech_ai_cam

# 2. Upload semua file ke server
scp -r . root@10.26.27.109:/root/riftech_ai_cam
```

### Lalu login ke server dan install:

```bash
# 1. SSH ke server
ssh root@10.26.27.109

# 2. Masuk ke folder project
cd /root/riftech_ai_cam

# 3. Pastikan file sudah terupload
ls -la

# 4. Beri permission pada script
chmod +x QUICK_SETUP.sh
chmod +x test_rtsp.py

# 5. Edit .env untuk secret key dan password
nano .env

# 6. Jalankan setup
./QUICK_SETUP.sh

# 7. Setelah setup selesai, edit .env lagi
nano .env
# Tambahkan:
# SECRET_KEY=<hasil openssl>
# WEB_USERNAME=admin
# WEB_PASSWORD=password_anda

# 8. Jalankan aplikasi
source venv/bin/activate
python3 main.py
```

---

## 📦 Metode 2: SSH dan Copy-Paste (Tanpa Upload File)

### Langkah demi langkah:

#### 1. SSH ke server

```bash
ssh root@10.26.27.109
```

#### 2. Buat folder project

```bash
mkdir -p /root/riftech_ai_cam
cd /root/riftech_ai_cam
```

#### 3. Install dependencies dan buat file

```bash
# Update system
apt update && apt upgrade -y

# Install tools
apt install -y build-essential cmake git wget curl python3 python3-pip python3-dev libopencv-dev python3-opencv libgtk-3-dev libboost-python-dev cpufrequtils htop

# Install dlib (ini butuh waktu lama, 10-20 menit)
cd /tmp
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_SSE2_INSTRUCTIONS=ON
cmake --build . --config Release
make install
cd ../..
rm -rf dlib

# Kembali ke folder project
cd /root/riftech_ai_cam
```

#### 4. Buat file requirements.txt

```bash
cat > requirements.txt << 'EOF'
# AI & Computer Vision
ultralytics==8.0.196
face-recognition==1.3.0
opencv-python==4.8.1.78
opencv-python-headless==4.8.1.78
numpy==1.24.3
Pillow==10.0.1

# Web Framework
Flask==3.0.0
Flask-Login==0.6.3
Werkzeug==3.0.1

# Telegram Bot
python-telegram-bot==20.7

# Utilities
requests==2.31.0
python-dotenv==1.0.0
EOF
```

#### 5. Buat file .env

```bash
cat > .env << 'EOF'
# RTSP Camera Configuration
RTSP_URL=rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1
CAMERA_NAME=Kamera Depan

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8501083554:AAHZcpcdsMYOrgUkT8Asu3N0YX_SE9GrSTQ
TELEGRAM_CHAT_ID=947624946

# AI Detection Settings
FRAME_PROCESS_INTERVAL=5
FRAME_RESIZE_WIDTH=640
ZOOM_FACTOR=2
CONFIDENCE_THRESHOLD=0.5

# Auto-Delete Old Photos
AUTO_DELETE_AFTER=7
CLEANUP_CHECK_INTERVAL=86400

# Web Interface Settings
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password-here
WEB_PORT=5000
WEB_HOST=0.0.0.0

# Database
DATABASE_PATH=detections.db
EOF
```

#### 6. Buat folder

```bash
mkdir -p known_faces uploads logs templates static
touch known_faces/.gitkeep uploads/.gitkeep logs/.gitkeep
```

#### 7. Install Python dependencies

```bash
# Upgrade pip
pip3 install --upgrade pip

# Install virtualenv
pip3 install virtualenv

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 8. Download YOLOv8n model

```bash
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O /root/riftech_ai_cam/yolov8n.pt
```

#### 9. Edit .env untuk secret key dan password

```bash
# Generate secret key
openssl rand -hex 32
# Copy hasilnya

# Edit .env
nano .env

# Ganti:
# SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
# SECRET_KEY=<hasil dari openssl>

# Ganti:
# WEB_USERNAME=admin
# WEB_PASSWORD=your-secure-password-here
# WEB_USERNAME=admin
# WEB_PASSWORD=password_anda_disini
```

#### 10. Buat main.py (File besar, copy dari project Anda)

```bash
# Upload main.py dari PC Anda ke server
# Di PC Anda:
scp main.py root@10.26.27.109:/root/riftech_ai_cam/

# Atau gunakan editor di server
nano /root/riftech_ai_cam/main.py
# Paste isi main.py di sini
# Tekan Ctrl+X, lalu Y, lalu Enter untuk save
```

#### 11. Buat templates

```bash
# Di PC Anda:
scp templates/* root@10.26.27.109:/root/riftech_ai_cam/templates/

# Atau buat manual di server
nano /root/riftech_ai_cam/templates/login.html
# Paste isi login.html

nano /root/riftech_ai_cam/templates/dashboard.html
# Paste isi dashboard.html
```

#### 12. Test RTSP

```bash
# Buat test_rtsp.py
nano test_rtsp.py
# Paste isi test_rtsp.py

# Jalankan test
python3 test_rtsp.py
```

#### 13. Jalankan aplikasi

```bash
# Pastikan di folder project
cd /root/riftech_ai_cam

# Aktifkan virtual environment
source venv/bin/activate

# Jalankan aplikasi
python3 main.py
```

---

## 📦 Metode 3: Upload via SFTP/FTP Client

### Gunakan FileZilla, WinSCP, atau Cyberduck:

1. **Buat koneksi SFTP:**
   - Host: 10.26.27.109
   - Username: root
   - Password: password root Anda
   - Port: 22

2. **Upload semua file dari PC Anda:**
   - Konek ke server
   - Buka folder /root/riftech_ai_cam
   - Drag & drop semua file dari PC ke server

3. **SSH ke server:**
   ```bash
   ssh root@10.26.27.109
   cd /root/riftech_ai_cam
   ```

4. **Lanjutkan dengan langkah install:**
   - Ikuti langkah di "Metode 2" mulai dari step 7

---

## 📦 Metode 4: GitHub (Paling Mudah jika file sudah di GitHub)

### Di server:

```bash
# 1. Install git
apt install -y git

# 2. Clone repository (ganti URL dengan repo Anda)
cd /root
git clone https://github.com/username/riftech_ai_cam.git
cd riftech_ai_cam

# 3. Edit .env
nano .env
# Update dengan konfigurasi Anda

# 4. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Download YOLOv8n
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt

# 6. Jalankan aplikasi
python3 main.py
```

---

## ✅ Setelah Berhasil Install

### Test koneksi:

```bash
# 1. Test RTSP
source venv/bin/activate
python3 test_rtsp.py

# 2. Jalankan aplikasi
python3 main.py
```

### Akses dashboard:

- URL: http://10.26.27.109:5000
- Login dengan credentials dari `.env`

### Test Telegram bot:

1. Kirim pesan ke bot Anda
2. Berdiri di depan kamera
3. Tunggu notifikasi

---

## 🔧 Troubleshooting

### Permission denied

```bash
# Beri permission
chmod +x main.py
chmod +x QUICK_SETUP.sh
chmod +x test_rtsp.py
```

### dlib install gagal

```bash
# Install dependencies dulu
apt install -y build-essential cmake libboost-python-dev

# Coba install lagi
pip3 install dlib
```

### Python version error

```bash
# Cek python version
python3 --version

# Harus Python 3.8 atau lebih baru
```

### Port 5000 sudah dipakai

```bash
# Cek port
lsof -i :5000

# Kill process jika perlu
kill -9 <PID>

# Atau ubah port di .env
WEB_PORT=5001
```

---

## 💡 Rekomendasi

**Paling Mudah untuk Pertama Kali:**
1. Gunakan Metode 2 (SSH + Copy-Paste) untuk files kecil (.env, requirements.txt)
2. Gunakan SCP untuk file besar (main.py, templates)
3. Jalankan QUICK_SETUP.sh jika sudah ada semua file

**Untuk Produksi:**
- Setup systemd service (lihat SETUP_GUIDE.md)
- Setup firewall
- Enable HTTPS dengan nginx + certbot
