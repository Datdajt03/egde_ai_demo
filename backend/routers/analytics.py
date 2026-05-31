from fastapi import APIRouter, HTTPException
from db import get_collection
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pymongo

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/{classroom_id}/realtime")
async def get_realtime_analytics(classroom_id: str):
    """
    Returns the most recent telemetry logs (attendance and focus) for a classroom.
    """
    attendance_col = get_collection("attendance_logs")
    focus_col = get_collection("focus_logs")
    
    # Get latest logs
    latest_attendance = await attendance_col.find_one(
        {"classroom_id": classroom_id},
        sort=[("timestamp", pymongo.DESCENDING)]
    )
    
    latest_focus = await focus_col.find_one(
        {"classroom_id": classroom_id},
        sort=[("timestamp", pymongo.DESCENDING)]
    )
    
    if not latest_attendance or not latest_focus:
        # Return fallback mock realtime values if database is empty
        return {
            "classroom_id": classroom_id,
            "timestamp": datetime.utcnow().isoformat(),
            "present_count": 0,
            "attendance_rate": 0.0,
            "focused_count": 0,
            "neutral_count": 0,
            "distracted_count": 0,
            "focus_score": 0.0
        }
        
    return {
        "classroom_id": classroom_id,
        "timestamp": latest_attendance.get("timestamp"),
        "present_count": latest_attendance.get("present_count"),
        "attendance_rate": latest_attendance.get("attendance_rate"),
        "focused_count": latest_focus.get("focused_count"),
        "neutral_count": latest_focus.get("neutral_count"),
        "distracted_count": latest_focus.get("distracted_count"),
        "focus_score": latest_focus.get("focus_score")
    }

@router.get("/{classroom_id}/history")
async def get_historical_analytics(classroom_id: str, limit: int = 30):
    """
    Fetches synchronized historical records for charting.
    Retrieves the last N records of attendance and focus logs, aligning them by proximity of timestamp.
    """
    attendance_col = get_collection("attendance_logs")
    focus_col = get_collection("focus_logs")
    
    # Get attendance logs
    att_cursor = attendance_col.find({"classroom_id": classroom_id}).sort("timestamp", pymongo.DESCENDING).limit(limit)
    attendance_logs = []
    async for doc in att_cursor:
        doc["_id"] = str(doc["_id"])
        attendance_logs.append(doc)
        
    # Get focus logs
    foc_cursor = focus_col.find({"classroom_id": classroom_id}).sort("timestamp", pymongo.DESCENDING).limit(limit)
    focus_logs = []
    async for doc in foc_cursor:
        doc["_id"] = str(doc["_id"])
        focus_logs.append(doc)
        
    # Reverse so they are chronological
    attendance_logs.reverse()
    focus_logs.reverse()
    
    # Align logs by indices since they are logged together
    history = []
    max_len = min(len(attendance_logs), len(focus_logs))
    
    for i in range(max_len):
        att = attendance_logs[i]
        foc = focus_logs[i]
        
        # Simple isoformat converter
        ts = att["timestamp"]
        if isinstance(ts, datetime):
            ts = ts.strftime("%H:%M:%S")
            
        history.append({
            "timestamp": ts,
            "present_count": att.get("present_count"),
            "attendance_rate": att.get("attendance_rate"),
            "focused_count": foc.get("focused_count"),
            "neutral_count": foc.get("neutral_count"),
            "distracted_count": foc.get("distracted_count"),
            "focus_score": foc.get("focus_score")
        })
        
    return history

@router.get("/{classroom_id}/summary")
async def get_analytics_summary(classroom_id: str):
    """
    Returns aggregated session statistics.
    """
    attendance_col = get_collection("attendance_logs")
    focus_col = get_collection("focus_logs")
    classroom_col = get_collection("classrooms")
    
    classroom = await classroom_col.find_one({"_id": classroom_id})
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
        
    # Aggegrate attendance
    att_cursor = attendance_col.find({"classroom_id": classroom_id})
    att_rates = []
    present_counts = []
    async for doc in att_cursor:
        att_rates.append(doc.get("attendance_rate", 0))
        present_counts.append(doc.get("present_count", 0))
        
    # Aggregate focus
    foc_cursor = focus_col.find({"classroom_id": classroom_id})
    focus_scores = []
    async for doc in foc_cursor:
        focus_scores.append(doc.get("focus_score", 0))
        
    if not att_rates:
        return {
            "classroom_id": classroom_id,
            "average_attendance_rate": 0.0,
            "average_focus_score": 0.0,
            "peak_students": 0,
            "classroom_capacity": classroom.get("capacity", 30)
        }
        
    avg_att = sum(att_rates) / len(att_rates)
    avg_foc = sum(focus_scores) / len(focus_scores) if focus_scores else 0.0
    peak_std = max(present_counts) if present_counts else 0
    
    return {
        "classroom_id": classroom_id,
        "average_attendance_rate": round(avg_att, 2),
        "average_focus_score": round(avg_foc, 2),
        "peak_students": peak_std,
        "classroom_capacity": classroom.get("capacity", 30)
    }
