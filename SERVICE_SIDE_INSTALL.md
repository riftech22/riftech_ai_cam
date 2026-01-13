# Panduan Instalasi di Server - Copy & Paste Commands

## 🚀 Cara Instalasi di Server (Copy-Paste Langsung)

### Lakukan ini di server Anda (10.26.27.109):

---

## STEP 1: SSH ke Server

```bash
ssh root@10.26.27.109
```

---

## STEP 2: Update System dan Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install system dependencies
apt install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    libopencv-dev \
    python3-opencv \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-all-dev \
    cpufrequtils \
    htop \
    vim \
    unzip
```

---

## STEP 3: Set CPU ke Performance Mode

```bash
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
```

---

## STEP 4: Install dlib dari Source (10-20 menit)

```bash
cd /tmp
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_SSE2_INSTRUCTIONS=ON
cmake --build . --config Release
make install
cd /tmp
rm -rf dlib
```

---

## STEP 5: Buat Folder Project

```bash
mkdir -p /root/riftech_ai_cam
cd /root/riftech_ai_cam

# Buat subdirectories
mkdir -p known_faces uploads logs templates static
touch known_faces/.gitkeep uploads/.gitkeep logs/.gitkeep
```

---

## STEP 6: Buat requirements.txt

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

---

## STEP 7: Buat .env Configuration

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

---

## STEP 8: Setup Python Virtual Environment

```bash
# Upgrade pip
pip3 install --upgrade pip

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## STEP 9: Download YOLOv8n Model

```bash
cd /root/riftech_ai_cam
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O yolov8n.pt
```

---

## STEP 10: Upload File yang Besar

### Di PC Anda (bukan di server):

```bash
# Upload main.py
scp main.py root@10.26.27.109:/root/riftech_ai_cam/

# Upload templates
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

---

## STEP 11: Edit .env untuk Secret Key dan Password

```bash
cd /root/riftech_ai_cam

# Generate secret key
openssl rand -hex 32
# Copy hasilnya

# Edit .env
nano .env
```

Ganti di .env:
```bash
SECRET_KEY=<hasil dari openssl>
WEB_USERNAME=admin
WEB_PASSWORD=password_anda_disini
```

Tekan: `Ctrl+X`, lalu `Y`, lalu `Enter` untuk save

---

## STEP 12: Buat Helper Scripts

### Buat test_rtsp.py:

```bash
cat > test_rtsp.py << 'EOF'
#!/usr/bin/env python3
import cv2
import sys
from dotenv import load_dotenv
import os

load_dotenv()
RTSP_URL = os.getenv('RTSP_URL', 'rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1')

def test_rtsp():
    print("=" * 50)
    print("RTSP Connection Test")
    print("=" * 50)
    print(f"RTSP URL: {RTSP_URL}")
    print("")
    
    print("Attempting to connect to camera...")
    
    try:
        cap = cv2.VideoCapture(RTSP_URL)
        
        if not cap.isOpened():
            print("❌ FAILED: Cannot open RTSP stream")
            return False
        
        print("✅ SUCCESS: Connected to camera")
        print("")
        
        frame_count = 0
        while frame_count < 10:
            ret, frame = cap.read()
            if not ret:
                print(f"❌ FAILED: Cannot read frame {frame_count + 1}")
                cap.release()
                return False
            
            frame_count += 1
            print(f"Frame {frame_count}: {frame.shape[1]}x{frame.shape[0]} pixels")
        
        print("")
        print(f"✅ SUCCESS: Successfully read {frame_count} frames")
        print("")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_rtsp()
    sys.exit(0 if success else 1)
EOF

chmod +x test_rtsp.py
```

### Buat start.sh:

```bash
cat > start.sh << 'EOF'
#!/bin/bash
cd /root/riftech_ai_cam
source venv/bin/activate
python3 main.py
EOF

chmod +x start.sh
```

### Buat stop.sh:

```bash
cat > stop.sh << 'EOF'
#!/bin/bash
pkill -f "python3 main.py"
EOF

