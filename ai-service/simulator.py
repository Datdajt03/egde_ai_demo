import cv2
import numpy as np
import random
import time
from typing import Dict, Any, List, Tuple

class ClassroomSimulator:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        
        # Grid of desks (row, col)
        # Back row: y=180, Middle row: y=280, Front row: y=380
        self.students = [
            # Row 1 (Back)
            {"id": 1, "base_x": 120, "base_y": 160, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 2, "base_x": 240, "base_y": 160, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 3, "base_x": 360, "base_y": 160, "state": "Neutral", "offset_x": 0, "offset_y": 0},
            {"id": 4, "base_x": 480, "base_y": 160, "state": "Distracted", "offset_x": 0, "offset_y": 0},
            
            # Row 2 (Middle)
            {"id": 5, "base_x": 150, "base_y": 260, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 6, "base_x": 270, "base_y": 260, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 7, "base_x": 390, "base_y": 260, "state": "Neutral", "offset_x": 0, "offset_y": 0},
            {"id": 8, "base_x": 510, "base_y": 260, "state": "Focused", "offset_x": 0, "offset_y": 0},
            
            # Row 3 (Front)
            {"id": 9, "base_x": 180, "base_y": 360, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 10, "base_x": 320, "base_y": 360, "state": "Focused", "offset_x": 0, "offset_y": 0},
            {"id": 11, "base_x": 460, "base_y": 360, "state": "Distracted", "offset_x": 0, "offset_y": 0},
        ]
        self.last_state_change = time.time()
        self.pulse_val = 0
        self.pulse_dir = 1

    def update_states(self):
        """
        Periodically change student focus states and add micro-movements to simulate breathing/fidgeting.
        """
        now = time.time()
        # Change state of 1-2 students every 4 seconds
        if now - self.last_state_change > 4.0:
            num_changes = random.randint(1, 2)
            for _ in range(num_changes):
                student = random.choice(self.students)
                student["state"] = random.choice(["Focused", "Neutral", "Distracted"])
            self.last_state_change = now
            
        # Minor position fluctuations
        for student in self.students:
            student["offset_x"] += random.uniform(-0.5, 0.5)
            student["offset_y"] += random.uniform(-0.5, 0.5)
            # Bound offsets
            student["offset_x"] = np.clip(student["offset_x"], -5, 5)
            student["offset_y"] = np.clip(student["offset_y"], -5, 5)
            
        # Record indicator pulsing
        self.pulse_val += self.pulse_dir * 10
        if self.pulse_val >= 255:
            self.pulse_val = 255
            self.pulse_dir = -1
        elif self.pulse_val <= 50:
            self.pulse_val = 50
            self.pulse_dir = 1

    def get_analytics(self) -> Dict[str, int]:
        """
        Get the numeric count of total, focused, neutral, and distracted students.
        """
        focused = sum(1 for s in self.students if s["state"] == "Focused")
        neutral = sum(1 for s in self.students if s["state"] == "Neutral")
        distracted = sum(1 for s in self.students if s["state"] == "Distracted")
        
        return {
            "total": len(self.students),
            "focused": focused,
            "neutral": neutral,
            "distracted": distracted
        }

    def generate_frame(self) -> np.ndarray:
        """
        Generates an RGB frame representing the classroom with moving students,
        YOLO bounding boxes, and statistics overlay.
        """
        self.update_states()
        
        # 1. Create classroom background (nice elegant slate-gray blueprint look)
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Gradient background
        for y in range(self.height):
            # Dark tech slate color gradient
            color_val = int(25 + (y / self.height) * 25)
            frame[y, :] = [color_val, 20, 15] # BGR
            
        # Draw some gridlines to simulate floor tiles/depth
        for i in range(0, self.width, 40):
            cv2.line(frame, (i, 100), (int((i - 320) * 1.5 + 320), self.height), (40, 35, 30), 1)
        for y_line in range(120, self.height, 50):
            cv2.line(frame, (0, y_line), (self.width, y_line), (40, 35, 30), 1)
            
        # Draw "Teacher Podium / Blackboard" at the top
        cv2.rectangle(frame, (80, 10), (560, 45), (15, 10, 8), -1)
        cv2.rectangle(frame, (80, 10), (560, 45), (50, 45, 40), 2)
        cv2.putText(frame, "BOARD / SLIDES SCREEN", (220, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 110, 100), 2)

        # 2. Draw Students and their YOLO Detections
        # Sort students from back to front (by base_y) to render layers correctly
        sorted_students = sorted(self.students, key=lambda s: s["base_y"])
        
        for student in sorted_students:
            x = int(student["base_x"] + student["offset_x"])
            y = int(student["base_y"] + student["offset_y"])
            state = student["state"]
            
            # Determine color and bounding box coordinates
            # Bounding box sizing expands slightly for foreground rows (depth simulation)
            scale = 0.8 + (y / self.height) * 0.4 # 0.8 to 1.2
            box_w = int(65 * scale)
            box_h = int(95 * scale)
            
            x1, y1 = x - box_w // 2, y - box_h // 2
            x2, y2 = x + box_w // 2, y + box_h // 2
            
            # State color coding (BGR)
            if state == "Focused":
                color = (46, 204, 113)    # Green
                indicator_text = "FOCUSED"
            elif state == "Neutral":
                color = (52, 152, 219)   # Blue/Yellowish-orange
                color = (241, 196, 15)   # Yellow
                indicator_text = "NEUTRAL"
            else:
                color = (231, 76, 60)    # Red
                indicator_text = "DISTRACTED"
                
            # Draw shoulder (ellipse)
            cv2.ellipse(frame, (x, y + int(25 * scale)), (int(25 * scale), int(15 * scale)), 0, 0, 360, (70, 60, 50), -1)
            # Draw head (circle)
            cv2.circle(frame, (x, y - int(10 * scale)), int(16 * scale), (210, 180, 160), -1)
            
            # Draw hair/caps/accessories based on ID to make them look distinct
            if student["id"] % 3 == 0: # Cap
                cv2.rectangle(frame, (x - int(12 * scale), y - int(24 * scale)), (x + int(12 * scale), y - int(14 * scale)), (220, 50, 50), -1)
            elif student["id"] % 3 == 1: # Hair
                cv2.circle(frame, (x, y - int(14 * scale)), int(16 * scale), (30, 20, 10), -1)
                
            # Draw face indicators: eyes/gaze orientation depending on focus level
            eye_y = y - int(11 * scale)
            eye_color = (20, 20, 20)
            
            if state == "Focused":
                # Eyes looking straight ahead
                cv2.circle(frame, (x - int(6 * scale), eye_y), 2, eye_color, -1)
                cv2.circle(frame, (x + int(6 * scale), eye_y), 2, eye_color, -1)
                # Smily face
                cv2.ellipse(frame, (x, y - int(2 * scale)), (int(4 * scale), int(3 * scale)), 0, 0, 180, eye_color, 1)
            elif state == "Neutral":
                # Eyes looking slightly sideways
                cv2.circle(frame, (x - int(8 * scale), eye_y), 2, eye_color, -1)
                cv2.circle(frame, (x + int(4 * scale), eye_y), 2, eye_color, -1)
                # Flat mouth
                cv2.line(frame, (x - int(3 * scale), y - int(2 * scale)), (x + int(3 * scale), y - int(2 * scale)), eye_color, 1)
            else:
                # Eyes closed / looking down or completely turned away
                cv2.line(frame, (x - int(8 * scale), eye_y), (x - int(4 * scale), eye_y), eye_color, 2)
                cv2.line(frame, (x + int(4 * scale), eye_y), (x + int(8 * scale), eye_y), eye_color, 2)
                # Sad mouth
                cv2.ellipse(frame, (x, y + int(2 * scale)), (int(4 * scale), int(3 * scale)), 0, 180, 360, eye_color, 1)

            # Draw Simulated YOLO Bounding Box around student
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label background
            label = f"person {0.85 + (student['id']%10)/100:.2f} [{indicator_text}]"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(frame, (x1, y1 - label_h - 6), (x1 + label_w + 6), color, -1)
            cv2.putText(frame, label, (x1 + 3, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 20, 20), 1)

        # 3. Draw HUD Overlays (Professional aesthetic)
        # Pulse Recording Dot (Live)
        cv2.circle(frame, (25, 25), 8, (0, 0, self.pulse_val), -1)
        cv2.putText(frame, "LIVE EDGE CAMERA (SIMULATOR)", (45, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 2)
        
        # Details overlay box at the bottom
        overlay = frame.copy()
        cv2.rectangle(overlay, (15, self.height - 50), (self.width - 15, self.height - 15), (20, 15, 10), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Telemetry Text
        stats = self.get_analytics()
        hud_text = f"STUDENTS: {stats['total']}  |  FOCUSED: {stats['focused']}  |  NEUTRAL: {stats['neutral']}  |  DISTRACTED: {stats['distracted']}"
        cv2.putText(frame, hud_text, (35, self.height - 27), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        
        # Model description
        cv2.putText(frame, "YOLOv8n-Classroom", (self.width - 165, self.height - 27), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)

        return frame
