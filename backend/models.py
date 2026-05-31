from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class ClassroomBase(BaseModel):
    name: str
    capacity: int
    subject: str
    instructor: str

class ClassroomCreate(ClassroomBase):
    id: str = Field(..., description="Unique identifier for the classroom, e.g. room_101")

class Classroom(ClassroomBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "room_101",
                "name": "Smart Classroom 101",
                "capacity": 30,
                "subject": "Advanced Artificial Intelligence",
                "instructor": "Dr. Sarah Jenkins"
            }
        }

class AttendanceLogCreate(BaseModel):
    classroom_id: str
    present_count: int
    attendance_rate: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AttendanceLog(AttendanceLogCreate):
    id: Optional[str] = Field(None, alias="_id")

class FocusLogCreate(BaseModel):
    classroom_id: str
    focused_count: int
    neutral_count: int
    distracted_count: int
    focus_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FocusLog(FocusLogCreate):
    id: Optional[str] = Field(None, alias="_id")

class AnalyticsSummary(BaseModel):
    classroom_id: str
    session_date: str
    average_attendance: float
    average_focus_score: float
    peak_students: int
    total_samples: int

class AIReportCreate(BaseModel):
    classroom_id: str
    report_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class AIReport(AIReportCreate):
    id: Optional[str] = Field(None, alias="_id")
