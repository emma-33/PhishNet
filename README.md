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

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Backend Dependencies (`requirements.txt`):**
```
flask>=3.0.0
flask-cors>=6.0.2
pytest>=9.0.2
requests>=2.31.0
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

**Key Frontend Dependencies:**
- React 18.2
- Vite 7.3
- TailwindCSS 4.1.18
- Axios 1.13.2
- React Router 7.11
- Recharts 3.6.0
- Lucide React 0.562

### 4. GoPhish Setup

```bash
cd gophish

# Download GoPhish from official releases
# Extract gophish.exe (Windows) or gophish (Linux/Mac) to this folder

# Review config.json settings (already configured)
# Admin interface: localhost:3333
# Phish server: 0.0.0.0:8080
```

**Generate API Key:**
1. Run GoPhish: `./gophish.exe`
2. Login at `http://localhost:3333` (credentials shown in terminal)
3. Go to Settings → Generate API Key
4. Copy the API key

---

## ⚙️ Configuration

### Backend Configuration

Create `backend/.env`:

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# GoPhish Integration
GOPHISH_ENABLED=true
GOPHISH_API_URL=http://localhost:3333
GOPHISH_API_KEY=your-gophish-api-key-here

# MailTrap SMTP
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=phishnet@example.com

# Database
DATABASE_PATH=phishnet.db
```

### Frontend Configuration

Create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:5000
```

---

## 🏃 Running the Application

### Start All Services (3 separate terminals)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python app.py
```
Backend runs on: `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

**Terminal 3 - GoPhish:**
```bash
cd gophish
./gophish.exe  # Windows
# ./gophish  # Linux/Mac
```
GoPhish admin: `http://localhost:3333`

---

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


## 🔒 Security Notes

⚠️ **Development Environment Only**
- No authentication implemented yet
- Database stores credentials in plain text (for testing)
- CORS enabled for localhost only
- Use only in controlled environments
- Never expose to public internet

🔐 **Sensitive Files (not in git):**
- `backend/.env` - SMTP passwords, API keys
- `backend/phishnet.db` - User submissions
- `gophish/gophish.db` - Campaign data
- `gophish/*.crt/*.key` - SSL certificates

---

## 📊 Features

✅ **Backend (Complete - Phase 0-4)**
- Flask REST API with 9 dashboard endpoints
- GoPhish integration (campaigns, templates, groups)
- MailTrap SMTP email sending
- Email tracking (pixel, click tracking)
- Landing page serving with form capture
- SQLite database for tracking
- 81/81 tests passing

✅ **Frontend (In Progress - Phase 5.1-5.2)**
- React dashboard with real-time data
- System health monitoring
- Campaign management with metrics
- Email sending interface
- Template & group management
- Submission tracking with password reveal
- 19/19 tests passing

⏳ **Planned Features (Phase 5.3-5.8)**
- Advanced campaign analytics
- Timeline visualization (Recharts)
- Bulk email operations
- Target management UI
- Settings & configuration page

---

## 📖 API Endpoints

### Dashboard
- `GET /api/dashboard/overview` - System health & stats
- `GET /api/dashboard/campaigns` - List campaigns
- `GET /api/dashboard/campaigns/<id>/metrics` - Campaign metrics
- `POST /api/dashboard/campaigns/compare` - Compare campaigns
- `POST /api/dashboard/email/send` - Send phishing email
- `GET /api/dashboard/templates` - Email templates
- `GET /api/dashboard/groups` - Target groups
- `GET /api/dashboard/landing-pages` - Landing pages
- `GET /api/dashboard/analytics/timeline` - Analytics data

### Tracking
- `GET /track/pixel/<campaign_id>` - Email open tracking (1x1 GIF)
- `GET /track/click/<campaign_id>` - Link click tracking
- `GET /api/tracking/visits` - Page visits
- `GET /api/tracking/submissions?reveal_passwords=true` - Form submissions

### Landing Pages
- `GET /landing/<page_id>` - Serve landing page
- `POST /landing/<page_id>` - Capture form submission

---

