import os
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download_model")

def download():
    logger.info("Pre-downloading YOLOv8n weights...")
    model_name = "yolov8n.pt"
    # This will download the model to the current directory
    model = YOLO(model_name)
    logger.info("YOLOv8n weights downloaded successfully.")

if __name__ == "__main__":
    download()
