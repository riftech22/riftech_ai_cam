#!/bin/bash
# Quick Setup Script for AI CCTV Security System
# Server IP: 10.26.27.109
# Camera RTSP: rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1

echo "================================"
echo "AI CCTV Security System Setup"
echo "Server IP: 10.26.27.109"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Update system
echo "[1/7] Updating system..."
apt update && apt upgrade -y

# Install essential build tools
echo "[2/7] Installing build tools..."
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
    cpufrequtils \
    htop

# Set CPU governor to performance
echo "[3/7] Setting CPU governor to performance..."
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils

# Install dlib from source
echo "[4/7] Installing dlib (this may take 10-20 minutes)..."
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

# Upgrade pip
echo "[5/7] Upgrading pip..."
pip3 install --upgrade pip
pip3 install virtualenv

# Install Python dependencies
echo "[6/7] Installing Python dependencies..."
cd /root/riftech_ai_cam
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Download YOLOv8n model
echo "[7/7] Downloading YOLOv8n model..."
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt -O /root/riftech_ai_cam/yolov8n.pt

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "Next Steps:"
echo "1. Edit .env file and add your Telegram bot token and chat ID"
echo "   nano /root/riftech_ai_cam/.env"
echo ""
echo "2. Get Telegram Bot Token:"
echo "   - Open Telegram and search for @BotFather"
echo "   - Send /newbot and follow instructions"
echo ""
echo "3. Get Telegram Chat ID:"
echo "   - Open Telegram and search for @userinfobot"
echo "   - Send any message to the bot"
echo ""
echo "4. Generate Secret Key:"
echo "   openssl rand -hex 32"
echo ""
echo "5. Set Web Username and Password in .env"
echo ""
echo "6. Test the application:"
echo "   cd /root/riftech_ai_cam"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "7. Access web interface:"
echo "   http://10.26.27.109:5000"
echo ""
echo "8. To run as service, follow SETUP_GUIDE.md"
echo ""
