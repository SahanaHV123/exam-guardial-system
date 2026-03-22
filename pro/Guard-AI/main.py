import threading
import queue
import cv2  # type: ignore
import mediapipe as mp  # type: ignore
import numpy as np  # type: ignore
import sounddevice as sd  # type: ignore
import psutil  # type: ignore
import os
import time
import subprocess
from datetime import datetime, timedelta
import logging
import sys
from fpdf import FPDF  # type: ignore
import uuid
import signal
import random
import config as cfg  # type: ignore

# Generate unique session ID
SESSION_ID = str(uuid.uuid4())[:8]

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/guard_ai_logs.txt",
    level=logging.INFO,
    format=f"[{SESSION_ID}] %(asctime)s - %(message)s",
    encoding="utf-8"
)

# Paths
log_file_path = "website_usage_logs.txt"
session_report_path = "logs/session_report.txt"

# Lip Detection Constants (from config)
UPPER_LIP = [13, 14]
LOWER_LIP = [17, 18]
LIP_MOVEMENT_THRESHOLD = cfg.LIP_MOVEMENT_THRESHOLD
SPEAKING_AUDIO_THRESHOLD = cfg.SPEAKING_AUDIO_THRESHOLD
BACKGROUND_NOISE_THRESHOLD = cfg.BACKGROUND_NOISE_THRESHOLD
AUDIO_DURATION = cfg.AUDIO_DURATION
FS = cfg.AUDIO_SAMPLE_RATE
MINIMUM_SPEAKING_DURATION = cfg.MINIMUM_SPEAKING_DURATION

# Gaze Tracking Constants (from config)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LOOK_AWAY_DURATION = cfg.LOOK_AWAY_DURATION
MINIMUM_LOOK_AWAY_DURATION = cfg.MINIMUM_LOOK_AWAY_DURATION

# Global Variables
audio_detected = False
background_noise_detected = False
frame_queue = queue.Queue()
multiple_persons_detected = False
session_start_time = datetime.now()
is_running = True


def signal_handler(sig, frame):
    global is_running
    print(f"\n[Signal Handler] Received signal {sig}. Stopping Guard AI...")
    logging.info(f"Received signal {sig}. Initiating graceful shutdown.")
    is_running = False


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Clear session report at startup for fresh session


def clear_session_report():
    if os.path.exists(session_report_path):
        with open(session_report_path, 'w', encoding="utf-8") as f:
            f.write(f"# Guard AI Session Report - {SESSION_ID}\n")
            f.write(f"# Session Started: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        logging.info("Session report cleared for new session")
    else:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(session_report_path), exist_ok=True)
        with open(session_report_path, 'w', encoding="utf-8") as f:
            f.write(f"# Guard AI Session Report - {SESSION_ID}\n")
            f.write(f"# Session Started: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")


clear_session_report()

# Helper Functions


def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"[{SESSION_ID}] [{timestamp}] {message}\n")
    logging.info(message)


def log_session_event(event_type, start_time, details):
    with open(session_report_path, "a", encoding="utf-8") as f:
        f.write(f"{event_type} | {start_time} | {details}\n")

def send_violation(message, penalty):
    try:
        import urllib.request
        import json
        
        current_module = sys.modules[__name__]
        student_name = getattr(current_module, 'current_student_name', 'Unknown Student')
        reg_no = getattr(current_module, 'current_reg_no', 'UnknownReg')

        url = "http://127.0.0.1:5000/api/log_violation"
        payload = {
            "message": message,
            "penalty": penalty,
            "studentName": student_name,
            "regNo": reg_no
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=1)
    except Exception as e:
        print(f"Failed to push API violation: {e}")


def is_safari_open():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Safari' in proc.info['name']:
            return True
    return False


