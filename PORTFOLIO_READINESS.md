# Portfolio Readiness Plan

This document outlines the decisions and implementation plan to make TradeStrat production-ready for portfolio/resume showcase.

## Decisions

### 1. Landing Page
- **Decision**: Create a professional landing page with project overview, features, and demo
- **Current State**: App opens directly on backtesting tab
- **Target**: Dedicated landing page with "Try Demo" CTA

### 2. Deployment
- **Decision**: Docker containerization
- **Rationale**: Reproducible builds, platform-independent deployment, industry standard

### 3. Hosting
- **Decision**: Render.com
- **Rationale**: Free tier, auto-deploy from GitHub, zero-config, built-in SSL

### 4. CI/CD
- **Decision**: GitHub Actions
- **Rationale**: Automated testing on push, auto-deploy to Render on merge to main

### 5. Documentation
- **Setup Instructions**: Step-by-step guide to run locally
- **API Documentation**: Endpoint specifications for `/backtest` and `/compare`
- **Architecture Decision Records (ADRs)**: Document key technical decisions (SQLite caching, Plotly visualization, pluggable risk framework, backend-driven charts, synchronous execution)

### 6. Testing & Quality
- **Decision**: Add test coverage badge to README
- **Rationale**: Showcase code quality and testing discipline

### 7. Multi-User Handling
- **Decision**: Implement rate limiting
- **Rationale**: Prevent abuse, protect resources, professional API standard
- **Scope**: 10 backtests per minute per IP

### 8. Production-Ready Features
- **Decision**: Environment configuration (dev/prod separation)
- **Rationale**: Required for Render deployment, security best practices
- **Scope**: Separate debug mode, host, port, database paths for dev vs prod

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
**Goal**: Make the app deployable

#### 1.1 Environment Configuration
- [ ] Create `config.py` with `DevelopmentConfig` and `ProductionConfig`
- [ ] Separate dev/prod settings: debug mode, host, port, database paths
- [ ] Update `app.py` to load config based on `FLASK_ENV` environment variable
- [ ] Test locally with both configs

#### 1.2 Rate Limiting
- [ ] Add `flask-limiter` to `requirements.txt`
- [ ] Implement rate limiting on `/backtest` and `/compare` endpoints
- [ ] Set limits: 10 requests/minute per IP
- [ ] Test rate limit behavior

#### 1.3 Docker Setup
- [ ] Create `Dockerfile` for Flask app
- [ ] Create `.dockerignore` file
- [ ] Create `docker-compose.yml` for local development
- [ ] Test Docker build and run locally
- [ ] Document Docker commands in setup guide

### Phase 2: Deployment & CI/CD (Week 1-2)
**Goal**: Automate testing and deployment

#### 2.1 GitHub Actions Workflow
- [ ] Create `.github/workflows/test.yml` for automated testing
- [ ] Run pytest on every push
- [ ] Generate coverage report
- [ ] Add status badge to README

#### 2.2 Render Deployment
- [ ] Create `render.yaml` for deployment configuration
- [ ] Set up Render account and link GitHub repository
- [ ] Configure environment variables on Render
- [ ] Deploy and test production instance
- [ ] Add deployment status badge to README

#### 2.3 CI/CD Pipeline
- [ ] Create `.github/workflows/deploy.yml` for auto-deployment
- [ ] Trigger deployment on merge to `main` branch
- [ ] Test full pipeline: commit → test → deploy

### Phase 3: Documentation (Week 2)
**Goal**: Professional documentation for recruiters and users

#### 3.1 Setup Instructions
- [ ] Create `docs/SETUP.md`
- [ ] Include: Prerequisites, local installation, running with Docker, running tests
- [ ] Add troubleshooting section
- [ ] Link from README

#### 3.2 API Documentation
- [ ] Create `docs/API.md`
- [ ] Document `POST /backtest` endpoint (request/response schemas)
- [ ] Document `POST /compare` endpoint (request/response schemas)
- [ ] Include example requests
- [ ] Link from README

