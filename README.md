# AI CCTV Security System

Sistem keamanan CCTV berbasis AI dengan deteksi orang, pengenalan wajah, bot Telegram interaktif, dan dashboard web yang aman. Dioptimalkan untuk Intel i5 CPU (tanpa GPU).

## 🌟 Fitur Utama

### 🔍 Deteksi AI Cerdas
- **Person Detection**: Menggunakan YOLOv8n (Ultralytics) untuk mendeteksi orang secara real-time
- **Face Recognition**: Menggunakan dlib + face_recognition untuk identifikasi wajah
- **CPU Optimized**: Dikonfigurasi untuk performa maksimal tanpa GPU
  - Resize frame ke 640px
  - Proses setiap 5-10 frame
  - Menggunakan HOG model untuk face detection (bukan CNN yang berat)

### 📱 Telegram Bot Interaktif
- **Notifikasi Real-time**: Kirim 2 foto saat mendeteksi orang:
  - Foto original (full frame)
  - Foto zoom pada area wajah/orang
- **Info Lengkap**: Menampilkan tanggal, jam, status, dan lokasi
- **Self-Learning**: Reply nama pada notifikasi untuk menambah ke known_faces otomatis
- **Manual Upload**: Kirim foto + caption nama langsung ke bot untuk training

### 🖥️ Web Dashboard Aman
- **Live Streaming**: Stream CCTV real-time dengan MJPEG
- **Gallery Deteksi**: Tampilkan semua snapshot (known & unknown)
  - Filter: Semua | Dikenal | Tidak Dikenal
  - Klik untuk memperbesar foto
  - Hapus deteksi individually
- **Known Faces List**: Daftar wajah yang sudah dikenali
- **Authentication**: Login aman dengan username & password

### 🗄️ Database & Storage
- **SQLite Database**: Menyimpan semua deteksi dengan metadata lengkap
- **Auto-Delete**: Hapus foto otomatis setelah X hari (configurable)
- **Organized Storage**: Folder structure yang rapi untuk photos

## 📋 Persyaratan Sistem

### Minimum Requirements
- **CPU**: Intel i5 (atau setara)
- **RAM**: 2GB (4GB recommended)
- **Storage**: 10GB
- **OS**: Ubuntu 22.04 LTS (via Proxmox LXC)

### Hardware
- Kamera IP dengan RTSP support (V380 atau compatible)
- Koneksi jaringan stabil

## 🚀 Quick Start

### 1. Clone/Download Project
```bash
cd /root/riftech_ai_cam
```

### 2. Install Dependencies
```bash
# Install system dependencies (detailed in SETUP_GUIDE.md)
apt install -y build-essential cmake git python3 python3-pip python3-dev libopencv-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Configure Application
```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

Required settings:
```bash
RTSP_URL=rtsp://username:password@camera-ip:554/stream
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
WEB_USERNAME=admin
WEB_PASSWORD=your-secure-password
```

### 4. Run Application
```bash
source venv/bin/activate
python3 main.py
```

### 5. Access Web Interface
- URL: `http://your-server-ip:5000`
- Login with credentials from `.env`

## 📖 Dokumentasi Lengkap

Untuk panduan instalasi lengkap di Proxmox LXC dengan optimasi Intel i5, lihat:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Panduan lengkap instalasi dan konfigurasi

## 📁 Struktur Project

```
riftech_ai_cam/
├── main.py                  # Main application code
├── requirements.txt         # Python dependencies
├── .env.example            # Configuration template
├── .env                    # Your configuration (create this)
├── SETUP_GUIDE.md          # Installation guide
├── README.md              # This file
├── venv/                  # Python virtual environment
├── known_faces/           # Known face photos
│   ├── Person1.jpg
│   └── Person2.jpg
├── uploads/               # Detection snapshots
│   ├── det_xxx_original.jpg
│   └── det_xxx_zoom.jpg
├── logs/                  # Application logs
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
│   ├── login.html
│   └── dashboard.html
├── detections.db          # SQLite database
└── yolov8n.pt            # YOLOv8n model (auto-download)
```

