from fastapi import APIRouter, HTTPException
from db import get_collection
from config import settings
from datetime import datetime
import pymongo
import google.generativeai as genai
import logging

logger = logging.getLogger("backend")
router = APIRouter(prefix="/reports", tags=["AI Reports"])

# Configure Gemini
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
else:
    logger.warning("GEMINI_API_KEY not found in environment. Fallback simulated reports will be used.")

def get_fallback_report(classroom_name: str, subject: str, instructor: str, avg_attendance: float, avg_focus: float, peak_students: int) -> str:
    """
    Generates a high-quality mock classroom report when Gemini API key is not present.
    """
    return f"""# 📊 Báo Cáo Phân Tích Lớp Học Thông Minh
*Hệ thống phân tích Edge AI kết hợp Gemini API*

---

## 🏫 Thông Tin Lớp Học
* **Lớp học:** {classroom_name}
* **Môn học:** {subject}
* **Giảng viên:** {instructor}
* **Thời gian báo cáo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---

## 📈 Đánh Giá Tình Hình Hiện Diện (Attendance Assessment)
* **Tỷ lệ hiện diện trung bình:** **{avg_attendance:.1f}%**
* **Số lượng sinh viên cao nhất ghi nhận:** **{peak_students} sinh viên**

### 🔍 Nhận xét:
* Lớp học duy trì được sự chuyên cần tương đối ổn định. Tỷ lệ hiện diện đạt **{avg_attendance:.1f}%** cho thấy đa số sinh viên có trách nhiệm tham gia học tập.
* Có sự biến động nhẹ về số lượng ở đầu buổi học (thường do đi trễ 5-10 phút). Số lượng đạt đỉnh **{peak_students}** cho thấy lớp học hoạt động tối đa công suất ở giữa buổi học.

---

## 🧠 Phân Tích Mức Độ Tập Trung (Focus & Engagement Analytics)
* **Chỉ số tập trung trung bình (Focus Score):** **{avg_focus:.1f}/100**
* **Phân bố trạng thái:**
  * 🟢 **Tập trung (Focused):** {min(100.0, avg_focus + 5.0):.1f}%
  * 🟡 **Bình thường (Neutral):** {max(0.0, 100.0 - (avg_focus + 5.0) - (15.0 - avg_focus/10)):.1f}%
  * 🔴 **Phân tâm/Mất tập trung (Distracted):** {max(0.0, 15.0 - avg_focus/10):.1f}%

### 🔍 Nhận xét:
* Chỉ số tập trung ở mức **{avg_focus:.1f}/100** phản ánh chất lượng tiếp thu kiến thức tốt. Đa số sinh viên có thái độ học tập tích cực, duy trì ánh nhìn hướng lên bảng hoặc làm bài tập.
* Giai đoạn mất tập trung (Distracted) thường tăng nhẹ vào khoảng **30-40 phút** sau khi bắt đầu bài học. Đây là chu kỳ sinh học bình thường khi não bộ bắt đầu mỏi mệt.

---

## 💡 Khuyến Nghị Sư Phạm Cho Giảng Viên (Pedagogical Recommendations)
1. **Tối ưu hóa chu kỳ tập trung**: Sau mỗi 35 phút giảng lý thuyết, nên xen kẽ các hoạt động thảo luận ngắn (3-5 phút) hoặc mini-quiz để kéo sự chú ý của sinh viên quay lại.
2. **Khuyến khích sinh viên đi trễ**: Xem xét áp dụng phương pháp điểm danh nhanh qua mã QR đầu giờ để giảm thiểu việc sinh viên vào trễ làm gián đoạn bài giảng.
3. **Cải tiến bài giảng trực quan**: Sử dụng nhiều hình ảnh, sơ đồ tư duy hoặc video minh họa để giảm thiểu trạng thái "Neutral" và chuyển dịch sang "Focused".
"""