def get_safari_tabs():
    script = '''
    tell application "Safari"
        set windowList to windows
        set tabList to {}
        repeat with aWindow in windowList
            set tabList to tabList & (get name of tabs of aWindow)
        end repeat
        return tabList
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split(", ")
        else:
            return []
    except Exception as e:
        print(f"Error running AppleScript: {e}")
        log_event(f"Error running AppleScript: {e}")
        return []


def create_pdf_report(
    txt_path, 
    pdf_path, 
    trust_score=100, 
    app_violations=None, 
    student_name="Unknown Student", 
    reg_no="UnknownReg"
):
    """Generate a professional PDF report from session data"""
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', size=20)
    pdf.set_text_color(0, 51, 102)  # Dark blue
    pdf.cell(0, 15, "Guard AI - Proctoring Report", ln=True, align='C')
    pdf.ln(3)

    # Session Info Box
    pdf.set_fill_color(240, 240, 240)  # Light gray background
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Student & Session Information", ln=True, fill=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(0, 6, f"Student Name: {student_name}", ln=True)
    pdf.cell(0, 6, f"Registration No: {reg_no}", ln=True)
    pdf.cell(0, 6, f"Session ID: {SESSION_ID}", ln=True)
    pdf.cell(0, 6, f"Session Start: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 6, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(8)

    speaking_events = []
    looking_events = []
    multiple_person_events = []

    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Parse different log formats
                if line.startswith("Speaking"):
                    parts = line.split("|")
                    if len(parts) >= 3:
                        start = parts[1].strip()
                        end = parts[2].strip()
                        speaking_events.append({"start": start, "end": end})

                elif line.startswith("Looking Away"):
                    parts = line.split("|")
                    if len(parts) >= 3:
                        start = parts[1].strip()
                        end = parts[2].strip()
                        looking_events.append({"start": start, "end": end})

                elif line.startswith("Multiple Persons"):
                    parts = line.split("|")
                    if len(parts) >= 2:
                        time_part = parts[1].strip()
                        details = parts[2].strip() if len(parts) > 2 else "N/A"
                        multiple_person_events.append({"time": time_part, "details": details})

        # Highlight Trust Score
        pdf.set_font("Arial", 'B', size=16)
        color = (16, 185, 129) if trust_score > 70 else ((245, 158, 11) if trust_score > 40 else (239, 68, 68))
        pdf.set_text_color(*color)
        pdf.cell(0, 10, f"Final Trust Score: {trust_score}/100", ln=True, align='C')
        pdf.ln(5)

        # Real-Time Violation Log
        if app_violations:
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, "Real-Time Violation Log", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", 'B', size=9)
            pdf.cell(40, 6, "Time", border=1, align='C')
            pdf.cell(120, 6, "Violation", border=1, align='C')
            pdf.cell(30, 6, "Penalty", border=1, align='C', ln=True)
            pdf.set_font("Arial", size=8)
            for v in app_violations:
                pdf.cell(40, 6, str(v.get("timestamp", ""))[:20], border=1)
                pdf.cell(120, 6, str(v.get("message", ""))[:70], border=1)
                pdf.cell(30, 6, f'-{v.get("penalty", 0)} pts', border=1, align='C', ln=True)
            pdf.ln(8)


        # Footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', size=8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, "This report was automatically generated by Guard AI Proctoring System", ln=True, align='C')
        pdf.cell(0, 5, "For questions or concerns, please contact your exam administrator", ln=True, align='C')

        pdf.output(pdf_path)
        print(f"✅ Final report saved to {pdf_path}")
        logging.info(f"PDF report generated successfully: {pdf_path}")

    except Exception as e:
        print(f"❌ PDF creation error: {e}")
        logging.error(f"PDF generation failed: {e}")

# Lip Detection


def get_lip_distance(landmarks, upper_lip_idx, lower_lip_idx, frame_w, frame_h):
    upper_lip_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in upper_lip_idx])
    lower_lip_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in lower_lip_idx])
    return np.linalg.norm(np.mean(upper_lip_points, axis=0) - np.mean(lower_lip_points, axis=0))


def audio_listener():
    global audio_detected, background_noise_detected
    print("[Audio Listener] Started")
    logging.info("Audio listener thread started")

    try:
        devices = sd.query_devices()
        print(f"[Audio] Available devices: {len(devices)}")
        default_input = sd.query_devices(kind='input')
        if default_input:
            print(f"[Audio] Default input device: {default_input['name']}")
    except Exception as e:
        print(f"⚠️ Warning: Could not query audio devices: {e}")
        logging.warning(f"Audio device query failed: {e}")

    while is_running:
        try:
            # Record a small chunk of audio
            audio_data = sd.rec(int(AUDIO_DURATION * FS), samplerate=FS, channels=1, dtype='float64')
            sd.wait()
            volume_norm = np.linalg.norm(audio_data) * 10
            audio_detected = volume_norm > SPEAKING_AUDIO_THRESHOLD
            background_noise_detected = volume_norm > BACKGROUND_NOISE_THRESHOLD
        except Exception as e:
            if is_running:
                print(f"❌ Audio Error: {e}")
                logging.error(f"Audio error: {e}")
            time.sleep(0.5)

# Gaze Tracking


def get_iris_position(landmarks, eye_landmarks, iris_landmarks, frame):
    h, w, _ = frame.shape
    eye_points = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_landmarks])
    x_min, y_min = np.min(eye_points, axis=0)
    x_max, y_max = np.max(eye_points, axis=0)

    eye_region = frame[y_min:y_max, x_min:x_max]
    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
    _, threshold_eye = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour = max(contours, key=cv2.contourArea)
        (x, y, w_eye, h_eye) = cv2.boundingRect(contour)
        cx = x + w_eye // 2
        cy = y + h_eye // 2
        if cx < eye_region.shape[1] // 3:
            return "Looking Left"
        elif cx > 2 * eye_region.shape[1] // 3:
            return "Looking Right"
        elif cy < eye_region.shape[0] // 3:
            return "Looking Up"
        elif cy > 2 * eye_region.shape[0] // 3:
            return "Looking Down"
        else:
            return "Looking Center"
    return "Looking Center"

# Combined Detection


def run_combined_detection():
    global multiple_persons_detected
    print(f"[Combined Detection] Started - Session ID: {SESSION_ID}")
    logging.info("Starting Guard AI monitoring session")

    iris_tracking_enabled = False

    try:
        # Try initializing with refine_landmarks=True for Iris Tracking
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        iris_tracking_enabled = True
        print("✅ Face Mesh initialized successfully (Iris Tracking Enabled)")
        logging.info("Face Mesh initialized with Iris Tracking")
    except Exception as e:
        print(f"⚠️ Warning: High-precision tracking failed: {e}")
        logging.warning(f"Iris tracking initialization failed: {e}")

        try:
            # Fallback to standard tracking (No Iris)
            face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=2,
                refine_landmarks=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            iris_tracking_enabled = False
            print("✅ Face Mesh initialized in Standard Mode (No Iris Tracking)")
            logging.info("Face Mesh initialized in Standard Mode")
        except Exception as e2:
            print(f"❌ Error initializing face detection: {e2}")
            logging.error(f"Face detection initialization failed: {e2}")
            return

    threading.Thread(target=audio_listener, daemon=True).start()

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("❌ Error: Cannot access camera. Please check permissions.")
            logging.error("Camera access denied or unavailable")
            return
    except Exception as e:
        print(f"❌ Error opening camera: {e}")
        logging.error(f"Camera error: {e}")
        return

    previous_distance = 0
    look_away_start = ""
    look_away_start_time = 0.0  # Track time.time() for duration calculation
    look_away_start_timestamp = ""  # Track actual start time for logging
    speaking_start = ""
    speaking_start_time = 0.0  # Track time.time() for duration calculation
    speaking_start_timestamp = ""  # Track actual start time for logging
    multiple_person_start = None

    while cap.isOpened() and is_running:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb_frame)

        status = "Not Speaking"
        direction = "No face detected"
        warning = ""
        num_faces = 0

        if result.multi_face_landmarks:
            num_faces = len(result.multi_face_landmarks)

            # Check for multiple persons
            if num_faces > 1:
                multiple_persons_detected = True
                current_time = datetime.now().strftime("%H:%M:%S")
                if multiple_person_start is None:
                    multiple_person_start = current_time
                    log_session_event("Multiple Persons", current_time, f"{num_faces} faces detected")
                    logging.warning(f"Multiple persons detected: {num_faces} faces")
                    send_violation(f"AI: Multiple Persons Detected ({num_faces} faces)", 15)
                warning = f"⚠️ WARNING: {num_faces} persons detected!"
            else:
                if multiple_person_start is not None:
                    multiple_person_start = None
                multiple_persons_detected = False

        if result.multi_face_landmarks:
            for landmarks in result.multi_face_landmarks:
                distance = get_lip_distance(landmarks.landmark, UPPER_LIP, LOWER_LIP, w, h)
                lip_diff = abs(distance - previous_distance)
                lip_moving = lip_diff > LIP_MOVEMENT_THRESHOLD
                previous_distance = distance

                # Debug: Print status if any activity is detected
                if audio_detected or lip_moving:
                    print(
                        f"\r[DEBUG] Audio: {audio_detected} | Lip Move: {lip_moving} (Diff: {lip_diff:.2f})", end="", flush=True)
                current_time = datetime.now().strftime("%H:%M:%S")

                if lip_moving and audio_detected:
                    status = "Speaking"
                    if not speaking_start:
                        speaking_start = current_time
                        speaking_start_time = time.time()
                        speaking_start_timestamp = current_time
                else:
                    if speaking_start and speaking_start_time > 0.0:
                        # Only log if speaking duration >= MINIMUM_SPEAKING_DURATION
                        duration = time.time() - speaking_start_time  # type: ignore
                        if duration >= MINIMUM_SPEAKING_DURATION:
                            log_session_event("Speaking", speaking_start_timestamp, current_time)
                            logging.info(f"Speaking event logged: {duration:.1f}s")
                            send_violation(f"AI: Speaking Detected ({duration:.1f}s)", 10)
                        speaking_start = ""
                        speaking_start_time = 0.0
                        speaking_start_timestamp = ""

                # Gaze Tracking (Only if Iris Tracking is enabled)
                if iris_tracking_enabled:
                    try:
                        left_eye_direction = get_iris_position(landmarks.landmark, LEFT_EYE, LEFT_IRIS, frame)
                        right_eye_direction = get_iris_position(landmarks.landmark, RIGHT_EYE, RIGHT_IRIS, frame)
                        direction = left_eye_direction if left_eye_direction == right_eye_direction else "Looking Away"
                    except Exception:
                        direction = "Gaze Error"
                else:
                    direction = "Gaze Unavailable"

        if direction != "Looking Center":
            if not look_away_start:
                look_away_start = datetime.now().strftime("%H:%M:%S")
                look_away_start_time = time.time()  # Record start time for duration
                look_away_start_timestamp = look_away_start
            elif look_away_start_time > 0.0 and (time.time() - look_away_start_time) > LOOK_AWAY_DURATION:  # type: ignore
                warning = "⚠ Please focus on screen!"
        else:
            if look_away_start and look_away_start_time > 0.0:
                # Only log if looking away duration >= MINIMUM_LOOK_AWAY_DURATION
                duration = time.time() - look_away_start_time  # type: ignore
                if duration >= MINIMUM_LOOK_AWAY_DURATION:
                    end_time_away = datetime.now().strftime("%H:%M:%S")
                    log_session_event("Looking Away", look_away_start_timestamp, end_time_away)
                    logging.info(f"Looking away event logged: {duration:.1f}s")
                    send_violation(f"AI: Looking Away Detected ({duration:.1f}s)", 5)
            look_away_start = ""
            look_away_start_time = 0.0
            look_away_start_timestamp = ""

        # Display warnings
        cv2.putText(frame, f"Lip Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Gaze Direction: {direction}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"Faces Detected: {num_faces}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if warning:
            cv2.putText(frame, warning, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if not frame_queue.full():
            frame_queue.put(frame)

    cap.release()

# Website Monitor (Disabled for Windows Support/Request)

def run_website_monitor():
    pass

# Demo Mode Event Generator


def run_demo_mode():
    if not cfg.DEMO_MODE:
        return
    print("[Demo Mode] Started")
    while is_running:
        time.sleep(random.randint(10, 20))
        if not is_running:
            break

        event_type = random.choice(["Speaking", "Looking Away", "Multiple Persons"])
        current_time = datetime.now().strftime("%H:%M:%S")

        if event_type == "Speaking":
            end_time = (datetime.now() + timedelta(seconds=random.randint(2, 5))).strftime("%H:%M:%S")
            log_session_event("Speaking", current_time, end_time)
            logging.info(f"[DEMO] Generated Speaking event at {current_time}")
            send_violation("AI: Speaking Detected (Simulated)", 10)
        elif event_type == "Looking Away":
            end_time = (datetime.now() + timedelta(seconds=random.randint(3, 7))).strftime("%H:%M:%S")
            log_session_event("Looking Away", current_time, end_time)
            logging.info(f"[DEMO] Generated Looking Away event at {current_time}")
            send_violation("AI: Looking Away Detected (Simulated)", 5)
        elif event_type == "Multiple Persons":
            log_session_event("Multiple Persons", current_time, "2 faces detected (Simulated)")
            logging.info(f"[DEMO] Generated Multiple Persons event at {current_time}")
            send_violation("AI: Multiple Persons Detected (Simulated)", 15)

# Main


def start_detection_process(headless=False):
    global is_running
    is_running = True

    combined_thread = threading.Thread(target=run_combined_detection, daemon=True)
    demo_thread = threading.Thread(target=run_demo_mode, daemon=True)

    combined_thread.start()
    if cfg.DEMO_MODE:
        demo_thread.start()

    print("All features are running. Press Ctrl+C to stop.")
    
    if headless:
        return  # Return immediately let the threads run in background

    try:
        while is_running:
            if not frame_queue.empty():
                frame = frame_queue.get()
                cv2.imshow("Guard-AI", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    is_running = False
                    break
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting Guard-AI...")
    finally:
        print("\nSaving Final Report...")
        session_pdf_path = "logs/final_report.pdf"
        create_pdf_report(session_report_path, session_pdf_path)
        print(f"Report saved as: {session_pdf_path}")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    start_detection_process()
