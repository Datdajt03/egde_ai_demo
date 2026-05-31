from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from models import Classroom, ClassroomCreate, AttendanceLog, AttendanceLogCreate, FocusLog, FocusLogCreate
from db import get_collection
from datetime import datetime

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])

@router.post("/", response_model=ClassroomCreate, status_code=status.HTTP_201_CREATED)
async def create_classroom(classroom: ClassroomCreate):
    classroom_col = get_collection("classrooms")
    
    # Check if exists
    existing = await classroom_col.find_one({"_id": classroom.id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom with id {classroom.id} already exists."
        )
    
    doc = classroom.dict()
    doc["_id"] = doc.pop("id")
    await classroom_col.insert_one(doc)
    return classroom

@router.get("/", response_model=List[Classroom])
async def list_classrooms():
    classroom_col = get_collection("classrooms")
    cursor = classroom_col.find()
    classrooms = []
    async for doc in cursor:
        classrooms.append(Classroom(**doc))
    return classrooms

@router.get("/{classroom_id}", response_model=Classroom)
async def get_classroom(classroom_id: str):
    classroom_col = get_collection("classrooms")
    doc = await classroom_col.find_one({"_id": classroom_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with id {classroom_id} not found."
        )
    return Classroom(**doc)

@router.post("/{classroom_id}/attendance", status_code=status.HTTP_201_CREATED)
async def log_attendance(classroom_id: str, log: AttendanceLogCreate):
    # Verify classroom exists
    classroom_col = get_collection("classrooms")
    classroom = await classroom_col.find_one({"_id": classroom_id})
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    attendance_col = get_collection("attendance_logs")
    doc = log.dict()
    doc["classroom_id"] = classroom_id
    if "timestamp" not in doc or doc["timestamp"] is None:
        doc["timestamp"] = datetime.utcnow()
    await attendance_col.insert_one(doc)
    return {"status": "success", "message": "Attendance log recorded"}

@router.post("/{classroom_id}/focus", status_code=status.HTTP_201_CREATED)
async def log_focus(classroom_id: str, log: FocusLogCreate):
    # Verify classroom exists
    classroom_col = get_collection("classrooms")
    classroom = await classroom_col.find_one({"_id": classroom_id})
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    focus_col = get_collection("focus_logs")
    doc = log.dict()
    doc["classroom_id"] = classroom_id
    if "timestamp" not in doc or doc["timestamp"] is None:
        doc["timestamp"] = datetime.utcnow()
    await focus_col.insert_one(doc)
    return {"status": "success", "message": "Focus log recorded"}
