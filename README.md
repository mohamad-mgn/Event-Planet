# 🎪 Event Planet - Event Planning & Management Platform

A comprehensive API-first event management platform built with Django REST Framework.

## 🚀 Features

- **🔐 OTP Authentication** - Phone number-based authentication with OTP
- **👥 Multi-Role System** - Participants and Organizers with different permissions
- **🎭 Event Management** - Full CRUD operations for events with status lifecycle
- **📅 Multi-Stage Events** - Support for events with multiple stages/sessions
- **🎨 Dynamic Attributes** - EAV pattern for flexible event properties
- **📝 Registration System** - Event registration with capacity management
- **⭐ Feedback System** - Rating and review system with statistics
- **🔔 Real-time Notifications** - Signal-based notification system
- **📊 API Documentation** - Swagger & ReDoc integration

## 🛠️ Tech Stack

- **Backend:** Django 5.0, Django REST Framework
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **Task Queue:** Celery
- **Authentication:** JWT (Simple JWT)
- **Documentation:** drf-spectacular (Swagger/OpenAPI)
- **Deployment:** Docker & Docker Compose

## 📋 Prerequisites

- Docker & Docker Compose
- Git

## 🏃 Quick Start

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd event_planet
```

### 2️⃣ Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` file with your configurations.

### 3️⃣ Build and run with Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### 4️⃣ Create superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5️⃣ Access the application

- **API Base:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **Swagger Docs:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/

## 📚 API Endpoints

### Authentication

```
POST   /api/accounts/auth/send-otp/      - Send OTP
POST   /api/accounts/auth/verify-otp/    - Verify OTP & Login
GET    /api/accounts/profile/            - Get Profile
PATCH  /api/accounts/profile/            - Update Profile
POST   /api/accounts/auth/logout/        - Logout
```

### Categories

```
GET    /api/categories/                  - List Categories
GET    /api/categories/{slug}/           - Category Detail
```

### Events (Public)

```
GET    /api/events/public/               - List Published Events
GET    /api/events/public/{slug}/        - Event Detail
GET    /api/events/public/{slug}/results/ - Event Results
```

### Events (Organizer)

```
GET    /api/events/organizer/            - List My Events
POST   /api/events/organizer/create/     - Create Event
GET    /api/events/organizer/{slug}/     - Event Detail
PATCH  /api/events/organizer/{slug}/     - Update Event
DELETE /api/events/organizer/{slug}/     - Delete Event
POST   /api/events/organizer/{slug}/status/ - Change Status
```

### Registrations

```
GET    /api/registrations/               - My Registrations
POST   /api/registrations/create/        - Register for Event
POST   /api/registrations/{id}/cancel/   - Cancel Registration
```

### Feedback

```
GET    /api/feedback/my-feedbacks/       - My Feedbacks
POST   /api/feedback/create/             - Submit Feedback
GET    /api/feedback/event/{slug}/       - Public Event Feedbacks
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Restart a service
docker-compose restart [service_name]
```

## 📂 Project Structure

```
event_planet/
├── apps/
│   ├── accounts/          # User authentication & OTP
│   ├── categories/        # Event categories
│   ├── events/           # Event management
│   ├── registrations/    # Registration system
│   ├── feedback/         # Feedback & ratings
│   └── core/             # Shared utilities
├── config/
│   ├── settings/         # Settings (base, dev, staging, prod)
│   ├── urls.py          # Main URL configuration
│   ├── wsgi.py
│   └── celery.py        # Celery configuration
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Development

### Without Docker

1. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create categories:

```bash
python manage.py create_default_categories
```

5. Run development server:

```bash
python manage.py runserver
```

## 🧪 Testing with Postman

Import the API collection and test all endpoints.

Example: Register and Login

```json
// 1. Send OTP
POST /api/accounts/auth/send-otp/
{
  "phone_number": "+989123456789"
}

// 2. Verify OTP
POST /api/accounts/auth/verify-otp/
{
  "phone_number": "+989123456789",
  "otp": "123456",
  "full_name": "John Doe",
  "role": "organizer"
}

// 3. Use access token in headers
Authorization: Bearer <access_token>
```

## 🌍 Environment Variables

Key environment variables:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=event_planet_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# OTP
OTP_EXPIRY_TIME=300
```

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- Mohammad Moghanloo
