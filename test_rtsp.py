#!/usr/bin/env python3
"""
Test RTSP Connection Script
Test if RTSP camera is accessible
"""

import cv2
import sys
from dotenv import load_dotenv
import os

load_dotenv()

RTSP_URL = os.getenv('RTSP_URL', 'rtsp://admin:Kuncong0203@10.26.27.196:554/live/ch00_1')

def test_rtsp():
    """Test RTSP connection"""
    print("=" * 50)
    print("RTSP Connection Test")
    print("=" * 50)
    print(f"RTSP URL: {RTSP_URL}")
    print("")
    
    print("Attempting to connect to camera...")
    
    try:
        # Create video capture object
        cap = cv2.VideoCapture(RTSP_URL)
        
        if not cap.isOpened():
            print("❌ FAILED: Cannot open RTSP stream")
            print("")
            print("Troubleshooting:")
            print("1. Check if camera is on and connected to network")
            print("2. Verify RTSP URL format")
            print("3. Test with VLC player: vlc <RTSP_URL>")
            print("4. Check firewall settings")
            return False
        
        print("✅ SUCCESS: Connected to camera")
        print("")
        
        # Read a few frames to test
        print("Reading frames...")
        frame_count = 0
        max_frames = 100
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                print(f"❌ FAILED: Cannot read frame {frame_count + 1}")
                cap.release()
                return False
            
            frame_count += 1
            print(f"Frame {frame_count}: {frame.shape[1]}x{frame.shape[0]} pixels")
            
            # Stop after 10 frames for quick test
            if frame_count >= 10:
                break
        
        print("")
        print(f"✅ SUCCESS: Successfully read {frame_count} frames")
        print("")
        
        # Get stream properties
        print("Stream Properties:")
        print(f"  Width: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}")
        print(f"  Height: {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS):.2f}")
        print(f"  Codec: {hex(int(cap.get(cv2.CAP_PROP_FOURCC)))}")
        print("")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_rtsp()
    sys.exit(0 if success else 1)
