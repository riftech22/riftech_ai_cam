#!/usr/bin/env python3
"""
AI-Based CCTV Security System
Features: Person detection, face recognition, Telegram bot, Web dashboard
Optimized for Intel i5 CPU (no GPU)
"""

import os
import sys
import time
import threading
import sqlite3
import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# AI & Computer Vision
from ultralytics import YOLO
import face_recognition

# Web Framework
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Telegram Bot
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# ============== CONFIGURATION ==============
RTSP_URL = os.getenv('RTSP_URL', '')
CAMERA_NAME = os.getenv('CAMERA_NAME', 'Kamera Depan')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
FRAME_PROCESS_INTERVAL = int(os.getenv('FRAME_PROCESS_INTERVAL', 5))
FRAME_RESIZE_WIDTH = int(os.getenv('FRAME_RESIZE_WIDTH', 640))
ZOOM_FACTOR = float(os.getenv('ZOOM_FACTOR', 2))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
AUTO_DELETE_AFTER = int(os.getenv('AUTO_DELETE_AFTER', 7))
CLEANUP_CHECK_INTERVAL = int(os.getenv('CLEANUP_CHECK_INTERVAL', 86400))
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')
WEB_USERNAME = os.getenv('WEB_USERNAME', 'admin')
WEB_PASSWORD = os.getenv('WEB_PASSWORD', 'admin')
WEB_PORT = int(os.getenv('WEB_PORT', 5000))
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'detections.db')

# ============== DIRECTORIES ==============
KNOWN_FACES_DIR = Path('known_faces')
UPLOADS_DIR = Path('uploads')
LOGS_DIR = Path('logs')

