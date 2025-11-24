# Procure-to-Pay System

**Deployed API Docs:** [https://ist-procure-to-pay.onrender.com/api/docs/](https://ist-procure-to-pay.onrender.com/api/docs/)

A comprehensive **Procure-to-Pay (P2P)** application built with Django REST Framework. This system streamlines the entire procurement lifecycle from purchase request creation, through multi-level approvals, to purchase order generation and receipt validation using AI-powered verification.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [User Roles](#-user-roles)
- [Workflow](#-workflow)
- [Development](#-development)
- [Deployment](#-deployment)

---

## ✨ Features

### Core Functionality
- **Purchase Request Management** - Staff can create, view, and track purchase requests with multiple line items
- **Multi-Level Approval Workflow** - Configurable two-level approval process with comment support
- **Vendor Management** - Track vendor information for each purchase request
- **Purchase Order Generation** - Automatic PO generation upon final approval with PDF export
- **Receipt Validation** - AI-powered receipt verification using Google Gemini
- **File Storage** - Cloud-based file storage using Cloudinary for receipts, POs, and proforma invoices
- **Role-Based Access Control** - Granular permissions based on user roles
- **RESTful API** - Complete REST API with JWT authentication
- **Interactive API Documentation** - Auto-generated API docs using drf-spectacular

### AI-Powered Features
- **Receipt Text Extraction** - OCR technology using Tesseract for extracting text from receipts
- **Intelligent Validation** - Google Gemini AI compares receipt data against purchase orders
- **Discrepancy Detection** - Automatic flagging of amount mismatches and missing items
- **Validation Reports** - Detailed JSON reports with validation results and discrepancy details

---

## 🛠 Tech Stack

### Backend
- **Django 4.2** - High-level Python web framework
- **Django REST Framework 3.14** - Powerful toolkit for building Web APIs
- **PostgreSQL 15** - Advanced open-source relational database
- **Gunicorn** - Python WSGI HTTP Server for UNIX

### Authentication & Security
- **JWT Authentication** - djangorestframework-simplejwt for token-based auth
- **CORS Headers** - django-cors-headers for Cross-Origin Resource Sharing

### Document Processing
- **PyPDF2 & pdfplumber** - PDF parsing and text extraction
- **Tesseract OCR** - pytesseract for optical character recognition
- **ReportLab** - PDF generation for purchase orders

### AI & Cloud Services
- **Google Gemini AI** - google-genai for receipt validation
- **Cloudinary** - Cloud-based media storage and management

### DevOps
- **Docker & Docker Compose** - Containerization and orchestration
- **Python 3.11** - Latest Python version

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (v20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **Git** (for cloning the repository)

### External Accounts Required
- **Cloudinary Account** - For file storage ([Sign up here](https://cloudinary.com/))
- **Google AI Studio Account** - For Gemini API key ([Get API key](https://makersuite.google.com/app/apikey))

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/bencyubahiro77/Procure-to-Pay-BE.git
cd procure_to_pay_full
```

### 2. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration
POSTGRES_DB=ptp
POSTGRES_USER=ptp_user
POSTGRES_PASSWORD=ptp_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

# JWT Token Settings (in minutes/days)
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Build and Run with Docker

Start the application using Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

This will:
- Build the Django application container
- Start PostgreSQL database container
- Start the application on `http://localhost:8000`

> [!IMPORTANT]
> While the `entrypoint.sh` script attempts to run migrations automatically, it's best practice to verify migrations have completed successfully before proceeding.

### 4. Run Database Migrations

**Before creating users or seeding data, you must create the database tables:**

```bash
# Run migrations to create all database tables
docker-compose exec web python manage.py migrate
```

This command creates all necessary tables including `auth_user`, purchase requests, approvals, and other models.

### 5. Create Initial Users

The application includes a management command to seed default users:

```bash
docker-compose exec web python manage.py seed_users
```

This creates users with different roles for testing purposes.

**Default Test Accounts:**

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin_user` | `password123` |
| **Staff** | `staff_user` | `password123` |
| **Approver L1** | `approver1_user` | `password123` |
| **Approver L2** | `approver2_user` | `password123` |
| **Finance** | `finance_user` | `password123` |

**Alternative:** Create a superuser manually:

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Access the Application

- **API Base URL:** `http://localhost:8000/api/`
- **API Documentation:** `http://localhost:8000/api/docs/`
- **Admin Panel:** `http://localhost:8000/admin/`

> [!NOTE]
> **Dependencies are handled automatically!** When you run `docker-compose up --build`, Docker automatically installs all Python dependencies from `requirements.txt` during the build process. You don't need to manually install anything.

---

## 🔧 Alternative: Local Setup (Without Docker)

If you prefer to run the application locally without Docker:

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Tesseract OCR
- Poppler Utils

### Setup Steps

1. **Create and activate virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database** and update `.env` file with your local database credentials:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Seed default users (optional):**
```bash
python manage.py seed_users
```

7. **Run development server:**
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

---

## 🔐 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key for cryptographic signing | - | ✅ |
| `DEBUG` | Enable Django debug mode (1=True, 0=False) | `1` | ✅ |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `127.0.0.1,localhost` | ✅ |
| `POSTGRES_DB` | PostgreSQL database name | `ptp` | ✅ |
| `POSTGRES_USER` | PostgreSQL username | `ptp_user` | ✅ |
| `POSTGRES_PASSWORD` | PostgreSQL password | `ptp_pass` | ✅ |
| `POSTGRES_HOST` | PostgreSQL host | `db` | ✅ |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | ✅ |
| `ACCESS_TOKEN_LIFETIME` | JWT access token lifetime (minutes) | `60` | ✅ |
| `REFRESH_TOKEN_LIFETIME` | JWT refresh token lifetime (days) | `1` | ✅ |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | - | ✅ |
| `CLOUDINARY_API_KEY` | Cloudinary API key | - | ✅ |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | - | ✅ |
| `GEMINI_API_KEY` | Google Gemini AI API key | - | ✅ |

---

## 📚 API Documentation

### Authentication Endpoints

#### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

#### Get Current User
```http
GET /api/accounts/me/
Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "profile": {
    "role": "staff"
  }
}
```

#### Refresh Token
```http
POST /api/accounts/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

### Purchase Request Endpoints

#### Create Purchase Request
```http
POST /api/requests/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Office Supplies",
  "description": "Monthly office supplies purchase",
  "vendor": "Office Depot",
  "amount": 5000.00,
  "items": [
    {
      "name": "Printer Paper",
      "qty": 10,
      "unit_price": 25.00
    },
    {
      "name": "Ink Cartridges",
      "qty": 5,
      "unit_price": 450.00
    }
  ]
}
```

#### List Purchase Requests
```http
GET /api/requests/
Authorization: Bearer <access_token>

# Staff users see only their own requests
# Approvers and Finance see all requests
```

#### Get Purchase Request Details
```http
GET /api/requests/{id}/
Authorization: Bearer <access_token>
```

#### Approve Purchase Request
```http
PATCH /api/requests/{id}/approve/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "comment": "Approved for procurement"
}
```

#### Reject Purchase Request
```http
PATCH /api/requests/{id}/reject/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "comment": "Budget exceeded, please revise"
}
```

#### Submit Receipt
```http
POST /api/requests/{id}/submit-receipt/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <receipt_file.pdf or receipt_image.jpg>
```

#### Download Purchase Order
```http
GET /api/requests/download_po_by_cloudinary_id/?cloudinary_id={cloudinary_id}
Authorization: Bearer <access_token>

# Returns signed Cloudinary URL for secure download
```

---

## 📁 Project Structure

```
procure_to_pay_full/
├── accounts/                    # User authentication and profile management
│   ├── management/
│   │   └── commands/
│   │       └── seed_users.py   # Seed default users
│   ├── models.py               # User profile and role models
│   ├── permissions.py          # Custom permission classes
│   ├── serializers.py          # User serializers
│   ├── urls.py                 # Authentication routes
│   └── views.py                # Login, user info endpoints
│
├── procure/                     # Core procure-to-pay functionality
│   ├── management/
│   │   └── commands/
│   ├── migrations/
│   ├── admin.py                # Django admin configuration
│   ├── document_processing.py  # Receipt validation and OCR
│   ├── models.py               # PurchaseRequest, Approval, PO models
│   ├── serializers.py          # Request/approval serializers
│   ├── urls.py                 # Procurement routes
│   └── views.py                # Request, approval, receipt endpoints
│
├── procure_to_pay/             # Django project settings
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI application
│
├── staticfiles/                # Collected static files
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── entrypoint.sh               # Container startup script
├── manage.py                   # Django management script
├── Makefile                    # Common commands (if applicable)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 👥 User Roles

The system supports five distinct user roles with specific permissions:

| Role | Code | Permissions |
|------|------|-------------|
| **Staff** | `staff` | Create purchase requests, view own requests, submit receipts |
| **Approver Level 1** | `approver_l1` | View all requests, approve/reject at level 1 |
| **Approver Level 2** | `approver_l2` | View all requests, approve/reject at level 2 (final approval) |
| **Finance** | `finance` | View all approved requests, download POs, view receipt validations |
| **Admin** | `admin` | Full system access, manage users and settings |

Roles are assigned via the `Profile` model linked to each user account.

---

## 🔄 Workflow

### 1. Purchase Request Creation
- Staff member creates a purchase request with line items
- System calculates total amount
- Request status: `PENDING`

### 2. Level 1 Approval
- Approver L1 reviews the request
- Can approve or reject with comment
- If approved, moves to Level 2
- If rejected, request status: `REJECTED`

### 3. Level 2 Approval (Final)
- Approver L2 performs final review
- Can approve or reject with comment
- If approved:
  - Request status: `APPROVED`
  - Purchase Order is auto-generated
  - PO PDF is created and stored in Cloudinary
- If rejected, request status: `REJECTED`

### 4. Receipt Submission
- Staff member uploads receipt (PDF or image)
- System extracts text using OCR (Tesseract)
- Gemini AI validates receipt against PO
- Validation checks:
  - Total amount match (within tolerance)
  - Line items verification
  - Missing items detection
  - Discrepancy reporting

### 5. Finance Review
- Finance team views approved requests
- Downloads purchase orders
- Reviews receipt validation status:
  - ✅ **Valid** - Receipt matches PO
  - ⚠️ **Flagged** - Discrepancies detected
  - ⏳ **Not Submitted** - Awaiting receipt

---

## 💻 Development

### Run Migrations

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Access Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Stop Services

```bash
docker-compose down

# Remove volumes (WARNING: deletes database data)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

---

## 🌐 Deployment

### Render Deployment

This application is configured for easy deployment on Render:

1. **Connect Repository** - Link your GitHub repository to Render

2. **Configure Environment Variables** - Add all required environment variables in Render dashboard

3. **Database** - Create a PostgreSQL database on Render and update `POSTGRES_*` variables

4. **Deploy** - Render will automatically:
   - Build the Docker image
   - Run migrations via `entrypoint.sh`
   - Start the Gunicorn server

5. **Post-Deployment**
   ```bash
   # Seed users
   python manage.py seed_users
   
   # Create superuser
   python manage.py createsuperuser
   ```

### Production Considerations

> [!WARNING]
> Before deploying to production:

- Set `DEBUG=0` in environment variables
- Use a strong `SECRET_KEY` (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- Configure proper `ALLOWED_HOSTS` with your domain
- Set up HTTPS/SSL certificates
- Configure proper CORS settings (disable `CORS_ALLOW_ALL_ORIGINS`)
- Enable database backups
- Set up logging and monitoring
- Review and strengthen password validators
- Implement rate limiting
- Add comprehensive tests
- Set up CI/CD pipeline

---


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For questions or issues:
- Open an issue in the repository
- Contact the development team(bencyubahiro77@gmail.com)

---

## 🙏 Acknowledgments

- Django REST Framework for the excellent API toolkit
- Google Gemini for AI-powered receipt validation
- Cloudinary for reliable cloud storage
- The open-source community for all the amazing tools

---

**Happy Procuring! 🎉**
