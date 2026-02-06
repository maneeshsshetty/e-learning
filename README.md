# 🎓 Online Learning Platform (E-Learning)

Welcome to the **Online Learning Platform**, a powerful and modern educational management system built with **Django** and **Django REST Framework (DRF)**.

This project is designed with a **Hybrid Architecture**:
- 🌐 **Dynamic UI**: Uses Django Templates for a smooth, server-side rendered experience.
- ⚡ **Data-Driven**: Uses a REST API (DRF) to power real-time dashboards and interactive data tables.

---

## � Live Demo
Visit the live application here:  
🚀 **[https://e-learning-q536.onrender.com/](https://e-learning-q536.onrender.com/)**

---

## 🛠️ How it Works

The platform supports three distinct user roles, each with their own specialized workflow:

| Role | Workflow | Key Actions |
| :--- | :--- | :--- |
| **Admin** | **Manage & Monitor** | Create courses, view all users, and track platform-wide growth. |
| **Teacher** | **Instruct & Guide** | Opt-in to teach courses, manage classes, and share meeting links. |
| **Student** | **Learn & Grow** | Browse available subjects, choose teachers, and join live classes. |

---

## ✨ Key Features

### 🏢 Intelligent Dashboards
Unlike traditional systems, our dashboards are "thin clients." They load the page layout first and then use **JavaScript (Fetch API)** to pull in the latest data from our backend API. This makes the experience fast and responsive.

### 🔐 Secure Authentication & Roles
- **CSRF Protected**: Robust security for all form submissions and API interactions.
- **Environment Driven**: Sensitive keys and database credentials are kept safe in `.env` files.

### 📚 Course & Classroom Integration
- **Media Support**: Modern course icons and photo uploads.
- **Google Meet**: Integrated fields for teachers to share live class links directly with their students.
- **Automated Enrollments**: Simple one-click enrollment for students.

---

## 🏗️ Technology Stack

- **Backend Logic**: Python 3.x & Django 6.0+
- **API Engine**: Django REST Framework (DRF)
- **Database**: PostgreSQL (Production-ready) / SQLite (Local)
- **UI Styling**: Bootstrap 5 + Crispy Forms
- **Environment**: Dotenv for secure configuration

---

## ⚙️ Setting Up Locally

Follow these steps to get the project running on your own machine.

### 1. Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### 2. Clone and Prepare
```bash
git clone <repository-url>
cd learning-class
```

### 3. Setup Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate  
# Linux/Mac:
source venv/bin/activate 
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Secrets
Create a `.env` file in the root folder and add your credentials:
```env
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=your_secure_unique_key
DEBUG=True
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 6. Initialize Database
```bash
python manage.py migrate
```

### 7. Launch
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser to see the platform in action!

---

## 📂 Project Structure
- `core_project/`: Main settings, secure configuration, and URL routing.
- `courses/`: The heartbeat of the app—contains logic for users, courses, and the REST API.
- `templates/`: Modern, responsive HTML layouts.
- `static/`: Custom CSS and JavaScript for dashboard interactions.

---

## 📝 License
This project is built for professional training and educational purposes.
