from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from db import connect_to_mongo, close_mongo_connection, get_collection
from routers import classroom, analytics, ai_report
import uvicorn
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(
    title="Smart Classroom Analytics - Edge AI Edition",
    version="1.0.0",
    description="Central backend for student counting, attendance analytics, and pedagogical reporting using Gemini API."
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(classroom.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(ai_report.router, prefix="/api")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await seed_initial_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {
        "service": "Smart Classroom Analytics API Backend",
        "status": "healthy",
        "documentation": "/docs"
    }

async def seed_initial_data():
    """
    Seeds initial demonstration data if MongoDB collections are empty.
    Allows immediate, beautiful visualization in dashboard.
    """
    classroom_col = get_collection("classrooms")
    attendance_col = get_collection("attendance_logs")
    focus_col = get_collection("focus_logs")
    
    # 1. Check if classrooms are empty
    count = await classroom_col.count_documents({})
    if count == 0:
        logger.info("MongoDB is empty. Seeding initial demonstration data...")
        
        # Insert classroom
        default_classroom = {
            "_id": "room_101",
            "name": "Phòng Học Thông Minh 101",
            "capacity": 30,
            "subject": "Trí Tuệ Nhân Tạo & Edge AI",
            "instructor": "PGS. TS. Nguyễn Văn A"
        }
        await classroom_col.insert_one(default_classroom)
        
        # Generate 30 points of historical data representing a 2.5 hour class (every 5 mins)
        now = datetime.utcnow()
        attendance_logs = []
        focus_logs = []
        
        # Base parameters that fluctuate realistically
        base_students = 24
        capacity = 30
        
        for i in range(30):
            time_offset = timedelta(minutes=5 * (30 - i))
            log_time = now - time_offset
            
            # Fluctuate student count: lower at beginning, peak in middle, slight drop at end
            if i < 5:
                present = random.randint(15, 20)  # coming in late
            elif i > 25:
                present = random.randint(21, 23)  # left early
            else:
                present = random.randint(22, 26)  # core attendance
                
            att_rate = (present / capacity) * 100
            
            attendance_logs.append({
                "classroom_id": "room_101",
                "present_count": present,
                "attendance_rate": round(att_rate, 2),
                "timestamp": log_time
            })
            
            # Focus score fluctuations: lower at start/end, high in middle
            if i < 5:
                focused = int(present * 0.5)
                distracted = int(present * 0.2)
            elif i > 22:
                focused = int(present * 0.4)
                distracted = int(present * 0.3)
            else:
                focused = int(present * 0.7)
                distracted = int(present * 0.1)
                
            neutral = present - focused - distracted
            focus_score = ((focused * 1.0 + neutral * 0.5) / present * 100) if present > 0 else 0
            
            focus_logs.append({
                "classroom_id": "room_101",
                "focused_count": focused,
                "neutral_count": neutral,
                "distracted_count": distracted,
                "focus_score": round(focus_score, 2),
                "timestamp": log_time
            })
            
        await attendance_col.insert_many(attendance_logs)
        await focus_col.insert_many(focus_logs)
        
        logger.info("Successfully seeded classrooms, attendance logs, and focus logs in MongoDB.")
    else:
        logger.info("MongoDB already contains data. Seeding skipped.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
