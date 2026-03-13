<p align="center">
  <h1><strong>Guard AI</strong></h1>
</p>

<img width="921" alt="image" src="https://github.com/user-attachments/assets/af00313d-d908-4364-9fd8-d66df4320906" /><br><br>


**Welcome to the Guard AI project !! 🚨**

Guard AI is a lightweight, AI-powered exam monitoring tool that provides real-time proctoring by detecting suspicious activities during online exams such as unauthorized speaking, gaze deviation, and usage of restricted websites.

<p align="center">
  <h1><strong>🔍 Features :-</strong></h1>
</p>

>> Lip Movement Detection + Audio Analysis
>> Detects if the user is speaking during the exam.
>> Differentiates between yawning and speaking.


![Screenshot 2025-04-22 080606](https://github.com/user-attachments/assets/593bdd54-aefe-4661-9372-23dd122bc329)<br><br>



<p align="center">
  <h1><strong>👀 Gaze Tracking :-</strong></h1>
</p>

>> Tracks user's eye and head movement.
>> Detects if the user looks away from the screen.

![Screenshot 2025-04-22 080633](https://github.com/user-attachments/assets/02e1a10c-1b59-42de-b5d4-9909a570e5ee)<br><br>



<p align="center">
  <h1><strong>🖥️ Website Monitoring :-</strong></h1>
</p>

>> Detects if the user opens any non-permitted websites.
>> A warning signal is provided if done so.

![image](https://github.com/user-attachments/assets/9483937b-ed4f-49f1-bffe-576b46809111)<br><br>



<p align="center">
  <h1><strong>📂 Comprehensive Report Generation :-</strong></h1>
</p>

>> Summarizes user behavior during the exam.
>> Includes start and end times of suspicious activities.
>> Generates a clean PDF report after each test session.

<p align="center">
  <h1><strong>📚 Project Structure :-</strong></h1>
</p>

guard_ai_project/
│
├── features/
│   ├── __init__.py
│   ├── lip_detection.py
│   ├── gaze_tracking.py
│   └── website_monitor.py
│
├── logs/
│   ├── lip_audio_logs.txt
│   ├── gaze_tracking_logs.txt
│   └── website_usage_logs.txt
│
├── reports/
│   └── final_report.pdf (auto-generated)
│
├── main.py
├── generate_report.py
├── README.md
├── requirements.txt

<p align="center">
  <h1><strong>📂 Comprehensive Report Generation :-</strong></h1>
</p>🔧 **Installation** :-
1. Clone the repository: git clone https://github.com/your-username/guard-ai-project.git
2. Install the required libraries: pip install -r requirements.txt

<p align="center">
  <h1><strong>📅 How to Use :-</strong></h1>
</p>
1. Run the application: python main.py

2. After finishing, you can generate an intermediate report.
  
3. At the end, generate a final comprehensive PDF report.

<p align="center">
  <h1><strong>📊 Reports :-</strong></h1>
</p>
Reports will be generated automatically in the reports/ folder.

The report includes:
Activities detected.
Time intervals.
Observations.

<p align="center">
  <h1><strong>🎉 Credits :</strong></h1>
</p>

Developed by **Nikhil Balamurugan** and **Vishaal Pillay**👨‍💻

<p align="center">
  <h1><strong>🌍 License :</strong></h1>
</p>

This project is licensed under the MIT License.
