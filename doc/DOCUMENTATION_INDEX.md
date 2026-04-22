# 📚 Chatbot PSB - Documentation Index

Complete guide to all documentation files and how to navigate them.

---

## Quick Navigation

### 🚀 Getting Started
- **[Quick Start Guide](QUICK_START.md)** - Set up and run in 5 minutes
  - Installation steps
  - Configuration
  - Testing
  - Common issues quick fixes

### 🏗️ Architecture & Design
- **[Architecture Guide](ARCHITECTURE.md)** - Complete system design
  - Double Guard Architecture diagram
  - System components overview
  - Technology stack
  - Design patterns
  - Security & safety measures

- **[Components Reference](COMPONENTS.md)** - Detailed component documentation
  - Telegram Bot Handler
  - FastAPI Application
  - Response Router
  - Intent Classifier
  - Groq Client
  - Database
  - Data classes and configuration

- **[Data Flow Diagrams](DATA_FLOW.md)** - Visual representation of data movement
  - Request-response flow
  - Intent classification pipeline
  - Error handling flow
  - Deployment architecture
  - Database schema

### 📡 API & Integration
- **[API Reference](API_REFERENCE.md)** - REST API documentation
  - HTTP endpoints
  - Telegram webhook
  - Response formats
  - Error codes
  - Integration examples
  - Rate limiting

### 🚀 Deployment
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment
  - Railway deployment (recommended)
  - Docker deployment
  - Environment configuration
  - Monitoring & maintenance
  - Troubleshooting
  - Scaling strategies

### 🛠️ Development
- **[Development Guide](DEVELOPMENT_GUIDE.md)** - For developers
  - Development setup
  - Project structure
  - Code style standards
  - Development workflow
  - Testing guidelines
  - Debugging techniques
  - Common development tasks

- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Problem solving
  - Installation issues
  - Runtime issues
  - API issues
  - Database issues
  - Performance issues
  - Testing issues
  - Deployment issues
  - FAQ

---

## Documentation by Use Case

### "I want to set up the bot locally"
1. Read: [Quick Start Guide](QUICK_START.md)
2. Reference: [Architecture Guide](ARCHITECTURE.md) (optional, for understanding)
3. Help: [Troubleshooting Guide](TROUBLESHOOTING.md) if issues arise

### "I want to understand how the system works"
1. Start: [Architecture Guide](ARCHITECTURE.md) - Overall design
2. Deep dive: [Components Reference](COMPONENTS.md) - Each component
3. Visual: [Data Flow Diagrams](DATA_FLOW.md) - How data moves

### "I want to integrate with the API"
1. Reference: [API Reference](API_REFERENCE.md)
2. Examples: Integration examples in API_REFERENCE.md
3. Deployment: [Deployment Guide](DEPLOYMENT_GUIDE.md) - Where to point

