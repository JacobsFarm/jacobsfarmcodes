from ultralytics import YOLO

# Load trained model
model = YOLO("custom_model.pt")

# Run the prediction on .mp4 /.jpg / .png etc. files
model.predict(source="file_name.mp4", show=True, save=True, conf=0.4, verbose=True)
