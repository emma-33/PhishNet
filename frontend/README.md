# PhishNet Frontend

**Version:** 1.0.0  
**Framework:** React 18 + Vite  
**Styling:** TailwindCSS 4  

---

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

Frontend runs on: http://localhost:5173  
Backend API: http://localhost:5000

## Backend API Endpoints

### Dashboard
- `GET /api/dashboard/overview` - System status & stats
- `GET /api/dashboard/campaigns` - List campaigns
- `GET /api/dashboard/campaigns/<id>/metrics` - Campaign metrics
- `POST /api/dashboard/campaigns/compare` - Compare campaigns
- `POST /api/dashboard/email/send` - Send email
- `GET /api/dashboard/templates` - List templates
- `GET /api/dashboard/groups` - List groups
- `GET /api/dashboard/landing-pages` - List landing pages
- `GET /api/dashboard/analytics/timeline` - Analytics data
