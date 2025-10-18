# 🔒 VulnVerse – Web Security Learning Platform

VulnVerse is a **Django-based web application** designed for learning and practicing **web application vulnerabilities** in a safe and controlled environment.  
It currently focuses on **Web Application Labs** (OWASP Top 10) and uses **Docker** for deployment.

> ⚠️ Note: This version includes only the **Web Application Labs** module.  
> Future releases will include integrated tools, API testing, Wi-Fi simulations, and an AI chatbot.
>  ⚠️ Note: For labs to be working containers should be open from my end to remotely access the labs.
---

## 🚀 Features

- Hands-on labs for common web vulnerabilities:
  - SQL Injection (SQLi)
  - IDOR (Insecure Direct Object References)
- Django backend with modular lab structure
- HTML & CSS frontend
- Dockerized environment for isolated execution

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML, CSS |
| **Backend** | Django (Python) |
| **Containerization** | Docker |
| **Database** | SQLite (default Django DB) |

---

## 🧩 Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/antonysimoncodes/VulnVerseProject.git
cd VulnVerseProject

2. Activate Virtual Environment
virtual\Scripts\activate        # On Windows
source virtual/bin/activate     # On macOS/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Apply Migrations
python manage.py migrate

5. Run the Development Server
python manage.py runserver


Access the app in your browser at:
👉 http://127.0.0.1:8000