## ⚙️ Konfigurasi Utama

### AI Detection Settings (`.env`)
```bash
FRAME_PROCESS_INTERVAL=5      # Process every 5th frame (CPU optimization)
FRAME_RESIZE_WIDTH=640       # Resize to 640px width
ZOOM_FACTOR=2                # Zoom factor for face detection
CONFIDENCE_THRESHOLD=0.5     # YOLOv8 confidence threshold
```

### Auto-Delete Settings
```bash
AUTO_DELETE_AFTER=7          # Delete photos after 7 days (0 = disable)
CLEANUP_CHECK_INTERVAL=86400  # Check every 24 hours
```

### Performance Tuning
- **CPU Usage Tinggi (>80%)**: Increase `FRAME_PROCESS_INTERVAL` to 10
- **Detection Lambat**: Reduce `FRAME_RESIZE_WIDTH` to 480
- **False Positives**: Increase `CONFIDENCE_THRESHOLD` to 0.6

## 🤖 Cara Menggunakan Telegram Bot

### 1. Terima Notifikasi
Saat orang terdeteksi, bot mengirim 2 foto:
- Foto original (full frame)
- Foto zoom (zoom pada wajah/orang)

### 2. Self-Learning (Reply Nama)
- Reply foto notifikasi dengan nama orang
- Bot otomatis menambah ke `known_faces/`
- Deteksi berikutnya akan mengenali orang tersebut

### 3. Manual Upload
- Kirim foto orang ke bot
- Sertakan caption: "Nama Orang"
- Bot mengekstrak wajah dan menyimpan

## 📊 Performance Benchmarks

Expected performance pada Intel i5 (4 cores, no GPU):

| Konfigurasi | CPU Usage | Detection Speed |
|-------------|-----------|-----------------|
| 640px, Interval 5 | 40-60% | ~3-5 FPS |
| 640px, Interval 10 | 25-35% | ~2-3 FPS |
| 480px, Interval 5 | 30-45% | ~4-6 FPS |
| 480px, Interval 10 | 20-30% | ~2-4 FPS |

**Recommended**: Mulai dengan 640px, Interval 5, lalu sesuaikan berdasarkan CPU usage.

## 🔧 Troubleshooting

### RTSP Connection Issues
```bash
# Test RTSP dengan VLC player
vlc rtsp://username:password@camera-ip:554/stream

# Check network connectivity
ping camera-ip
```

### High CPU Usage
- Increase `FRAME_PROCESS_INTERVAL` di `.env`
- Reduce `FRAME_RESIZE_WIDTH` di `.env`
- Check processes: `htop`

### Face Recognition Not Working
- Pastikan foto di `known_faces/` jelas dan front-facing
- Format nama file: `Nama.jpg`
- Reload application setelah menambah foto

## 🔒 Security Best Practices

1. **Web Interface**: Gunakan password yang kuat
2. **RTSP Stream**: Gunakan password camera yang kuat
3. **Secret Key**: Generate dengan `openssl rand -hex 32`
4. **Network**: Batasi akses ke local network jika memungkinkan
5. **Firewall**: Hanya buka port yang diperlukan

## 🛠️ Maintenance

### Monitor Logs
```bash
# Jika dijalankan sebagai service
journalctl -u ai-cctv -f
```

### Backup Database
```bash
# Backup database
cp detections.db backup/detections_$(date +%Y%m%d).db

# Backup known faces
tar -czf backup/known_faces_$(date +%Y%m%d).tar.gz known_faces/
```

### Restart Service
```bash
systemctl restart ai-cctv
```

## 📝 Changelog

### Version 1.0.0 (January 2026)
- Initial release
- YOLOv8n person detection
- Face recognition with dlib
- Telegram bot with notifications
- Web dashboard with live stream
- Auto-delete old photos
- Self-learning feature
- Manual photo upload

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for educational and personal use.

## 📧 Support

For issues and questions:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Review troubleshooting section
3. Check logs for error messages

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Flask](https://flask.palletsprojects.com/)

---

**Built with ❤️ for home security**