### "I want to deploy to production"
1. Follow: [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. Understand: [Architecture Guide](ARCHITECTURE.md) - Deployment architecture section
3. Verify: [Troubleshooting Guide](TROUBLESHOOTING.md) - Deployment issues

### "I want to develop features"
1. Setup: [Quick Start Guide](QUICK_START.md) - Local setup
2. Guidelines: [Development Guide](DEVELOPMENT_GUIDE.md)
3. Reference: [Components Reference](COMPONENTS.md) - Component APIs
4. Help: [Troubleshooting Guide](TROUBLESHOOTING.md)

### "Something is broken"
1. Check: [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Verify: [Deployment Guide](DEPLOYMENT_GUIDE.md) - If in production
3. Debug: See debugging section in [Development Guide](DEVELOPMENT_GUIDE.md)

---

## File Structure in `/doc`

```
doc/
├── README.md                    # Main overview (old)
├── DOCUMENTATION_INDEX.md       # This file - navigation guide
│
├── QUICK_START.md              # Getting started (5 min setup)
│
├── ARCHITECTURE.md             # System design & overview
│   ├─ Double Guard Architecture
│   ├─ System overview
│   ├─ Component descriptions
│   ├─ Technology stack
│   ├─ Design patterns
│   ├─ Security
│   └─ Deployment architecture
│
├── COMPONENTS.md               # Detailed component reference
│   ├─ Component APIs
│   ├─ Data classes
│   ├─ Configuration
│   └─ Dependencies
│
├── DATA_FLOW.md               # Visual data flow diagrams
│   ├─ Sequence diagrams
│   ├─ Flow charts
│   ├─ Entity relationships
│   └─ Deployment flows
│
├── API_REFERENCE.md           # REST API documentation
│   ├─ Endpoints
│   ├─ Request/response formats
│   ├─ Error codes
│   ├─ Integration examples
│   └─ Rate limiting
│
├── DEPLOYMENT_GUIDE.md        # Production deployment
│   ├─ Railway setup
│   ├─ Docker setup
│   ├─ Configuration
│   ├─ Monitoring
│   ├─ Troubleshooting
│   └─ Scaling
│
├── DEVELOPMENT_GUIDE.md       # Development guidelines
│   ├─ Setup
│   ├─ Code standards
│   ├─ Testing
│   ├─ Debugging
│   ├─ Common tasks
│   └─ Release process
│
└── TROUBLESHOOTING.md         # Problem solving guide
    ├─ Installation issues
    ├─ Runtime issues
    ├─ API issues
    ├─ Database issues
    ├─ Performance issues
    └─ FAQ
```

---

## Learning Path by Role

### For End Users
- Nothing here! Use the Telegram bot directly 😊

### For Bot Administrators
1. [Quick Start Guide](QUICK_START.md) - Setup
2. [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues
3. [Architecture Guide](ARCHITECTURE.md#knowledge-base-system) - Knowledge base section
4. [Deployment Guide](DEPLOYMENT_GUIDE.md#monitoring--maintenance) - Monitoring

### For DevOps / System Administrators
1. [Architecture Guide](ARCHITECTURE.md#deployment-architecture)
2. [Deployment Guide](DEPLOYMENT_GUIDE.md)
3. [Components Reference](COMPONENTS.md) - Dependencies
4. [Troubleshooting Guide](TROUBLESHOOTING.md) - Deployment issues

### For Backend Developers
1. [Quick Start Guide](QUICK_START.md)
2. [Architecture Guide](ARCHITECTURE.md)
3. [Components Reference](COMPONENTS.md)
4. [Development Guide](DEVELOPMENT_GUIDE.md)
5. [API Reference](API_REFERENCE.md)
6. [Data Flow Diagrams](DATA_FLOW.md)

### For Data Scientists / ML Engineers
1. [Architecture Guide](ARCHITECTURE.md) - Intent classifier section
2. [Components Reference](COMPONENTS.md#4-intent-classifier)
3. [Development Guide](DEVELOPMENT_GUIDE.md#train-new-intent-classifier)
4. Jupyter notebook in `notebooks/`

### For Integration Partners
1. [API Reference](API_REFERENCE.md)
2. Integration examples in API_REFERENCE.md
3. [Deployment Guide](DEPLOYMENT_GUIDE.md) - For your deployment

---

## Key Concepts Explained

### Double Guard Architecture
- **Guard 1 (Intent Classifier)**: Traditional ML for intent prediction
- **Guard 2 (LLM Reasoning)**: Modern LLM for language refinement
- **Why?**: Prevents hallucination while maintaining response quality
- **Read**: [Architecture Guide](ARCHITECTURE.md#double-guard-architecture)

### Knowledge Base
- Single source of truth for all facts
- JSON files organized by intent
- Never changes during conversation
- **Read**: [Architecture Guide](ARCHITECTURE.md#6-knowledge-base-system)

### Response Router
- Central orchestrator
- Manages pipeline through both guards
- Handles errors gracefully
- **Read**: [Components Reference](COMPONENTS.md#3-response-router)

### Confidence Scoring
- 0.0 - 1.0 scale from intent classifier
- Determines response pipeline
- Used for validation
- **Read**: [Data Flow Diagrams](DATA_FLOW.md#confidence-based-response-selection-flow)

---

## Common Tasks & Where to Find Them

### Setup & Installation
- Local setup: [Quick Start Guide](QUICK_START.md#1-clone--setup)
- Production setup: [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Docker setup: [Deployment Guide](DEPLOYMENT_GUIDE.md#docker-deployment)

### Configuration
- Environment variables: [Quick Start Guide](QUICK_START.md#3-configure-environment)
- Advanced config: [Components Reference](COMPONENTS.md#configuration)
- Production config: [Deployment Guide](DEPLOYMENT_GUIDE.md#environment-configuration)

### Development
- New feature: [Development Guide](DEVELOPMENT_GUIDE.md#feature-development)
- Bug fix: [Development Guide](DEVELOPMENT_GUIDE.md#bug-fix-workflow)
- Testing: [Development Guide](DEVELOPMENT_GUIDE.md#testing)
- Code style: [Development Guide](DEVELOPMENT_GUIDE.md#code-style--standards)

### Knowledge Base
- Update KB: [Development Guide](DEVELOPMENT_GUIDE.md#add-new-knowledge-base-topic)
- New intent: [Development Guide](DEVELOPMENT_GUIDE.md#add-new-knowledge-base-topic)
- Retrain: [Development Guide](DEVELOPMENT_GUIDE.md#train-new-intent-classifier)

### Deployment
- To Railway: [Deployment Guide](DEPLOYMENT_GUIDE.md#railway-deployment)
- To Docker: [Deployment Guide](DEPLOYMENT_GUIDE.md#docker-deployment)
- Monitoring: [Deployment Guide](DEPLOYMENT_GUIDE.md#monitoring--maintenance)
- Scaling: [Deployment Guide](DEPLOYMENT_GUIDE.md#scaling)

### Troubleshooting
- All issues: [Troubleshooting Guide](TROUBLESHOOTING.md)
- Installation: [Troubleshooting Guide](TROUBLESHOOTING.md#installation-issues)
- Runtime: [Troubleshooting Guide](TROUBLESHOOTING.md#runtime-issues)
- Database: [Troubleshooting Guide](TROUBLESHOOTING.md#database-issues)
- Performance: [Troubleshooting Guide](TROUBLESHOOTING.md#performance-issues)

---

## External Links & Resources

### Official Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Groq API](https://console.groq.com/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### Deployment Platforms
- [Railway.app](https://railway.app) - Recommended
- [Heroku](https://www.heroku.com)
- [DigitalOcean](https://www.digitalocean.com)
- [AWS](https://aws.amazon.com)

### Development Tools
- [VS Code](https://code.visualstudio.com)
- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Git](https://git-scm.com)
- [Docker](https://www.docker.com)

### Libraries & Frameworks
- [scikit-learn](https://scikit-learn.org) - ML
- [SQLAlchemy](https://www.sqlalchemy.org) - ORM
- [Pydantic](https://pydantic-settings.readthedocs.io) - Validation
- [Pytest](https://pytest.org) - Testing

---

## Documentation Maintenance

### How to Update Docs
1. Edit relevant .md files
2. Keep examples current
3. Update diagrams if architecture changes
4. Add new documents as needed
5. Keep INDEX updated
6. Commit with clear message: "docs: update FILENAME"

### Version Information
- **Last Updated**: January 1, 2026
- **API Version**: 1.0.0
- **Python**: 3.10+
- **FastAPI**: >=0.104.0

---

## Quick Reference

### Environment Variables (Complete List)

```bash
# REQUIRED
TELEGRAM_BOT_TOKEN=...
GROQ_API_KEY=...
DATABASE_URL=...

# OPTIONAL (have defaults)
LOG_LEVEL=INFO
ENVIRONMENT=production
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3
```

### Common Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Development
python app.py
pytest tests/ -v
black .
flake8 .

# Deployment
git push origin main  # Railway auto-deploys

# Database
python init_database.py
python export_training_data.py
python admin_labeling.py

# Training
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI entry point |
| `response_router.py` | Core orchestration |
| `intent_classifier.py` | Guard 1 (Intent prediction) |
| `groq_client.py` | Guard 2 (LLM refinement) |
| `database.py` | Data persistence |
| `telegram_bot.py` | Telegram integration |
| `.env` | Configuration (create from .env.example) |
| `knowledge_base/` | Curated facts (JSON files) |
| `models/` | Pre-trained ML models |

---

## Feedback & Contribution

To improve documentation:
1. Identify unclear sections
2. Propose improvements
3. Submit via GitHub issue or PR
4. Include:
   - What was confusing
   - What would help
   - Suggested changes

---

**Start with [Quick Start Guide](QUICK_START.md) or [Architecture Guide](ARCHITECTURE.md) depending on your needs!**

