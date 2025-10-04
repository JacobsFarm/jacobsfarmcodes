from ultralytics import YOLO

model = YOLO("custom_model.pt")

results = model.predict(
    # ============ SOURCE OPTIONS ============
    # Bestanden
    source="file_name.mp4",           # Enkele video
    # source="image.jpg",             # Enkele afbeelding (.jpg, .png, .bmp, etc.)
    # source="video.avi",             # Video (.mp4, .avi, .mov, .mkv, etc.)
    # source=["img1.jpg", "img2.jpg", "video.mp4"],  # Meerdere bestanden
    
    # Folders
    # source="path/to/folder/",       # Folder met afbeeldingen/videos
    # source="data/images/",          # Subfolder
    # source="dataset/*.jpg",         # Wildcards - alle jpg bestanden
    # source="videos/*.mp4",          # Alle mp4 bestanden in folder
    
    # Streams & Cameras
    # source=0,                       # Webcam (0=default, 1,2,3=andere cameras)
    # source="rtsp://username:password@192.168.1.100:554/stream",  # IP Camera/RTSP
    # source="http://example.com/stream.mjpg",  # HTTP Stream
    # source="https://www.youtube.com/watch?v=...",  # YouTube URL
    
    # Andere
    # source="screen",                # Screenshot (scherm opname)
    # source="screen 0",              # Specifieke monitor
    # source="https://example.com/image.jpg",  # URL naar afbeelding
    
    # ============ DETECTION PARAMETERS ============
    # conf=0.25,                      # Confidence threshold (0.0-1.0)
    # iou=0.7,                        # IoU threshold voor NMS
    # imgsz=640,                      # Image size (int of tuple zoals (640, 480))
    # half=False,                     # FP16 half-precision inference
    # device='',                      # Device: '0', 'cpu', '0,1,2,3', etc.
    
    # ============ SAVE & DISPLAY ============
    # save=False,                     # Save resultaten
    # save_txt=False,                 # Save als .txt bestanden
    # save_conf=False,                # Include confidence in txt
    # save_crop=False,                # Save cropped detecties
    # save_frames=False,              # Save frames bij video
    # show=False,                     # Toon resultaten real-time
    # show_labels=True,               # Toon labels in plot
    # show_conf=True,                 # Toon confidence scores
    # show_boxes=True,                # Toon bounding boxes
    
    # ============ VIDEO/STREAM OPTIONS ============
    # stream=False,                   # Stream mode voor lange videos
    # vid_stride=1,                   # Frame stride (1=elk frame, 2=elk 2e frame)
    # stream_buffer=False,            # Buffer streaming
    
    # ============ OUTPUT OPTIONS ============
    # project='runs/detect',          # Project folder
    # name='exp',                     # Experiment naam
    # exist_ok=False,                 # Overschrijf bestaande folder
    # line_width=None,                # Bounding box lijndikte (None=auto)
    # visualize=False,                # Visualiseer feature maps
    
    # ============ ADVANCED OPTIONS ============
    # augment=False,                  # Test-time augmentation
    # agnostic_nms=False,             # Class-agnostic NMS
    # classes=None,                   # Filter classes: bijv. [0, 2, 3]
    # retina_masks=False,             # High-res masks (segmentatie)
    # embed=None,                     # Return feature vectors
    # max_det=300,                    # Maximum detecties per image
    # verbose=True,                   # Verbose output
    # boxes=True,                     # Toon boxes (voor segmentatie/pose)
)
