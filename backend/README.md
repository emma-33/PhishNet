# PhishNet Backend

Backend API for PhishNet - A B2B phishing simulation and security-awareness training platform.

## 🎯 Purpose

This backend provides APIs for:
- Phishing campaign simulation
- Employee interaction tracking (email opens, clicks, form submissions)
- Security metrics and recommendations

**⚠️ For DEFENSIVE SECURITY PURPOSES ONLY** - Employee training and security awareness

## 🏗️ Architecture

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── requirements.txt    # Dependencies
├── routes/            # API route handlers
├── models/            # Data models
├── utils/             # Utility functions
└── tests/             # Test suite
```

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- pip

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

   Server starts at: `http://localhost:5000`

3. **Run tests:**
   ```bash
   pytest
   ```

## 📡 API Endpoints

### Root Endpoint
```
GET /
```
Returns basic API information

**Response:**
```json
{
  "name": "PhishNet Backend API",
  "version": "0.1.0",
  "status": "running"
}
```

### Health Check
```
GET /health
```
Returns health status and timestamp (for monitoring)

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T17:00:00.000000+00:00",
  "service": "phishnet-backend"
}
```

## 🧪 Testing

### Automated Tests
```bash
pytest -v
```

### Manual Testing
```bash
python manual_test.py
```

Or use curl:
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

## ⚙️ Configuration

Configuration is managed in `config.py`:

- **DevelopmentConfig**: Local development (DEBUG=True)
- **TestingConfig**: Test environment (in-memory DB)

Set environment:
```bash
export FLASK_ENV=development  # Linux/Mac
$env:FLASK_ENV="development"  # Windows PowerShell
```

## 📋 Current Status

**Phase 0: Initial Setup** - ✅ COMPLETE

Implemented:
- Flask application with factory pattern
- Configuration system (dev/testing)
- Health check endpoint
- Test suite (4/4 passing)

**Next Phase:** GoPhish Integration

## 🔧 Development

### Project Structure
- Uses application factory pattern for testability
- Separate configs for dev/test environments
- pytest for testing with fixtures
- Timezone-aware datetime handling

### Running in Development
```bash
python app.py
```
- Debug mode: ON
- Auto-reload: ON (note: may need restart if issues)
- Accessible at: `http://localhost:5000`

## 📚 Documentation

See [`/docs/PROJECT_CONTEXT.md`](../docs/PROJECT_CONTEXT.md) for:
- Complete architecture details
- Implementation phases
- Decision log
- Development guidelines

## 🛠️ Tech Stack

- **Framework:** Flask
- **Language:** Python 3.x
- **Database:** SQLite (future)
- **Testing:** pytest
- **Environment:** Local development

## ⚠️ Important Notes

- This is a **development environment** - no production hardening
- No authentication implemented yet
- Focus on functionality over best practices
- Backend only (no frontend integration)

---

**For questions or issues, see PROJECT_CONTEXT.md for current status and next steps.**
