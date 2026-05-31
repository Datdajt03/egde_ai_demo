from fastapi import FastAPI, UploadFile, File, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import cv2
import numpy as np
import asyncio
import httpx
import time
import logging
from typing import Dict, Any

from simulator import ClassroomSimulator
from yolo_detector import YOLODetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

app = FastAPI(
    title="Smart Classroom - Edge AI Service",
    version="1.0.0",
    description="Local Edge AI video processor running YOLOv8 student detection and focus state tracking."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
detector = YOLODetector("yolov8n.pt")
simulator = ClassroomSimulator()
use_simulation = True # Default to simulation since physical cameras fail in containerized environments
camera = None

def init_camera():
    global camera, use_simulation
    logger.info("Attempting to initialize physical webcam (index 0)...")
    try:
        # Try to open webcam (0)
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            # Check if camera actually yields a frame
            ret, frame = camera.read()
            if ret:
                logger.info("Physical webcam detected and working. Disabling simulation mode.")
                use_simulation = False
            else:
                logger.warning("Physical webcam opened but failed to read frames. Falling back to simulation.")
                camera.release()
                camera = None
                use_simulation = True
        else:
            logger.warning("No physical webcam found at index 0. Falling back to simulation mode.")
            camera = None
            use_simulation = True
    except Exception as e:
        logger.error(f"Error initializing webcam: {e}. Falling back to simulation mode.")
        use_simulation = True

@app.on_event("startup")
async def startup_event():
    init_camera()
    # Start background telemetry loop to backend
    asyncio.create_task(telemetry_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global camera
    if camera:
        camera.release()
        logger.info("Released physical webcam resource.")

def get_current_metrics() -> Dict[str, Any]:
    """
    Retrieves telemetry metrics from either the active webcam (YOLO) or the simulator.
    """
    global use_simulation, camera, detector, simulator
    
    if use_simulation:
        stats = simulator.get_analytics()
        focus_score = ((stats["focused"] * 1.0 + stats["neutral"] * 0.5) / stats["total"] * 100) if stats["total"] > 0 else 0
        return {
            "classroom_id": "room_101",
            "present_count": stats["total"],
            "attendance_rate": round((stats["total"] / 30) * 100, 2), # capacity = 30
            "focused_count": stats["focused"],
            "neutral_count": stats["neutral"],
            "distracted_count": stats["distracted"],
            "focus_score": round(focus_score, 2)
        }
    else:
        # Read a frame from camera, run detection
        if camera and camera.isOpened():
            ret, frame = camera.read()
            if ret:
                _, detections = detector.detect_students(frame)
                total = len(detections)
                focused = sum(1 for d in detections if d["state"] == "Focused")
                neutral = sum(1 for d in detections if d["state"] == "Neutral")
                distracted = sum(1 for d in detections if d["state"] == "Distracted")
                focus_score = ((focused * 1.0 + neutral * 0.5) / total * 100) if total > 0 else 0
                
                return {
                    "classroom_id": "room_101",
                    "present_count": total,
                    "attendance_rate": round((total / 30) * 100, 2),
                    "focused_count": focused,
                    "neutral_count": neutral,
                    "distracted_count": distracted,
                    "focus_score": round(focus_score, 2)
                }
        
        # Fallback if webcam read fails on the fly
        logger.warning("Webcam read failed, using simulator telemetry as fallback.")
        return get_current_metrics()

async def telemetry_loop():
    """
    Pushes telemetry logs to the FastAPI backend API every 5 seconds.
    """
    backend_url = "http://backend:8000/api/classrooms/room_101"
    client = httpx.AsyncClient()
    
    logger.info("Starting background telemetry push loop...")
    await asyncio.sleep(5) # Let backend seed data and startup first
    
    while True:
        try:
            metrics = get_current_metrics()
            
            # Post Attendance Log
            attendance_data = {
                "classroom_id": "room_101",
                "present_count": metrics["present_count"],
                "attendance_rate": metrics["attendance_rate"]
            }
            att_resp = await client.post(f"{backend_url}/attendance", json=attendance_data, timeout=2.0)
            
            # Post Focus Log
            focus_data = {
                "classroom_id": "room_101",
                "focused_count": metrics["focused_count"],
                "neutral_count": metrics["neutral_count"],
                "distracted_count": metrics["distracted_count"],
                "focus_score": metrics["focus_score"]
            }
            foc_resp = await client.post(f"{backend_url}/focus", json=focus_data, timeout=2.0)
            
            if att_resp.status_code == 201 and foc_resp.status_code == 201:
                logger.info(f"Telemetry pushed successfully. Students: {metrics['present_count']}, Focus Score: {metrics['focus_score']}%")
            else:
                logger.warning(f"Failed to push telemetry. Backend status: Attendance={att_resp.status_code}, Focus={foc_resp.status_code}")
                
        except Exception as e:
            logger.error(f"Error pushing telemetry to backend: {e}. Retrying in 5s...")
            
        await asyncio.sleep(5.0)

def generate_video_stream():
    """
    Generates annotated video frames as MJPEG parts.
    """
    global camera, use_simulation, detector, simulator
    
    while True:
        try:
            if use_simulation:
                frame = simulator.generate_frame()
            else:
                if camera and camera.isOpened():
                    ret, frame = camera.read()
                    if ret:
                        frame, _ = detector.detect_students(frame)
                    else:
                        logger.warning("Camera frame read failed. Reverting to simulator.")
                        use_simulation = True
                        frame = simulator.generate_frame()
                else:
                    use_simulation = True
                    frame = simulator.generate_frame()

            # Encode frame to JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Limit framerate to 10-15 fps to reduce CPU overhead
            time.sleep(0.08)
            
        except Exception as e:
            logger.error(f"Error in video streaming generator: {e}")
            time.sleep(1.0)

@app.get("/video_feed")
def video_feed():
    """
    Exposes the real-time annotated video stream.
    """
    return StreamingResponse(
        generate_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/analytics")
def get_analytics():
    """
    Returns current analytics statistics.
    """
    return get_current_metrics()

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image and performs YOLO detection.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        annotated_frame, detections = detector.detect_students(frame)
        
        # Calculate scores
        total = len(detections)
        focused = sum(1 for d in detections if d["state"] == "Focused")
        neutral = sum(1 for d in detections if d["state"] == "Neutral")
        distracted = sum(1 for d in detections if d["state"] == "Distracted")
        focus_score = ((focused * 1.0 + neutral * 0.5) / total * 100) if total > 0 else 0
        
        return {
            "status": "success",
            "students_detected": total,
            "focused": focused,
            "neutral": neutral,
            "distracted": distracted,
            "focus_score": round(focus_score, 2),
            "detections": [
                {
                    "id": d["id"],
                    "bounding_box": d["box"],
                    "confidence": round(d["confidence"], 2),
                    "state": d["state"]
                } for d in detections
            ]
        }
    except Exception as e:
        logger.error(f"Error processing image upload: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
def healthcheck():
    return {
        "status": "healthy",
        "simulation_mode": use_simulation,
        "yolo_loaded": detector.model_loaded
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
