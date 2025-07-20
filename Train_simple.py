from ultralytics import YOLO

model = YOLO("yolo11m.pt")

model.train(data = "dataset_custom2.yaml", imgsz = 640, 
	batch = 8, epochs = 100, patience=20, workers = 0, device=0)
