from ultralytics import YOLO

# Load trained model
model = YOLO("custom_model.pt")

# Run the prediction on your folder
model.predict(source=r"path/to/folder/", show=True, save=True, conf=0.4, verbose=True)
