# 🎨 Excel Interviewer Frontend

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit)](https://streamlit.io/)  

Streamlit web application for the **AI-powered Excel skills assessment platform**.  
Provides an intuitive interface for taking interviews, tracking progress, and downloading PDF reports.

---

## 🚀 Features

- ⚡ **Streamlit** for rapid UI development  
- 🔄 Multi-step interview flow with progress tracking  
- 📱 Responsive design across devices  
- 📊 Real-time feedback & analytics  
- 📄 PDF report download with professional formatting  
- 👤 Session persistence for users  

---

## 🛠️ Tech Stack

- **Framework**: Streamlit  
- **HTTP Client**: Requests  
- **Session Management**: Streamlit Session State  
- **PDF Handling**: Base64 encoding  

---

## ⚙️ Installation

### Prerequisites
- Python **3.8+**  
- Backend API running (see backend [README](../backend/README.md))  

### Setup
```bash
# Clone repository
git clone <repository-url>
cd excel-interviewer-frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
## Configuration
Update backend URL in app.py:
```bash
API_BASE = "https://your-backend-url.com"  # Production
```
## 🎯 User Flow
* Welcome Screen → Introduction + "Continue to Assessment"
* User Details Form → Collects candidate info
* Instructions → Guidelines + time estimate
* Interview Session → Progress bar, Q&A, real-time feedback
* Results & Report → Performance summary + PDF download

## 💻 Running the Application
Local Development
```bash
streamlit run app.py
```
Access locally: [http://localhost:8501](url)
