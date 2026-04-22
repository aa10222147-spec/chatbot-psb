# 📖 Chatbot PSB - Complete Project Documentation

> Comprehensive documentation suite for the PSB Chatbot system
>
> **Last Updated**: January 1, 2026  
> **Version**: 1.0.0

---

## 🚀 Quick Links

| Need | Link |
|------|------|
| **Get started in 5 min?** | [Quick Start Guide](doc/QUICK_START.md) |
| **Understand the architecture?** | [Architecture Guide](doc/ARCHITECTURE.md) |
| **Develop features?** | [Development Guide](doc/DEVELOPMENT_GUIDE.md) |
| **Deploy to production?** | [Deployment Guide](doc/DEPLOYMENT_GUIDE.md) |
| **Something broken?** | [Troubleshooting Guide](doc/TROUBLESHOOTING.md) |
| **Need API docs?** | [API Reference](doc/API_REFERENCE.md) |
| **Lost in docs?** | [Documentation Index](doc/DOCUMENTATION_INDEX.md) |

---

## 📋 What is Chatbot PSB?

**Chatbot PSB** is an intelligent conversational chatbot for **Penerimaan Santri Baru (PSB)** - Student Admission for Islamic Boarding School - using a hybrid NLP architecture.

### Key Features

✅ **Intent-Based Classification** - TF-IDF + Logistic Regression  
✅ **Double Guard Architecture** - Prevents hallucination  
✅ **Knowledge-Driven Responses** - All facts from curated knowledge base  
✅ **Modern NLP** - LLaMA 3.3 70B for natural language  
✅ **Production Ready** - Comprehensive logging, error handling, monitoring  
✅ **Easy Deployment** - Railway.app with one-click setup  

### Architecture Overview

```
User (Telegram) 
    ↓
Guard 1: Intent Classifier (Determines answer space)
    ↓
Knowledge Base (Facts only, no hallucination)
    ↓
Guard 2: Groq LLM (Natural language refinement)
    ↓
Database (Persistent logging & analytics)
    ↓
Response back to User
```

---

## 📚 Documentation Map

```
chatbot-psb/
├── doc/
│   ├── DOCUMENTATION_INDEX.md ← Start here to navigate
│   │
│   ├── QUICK_START.md ← Installation & setup (5 min)
│   ├── ARCHITECTURE.md ← System design & overview
│   ├── COMPONENTS.md ← Detailed component reference
│   ├── DATA_FLOW.md ← Visual diagrams & flows
│   │
│   ├── API_REFERENCE.md ← REST API documentation
│   ├── DEPLOYMENT_GUIDE.md ← Production deployment
│   ├── DEVELOPMENT_GUIDE.md ← Contributing & development
│   ├── TROUBLESHOOTING.md ← Problem solving
│   │
│   └── ... (other guides)
│
├── app.py ← FastAPI entry point
├── telegram_bot.py ← Telegram integration
├── response_router.py ← Core orchestration
├── intent_classifier.py ← Guard 1
├── groq_client.py ← Guard 2
├── database.py ← Data persistence
│
├── knowledge_base/ ← JSON facts files
├── models/ ← Pre-trained ML models
├── tests/ ← Test suite
└── notebooks/ ← Training notebooks
```

---

## 🎯 Getting Started

### For First-Time Users

1. **[Quick Start Guide](doc/QUICK_START.md)** (5 minutes)
   - Clone and install
   - Configure environment
   - Run locally
   - Test in Telegram

2. **[Architecture Guide](doc/ARCHITECTURE.md)** (10 minutes, optional)
   - Understand system design
   - Learn about Double Guard
   - See technology stack

### For Different Roles

