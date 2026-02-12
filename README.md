# 🎓 Learning Platform (LMS)

> A modern, full-featured Learning Management System built with Django & Django REST Framework.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.0%2B-green)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/bootstrap-5-purple)](https://getbootstrap.com/)

## 🚀 Overview

**Learning Platform** is a robust E-Learning solution designed to bridge the gap between Students, Teachers, and Administrators. It features a hybrid architecture combining the speed of server-side rendering (Django Templates) with the flexibility of a modern REST API.

Whether you're selling courses, managing virtual classrooms, or issuing certificates, this platform handles it all out of the box.

---

## ✨ Key Features

### 🔐 Advanced Authentication
- **Secure Login & Registration**: Role-based access control (Admin, Teacher, Student).
- **OTP Verification**: Email-based Two-Factor Authentication (2FA) for secure sign-ups.
- **Session Management**: Secure session handling with auto-expiry.

### 👨‍🏫 Teacher Dashboard
- **Course Management**: Create courses, set prices, and upload thumbnails.
- **Classroom Tools**: Manage course offerings, schedule live classes (Google Meet integration).
- **Content Studio**: Upload video lessons, PDF resources, and external links.
- **Quiz Builder**: Create interactive quizzes with multiple-choice questions.

### 👩‍🎓 Student Experience
- **Easy Enrollment**: Browse courses and enroll instantly.
- **Payments**: Integrated **PayPal** gateway for secure course purchases.
- **Learning Hub**: Access course materials, videos, and resources in a clean interface.
- **Assessments**: Take quizzes and get instant feedback.
- **Certification**: Auto-generated **PDF Certificates** upon course completion.

### �️ technical Highlights
- **Hybrid Architecture**: HTML templates for SEO + API for dynamic data interactions.
- **Cloud Storage**: Seamless media handling with **Cloudinary**.
- **Transactional Emails**: Reliable email delivery via **Brevo (Sendinblue)**.
- **PDF Generation**: Dynamic certificate generation using `xhtml2pdf`.
- **Production Ready**: Configured for deployment on platforms like Render (PostgreSQL, Whitenoise).

---

## 🏗️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python, Django | Core logic and ORM. |
| **API** | Django REST Framework | RESTful endpoints for data exchange. |
| **Frontend** | Bootstrap 5, Crispy Forms | Responsive, modern UI components. |
| **Database** | PostgreSQL (Prod) / SQLite (Dev) | Relational data storage. |
| **Payments** | PayPal REST SDK | Secure payment processing. |
| **Email** | Brevo API | OTPs and notifications. |
| **Storage** | Cloudinary | Asset management (Images/Videos/PDFs). |
| **PDF** | xhtml2pdf | HTML to PDF conversion for certificates. |

---

## ⚙️ Installation & Setup

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone <repository-url>
cd learning-class
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Core Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database (Optional - defaults to SQLite if empty)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# External Services
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=noreply@yourdomain.com

PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret

RENDER_EXTERNAL_HOSTNAME=  # Leave empty for local development
```

### 5. Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to access the application.

---

## � API Documentation

The project includes a browsable API for developers.

- **Base URL**: `/api/`
- **Endpoints**:
    - `/api/courses/`: List and manage courses.
    - `/api/offerings/`: Class schedules and teacher assignments.
    - `/api/users/`: User management.
    - `/api/enrollments/`: Student enrollment tracking.
    - `/api/payments/`: Transaction history.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
