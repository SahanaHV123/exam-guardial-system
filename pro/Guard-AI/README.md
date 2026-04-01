<p align="center">
  <h1 align="center">🛡️ Guard AI - Intelligent Proctoring 🛡️</h1>
  <p align="center">
    <strong>A powerful, real-time AI-powered exam monitoring system.</strong>
  </p>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/af00313d-d908-4364-9fd8-d66df4320906" alt="Guard AI Banner" width="800">
</p>

---

## 🌟 Overview

**Guard AI** is a state-of-the-art, lightweight proctoring solution designed for online examinations. It leverages computer vision and audio analysis to detect suspicious activities in real-time, ensuring exam integrity without heavy infrastructure.

## 🚀 Key Features

- 👄 **Lip Movement & Audio Analysis**: Detects speaking during exams and differentiates it from natural movements like yawning.
- 👀 **Gaze Tracking & Head Position**: Monitors eye and head movements to detect when a student looks away from the screen for extended periods.
- 👥 **Multiple Person Detection**: Detects and warns when more than one face appears in the camera frame.
- 🌐 **Web Dashboard**: Modern Flask-based interface for students to take exams and for admins to monitor violations.
- 📊 **Comprehensive PDF Reporting**: Automatically generates detailed behavior reports with trust scores after each session.
- ⚙️ **Configurable Thresholds**: Easily tune detection sensitivity via `config.py`.

---

## 🏗️ Project Structure

```text
Guard-AI/
├── Frontend/           # Web interface (HTML, CSS, JS)
├── logs/               # Session logs and generated PDF reports
├── app.py              # Flask Web Server (Main Entry Point)
├── main.py             # Core AI Detection Logic
├── config.py           # Thresholds and Configuration
├── requirements.txt    # Project Dependencies
└── tests/              # Backend and hardware test scripts
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- Webcam and Microphone access

### 2. Clone & Install
```bash
# Clone the repository
git clone https://github.com/your-username/guard-ai.git
cd Guard-AI

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 How to Use

### Option A: Web Interface (Recommended)
The web interface provides the most comprehensive experience, including an exam portal and admin dashboard.

1. **Start the Server:**
   ```bash
   python app.py
   ```
2. **Access the Portal:**
   Open `http://127.0.0.1:5000` in your browser.
3. **Take the Exam:**
   Enter the secret code (default: `GUARD2026`) and start the session.
4. **Admin Dashboard:**
   Access `http://127.0.0.1:5000/admin` (Creds: `admin` / `admin123`) to monitor real-time violations.

### Option B: Standalone Mode
Run the detection logic directly in your terminal.

```bash
python main.py
```
*Press `Ctrl+C` to stop and generate the final report.*

---

## 📊 Security & Compliance

Guard AI generates a **Trust Score** for each student based on detected violations:
- **Speaking Detected**: -10 pts
- **Looking Away**: -5 pts
- **Multiple Persons**: -15 pts

Reports are saved in the `logs/` directory as `final_report_[reg_no].pdf`.

---

## 👨‍💻 Credits

Based on the original work by **Nikhil Balamurugan** and **Vishaal Pillay**.
Further developed and customized by **Sahana H V**,**Yashaswini S N** and **Varsha H R**.

## 🌍 License

This project is licensed under the MIT License.