| Role | Start Here |
|------|-----------|
| **Bot User** | Just use in Telegram! |
| **Administrator** | [Quick Start](doc/QUICK_START.md) |
| **Backend Developer** | [Architecture](doc/ARCHITECTURE.md) → [Development](doc/DEVELOPMENT_GUIDE.md) |
| **DevOps/SRE** | [Deployment Guide](doc/DEPLOYMENT_GUIDE.md) |
| **Data Scientist** | [Components](doc/COMPONENTS.md#4-intent-classifier) → [Notebooks](notebooks/) |
| **API Consumer** | [API Reference](doc/API_REFERENCE.md) |

---

## 🔧 Common Tasks

### Setup & Installation
```bash
# 1. Clone
git clone <repo>
cd chatbot-psb

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your credentials

# 5. Database
python init_database.py

# 6. Run
python app.py
```

**Full guide**: [Quick Start](doc/QUICK_START.md)

### Deploy to Production
```bash
# 1. Create Railway account
# 2. Connect GitHub repo
# 3. Link PostgreSQL
# 4. Set environment variables
# 5. Railway auto-deploys!
```

**Full guide**: [Deployment Guide](doc/DEPLOYMENT_GUIDE.md)

### Develop Features
```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit code, add tests

# 3. Run tests
pytest tests/ -v

# 4. Format code
black . && flake8 .

# 5. Commit & push
git commit -m "feat: description"
git push origin feature/my-feature
```

**Full guide**: [Development Guide](doc/DEVELOPMENT_GUIDE.md)

### Something Broken?
- Check: [Troubleshooting Guide](doc/TROUBLESHOOTING.md)
- Common issues with solutions
- Debug techniques
- FAQ section

---

## 📦 What's Included

### Core Features
- **Telegram Bot Integration** - Full support for Telegram Bot API
- **Intent Classification** - ML-powered context detection
- **Knowledge Base** - JSON-based facts management
- **LLM Integration** - Groq API for natural language
- **Database** - PostgreSQL for logging & analytics
- **Admin Tools** - Labeling interface, data export
- **Testing** - Comprehensive test suite (pytest)
- **Documentation** - Complete guides & API docs

### Technology Stack
- **Framework**: FastAPI (async Python web framework)
- **ML**: scikit-learn (TF-IDF + Logistic Regression)
- **LLM**: Groq API (LLaMA 3.3 70B)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API**: Telegram Bot API
- **Deployment**: Railway.app (recommended) or Docker

---

## 🏗️ System Architecture

### Double Guard Architecture

The system uses **two independent decision layers** to prevent hallucination:

**Guard 1: Intent Classifier**
- Classical ML for intent prediction
- Determines answer space
- Provides confidence score
- Runs first, always

**Guard 2: LLM Reasoning**
- Modern LLM for response refinement
- Can only refine language
- Cannot change intent
- Cannot add new facts
- Bounded by knowledge base

### Why Double Guard?

| Aspect | Guard 1 Only | Guard 2 Only | Double Guard |
|--------|-------------|------------|--------------|
| Intent Accuracy | ✅ Excellent | ❌ Poor | ✅ Excellent |
| Response Quality | ❌ Robotic | ✅ Natural | ✅ Natural |
| Hallucination Risk | ❌ Low | ⚠️ High | ✅ Very Low |

---

## 📖 Documentation Structure

### Quick References
- **[Quick Start Guide](doc/QUICK_START.md)** - Get running in 5 minutes
- **[Troubleshooting Guide](doc/TROUBLESHOOTING.md)** - Solve common issues
- **[Documentation Index](doc/DOCUMENTATION_INDEX.md)** - Navigate all docs

### Architecture & Design
- **[Architecture Guide](doc/ARCHITECTURE.md)** - Complete system design
- **[Components Reference](doc/COMPONENTS.md)** - Detailed API docs
- **[Data Flow Diagrams](doc/DATA_FLOW.md)** - Visual flows & diagrams

### Operational Guides
- **[API Reference](doc/API_REFERENCE.md)** - REST API documentation
- **[Deployment Guide](doc/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Development Guide](doc/DEVELOPMENT_GUIDE.md)** - Contributing guide

---

## 🚀 Getting Help

### Resources
- **Documentation**: Complete guides in `/doc` folder
- **Code Examples**: Throughout component guides
- **Tests**: Examples in `/tests` folder
- **Notebook**: Training example in `/notebooks`

### If You're Stuck
1. Check [Troubleshooting Guide](doc/TROUBLESHOOTING.md)
2. Review relevant component docs
3. Look at test files for examples
4. Check GitHub issues
5. Create detailed issue if needed

---

## 🎓 Learning Paths

### Path 1: "Just Get It Working" (15 min)
1. [Quick Start](doc/QUICK_START.md) - Setup
2. Test in Telegram
3. [Troubleshooting](doc/TROUBLESHOOTING.md) if issues

### Path 2: "Understand The System" (45 min)
1. [Architecture Guide](doc/ARCHITECTURE.md)
2. [Components Reference](doc/COMPONENTS.md)
3. [Data Flow Diagrams](doc/DATA_FLOW.md)
4. [Quick Start](doc/QUICK_START.md) - Hands-on

### Path 3: "Deploy To Production" (1 hour)
1. [Quick Start](doc/QUICK_START.md) - Local testing
2. [Architecture Guide](doc/ARCHITECTURE.md) - Deployment section
3. [Deployment Guide](doc/DEPLOYMENT_GUIDE.md)
4. Deploy to Railway

### Path 4: "Develop Features" (2+ hours)
1. [Quick Start](doc/QUICK_START.md)
2. [Architecture Guide](doc/ARCHITECTURE.md)
3. [Components Reference](doc/COMPONENTS.md)
4. [Development Guide](doc/DEVELOPMENT_GUIDE.md)
5. Start coding!

---

## 📊 System Statistics

- **Total Components**: 6 main Python modules
- **Lines of Code**: ~2,000+ (production code)
- **Test Coverage**: 80%+ (pytest)
- **Documentation Pages**: 8 comprehensive guides
- **External APIs**: 2 (Telegram, Groq)
- **Database Tables**: 1 main table (extendable)
- **Knowledge Base Files**: 11 JSON files
- **Training Data**: ~100+ examples per intent

---

## 🔗 Key Links

### Guides
- 📖 [Quick Start Guide](doc/QUICK_START.md)
- 🏗️ [Architecture Guide](doc/ARCHITECTURE.md)
- 🛠️ [Development Guide](doc/DEVELOPMENT_GUIDE.md)
- 🚀 [Deployment Guide](doc/DEPLOYMENT_GUIDE.md)
- 📡 [API Reference](doc/API_REFERENCE.md)
- 🔍 [Troubleshooting](doc/TROUBLESHOOTING.md)
- 📚 [Documentation Index](doc/DOCUMENTATION_INDEX.md)

### External
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Groq Console](https://console.groq.com)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Railway.app](https://railway.app)

---

## 📝 Project Status

- ✅ **Core System**: Production ready
- ✅ **Documentation**: Comprehensive
- ✅ **Testing**: Automated tests in place
- ✅ **Deployment**: Railway-ready
- ✅ **Monitoring**: Logging & analytics
- ⏳ **Future**: Additional features, more intents

---

## 📄 License & Attribution

- Project: Chatbot PSB
- Version: 1.0.0
- Type: Educational/Production
- Documentation: Complete
- Status: Active maintenance

---

## 🎉 Ready to Get Started?

### Next Steps

1. **New to the project?** → Start with [Quick Start Guide](doc/QUICK_START.md)
2. **Need to understand?** → Read [Architecture Guide](doc/ARCHITECTURE.md)
3. **Want to develop?** → Follow [Development Guide](doc/DEVELOPMENT_GUIDE.md)
4. **Deploying?** → Use [Deployment Guide](doc/DEPLOYMENT_GUIDE.md)
5. **Stuck?** → Check [Troubleshooting Guide](doc/TROUBLESHOOTING.md)

---

**Start with [Quick Start Guide](doc/QUICK_START.md) or [Documentation Index](doc/DOCUMENTATION_INDEX.md)**

---

*Last Updated: January 1, 2026*  
*For questions, see [Troubleshooting Guide](doc/TROUBLESHOOTING.md#faq)*