for dir_path in [KNOWN_FACES_DIR, UPLOADS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# ============== DATABASE SETUP ==============
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            person_name TEXT,
            status TEXT NOT NULL,
            original_photo_path TEXT,
            zoom_photo_path TEXT,
            camera_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON detections(timestamp)
    ''')
    
    conn.commit()
    conn.close()

def save_detection(timestamp, person_name, status, original_path, zoom_path, camera_name):
    """Save detection to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO detections (timestamp, person_name, status, original_photo_path, zoom_photo_path, camera_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, person_name, status, original_path, zoom_path, camera_name))
    
    conn.commit()
    conn.close()

def get_detections(limit=100, status=None):
    """Get detections from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute('''
            SELECT * FROM detections 
            WHERE status = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (status, limit))
    else:
        cursor.execute('''
            SELECT * FROM detections 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
    
    detections = cursor.fetchall()
    conn.close()
    return detections

def delete_old_detections():
    """Delete detections older than AUTO_DELETE_AFTER days"""
    if AUTO_DELETE_AFTER <= 0:
        return
    
    cutoff_date = datetime.now() - timedelta(days=AUTO_DELETE_AFTER)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get old detections
    cursor.execute('''
        SELECT id, original_photo_path, zoom_photo_path 
        FROM detections 
        WHERE timestamp < ?
    ''', (cutoff_date.isoformat(),))
    
    old_detections = cursor.fetchall()
    
    # Delete files and database records
    for detection in old_detections:
        detection_id, original_path, zoom_path = detection
        
        # Delete files
        try:
            if original_path and os.path.exists(original_path):
                os.remove(original_path)
            if zoom_path and os.path.exists(zoom_path):
                os.remove(zoom_path)
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        # Delete from database
        cursor.execute('DELETE FROM detections WHERE id = ?', (detection_id,))
    
    conn.commit()
    conn.close()
    
    if old_detections:
        print(f"[Cleanup] Deleted {len(old_detections)} old detections")

# ============== FACE RECOGNITION ==============
def load_known_faces():
    """Load known faces from known_faces directory"""
    known_encodings = []
    known_names = []
    
    for image_path in KNOWN_FACES_DIR.glob('*.jpg'):
        name = image_path.stem
        
        # Load image and detect faces
        image = face_recognition.load_image_file(str(image_path))
        
        # Detect face locations using HOG (CPU optimized)
        face_locations = face_recognition.face_locations(image, model='hog')
        
        if face_locations:
            # Get first face encoding
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            known_encodings.append(face_encoding)
            known_names.append(name)
    
    return known_encodings, known_names

def recognize_face(face_image, known_encodings, known_names):
    """Recognize face from image"""
    try:
        # Detect faces using HOG
        face_locations = face_recognition.face_locations(face_image, model='hog')
        
        if not face_locations:
            return None, None
        
        # Get face encoding
        face_encoding = face_recognition.face_encodings(face_image, face_locations)[0]
        
        # Compare with known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        
        if True in matches:
            match_index = matches.index(True)
            return known_names[match_index], face_locations[0]
        
        return None, face_locations[0]
    
    except Exception as e:
        print(f"[Face Recognition Error] {e}")
        return None, None

# ============== AI DETECTION ==============
# Load YOLOv8n model (nano version for CPU)
yolo_model = YOLO('yolov8n.pt')

# Load known faces
known_encodings, known_names = load_known_faces()

# Global variable for latest frame
latest_frame = None
frame_lock = threading.Lock()

def zoom_frame(frame, bbox, zoom_factor=2):
    """Zoom into the specified bounding box area"""
    x1, y1, x2, y2 = bbox
    
    # Calculate center
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    # Calculate dimensions
    width = x2 - x1
    height = y2 - y1
    
    # Calculate zoom dimensions
    zoom_width = int(width * zoom_factor)
    zoom_height = int(height * zoom_factor)
    
    # Calculate new coordinates
    new_x1 = max(0, center_x - zoom_width // 2)
    new_y1 = max(0, center_y - zoom_height // 2)
    new_x2 = min(frame.shape[1], new_x1 + zoom_width)
    new_y2 = min(frame.shape[0], new_y1 + zoom_height)
    
    # Crop and resize
    zoomed = frame[new_y1:new_y2, new_x1:new_x2]
    
    # Resize to a reasonable size for sending
    zoomed = cv2.resize(zoomed, (640, 480))
    
    return zoomed

def process_frame(frame):
    """Process frame for person detection and face recognition"""
    # Resize frame for CPU optimization
    height, width = frame.shape[:2]
    scale = FRAME_RESIZE_WIDTH / width
    resized_frame = cv2.resize(frame, (FRAME_RESIZE_WIDTH, int(height * scale)))
    
    # Detect persons using YOLOv8n
    results = yolo_model(resized_frame, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    persons_detected = []
    
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = box.conf[0].cpu().numpy()
            
            # Scale back to original frame
            x1 = int(x1 / scale)
            y1 = int(y1 / scale)
            x2 = int(x2 / scale)
            y2 = int(y2 / scale)
            
            # Extract person area
            person_area = frame[y1:y2, x1:x2]
            
            # Recognize face
            person_name, face_location = recognize_face(person_area, known_encodings, known_names)
            
            status = 'known' if person_name else 'unknown'
            
            persons_detected.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': float(confidence),
                'person_name': person_name if person_name else 'Unknown',
                'status': status,
                'face_location': face_location
            })
    
    return persons_detected

# ============== TELEGRAM BOT ==============
pending_detections = {}  # Store detection ID for self-learning

async def send_detection_notification(original_frame, zoomed_frame, person_name, status, timestamp):
    """Send detection notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare caption with detailed info
    caption = f"""🚨 PERSON DETECTED

📅 Tanggal: {timestamp_str}
👤 Status: {'Dikenal' if status == 'known' else 'Tidak Dikenal'}
📍 Lokasi: {CAMERA_NAME}"""
    
    if person_name and person_name != 'Unknown':
        caption += f"\n🏷️ Nama: {person_name}"
    
    caption += "\n\nReply foto ini dengan nama untuk menambah ke known_faces"
    
    try:
        # Save photos temporarily
        timestamp_id = int(time.time())
        original_path = UPLOADS_DIR / f"temp_original_{timestamp_id}.jpg"
        zoom_path = UPLOADS_DIR / f"temp_zoom_{timestamp_id}.jpg"
        
        cv2.imwrite(str(original_path), original_frame)
        cv2.imwrite(str(zoom_path), zoomed_frame)
        
        # Send original photo
        with open(original_path, 'rb') as photo:
            message = await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption=f"{caption}\n\n[Foto Original]"
            )
        
        # Store detection info for self-learning
        detection_id = message.message_id
        pending_detections[detection_id] = {
            'timestamp': timestamp,
            'original_path': str(original_path),
            'zoom_path': str(zoom_path),
            'status': status
        }
        
        # Send zoomed photo
        with open(zoom_path, 'rb') as photo:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo,
                caption="[Foto Zoom]"
            )
    
    except Exception as e:
        print(f"[Telegram Error] Failed to send notification: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual photo upload with name in caption"""
    if not update.message or not update.message.photo:
        return
    
    # Get the largest photo
    photo = update.message.photo[-1]
    caption = update.message.caption
    
    if not caption:
        await update.message.reply_text("❌ Mohon sertakan nama orang dalam caption")
        return
    
    name = caption.strip()
    
    try:
        # Download photo
        photo_file = await photo.get_file()
        photo_path = UPLOADS_DIR / f"upload_{int(time.time())}.jpg"
        await photo_file.download_to_drive(str(photo_path))
        
        # Load and process image
        image = cv2.imread(str(photo_path))
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face
        face_locations = face_recognition.face_locations(rgb_image, model='hog')
        
        if not face_locations:
            await update.message.reply_text("❌ Tidak ada wajah terdeteksi di foto")
            return
        
        # Extract and save face
        top, right, bottom, left = face_locations[0]
        face_image = rgb_image[top:bottom, left:right]
        
        # Save to known_faces
        face_path = KNOWN_FACES_DIR / f"{name}.jpg"
        cv2.imwrite(str(face_path), cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
        
        # Reload known faces
        global known_encodings, known_names
        known_encodings, known_names = load_known_faces()
        
        await update.message.reply_text(f"✅ Wajah {name} berhasil ditambahkan!")
        
    except Exception as e:
        print(f"[Photo Upload Error] {e}")
        await update.message.reply_text(f"❌ Gagal memproses foto: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reply to detection notification for self-learning"""
    if not update.message or not update.message.reply_to_message:
        return
    
    # Check if replying to a detection
    reply_message_id = update.message.reply_to_message.message_id
    
    # Find the detection (check if it's the original photo or zoom photo)
    detection_id = None
    if reply_message_id in pending_detections:
        detection_id = reply_message_id
    else:
        # Check if it's a reply to zoom photo (find the original)
        for det_id, det_info in pending_detections.items():
            if reply_message_id == det_id + 1:  # Zoom photo is sent after original
                detection_id = det_id
                break
    
    if detection_id is None:
        return
    
    detection_info = pending_detections[detection_id]
    name = update.message.text.strip()
    
    if not name:
        return
    
    try:
        # Load zoomed photo (better quality for face recognition)
        image = cv2.imread(detection_info['zoom_path'])
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect and extract face
        face_locations = face_recognition.face_locations(rgb_image, model='hog')
        
        if not face_locations:
            await update.message.reply_text("❌ Tidak ada wajah terdeteksi di foto")
            return
        
        # Extract and save face
        top, right, bottom, left = face_locations[0]
        face_image = rgb_image[top:bottom, left:right]
        
        # Save to known_faces
        face_path = KNOWN_FACES_DIR / f"{name}.jpg"
        cv2.imwrite(str(face_path), cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
        
        # Reload known faces
        global known_encodings, known_names
        known_encodings, known_names = load_known_faces()
        
        # Update database if this was an unknown person
        if detection_info['status'] == 'unknown':
            timestamp = detection_info['timestamp']
            # Update the detection record
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE detections 
                SET person_name = ?, status = 'known'
                WHERE timestamp = ? AND person_name = 'Unknown'
            ''', (name, timestamp))
            conn.commit()
            conn.close()
        
        # Delete pending detection
        del pending_detections[detection_id]
        
        await update.message.reply_text(f"✅ Wajah {name} berhasil ditambahkan ke known_faces!")
        
    except Exception as e:
        print(f"[Self-Learning Error] {e}")
        await update.message.reply_text(f"❌ Gagal memproses wajah: {e}")

