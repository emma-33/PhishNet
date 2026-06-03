# PhishNet

**B2B Phishing Simulation & Security Awareness Platform**

PhishNet is a full-stack application for conducting phishing simulations and security awareness training. Built for defensive security purposes, it enables organizations to test and improve employee awareness of phishing attacks.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 22.12+** (for Vite 7.3)
- **Git**
- **GoPhish v0.12.1** - [Download here](https://github.com/gophish/gophish/releases)
- **MailTrap Account** (free) - [Sign up here](https://mailtrap.io/)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PhishNet
```

### 2. Docker Containers setup
```bash
cp .env.example .env

# Configure the .env
docker compose up -d
```

## ⚙️ Configuration

```bash
# PostgreSQL Database Configuration
POSTGRES_DB=phishnet
POSTGRES_USER=phishnet
POSTGRES_PASSWORD=changeme_secure_password_here

# Flask Backend Configuration
SECRET_KEY=changeme_secret_key
JWT_SECRET_KEY=changeme_jwt_secret_key
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Database URL
DATABASE_URL=postgresql://phishnet:changeme_secure_password_here@db:5432/phishnet

# CORS Configuration
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost,http://localhost:80

# Frontend Configuration
FRONTEND_PORT=80

# Gophish Ports (configured in dashboard)
GOPHISH_ADMIN_PORT=3333
GOPHISH_PHISHING_PORT=8080
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_api.py # Run specific test file
```

**Test Coverage:** 81/81 tests passing (100%)

### Frontend Tests

```bash
cd frontend
npm test                 # Run tests
npm run test:ui         # Run tests with UI
npm run test:coverage   # Coverage report
```

**Test Coverage:** 19/19 tests passing (100%)

---

## 📊 Features

✅ **Backend**
- Flask REST API with 9 dashboard endpoints
- GoPhish integration (campaigns, templates, groups)
- Tenants integration (invitation system and permissions)
- 210/210 tests passing

✅ **Frontend**
- React dashboard with real-time data
- System health monitoring
- Campaign management with metrics
- Email sending interface
- Template & group management
- Submission tracking
- 57/57 tests passing

---

## 📖 API Endpoints

### Auth
- `POST /api/auth/login` - Login a user and receive a JWT token
- `POST /api/auth/register` - Register a new user using an invitation code

### Campaigns
- `GET /api/campaigns` - List all campaigns for your tenant
- `POST /api/campaigns` - Create a new phishing campaign
- `GET /api/campaigns/<id>` - Get detailed information about a specific campaign
- `GET /api/campaigns/<id>/summary` - Get real-time results and summary metrics for a campaign
- `POST /api/campaigns/<id>/complete` - Manually complete/stop a running campaign
- `DELETE /api/campaigns/<id>` - Delete a campaign

### Tenants (Admin Only)
- `GET /api/tenants` - List all tenants in the system
- `POST /api/tenants` - Create a new tenant and generate an initial invitation
- `GET /api/tenants/<id>` - Get tenant details
- `PUT /api/tenants/<id>` - Update tenant information
- `DELETE /api/tenants/<id>` - Remove a tenant from the system

### Tenant Invitations
- `POST /api/tenant-invitations` - Generate a new invitation code (Operator Only)
- `POST /api/tenant-invitations/validate` - Check if an invitation code is valid
- `GET /api/tenant-invitations/<codeShort>` - Get details for a specific invitation code
- `GET /api/tenant-invitations/tenant/<id>` - List all invitations issued for a specific tenant (Operator Only)

### Instances (Admin Only)
- `GET /api/instances` - List all connected Gophish instances
- `POST /api/instances` - Connect a new Gophish instance
- `GET /api/instances/<id>` - Get instance configuration
- `PUT /api/instances/<id>` - Update instance settings
- `PATCH /api/instances/<id>/toggle` - Enable or disable a Gophish instance
- `DELETE /api/instances/<id>` - Disconnect a Gophish instance

### Templates
- `GET /api/templates` - List all available phishing templates
- `POST /api/templates` - Create a new email and landing page template (Admin Only)
- `GET /api/templates/<id>` - Get full template content (Admin Only)
- `PUT /api/templates/<id>` - Update an existing template (Admin Only)
- `DELETE /api/templates/<id>` - Remove a template (Admin Only)

### Team
- `GET /api/team` - List all users belonging to your tenant and their roles (Operator/User)