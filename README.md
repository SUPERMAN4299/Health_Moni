# 🏥 Health Monitoring & Patient Dashboard

This project is a **Health Monitoring & Patient Management System** built with **Python, Flask, CustomTkinter, and PyQtGraph**. It enables secure login, patient data collection, health condition monitoring, real-time graph visualization, and server communication for storing/retrieving patient records.

---

## 📌 Features
- 🔐 Secure Authentication with session persistence.
- 📝 Patient Information Form (disease history, age, contacts, DOB).
- 📊 Health Dashboard (Heart Rate, AQI, GSR, Temperature).
- 📈 Real-time Graph Visualization with PyQtGraph.
- 📡 Server Communication (upload/retrieve patient records).
- 💊 Dynamic Prescription Panel (AI-ready).
- 🎨 Modern UI using CustomTkinter (dark theme, multi-panel).
- 🌐 Flask Templates for web-based visualization and management.

---

## 🛠️ Tech Stack
- **Frontend (GUI):** CustomTkinter, Tkinter  
- **Backend:** Flask (REST API + HTML templates)  
- **Visualization:** PyQtGraph  
- **Utilities:** NumPy, Requests, Multiprocessing, Threading  
- **Security:** Hex encoding/decoding, session handling  

---

## 📂 Project Structure

.
├── patient_data1.json 
├── session.txt
├── main.py 
├── server.py
├── templates/ 
│ ├── login.html
│ ├── dashboard.html 
│ └── patient_form.html 
└── README.md 



---

## 🚀 Installation & Usage
### 1️⃣ Clone Repository
`git clone https://github.com/your-username/health-dashboard.git && cd health-dashboard`

### 2️⃣ Install Dependencies
`pip install flask requests customtkinter pyqt5 pyqtgraph numpy bleak`

### 3️⃣ Run Flask Server
`python server.py`

### 4️⃣ Launch Dashboard
`python main.py`

---

## 🔑 Login
- Credentials are fetched from server endpoint `/s1`.  
- Username, password, and device IP must match.  
- Active session stored in `session.txt`.  

---

## 🎨 Flask Templates
The **templates** folder contains HTML files that define how the server-side UI looks:
- `login.html` → Simple login form styled with Bootstrap.
- `dashboard.html` → Displays patient data & health status.
- `patient_form.html` → Input form for new patient records.

> These templates can be customized to improve UI/UX with CSS, Bootstrap, or Tailwind.

---

---

## 📌 Future Improvements
- AI-generated prescriptions (OpenAI API).  
- Integration with ESP32/BLE sensors.  
- Advanced patient analytics.  
- Multi-user roles (Doctor, Patient, Admin).  

---


