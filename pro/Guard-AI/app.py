from flask import Flask, render_template, request, jsonify, send_file, Response, redirect, session  # type: ignore
import subprocess
import os
import time
from datetime import datetime
import cv2  # type: ignore
import main
import PyPDF2  # type: ignore
import re
from fpdf import FPDF  # type: ignore

app = Flask(__name__, static_folder="Frontend", template_folder="Frontend", static_url_path="")
app.secret_key = "guard_ai_secret_key_123"
main.is_running = False  # Ensure it doesn't spin up on import
violations = []
from typing import Dict, Any, List

students_data: Dict[str, Any] = {} # Format: { "regNo": { "name": "...", "trust_score": 100, "violations": [] } }
exam_secret_code = "GUARD2026"
exam_questions = [
    {
        "id": "q1",
        "question": "Which of the following best describes the principle of least privilege in cybersecurity?",
        "options": {
            "A": "A user should only have the minimum privileges necessary to perform their job.",
            "B": "All users should be granted administrator access for convenience.",
            "C": "Privilege should be granted loosely and revoked strictly.",
            "D": "The system operates without any privilege checking."
        }
    },
    {
        "id": "q2",
        "question": "What is the primary purpose of a salt in password hashing?",
        "options": {
            "A": "To make the password taste better.",
            "B": "To encrypt the password reversibly.",
            "C": "To protect against precomputed dictionary (rainbow table) attacks.",
            "D": "To reduce the length of the hashed output."
        }
    }
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/features")
def features():
    return render_template("feature.html")


@app.route("/exam")
def exam():
    return render_template("exam.html")


@app.route("/admin")
def admin():
    if session.get("logged_in"):
        return redirect("/admin-dashboard")
    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("logged_in"):
        return redirect("/admin")
    return render_template("admin.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    # Default admin credentials
    if data.get("username") == "admin" and data.get("password") == "admin123":
        session["logged_in"] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid Username or Password"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("logged_in", None)
    return jsonify({"status": "success"})


@app.route("/api/log_violation", methods=["POST"])
def log_violation():
    data = request.json
    message = data.get("message", "Unknown Violation")
    penalty = data.get("penalty", 5)
    student_name = data.get("studentName", "Unknown Student")
    reg_no = data.get("regNo", "UnknownReg")

    # Initialize student if missing
    if reg_no not in students_data:
        students_data[reg_no] = {"name": student_name, "trust_score": 100, "violations": []}

    students_data[reg_no]["trust_score"] = max(0, students_data[reg_no]["trust_score"] - penalty)
    
    violation_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "penalty": penalty,
        "trust_score": students_data[reg_no]["trust_score"],
        "student_name": student_name,
        "reg_no": reg_no
    }
    
    violation_list: List[Any] = students_data[reg_no]["violations"]
    violation_list.append(violation_record)
    violations.append(violation_record) # keep global track for live feed
    
    return jsonify({"status": "success", "trust_score": students_data[reg_no]["trust_score"]})


@app.route("/api/get_violations", methods=["GET"])
def get_violations():
    # Admin dashboard fetch - returns all violations grouped by global timeline
    return jsonify({"violations": violations, "students": students_data})


@app.route("/api/reset", methods=["POST"])
def reset():
    global violations, students_data
    violations = []
    students_data = {}
    return jsonify({"status": "success"})


@app.route("/api/set_exam_config", methods=["POST"])
def set_exam_config():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"})
    
    global exam_secret_code, exam_questions
    data = request.json
    exam_secret_code = data.get("secret_code", exam_secret_code)
    exam_questions = data.get("questions", exam_questions)
    return jsonify({"status": "success", "message": "Exam configuration updated successfully"})


@app.route("/api/get_exam_config", methods=["GET"])
def get_exam_config():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"})
    
    return jsonify({
        "status": "success", 
        "secret_code": exam_secret_code, 
        "questions": exam_questions
    })


@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    entered_code = data.get("secret_code", "")
    student_name = data.get("studentName", "")
    reg_no = data.get("regNo", "")
    
    if entered_code == exam_secret_code:
        # Register student in the tracker on valid login
        if reg_no and reg_no not in students_data:
            students_data[reg_no] = {"name": student_name, "trust_score": 100, "violations": []}
            
        return jsonify({
            "status": "success", 
            "questions": exam_questions
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid Secret Code"
        })

@app.route("/api/download_template", methods=["GET"])
def download_template():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    text = '''1. Which of the following best describes the principle of least privilege in cybersecurity?
A. A user should only have the minimum privileges necessary to perform their job.
B. All users should be granted administrator access for convenience.
C. Privilege should be granted loosely and revoked strictly.
D. The system operates without any privilege checking.

2. What is the primary purpose of a salt in password hashing?
A. To make the password taste better.
B. To encrypt the password reversibly.
C. To protect against precomputed dictionary (rainbow table) attacks.
D. To reduce the length of the hashed output.
'''
    for p in text.split('\n\n'):
        pdf.multi_cell(0, 8, txt=p)
        pdf.ln()
    
    template_path = "Frontend/GuardAI_Exam_Template.pdf"
    pdf.output(template_path)
    return send_file(template_path, as_attachment=True)

@app.route("/api/upload_pdf_questions", methods=["POST"])
def upload_pdf_questions():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"})
    
    if "pdf_file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"})
        
    file = request.files["pdf_file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty file name"})
        
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        questions_parsed = []
        # Split text into potential question blocks using regex "1. " or "1) "
        q_blocks = re.split(r'\n(?=\d+[\.\)])', text.strip())
        
        for idx, block in enumerate(q_blocks):
            if not block.strip():
                continue
            
            # Find Question text & options
            # Looking for A. B. C. D. or A) B) C) D) on newlines
            opts = re.split(r'\n(?=[A-Da-d][\.\)])', block)
            if len(opts) < 2:
                # Try inline options without newlines if it failed
                opts = re.split(r'\s+(?=[A-Da-d][\.\)])', block)
            
            q_text = opts[0].strip()
            q_text = re.sub(r'^\d+[\.\)]\s*', '', q_text) # remove leading number
            
            options_dict = {}
            for o in opts[1:]:  # type: ignore
                o = o.strip()
                match = re.match(r'^([A-Da-d])[\.\)]\s*(.*)', o, re.DOTALL)
                if match:
                    options_dict[match.group(1).upper()] = match.group(2).strip()
            
            if options_dict:
                questions_parsed.append({
                    "id": f"q_pdf_{int(time.time())}_{idx}",
                    "question": q_text,
                    "options": options_dict
                })
        
        if not questions_parsed:
            return jsonify({"status": "error", "message": "Could not extract questions. Please ensure standard list format."})
            
        return jsonify({"status": "success", "questions": questions_parsed})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/start-guard-ai", methods=["POST"])