# ============== FLASK WEB INTERFACE ==============
app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == WEB_USERNAME and password == WEB_PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Username atau password salah')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'known':
        detections = get_detections(limit=200, status='known')
    elif status_filter == 'unknown':
        detections = get_detections(limit=200, status='unknown')
    else:
        detections = get_detections(limit=200)
    
    return render_template('dashboard.html', detections=detections, status_filter=status_filter)

@app.route('/stream')
@login_required
def stream():
    """Video streaming route"""
    def generate():
        global latest_frame
        while True:
            with frame_lock:
                if latest_frame is not None:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', latest_frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    # Send placeholder if no frame
                    placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                    ret, buffer = cv2.imencode('.jpg', placeholder)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/known_faces')
@login_required
def api_known_faces():
    """API to get list of known faces"""
    known_faces = []
    for face_path in KNOWN_FACES_DIR.glob('*.jpg'):
        known_faces.append(face_path.stem)
    return jsonify(known_faces)

@app.route('/api/delete_detection/<int:detection_id>', methods=['DELETE'])
@login_required
def delete_detection(detection_id):
    """Delete a specific detection"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT original_photo_path, zoom_photo_path FROM detections WHERE id = ?', (detection_id,))
    detection = cursor.fetchone()
    
    if detection:
        original_path, zoom_path = detection
        
        # Delete files
        try:
            if original_path and os.path.exists(original_path):
                os.remove(original_path)
            if zoom_path and os.path.exists(zoom_path):
                os.remove(zoom_path)
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        # Delete from database
        cursor.execute('DELETE FROM detections WHERE id = ?', (detection_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    conn.close()
    return jsonify({'success': False}), 404

# ============== MAIN DETECTION LOOP ==============
def detection_loop():
    """Main AI detection loop"""
    global latest_frame, known_encodings, known_names
    
    print("[AI] Starting detection loop...")
    
    cap = cv2.VideoCapture(RTSP_URL)
    
    if not cap.isOpened():
        print(f"[Error] Cannot connect to RTSP stream: {RTSP_URL}")
        return
    
    frame_count = 0
    last_notification_time = {}
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("[Error] Failed to read frame")
            time.sleep(1)
            continue
        
        # Update latest frame for web streaming
        with frame_lock:
            latest_frame = frame.copy()
        
        # Process every Nth frame
        frame_count += 1
        if frame_count % FRAME_PROCESS_INTERVAL != 0:
            continue
        
        # Detect persons
        persons = process_frame(frame)
        
        if persons:
            for person in persons:
                person_name = person['person_name']
                status = person['status']
                
                # Generate unique ID for this person (based on bbox position)
                bbox_id = f"{int(person['bbox'][0]/50)}_{int(person['bbox'][1]/50)}"
                
                # Check cooldown for notifications (avoid spam)
                current_time = time.time()
                if bbox_id in last_notification_time:
                    if current_time - last_notification_time[bbox_id] < 30:  # 30 seconds cooldown
                        continue
                
                # Save photos
                timestamp_str = datetime.now().isoformat()
                timestamp_id = int(time.time())
                
                original_path = UPLOADS_DIR / f"det_{timestamp_id}_original.jpg"
                zoomed_path = UPLOADS_DIR / f"det_{timestamp_id}_zoom.jpg"
                
                # Draw bounding box on original
                annotated_frame = frame.copy()
                x1, y1, x2, y2 = person['bbox']
                color = (0, 255, 0) if status == 'known' else (0, 0, 255)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                label = f"{person_name} ({person['confidence']:.2f})"
                cv2.putText(annotated_frame, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Create zoomed frame
                zoomed_frame = zoom_frame(annotated_frame, person['bbox'], ZOOM_FACTOR)
                
                # Save files
                cv2.imwrite(str(original_path), annotated_frame)
                cv2.imwrite(str(zoomed_frame), zoomed_frame)
                
                # Save to database
                save_detection(
                    timestamp_str,
                    person_name,
                    status,
                    str(original_path),
                    str(zoomed_path),
                    CAMERA_NAME
                )
                
                # Send Telegram notification
                send_detection_notification(
                    annotated_frame,
                    zoomed_frame,
                    person_name,
                    status,
                    timestamp_str
                )
                
                # Update last notification time
                last_notification_time[bbox_id] = current_time
        
        time.sleep(0.01)

# ============== CLEANUP TASK ==============
def cleanup_task():
    """Periodic cleanup of old detections"""
    while True:
        delete_old_detections()
        time.sleep(CLEANUP_CHECK_INTERVAL)

# ============== MAIN ==============
if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start Telegram bot
    global bot
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot = bot_app.bot
    
    # Add handlers
    bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot in thread with asyncio
    def run_bot():
        asyncio.run(bot_app.run_polling())
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start cleanup task
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    # Start detection loop
    detection_thread = threading.Thread(target=detection_loop, daemon=True)
    detection_thread.start()
    
    # Start Flask web server
    print(f"[Web] Starting web server on {WEB_HOST}:{WEB_PORT}")
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False, threaded=True)
