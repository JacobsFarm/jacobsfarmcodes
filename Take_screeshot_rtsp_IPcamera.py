"""
Camera Screenshot Script - Simplified version
Automatically takes screenshots from an RTSP camera at regular intervals
"""

import cv2
import time
import os
from datetime import datetime

# ========================================
# CONFIGURATION PARAMETERS - EDIT HERE
# ========================================

# Camera settings - Choose one of the Soptions below:

# OPTION 1: Manual RTSP URL (uncomment to use)
# Generic RTSP URL format: rtsp://[username]:[password]@[ip_address]:[port]/[stream_path]
# RTSP_URL = "rtsp://admin:YourPassword123@192.168.178.26:554/h264Preview_01_sub"

# OPTION 2: RTSP URL from config.py (change CAMERA1 to desired camera)
# RTSP URL for the camera - now retrieved from config
# rtsp_url_camera1 = config.RTSP_URL_CAMERA1
# rtsp_url_camera2 = config.RTSP_URL_CAMERA2  
# rtsp_url_camera3 = config.RTSP_URL_CAMERA3
CONFIG_CAMERA = 'RTSP_URL_CAMERA1' 

# Screenshot timing
SCREENSHOT_INTERVAL = 10  # Interval in seconds (30 = every 30 seconds, 300 = every 5 minutes)

# File and folder settings
SCREENSHOT_DIR = "name_your_folder"  # Folder where screenshots are saved
SCREENSHOT_NAME = "name_image"  # Name for the screenshots
JPEG_QUALITY = 100  # Image quality for JPEG (0-100, higher = better quality)

# ========================================
# SCRIPT CODE - DO NOT EDIT BELOW HERE
# ========================================

# Camera URL configuration logic
# If RTSP_URL above is not set, try config.py
if 'RTSP_URL' not in locals():
    try:
        import config
        RTSP_URL = getattr(config, CONFIG_CAMERA, None)
        print(f"RTSP URL loaded from config.py ({CONFIG_CAMERA})")
    except ImportError:
        print("Error: No config.py found and no manual RTSP_URL set!")
        print("Set one of the following options:")
        print("1. Uncomment the RTSP_URL line above, OR")
        print("2. Create a config.py file with camera URLs")
        exit(1)
    
    if not RTSP_URL:
        print(f"Error: {CONFIG_CAMERA} not found in config.py!")
        print("Check available options in config.py...")
        exit(1)

def test_camera_connection():
    """Test the connection to the camera before starting the main program"""
    print("Testing camera connection...")
    
    try:
        # Try to connect with timeout
        cap = cv2.VideoCapture(RTSP_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Give the camera some time to connect
        time.sleep(2)
        
        if not cap.isOpened():
            print("❌ Error: Cannot connect to the camera")
            print(f"   RTSP URL: {RTSP_URL}")
            print("   Check:")
            print("   - If the camera is online")
            print("   - If the IP address and port are correct")
            print("   - If username and password are correct")
            print("   - If the stream path is correct")
            cap.release()
            return False
        
        # Try to read a frame
        print("Trying to read frame...")
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"✅ Camera connection successful!")
            print(f"   Resolution: {width}x{height}")
            print(f"   RTSP URL: {RTSP_URL}")
            return True
        else:
            print("❌ Error: Connection established but cannot read frame")
            print("   Camera possibly offline or stream not available")
            return False
            
    except Exception as e:
        print(f"❌ Error during connection test: {str(e)}")
        return False

def take_screenshot():
    """Take a screenshot from the camera"""
    try:
        # Connect to the camera
        cap = cv2.VideoCapture(RTSP_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("Error: Cannot connect to the camera")
            return False
        
        # Read a frame
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Generate filename with date and time
            now = datetime.now()
            filename = f"{SCREENSHOT_NAME}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Create directory if it doesn't exist
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            
            # Save screenshot
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            
            print(f"Screenshot saved: {filename}")
            return True
        else:
            print("Error: Could not read frame from camera")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    print(f"Camera screenshot service")
    print("=" * 50)
    
    # First test the camera connection
    if not test_camera_connection():
        print("\n❌ Connection test failed. Script will not start.")
        print("Fix the connection issues and try again.")
        return
    
    print("\n🚀 Service started!")
    print(f"Screenshots every {SCREENSHOT_INTERVAL} seconds in folder: {SCREENSHOT_DIR}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if take_screenshot():
                print(f"Waiting {SCREENSHOT_INTERVAL} seconds...")
            else:
                print("Screenshot failed. Retrying in 30 seconds...")
                time.sleep(30)
                continue
                
            time.sleep(SCREENSHOT_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nScript stopped by user")

if __name__ == "__main__":
    main()
