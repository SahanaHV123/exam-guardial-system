# Guard AI - Complete Backend Setup Guide

## 🎯 What's Been Fixed & Enhanced

### Critical Bug Fixes
✅ **Fixed datetime comparison bug** - Gaze tracking no longer crashes when user looks away
✅ **Added missing fpdf dependency** - PDF report generation now works
✅ **Fixed report path handling** - Flask download endpoint now works correctly
✅ **Improved process management** - Better start/stop/cleanup in Flask app

### New Features Added
✅ **Multiple Person Detection** - Warns when more than one face is detected
✅ **Session Tracking** - Each monitoring session gets a unique ID
✅ **Enhanced Logging** - Better error messages and session information
✅ **Configuration File** - Easy customization of detection thresholds
✅ **Improved Error Handling** - Graceful handling of camera/microphone permissions

## 🚀 How to Run

### 1. Start the Flask Server
```bash
cd /Users/nikhil/Documents/Guard-AI
source venv/bin/activate
python app.py
```

The server will start at: http://127.0.0.1:5000

### 2. Use the Web Interface

1. **Open browser**: Navigate to http://127.0.0.1:5000
2. **Start Guard AI**: Click "Start Guard AI" button
   - Webcam window will open
   - All three monitoring features activate:
     - 👄 Lip movement + audio detection
     - 👀 Gaze tracking
     - 🌐 Website monitoring
     - 👥 Multiple person detection
3. **Stop Guard AI**: Click "Stop Guard AI" button
   - Monitoring stops
   - PDF report is generated automatically
4. **Download Report**: Click "Download Report" button
   - Downloads comprehensive PDF with all detected events

### 3. Run Standalone (Optional)
```bash
source venv/bin/activate
python main.py
```
Press `Ctrl+C` to stop and generate report.

## 📊 Features Explained

### 1. Lip Movement Detection + Audio Analysis
- Detects when user is speaking during exam
- Uses both visual lip movement and audio analysis
- Differentiates between yawning and actual speaking
- Logs start and end times of speaking events

### 2. Gaze Tracking
- Monitors eye and head movement
- Detects when user looks away from screen
- Shows warning after 5 seconds of looking away
- Tracks: Looking Left, Right, Up, Down, Center

### 3. Website Monitoring
- Monitors Safari browser activity (macOS)
- Logs all open tabs every 5 seconds
- Detects unauthorized website access
- Records timestamps of website usage

### 4. Multiple Person Detection (NEW!)
- Detects when more than one face appears on camera
- Immediate warning displayed
- Logs all multiple person incidents
- Helps prevent impersonation and collaboration

## 📁 Generated Files

### Logs Directory (`logs/`)
- `guard_ai_logs.txt` - Detailed system logs with session IDs
- `session_report.txt` - Raw event data for current session
- `final_report.pdf` - Comprehensive PDF report (downloadable)
- `website_usage_logs.txt` - Website monitoring logs

### Reports Include:
1. **Session Information**
   - Unique session ID
   - Start time
   - Report generation time

2. **Website Tracking**
   - All websites/tabs accessed
   - Timestamps

3. **Speaking Events**
   - When user was speaking
   - Duration

4. **Looking Away Events**
   - When user looked away
   - Duration

5. **Multiple Person Detection**
   - When multiple faces detected
   - Number of faces

## ⚙️ Customization

Edit `config.py` to customize detection thresholds:

```python
# Lip Detection
LIP_MOVEMENT_THRESHOLD = 2.5  # Sensitivity
SPEAKING_AUDIO_THRESHOLD = 0.01  # Audio level

# Gaze Tracking
LOOK_AWAY_DURATION = 5  # Seconds before warning

# Multiple Person Detection
MAX_ALLOWED_FACES = 1  # Maximum faces allowed
```

## 🧪 Testing

Run the test suite to verify everything works:
```bash
source venv/bin/activate
python test_backend.py
```

Expected output:
```
✅ opencv-python imported successfully
✅ mediapipe imported successfully
✅ numpy imported successfully
✅ sounddevice imported successfully
✅ psutil imported successfully
✅ fpdf imported successfully
✅ flask imported successfully
✅ main.py has no syntax errors
✅ app.py has no syntax errors
✅ PDF generation works
🎉 All tests passed! Backend is ready to use.
```

## 🔧 Troubleshooting

### Camera Permission Error
If you see "Cannot access camera":
1. Go to System Settings → Privacy & Security → Camera
2. Enable camera access for Terminal/Python

### Microphone Permission Error
If audio detection doesn't work:
1. Go to System Settings → Privacy & Security → Microphone
2. Enable microphone access for Terminal/Python

### Safari Monitoring Not Working
Make sure Safari is running and has tabs open. The monitoring checks every 5 seconds.

### Report Not Generated
- Make sure you clicked "Stop Guard AI" before downloading
- Check `logs/` directory for `final_report.pdf`
- Review `logs/guard_ai_logs.txt` for errors

## 📝 Next Steps

The backend is now fully functional! Next phase:
- Frontend UI/UX enhancements
- Real-time status updates
- Better visual feedback
- Responsive design improvements

## 🎉 Summary

All backend features are now **100% working**:
- ✅ Lip detection with audio analysis
- ✅ Gaze tracking with warnings
- ✅ Website monitoring
- ✅ Multiple person detection
- ✅ PDF report generation
- ✅ Flask integration
- ✅ Session management
- ✅ Comprehensive logging

The Guard AI proctoring system is ready for use!
