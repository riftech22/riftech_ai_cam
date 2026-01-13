# Setup Guide - AI CCTV Security System on Proxmox LXC (Intel i5 CPU)

## Prerequisites

- Proxmox VE server
- LXC container with Ubuntu 22.04 LTS
- Intel i5 CPU (no GPU required)
- Minimum 2GB RAM (4GB recommended)
- 10GB disk space
- V380 IP Camera with RTSP access

---

## Step 1: Create LXC Container in Proxmox

### Container Configuration

```bash
# Create unprivileged LXC container
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --storage local-lvm \
  --cores 4 \
  --memory 4096 \
  --swap 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.1.100/24,gw=192.168.1.1 \
  --unprivileged 0 \
  --features nesting=1,keyctl=1

# Start the container
pct start 100

# Enter the container
pct enter 100
```

### Important: Enable Features

The container must have these features enabled:
- `nesting=1` - For running Docker (if needed) and nested processes
- `keyctl=1` - For key management

---

## Step 2: System Optimization for Intel i5 CPU

### 2.1 Update System

```bash
apt update && apt upgrade -y
```

### 2.2 Install Essential Build Tools

```bash
apt install -y \
  build-essential \
  cmake \
  git \
  wget \
  curl \
  python3 \
  python3-pip \
  python3-dev \
  libopencv-dev \
  python3-opencv \
  libgtk-3-dev \
  libboost-python-dev \
  dlib
```

### 2.3 Install dlib (Required for face_recognition)

```bash
# Install dlib from source (optimized for CPU)
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
```

### 2.4 CPU Optimizations

```bash
# Add CPU governor for performance
apt install -y cpufrequtils

# Set performance mode (run on boot)
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils

# Verify CPU governor
cpufreq-info
```

### 2.5 Enable Python Virtual Environment

```bash
# Install virtualenv
pip3 install --upgrade pip
pip3 install virtualenv

# Create project directory
mkdir -p /root/riftech_ai_cam
cd /root/riftech_ai_cam
```

---

## Step 3: Install Python Dependencies

### 3.1 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies

```bash
# Update pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Note:** First run may take 10-20 minutes to download and compile packages, especially `dlib` and `face_recognition`.

### 3.3 Download YOLOv8n Model

```bash
# The model will be automatically downloaded on first run
# Or download manually:
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O /root/riftech_ai_cam/yolov8n.pt
```

---

## Step 4: Configure Application

### 4.1 Copy and Configure .env

```bash
# Copy example file
cp .env.example .env

# Edit configuration
nano .env
```

### 4.2 Configuration Parameters

```bash
# RTSP Camera Configuration
RTSP_URL=rtsp://username:password@192.168.1.XX:554/stream
CAMERA_NAME=Kamera Depan

# Telegram Bot Configuration
# Get token from @BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
# Get chat ID from @userinfobot
TELEGRAM_CHAT_ID=123456789

# AI Detection Settings
FRAME_PROCESS_INTERVAL=5      # Process every 5th frame (lower = more CPU usage)
FRAME_RESIZE_WIDTH=640       # Resize to 640px width
ZOOM_FACTOR=2                # Zoom factor for face detection
CONFIDENCE_THRESHOLD=0.5     # YOLOv8 confidence threshold

# Auto-Delete Old Photos
AUTO_DELETE_AFTER=7          # Delete after 7 days (0 = disable)
CLEANUP_CHECK_INTERVAL=86400  # Check every 24 hours

# Web Interface Settings
SECRET_KEY=your-random-secret-key-change-this
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password
WEB_PORT=5000
WEB_HOST=0.0.0.0

# Database
DATABASE_PATH=detections.db
```

### 4.3 Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow instructions to create bot
4. Copy the token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 4.4 Get Telegram Chat ID

1. Open Telegram and search for `@userinfobot`
2. Send any message to the bot
3. Copy your Chat ID

### 4.5 Get V380 RTSP URL

1. Open V380 app on phone
2. Find camera IP address in settings
3. Default RTSP format: `rtsp://username:password@IP:554/stream`
4. Test with VLC player first

---

## Step 5: Test the Application

### 5.1 Manual Test Run

```bash
source venv/bin/activate
python3 main.py
```

Expected output:
```
[AI] Starting detection loop...
[Web] Starting web server on 0.0.0.0:5000
```

### 5.2 Test Web Interface

1. Open browser: `http://192.168.1.100:5000`
2. Login with credentials from `.env`
3. Check live stream (may take 10-20 seconds to connect)
4. Test detection by walking in front of camera

### 5.3 Test Telegram Bot

1. Send a message to your bot
2. Walk in front of camera
3. Wait for notification (2 photos: original + zoom)
4. Test self-learning: Reply with a name
5. Test manual upload: Send photo with caption "John Doe"

---

## Step 6: Run as System Service (Optional but Recommended)

### 6.1 Create Systemd Service

```bash
nano /etc/systemd/system/ai-cctv.service
```

### 6.2 Service Configuration

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

### 6.3 Enable and Start Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable service on boot
systemctl enable ai-cctv

# Start service
systemctl start ai-cctv

# Check status
systemctl status ai-cctv

# View logs
journalctl -u ai-cctv -f
```

---

## Step 7: Performance Monitoring and Tuning

### 7.1 Monitor CPU Usage

```bash
# Install htop
apt install -y htop

