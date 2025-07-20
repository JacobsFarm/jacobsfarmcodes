# Camera and Telegram Bot Configuration File
# Fill in your personal camera details below

# RTSP URLs for cameras
# Camera 1 - position?
RTSP_URL_CAMERA1 = "rtsp://admin:YourPassword123@192.168.178.21:554/h264Preview_01_sub"
# Camera 2 - position?
RTSP_URL_CAMERA2 = "rtsp://admin:YourPassword123@192.168.178.22:554/h264Preview_01_sub"

# Adding more cameras - copy and fill in rtsp://
# RTSP_URL_CAMERA3 = "rtsp://admin:YourPassword123@192.168.178.25:554/h264Preview_01_sub"
# RTSP_URL_CAMERA4 = "rtsp://admin:YourPassword123@192.168.178.26:554/h264Preview_01_sub"

# if no telegram bot easily delete the following lines
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather on Telegram
TELEGRAM_CHAT_ID = ["PRIMARY_CHAT_ID", "SECONDARY_CHAT_ID", "THIRD_CHAT_ID"]  # Add multiple users - Get ID from @userinfobot