#### 3.3 Architecture Decision Records
- [ ] Create `docs/adr/` directory
- [ ] Write `001-sqlite-caching.md` (Why SQLite over PostgreSQL/Redis)
- [ ] Write `002-plotly-visualization.md` (Why Plotly over Chart.js/D3)
- [ ] Write `003-pluggable-risk-framework.md` (Registry pattern for extensibility)
- [ ] Write `004-backend-driven-charts.md` (Chart specs generated in Python)
- [ ] Write `005-synchronous-backtests.md` (Why no Celery/async processing)
- [ ] Add ADR index to README

### Phase 4: Landing Page & UX (Week 3)
**Goal**: Professional first impression

#### 4.1 Landing Page Design
- [ ] Create landing page route (`/` → landing, `/app` → backtest tool)
- [ ] Design: Hero section with project description
- [ ] Features section with icons
- [ ] Technology stack badges
- [ ] Screenshots carousel
- [ ] "Try Demo" CTA button

#### 4.2 Demo Experience
- [ ] Implement pre-filled demo mode
- [ ] "Try Demo" button sets localStorage flag
- [ ] Auto-populate form with: AAPL, last 1 year, SMA Crossover
- [ ] Auto-run backtest on page load
- [ ] Clear demo flag after execution

#### 4.3 Polish
- [ ] Add favicon
- [ ] Update page title and meta tags
- [ ] Ensure mobile responsiveness
- [ ] Test cross-browser compatibility

### Phase 5: Testing & Quality (Week 3)
**Goal**: Demonstrate code quality

#### 5.1 Test Coverage
- [ ] Run coverage report: `pytest --cov=. --cov-report=html`
- [ ] Identify gaps in test coverage
- [ ] Add tests for critical paths (if needed)
- [ ] Generate coverage badge
- [ ] Add badge to README

#### 5.2 Code Quality
- [ ] Add `.github/workflows/lint.yml` for code quality checks
- [ ] Run on every PR
- [ ] Update README with quality badges

---

## Success Criteria

### Technical
- ✅ App runs in Docker container
- ✅ Deployed to Render with custom URL
- ✅ CI/CD pipeline: push → test → deploy
- ✅ Rate limiting prevents abuse
- ✅ Environment config separates dev/prod
- ✅ Test coverage >80%

### Documentation
- ✅ Setup guide allows new user to run locally in <5 minutes
- ✅ API docs clearly explain endpoints
- ✅ 5 ADRs showcase technical decision-making

### User Experience
- ✅ Landing page provides clear project overview
- ✅ Demo mode shows immediate value
- ✅ Professional appearance suitable for portfolio

### Portfolio Impact
- ✅ README has deployment URL, badges, and documentation links
- ✅ Project demonstrates: full-stack skills, DevOps knowledge, testing discipline, architectural thinking
- ✅ Recruiters can try the live app without local setup

---

## Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| **Week 1** | Infrastructure | Environment config, rate limiting, Docker, Render deployment |
| **Week 2** | Automation & Docs | CI/CD pipeline, setup guide, API docs, ADRs |
| **Week 3** | Polish | Landing page, demo mode, test coverage, final review |

**Total Effort**: ~3 weeks (part-time)

---

## Future Enhancements (Post-Portfolio)

These are intentionally deferred to avoid over-engineering:

- Authentication & user accounts
- Async processing with Celery
- PostgreSQL migration for >50 concurrent users
- Export results as PDF/CSV
- WebSocket real-time updates
- Custom domain
- Advanced analytics dashboard
- Mobile app

---

## Notes

- **Philosophy**: Ship a complete, polished MVP rather than an incomplete feature-rich app
- **Focus**: Demonstrate professional development practices, not just coding ability
- **Target Audience**: Recruiters, hiring managers, potential collaborators
- **Success Metric**: "Would I be proud to show this in an interview?"