# Run htop
htop
```

### 7.2 Tune Performance Based on CPU Usage

If CPU usage is too high (>80%):

**Option 1: Increase Frame Interval**
```bash
# Edit .env
FRAME_PROCESS_INTERVAL=10  # Process every 10th frame instead of 5
```

**Option 2: Reduce Frame Resolution**
```bash
# Edit .env
FRAME_RESIZE_WIDTH=480  # Reduce from 640 to 480
```

**Option 3: Reduce Confidence Threshold**
```bash
# Edit .env
CONFIDENCE_THRESHOLD=0.6  # Increase from 0.5 to 0.6
```

### 7.3 Monitor Memory Usage

```bash
# Check memory usage
free -h

# Check Python process memory
ps aux | grep python
```

---

## Step 8: Troubleshooting

### 8.1 RTSP Connection Issues

**Problem:** Cannot connect to RTSP stream

**Solutions:**
1. Verify RTSP URL with VLC player
2. Check network connectivity: `ping 192.168.1.XX`
3. Ensure camera is on same network
4. Check firewall settings: `iptables -L`

### 8.2 Telegram Bot Not Working

**Problem:** No notifications received

**Solutions:**
1. Verify bot token and chat ID in `.env`
2. Test with curl:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```
3. Check logs: `journalctl -u ai-cctv -f`
4. Ensure bot has been started

### 8.3 Face Recognition Not Working

**Problem:** Always shows "Unknown"

**Solutions:**
1. Add photos to `known_faces/` folder with format: `Name.jpg`
2. Ensure photos are clear, front-facing
3. Check face detection logs
4. Test with known face photo in Telegram bot

### 8.4 High CPU Usage

**Problem:** CPU usage consistently >80%

**Solutions:**
1. Increase `FRAME_PROCESS_INTERVAL` in `.env`
2. Reduce `FRAME_RESIZE_WIDTH` in `.env`
3. Ensure no other heavy processes running
4. Check CPU frequency: `cpufreq-info`

### 8.5 Out of Memory

**Problem:** OOM (Out of Memory) errors

**Solutions:**
1. Increase container RAM in Proxmox
2. Reduce detection frequency
3. Enable swap: `fallocate -l 2G /swapfile && mkswap /swapfile && swapon /swapfile`

---

## Step 9: Backup and Maintenance

### 9.1 Backup Database

```bash
# Create backup directory
mkdir -p /root/backup

# Backup database
cp /root/riftech_ai_cam/detections.db /root/backup/detections_$(date +%Y%m%d).db

# Backup known faces
tar -czf /root/backup/known_faces_$(date +%Y%m%d).tar.gz /root/riftech_ai_cam/known_faces/
```

### 9.2 Automated Backup Script

```bash
nano /root/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/root/backup"
DATE=$(date +%Y%m%d)

# Create backup
cp /root/riftech_ai_cam/detections.db $BACKUP_DIR/detections_$DATE.db
tar -czf $BACKUP_DIR/known_faces_$DATE.tar.gz /root/riftech_ai_cam/known_faces/

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /root/backup.sh

# Add to cron (daily at 2 AM)
crontab -e
0 2 * * * /root/backup.sh
```

---

## Step 10: Security Best Practices

### 10.1 Secure Web Interface

1. Change default username/password in `.env`
2. Use strong SECRET_KEY (generate with: `openssl rand -hex 32`)
3. Use HTTPS (setup with nginx + certbot)

### 10.2 Secure RTSP Stream

1. Use RTSP over TLS if supported
2. Use strong camera password
3. Restrict RTSP access to local network only

### 10.3 Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp  # Web interface
ufw enable
```

---

## Performance Benchmarks (Intel i5)

Expected performance on Intel i5 (4 cores, no GPU):

| Configuration | CPU Usage | Detection Speed | Notes |
|--------------|-----------|-----------------|-------|
| Frame: 640px, Interval: 5 | 40-60% | ~3-5 FPS | Balanced |
| Frame: 640px, Interval: 10 | 25-35% | ~2-3 FPS | More efficient |
| Frame: 480px, Interval: 5 | 30-45% | ~4-6 FPS | Faster |
| Frame: 480px, Interval: 10 | 20-30% | ~2-4 FPS | Most efficient |

**Recommended:** Start with Frame 640px, Interval 5, then adjust based on CPU usage.

---

## Complete Folder Structure

```
/root/riftech_ai_cam/
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── venv/
├── known_faces/
│   ├── John.jpg
│   ├── Jane.jpg
│   └── ...
├── uploads/
│   ├── det_xxx_original.jpg
│   ├── det_xxx_zoom.jpg
│   └── ...
├── logs/
├── static/
├── templates/
│   ├── login.html
│   └── dashboard.html
├── detections.db
└── yolov8n.pt
```

---

## Additional Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [face_recognition Library](https://github.com/ageitgey/face_recognition)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Proxmox Documentation](https://pve.proxmox.com/wiki/Main_Page)

---

## Support

For issues or questions:
1. Check logs: `journalctl -u ai-cctv -f`
2. Verify configuration in `.env`
3. Test RTSP stream with VLC
4. Test Telegram bot with curl
5. Check CPU and memory usage

---

**Last Updated:** January 2026
**Version:** 1.0.0
