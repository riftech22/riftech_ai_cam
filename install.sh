#!/bin/bash
# ============================================
# AI CCTV Security System - Complete Installation Script
# ============================================
# Server IP: 10.26.27.109
# Camera RTSP: rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1
# ============================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_header "AI CCTV Security System - Installation"
print_info "Server IP: 10.26.27.109"
print_info "Camera RTSP: rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1"
print_warning "This will take 15-30 minutes to complete"
echo ""

# ============================================
# Step 1: System Update
# ============================================
print_header "[1/10] Updating System"
apt update && apt upgrade -y
print_success "System updated"

# ============================================
# Step 2: Install System Dependencies
# ============================================
print_header "[2/10] Installing System Dependencies"
print_info "Installing build tools, cmake, git, etc..."

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

print_success "System dependencies installed"

# ============================================
# Step 3: Set CPU Governor to Performance
# ============================================
print_header "[3/10] Optimizing CPU Performance"
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
print_success "CPU governor set to performance mode"

# ============================================
# Step 4: Install dlib from Source
# ============================================
print_header "[4/10] Installing dlib (This takes 10-20 minutes)"
print_warning "Please be patient, this is a long process..."

cd /tmp
if [ -d "dlib" ]; then
    print_info "dlib directory exists, removing..."
    rm -rf dlib
fi

git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=0 -DUSE_SSE2_INSTRUCTIONS=ON
cmake --build . --config Release
make install
cd /tmp
rm -rf dlib

print_success "dlib installed successfully"

# ============================================
# Step 5: Create Project Directory
# ============================================
print_header "[5/10] Creating Project Directory"
mkdir -p /root/riftech_ai_cam
cd /root/riftech_ai_cam

# Create subdirectories
mkdir -p known_faces uploads logs templates static
touch known_faces/.gitkeep uploads/.gitkeep logs/.gitkeep

print_success "Project directory created at /root/riftech_ai_cam"

# ============================================
# Step 6: Create requirements.txt
# ============================================
print_header "[6/10] Creating requirements.txt"

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

print_success "requirements.txt created"

# ============================================
# Step 7: Create .env Configuration File
# ============================================
print_header "[7/10] Creating .env Configuration"

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

print_success ".env configuration created"
print_warning "You need to edit SECRET_KEY, WEB_USERNAME, and WEB_PASSWORD"

# ============================================
# Step 8: Setup Python Virtual Environment
# ============================================
print_header "[8/10] Setting Up Python Virtual Environment"

# Upgrade pip
pip3 install --upgrade pip

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

print_success "Virtual environment created"

# Install Python dependencies
print_info "Installing Python packages (this may take 5-10 minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Python dependencies installed"

# ============================================
# Step 9: Download YOLOv8n Model
# ============================================
print_header "[9/10] Downloading YOLOv8n Model"

if [ ! -f "yolov8n.pt" ]; then
    wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O yolov8n.pt
    print_success "YOLOv8n model downloaded"
else
    print_info "YOLOv8n model already exists"
fi

# ============================================
# Step 10: Create Helper Scripts
# ============================================
print_header "[10/10] Creating Helper Scripts"

# Create test_rtsp.py
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
        
        print("Stream Properties:")
        print(f"  Width: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}")
        print(f"  Height: {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS):.2f}")
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
print_success "test_rtsp.py created"

# Create start.sh
cat > start.sh << 'EOF'
#!/bin/bash
cd /root/riftech_ai_cam
source venv/bin/activate
python3 main.py
EOF

chmod +x start.sh
print_success "start.sh created"

# Create stop.sh
cat > stop.sh << 'EOF'
#!/bin/bash
pkill -f "python3 main.py"
EOF

chmod +x stop.sh
print_success "stop.sh created"

# Create systemd service file
cat > /root/riftech_ai_cam/ai-cctv.service << 'EOF'
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
EOF

print_success "Systemd service file created"

# ============================================
# Installation Complete
# ============================================
print_header "Installation Complete!"
echo ""

print_success "System is ready for configuration"
echo ""

print_info "Next Steps:"
echo ""
echo "1. Upload the following files to /root/riftech_ai_cam/:"
echo "   - main.py"
echo "   - templates/login.html"
echo "   - templates/dashboard.html"
echo ""
echo "2. Edit .env file:"
echo "   nano /root/riftech_ai_cam/.env"
echo ""
echo "3. Generate secret key and update .env:"
echo "   openssl rand -hex 32"
echo "   # Copy the result to SECRET_KEY in .env"
echo ""
echo "4. Set web credentials in .env:"
echo "   WEB_USERNAME=admin"
echo "   WEB_PASSWORD=your-secure-password"
echo ""
echo "5. Test RTSP connection:"
echo "   cd /root/riftech_ai_cam"
echo "   source venv/bin/activate"
echo "   python3 test_rtsp.py"
echo ""
echo "6. Start the application:"
echo "   ./start.sh"
echo ""
echo "7. Access web dashboard:"
echo "   http://10.26.27.109:5000"
echo ""
echo "8. (Optional) Install as systemd service:"
echo "   cp /root/riftech_ai_cam/ai-cctv.service /etc/systemd/system/"
echo "   systemctl daemon-reload"
echo "   systemctl enable ai-cctv"
echo "   systemctl start ai-cctv"
echo ""

print_warning "IMPORTANT: You must upload main.py and template files before running!"
print_info "These files are too large to include in this script"
echo ""

print_info "Files to upload:"
print "  - main.py (600+ lines)"
print "  - templates/login.html"
print "  - templates/dashboard.html"
echo ""

print_info "Upload methods:"
echo "  1. SCP: scp main.py root@10.26.27.109:/root/riftech_ai_cam/"
echo "  2. SFTP: Use FileZilla, WinSCP, or Cyberduck"
echo "  3. Copy-paste: nano main.py (paste content)"
echo ""

print_success "Installation script completed successfully!"
