# Mtaa Skills - Local Service Marketplace

![Mtaa Skills](https://img.shields.io/badge/Mtaa-Skills-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2.7-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)

A modern web platform connecting service seekers with verified local service providers in Kenya.

## 🚀 Current Progress - MVP LAUNCHED!

**✅ PHASE 1 COMPLETED - Foundation Built**
- Django project setup with custom User model
- Service categories and provider management
- Job posting system
- Beautiful Bootstrap UI
- Admin interface
- Database migrations applied
- Sample data created

## 📋 Features Implemented

### Core Functionality
- **User Management**: Custom User model with customer/provider roles
- **Service Categories**: Plumbing, Electrical, Cleaning, Tutoring
- **Provider Profiles**: Service providers with categories and rates
- **Job Posting**: Customers can post service requests
- **Admin Panel**: Full Django admin for data management

### Technical Stack
- **Backend**: Django 4.2.7
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5, Django Templates
- **Authentication**: Django built-in auth with custom User model

## 🏗️ Project Structure
mtaa_skills/

| Directory/File | Purpose |
|---------------|---------|
| `backend/` | Django project configuration |
| `users/` | Custom user authentication & management |
| `services/` | Service categories & provider profiles |
| `bookings/` | Job posting & booking system |
| `templates/` | HTML templates for frontend |
| `manage.py` | Django management script |

---
```
mtaa_skills/
├── backend/                    # Django project
│   ├── __init__.py
│   ├── settings.py            # Project configuration
│   ├── urls.py                # URL routing
│   ├── wsgi.py
│   ├── asgi.py
│   ├── admin.py               # Custom admin configurations
│   ├── apps.py
│   ├── models.py              # Shared models
│   ├── views.py               # Core views and shared logic
│   ├── decorators.py          # Custom decorators
│   └── signals.py             # Signal handlers
├── users/                     # Custom user management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Custom User model
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── services/                  # Service categories & providers
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # ServiceCategory & ServiceProvider models
│   ├── urls.py
│   ├── views.py
│   └── forms.py
├── bookings/                  # Job posting & booking system
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Job, Booking, JobApplication models
│   ├── urls.py
│   ├── views.py
│   └── forms.py
├── payments/                  # Payment processing & wallet
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Payment, ProviderWallet models
│   ├── urls.py
│   ├── views.py
│   └── mpesa.py               # M-Pesa integration
├── reviews/                   # Rating and review system
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Review model
│   ├── urls.py
│   ├── views.py
│   └── forms.py
├── notifications/             # Notification system
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Notification model
│   ├── urls.py
│   ├── views.py
│   └── manager.py             # Notification manager
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Main landing page
│   ├── home_public.html       # Public homepage
│   ├── home_customer.html     # Customer dashboard
│   ├── home_provider.html     # Provider dashboard
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   ├── users/
│   │   └── profile.html
│   ├── services/
│   │   ├── provider_list.html
│   │   ├── provider_detail.html
│   │   ├── provider_dashboard.html
│   │   └── become_provider.html
│   ├── bookings/
│   │   ├── post_job.html
│   │   ├── available_jobs.html
│   │   ├── job_detail.html
│   │   ├── my_jobs.html
│   │   ├── customer_jobs.html
│   │   └── provider_jobs.html
│   ├── payments/
│   │   ├── payment.html
│   │   ├── initiate_payment.html
│   │   └── payment_status.html
│   ├── reviews/
│   │   ├── create_review.html
│   │   ├── leave_review.html
│   │   └── provider_reviews.html
│   ├── notifications/
│   │   └── notification_list.html
│   ├── wallet/
│   │   └── provider_wallet.html
│   └── chat/
│       └── job_chat.html
├── static/                    # Static files
│   └── js/
│       └── notifications.js
├── media/                     # User uploaded files
│   └── provider_pics/         # Provider profile pictures
├── deployment/                # Deployment configurations
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
├── db.sqlite3                 # Development database
├── docker-compose.yml         # Docker compose configuration
├── Dockerfile                 # Docker configuration
└── venv/                      # Virtual environment (excluded from git)
```


## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Django 4.2.7

### Installation
```bash
# Clone repository
git clone https://github.com/Charlesmbuu/mtaa-skills.git
cd mtaa-skills

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django==4.2.7 pillow

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
Access the Application
Website: http://127.0.0.1:8000

Admin Panel: http://127.0.0.1:8000/admin
```

---

# 🎯 Next Features in Development

- User registration & authentication forms

- Service provider verification system

- Payment integration (M-Pesa & Stripe)

- Review and rating system

- Search and filtering functionality

- Mobile-responsive design improvements

---

# 👥 Team
Samburu - Project Lead & Full Stack Developer

# 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

# 🤝 Contributing
We welcome contributions! Please feel free to submit pull requests or open issues for suggestions.

Built with ❤️ for Kenyan communities using Django & Python

text

## **2. Git Ignore File**

Make sure you have `.gitignore` file in your project root.

*.log
```