def start_guard_ai():
    try:
        data = request.get_json(silent=True) or {}
        student_name = data.get("studentName", "Unknown Student")
        reg_no = data.get("regNo", "UnknownReg")
        
        main.current_student_name = student_name
        main.current_reg_no = reg_no
        
        if not main.is_running:
            main.start_detection_process(headless=True)
            return jsonify({"status": "success", "message": "Guard AI started successfully!"})
        else:
            return jsonify({"status": "error", "message": "Guard AI is already running!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/stop-guard-ai", methods=["POST"])
def stop_guard_ai():
    try:
        if main.is_running:
            main.is_running = False
            time.sleep(1) # Wait for threads to cleanly wrap up loops
            
            # Fetch for current student logic
            student_name = getattr(main, 'current_student_name', 'Unknown Student')
            reg_no = getattr(main, 'current_reg_no', 'UnknownReg')
             
            # Use global trust score tracking if found
            trust = 100
            app_v = []
            if reg_no in students_data:
                trust = students_data[reg_no]["trust_score"]
                app_v = students_data[reg_no]["violations"]
                 
            session_pdf_path = f"logs/final_report_{reg_no}.pdf"
            main.create_pdf_report(main.session_report_path, session_pdf_path, trust_score=trust, app_violations=app_v, student_name=student_name, reg_no=reg_no)
            cv2.destroyAllWindows()
            return jsonify({"status": "success", "message": "Guard AI stopped successfully!", "reportPath": session_pdf_path})
        else:
            return jsonify({"status": "error", "message": "Guard AI is not running!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def generate_frames():
    while m_running_check():
        if not main.frame_queue.empty():
            frame = main.frame_queue.get()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.01)

def m_running_check():
    return main.is_running

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/download-report", methods=["GET"])
def download_report():
    reg_no = request.args.get('regNo', '')
    report_path = f"logs/final_report_{reg_no}.pdf" if reg_no else "logs/final_report.pdf"
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "Report not found!"})


@app.route("/stream-logs")
def stream_logs():
    def generate_logs():
        log_file = "logs/guard_ai_logs.txt"
        if not os.path.exists(log_file):
            yield "data: Waiting for logs...\n\n"
            return

        with open(log_file, "r") as f:
            # Seek to end of file
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    time.sleep(0.5)

    return Response(generate_logs(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