@router.post("/{classroom_id}/generate")
async def generate_ai_report(classroom_id: str):
    classroom_col = get_collection("classrooms")
    attendance_col = get_collection("attendance_logs")
    focus_col = get_collection("focus_logs")
    reports_col = get_collection("ai_reports")
    
    # 1. Fetch classroom metadata
    classroom = await classroom_col.find_one({"_id": classroom_id})
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
        
    # 2. Fetch history statistics
    att_cursor = attendance_col.find({"classroom_id": classroom_id})
    att_rates = []
    present_counts = []
    async for doc in att_cursor:
        att_rates.append(doc.get("attendance_rate", 0))
        present_counts.append(doc.get("present_count", 0))
        
    foc_cursor = focus_col.find({"classroom_id": classroom_id})
    focus_scores = []
    focused_counts = []
    neutral_counts = []
    distracted_counts = []
    async for doc in foc_cursor:
        focus_scores.append(doc.get("focus_score", 0))
        focused_counts.append(doc.get("focused_count", 0))
        neutral_counts.append(doc.get("neutral_count", 0))
        distracted_counts.append(doc.get("distracted_count", 0))
        
    # Aggregate values
    avg_attendance = sum(att_rates) / len(att_rates) if att_rates else 0.0
    avg_present = sum(present_counts) / len(present_counts) if present_counts else 0.0
    avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 0.0
    peak_students = max(present_counts) if present_counts else 0
    
    total_focused = sum(focused_counts)
    total_neutral = sum(neutral_counts)
    total_distracted = sum(distracted_counts)
    total_sum = total_focused + total_neutral + total_distracted
    
    avg_focused_p = (total_focused / total_sum * 100) if total_sum > 0 else 0.0
    avg_neutral_p = (total_neutral / total_sum * 100) if total_sum > 0 else 0.0
    avg_distracted_p = (total_distracted / total_sum * 100) if total_sum > 0 else 0.0

    classroom_name = classroom.get("name", "Lớp học thông minh")
    subject = classroom.get("subject", "Chưa rõ")
    instructor = classroom.get("instructor", "Chưa rõ")
    capacity = classroom.get("capacity", 30)

    # 3. Call Gemini API or Fallback
    report_content = ""
    generated_by = "Fallback Simulated AI"
    
    if settings.GEMINI_API_KEY:
        try:
            logger.info("Generating report with Gemini model 'gemini-1.5-flash'...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Bạn là một chuyên gia phân tích sư phạm AI cao cấp. Hãy dựa trên dữ liệu thống kê từ camera Edge AI sau đây để viết một Báo cáo Phân tích Lớp học Thông minh thật chuyên nghiệp bằng tiếng Việt.
            
            DỮ LIỆU LỚP HỌC:
            - Phòng học: {classroom_name}
            - Môn học: {subject}
            - Giảng viên: {instructor}
            - Sức chứa tối đa: {capacity} sinh viên
            
            CHỈ SỐ THỐNG KÊ TRONG BUỔI HỌC:
            - Tỷ lệ hiện diện trung bình: {avg_attendance:.2f}% (Trung bình khoảng {avg_present:.1f} sinh viên có mặt)
            - Số lượng sinh viên nhiều nhất cùng lúc (Peak Students): {peak_students}
            - Điểm tập trung trung bình (Focus Score): {avg_focus:.2f}/100
            - Phân bố trạng thái tập trung của sinh viên:
              + Tập trung (Focused): {avg_focused_p:.1f}%
              + Bình thường (Neutral): {avg_neutral_p:.1f}%
              + Phân tâm (Distracted): {avg_distracted_p:.1f}%
            
            YÊU CẦU BÁO CÁO:
            1. Viết bằng tiếng Việt, sử dụng định dạng Markdown phong phú (sử dụng tiêu đề, danh sách, in đậm, bảng biểu hoặc trích dẫn).
            2. Báo cáo phải bao gồm:
               - **Đánh giá Chuyên cần (Attendance Assessment)**: Phân tích tỷ lệ đi học, đánh giá hiệu suất khai thác phòng học, chỉ ra biến động số lượng.
               - **Phân tích Trạng thái Học tập (Engagement & Focus Analysis)**: Giải thích ý nghĩa của các chỉ số tập trung, bình thường, mất tập trung.
               - **Đề xuất Sư phạm (Pedagogical Recommendations)**: Đưa ra 3-4 lời khuyên thiết thực, mang tính xây dựng cao để giảng viên cải thiện phương pháp dạy và tương tác dựa trên dữ liệu.
            
            Hãy tạo một phản hồi chất lượng cao, súc tích nhưng đầy đủ ý nghĩa và cực kỳ chuyên nghiệp.
            """
            
            response = model.generate_content(prompt)
            report_content = response.text
            generated_by = "Gemini API (gemini-1.5-flash)"
            logger.info("Gemini report generated successfully.")
        except Exception as e:
            logger.error(f"Error generating Gemini report, falling back to mock: {e}")
            report_content = get_fallback_report(classroom_name, subject, instructor, avg_attendance, avg_focus, peak_students)
    else:
        report_content = get_fallback_report(classroom_name, subject, instructor, avg_attendance, avg_focus, peak_students)

    # 4. Save report to database
    report_doc = {
        "classroom_id": classroom_id,
        "report_content": report_content,
        "generated_at": datetime.utcnow(),
        "metadata": {
            "avg_attendance": round(avg_attendance, 2),
            "avg_present": round(avg_present, 1),
            "avg_focus": round(avg_focus, 2),
            "peak_students": peak_students,
            "avg_focused_p": round(avg_focused_p, 1),
            "avg_neutral_p": round(avg_neutral_p, 1),
            "avg_distracted_p": round(avg_distracted_p, 1),
            "generated_by": generated_by
        }
    }
    
    # Save or update report for the classroom
    await reports_col.update_one(
        {"classroom_id": classroom_id},
        {"$set": report_doc},
        upsert=True
    )
    
    return {
        "status": "success",
        "generated_by": generated_by,
        "report": {
            "classroom_id": classroom_id,
            "report_content": report_content,
            "generated_at": report_doc["generated_at"].isoformat(),
            "metadata": report_doc["metadata"]
        }
    }

@router.get("/{classroom_id}")
async def get_latest_report(classroom_id: str):
    """
    Retrieves the latest generated AI report for a classroom.
    """
    reports_col = get_collection("ai_reports")
    report = await reports_col.find_one({"classroom_id": classroom_id})
    if not report:
        raise HTTPException(status_code=404, detail="No report found for this classroom yet.")
    
    report["_id"] = str(report["_id"])
    if isinstance(report.get("generated_at"), datetime):
        report["generated_at"] = report["generated_at"].isoformat()
        
    return report