chmod +x stop.sh
```

---

## STEP 13: Test RTSP

```bash
cd /root/riftech_ai_cam
source venv/bin/activate
python3 test_rtsp.py
```

Harusnya muncul:
```
✅ SUCCESS: Connected to camera
✅ SUCCESS: Successfully read 10 frames
```

---

## STEP 14: Jalankan Aplikasi

```bash
cd /root/riftech_ai_cam
./start.sh
```

Atau:
```bash
source venv/bin/activate
python3 main.py
```

---

## STEP 15: Akses Web Dashboard

Buka browser:
```
http://10.26.27.109:5000
```

Login dengan credentials dari .env

---

## STEP 16: (Opsional) Install sebagai Systemd Service

```bash
cp /root/riftech_ai_cam/ai-cctv.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-cctv
systemctl start ai-cctv
systemctl status ai-cctv
```

---

## ✅ Summary - Copy-Paste Semua Command Ini

### Di Server (10.26.27.109):

```bash
# 1. SSH ke server
ssh root@10.26.27.109

# 2. Update dan install dependencies
apt update && apt upgrade -y
apt install -y build-essential cmake git wget curl python3 python3-pip python3-dev python3-venv libopencv-dev python3-opencv libgtk-3-dev libboost-python-dev libboost-all-dev cpufrequtils htop vim unzip

# 3. Set CPU performance
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils

# 4. Install dlib (10-20 menit)
cd /tmp
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_SSE2_INSTRUCTIONS=ON
cmake --build . --config Release
make install
cd /tmp
rm -rf dlib

# 5. Buat folder project
mkdir -p /root/riftech_ai_cam
cd /root/riftech_ai_cam
mkdir -p known_faces uploads logs templates static
touch known_faces/.gitkeep uploads/.gitkeep logs/.gitkeep

# 6. Buat requirements.txt
cat > requirements.txt << 'EOF'
ultralytics==8.0.196
face-recognition==1.3.0
opencv-python==4.8.1.78
opencv-python-headless==4.8.1.78
numpy==1.24.3
Pillow==10.0.1
Flask==3.0.0
Flask-Login==0.6.3
Werkzeug==3.0.1
python-telegram-bot==20.7
requests==2.31.0
python-dotenv==1.0.0
EOF

# 7. Buat .env
cat > .env << 'EOF'
RTSP_URL=rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1
CAMERA_NAME=Kamera Depan
TELEGRAM_BOT_TOKEN=8501083554:AAHZcpcdsMYOrgUkT8Asu3N0YX_SE9GrSTQ
TELEGRAM_CHAT_ID=947624946
FRAME_PROCESS_INTERVAL=5
FRAME_RESIZE_WIDTH=640
ZOOM_FACTOR=2
CONFIDENCE_THRESHOLD=0.5
AUTO_DELETE_AFTER=7
CLEANUP_CHECK_INTERVAL=86400
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password-here
WEB_PORT=5000
WEB_HOST=0.0.0.0
DATABASE_PATH=detections.db
EOF

# 8. Setup Python
pip3 install --upgrade pip
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 9. Download YOLOv8n
cd /root/riftech_ai_cam
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O yolov8n.pt

# 10. Upload main.py dan templates dari PC Anda
# (Di PC Anda: scp main.py root@10.26.27.109:/root/riftech_ai_cam/)

# 11. Edit .env untuk SECRET_KEY dan password
nano .env
# openssl rand -hex 32 (copy hasilnya ke SECRET_KEY)

# 12. Test RTSP
source venv/bin/activate
python3 test_rtsp.py

# 13. Jalankan aplikasi
./start.sh
```

### Di PC Anda (untuk upload file):

```bash
scp main.py root@10.26.27.109:/root/riftech_ai_cam/
scp templates/login.html root@10.26.27.109:/root/riftech_ai_cam/templates/
scp templates/dashboard.html root@10.26.27.109:/root/riftech_ai_cam/templates/
```

---

## ⚠️ CATATAN PENTING

1. **STEP 4 (install dlib)** butuh 10-20 menit, jangan close terminal
2. **STEP 10** harus dilakukan dari PC Anda (bukan di server)
3. **STEP 11** harus edit .env untuk SECRET_KEY dan password
4. Pastikan **main.py** dan **templates** sudah diupload sebelum jalankan aplikasi

---

## 🚀 Setelah Selesai

- ✅ Akses http://10.26.27.109:5000
- ✅ Login dengan credentials dari .env
- ✅ Test Telegram bot (kirim pesan)
- ✅ Test deteksi (berdiri di depan kamera)
