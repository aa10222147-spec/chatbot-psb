# 🛠️ Chatbot PSB - Development Guide

Complete guide for developers contributing to the Chatbot PSB project.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Style & Standards](#code-style--standards)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Adding Features](#adding-features)
7. [Debugging](#debugging)
8. [Common Tasks](#common-tasks)

---

## Development Setup

### Prerequisites

- Python 3.10+ (3.11 recommended; `runtime.txt` = python-3.11)
- PostgreSQL 13+ untuk logging/admin tools (`database.py` hanya PostgreSQL, bukan SQLite)
- Git
- IDE (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd chatbot-psb

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Edit .env with your values
# TELEGRAM_BOT_TOKEN=test_token_for_dev
# GROQ_API_KEY=test_key_for_dev
# DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot_psb_dev
# ENVIRONMENT=development
# LOG_LEVEL=DEBUG

# Initialize database
python init_database.py

# Run tests to verify setup
pytest tests/ -v
```

### IDE Setup (VS Code)

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=100"],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

---

## Project Structure

```
chatbot-psb/
├── doc/                          # Documentation
│   ├── ARCHITECTURE.md           # System design
│   ├── COMPONENTS.md             # Component reference
│   ├── QUICK_START.md            # Setup guide
│   ├── DEPLOYMENT_GUIDE.md       # Production deployment
│   ├── API_REFERENCE.md          # REST API docs
│   ├── DEVELOPMENT_GUIDE.md      # This file
│   └── ...other docs
│
├── app.py                        # FastAPI entry point (webhook mode)
├── app_polling.py                # Polling mode untuk dev lokal
├── telegram_bot.py               # Telegram integration
├── response_router.py            # Core orchestration
├── intent_classifier.py          # Guard 1 (NLP)
├── groq_client.py                # Guard 2 (LLM)
├── database.py                   # Data persistence
├── init_database.py              # DB setup
├── export_training_data.py       # Data export
├── admin_labeling.py             # Admin interface
├── utils/
│   └── prompt_builder.py         # Prompt spec (tidak terhubung ke pipeline)
│
├── tests/                        # Unit & integration tests
│   ├── test_intent_classifier.py
│   ├── test_groq_client.py
│   ├── test_response_router.py
│   ├── test_database.py
│   ├── test_telegram_bot.py
│   ├── test_integration.py
│   ├── test_knowledge_base.py
│   └── conftest.py               # Pytest fixtures
│
├── knowledge_base/               # Curated knowledge base
│   ├── biaya_pendidikan.json
│   ├── info_pendaftaran.json
│   ├── syarat_pendaftaran.json
│   └── ... (11 JSON files)
│
├── models/                       # Pre-trained ML models (bundle v2)
│   ├── vectorizer_2.pkl
│   ├── lr_intent_model_2.pkl
│   ├── label_encoder_2.pkl
│   └── v1/                       # Fallback bundle v1
│
├── data/                         # Training data
│   ├── intents_v2.csv            # Training examples (~1.066 baris)
│   └── exports/                  # Data exports
│
├── notebooks/                    # Jupyter notebooks
│   └── intent_classifier_training_executed_v2.ipynb
│
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── Procfile                      # Deployment config
├── runtime.txt                   # Python version
├── railway.json                  # Railway deployment config
├── .env.example                  # Environment template
└── README.md                     # Project overview
```

---

## Code Style & Standards

### Python Code Style

We follow **PEP 8** with Black formatting.

#### Formatting

```bash
# Format all Python files
black .

# Check formatting
black --check .

# Format specific file
black app.py
```

#### Linting

```bash
# Check for style violations
flake8 .

# Check specific file
flake8 app.py

# Configuration in setup.cfg
[flake8]
max-line-length = 100
ignore = E203, E266, E501, W503
```

#### Type Hints

Always use type hints:

```python
# ✅ GOOD
def process_question(
    question: str,
    user_id: str = "anonymous",
    platform: str = "telegram"
) -> ResponseResult:
    """Process user question through chatbot pipeline."""
    pass

# ❌ BAD
def process_question(question, user_id="anonymous", platform="telegram"):
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def predict(self, question: str) -> IntentPrediction:
    """Predict intent from user question.
    
    Uses TF-IDF vectorization and Logistic Regression to classify
    the intent of the user's question. Returns confidence score and
    all probability scores for each intent.
    
    Args:
        question: User's question text
        
    Returns:
        IntentPrediction: Contains:
            - intent: Predicted intent label
            - confidence: Confidence score (0-1)
            - all_probabilities: Dict of all intent probabilities
            - is_confident: True if confidence >= threshold
            
    Raises:
        ValueError: If question is empty or models not loaded
        
    Examples:
        >>> classifier = IntentClassifier()
        >>> result = classifier.predict("Berapa biaya?")
        >>> print(result.intent)
        'biaya_pendidikan'
    """
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ GOOD
logger.info(f"Processing question from user {user_id}: {question[:50]}...")
logger.error(f"Classification failed: {exception}", exc_info=True)

# ❌ BAD
print("Question processed")  # Don't use print
logger.info("Processing")    # Too vague
```

#### Comments

```python
# ✅ GOOD: Explain WHY, not WHAT
# Skip low-confidence predictions to avoid incorrect answers
if confidence < threshold:
    return fallback_response

# ❌ BAD: State obvious facts
# This sets x to 5
x = 5

# ❌ BAD: Don't leave commented code
# result = old_function()
```

---

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/add-new-intent

# 2. Make changes
# Edit files, add code, etc.

# 3. Run tests locally
pytest tests/ -v

# 4. Format code
black .
flake8 .

# 5. Commit changes
git add .
git commit -m "feat: add new intent support"

# 6. Push to GitHub
git push origin feature/add-new-intent

# 7. Create Pull Request
# On GitHub, create PR with:
#   - Clear title: "Add support for new intent"
#   - Description: What, why, how
#   - Tests: Link to test file
#   - Screenshots: If UI-related
```

### Bug Fix Workflow

```bash
# 1. Create bug fix branch
git checkout -b fix/classifier-error

# 2. Write test that reproduces bug
# In tests/test_intent_classifier.py
def test_classifier_handles_empty_input():
    classifier = IntentClassifier()
    # Currently fails with ValueError
    result = classifier.predict("")
    assert result.intent == "unknown"

# 3. Run test to confirm it fails
pytest tests/test_intent_classifier.py::test_classifier_handles_empty_input -v

# 4. Fix the bug
# Edit intent_classifier.py

# 5. Run test to confirm it passes
pytest tests/test_intent_classifier.py::test_classifier_handles_empty_input -v

# 6. Run all tests to check for regressions
pytest tests/ -v

# 7. Commit and push
git add .
git commit -m "fix: handle empty input in classifier"
git push origin fix/classifier-error
```

### Commit Message Format

Follow conventional commits:

```
type(scope): subject

body

footer

---

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation
  test:     Test file changes
  refactor: Code refactoring
  perf:     Performance improvement
  ci:       CI/CD changes
  chore:    Dependency updates

Scope: Component (classifier, groq, router, etc.)

Subject: What was done (imperative, lowercase)

Body: Why it was done (if not obvious)

Footer: Breaking changes, Closes #123

---

Example:
feat(classifier): add support for low-confidence fallback

When classifier confidence is below threshold, system now
uses knowledge base response instead of rejecting.

Closes #42
```

---

## Testing

### Test Structure

```python
# tests/test_intent_classifier.py

import pytest
from intent_classifier import IntentClassifier, IntentPrediction

class TestIntentClassifier:
    """Tests for IntentClassifier"""
    
    @pytest.fixture
    def classifier(self):
        """Setup classifier for each test"""
        return IntentClassifier()
    
    def test_predict_high_confidence(self, classifier):
        """Test prediction with high confidence"""
        result = classifier.predict("Berapa biaya pendaftaran?")
        
        assert isinstance(result, IntentPrediction)
        assert result.intent == "biaya_pendidikan"
        assert result.confidence > 0.7
        assert result.is_confident is True
    
    def test_predict_low_confidence(self, classifier):
        """Test prediction with low confidence"""
        result = classifier.predict("xyz abc 123 random text")
        
        assert isinstance(result, IntentPrediction)
        assert result.confidence < 0.5
        assert result.is_confident is False
    
    def test_all_probabilities_sum_to_one(self, classifier):
        """Test that probabilities sum to 1"""
        result = classifier.predict("Pertanyaan apapun")
        
        total = sum(result.all_probabilities.values())
        assert abs(total - 1.0) < 0.01
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_intent_classifier.py -v

# Run specific test
pytest tests/test_intent_classifier.py::TestIntentClassifier::test_predict_high_confidence -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run only fast tests (no external APIs)
pytest tests/ -m "not external"

# Run with output
pytest tests/ -v -s  # -s shows print statements
```

### Coverage Goals

Target minimum 80% code coverage:

```bash
# Check coverage
pytest tests/ --cov=. --cov-report=term-missing

# Expected output shows:
# TOTAL    85%  (lines not covered marked with "!")
```

### Writing Tests

#### Unit Tests

Test single function/method in isolation:

```python
def test_intent_classifier_predict():
    """Unit test: intent classifier prediction"""
    classifier = IntentClassifier()
    result = classifier.predict("Berapa biaya?")
    
    assert result.intent is not None
    assert 0 <= result.confidence <= 1
```

#### Integration Tests

Test multiple components working together:

```python
@pytest.mark.integration
def test_response_router_full_pipeline():
    """Integration test: full question processing"""
    router = ResponseRouter()
    result = router.process_question(
        question="Berapa biaya pendaftaran?",
        user_id="test_user",
        platform="test"
    )
    
    assert result.success is True
    assert result.message is not None
    assert result.intent == "biaya_pendidikan"
```

#### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('groq_client.requests.post')
def test_groq_api_timeout(mock_post):
    """Test handling of Groq API timeout"""
    mock_post.side_effect = requests.exceptions.Timeout()
    
    client = GroqClient()
    # Should fallback gracefully
    result = client.generate_response(...)
    
    assert result.success is False
```

---

## Debugging

### Enable Debug Logging

```bash
# In .env or environment
LOG_LEVEL=DEBUG

# Then run:
python app.py

# You'll see detailed logs for all operations
```

### Debug Specific Component

```python
# Interactive debugging
from intent_classifier import get_intent_classifier

classifier = get_intent_classifier()

# Check available intents
print(classifier.get_all_intents())

# Check probabilities for a question
result = classifier.predict("Pertanyaan test")
print(f"Intent: {result.intent}")
print(f"Confidence: {result.confidence}")
print(f"All probs: {result.all_probabilities}")

# Check model accuracy
from data.intents_v2.csv import load_test_data
test_data = load_test_data()
accuracy = classifier.evaluate(test_data)
print(f"Accuracy: {accuracy:.2%}")
```

### Debug Response Router

```python
from response_router import ResponseRouter

router = ResponseRouter()

# Process with detailed output
result = router.process_question(
    question="Berapa biaya?",
    user_id="debug_user"
)

print(f"Success: {result.success}")
print(f"Message: {result.message}")
print(f"Intent: {result.intent}")
print(f"Confidence: {result.confidence}")
print(f"KB Used: {result.knowledge_base_used}")
print(f"LLM Used: {result.llm_used}")
print(f"Error: {result.error}")
```

### Debug Database

```python
from database import SessionLocal, UserQuestion

session = SessionLocal()

# View all logged questions
for q in session.query(UserQuestion).order_by(UserQuestion.created_at.desc()).limit(10):
    print(f"{q.created_at}: {q.question_text} -> {q.predicted_intent} (conf: {q.confidence_score})")

# Check specific user
user_q = session.query(UserQuestion).filter_by(user_id="123456789").all()
print(f"User has {len(user_q)} questions")

# Analytics
from sqlalchemy import func
intent_dist = session.query(
    UserQuestion.predicted_intent,
    func.count(UserQuestion.id)
).group_by(UserQuestion.predicted_intent).all()

for intent, count in intent_dist:
    print(f"{intent}: {count}")

session.close()
```

### Debugging with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app:app", "--reload"],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "justMyCode": false
    }
  ]
}
```

Then set breakpoints and use Debug menu.

---

## Common Tasks

### Train New Intent Classifier

```bash
# 1. Add training examples to data/intents_v2.csv
#    Format: question,intent
nano data/intents_v2.csv

# 2. Open and run training notebook
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb

# 3. Review results
# - Check accuracy metrics
# - Check confusion matrix
# - Review misclassified examples

# 4. If satisfied, models are saved to models/

# 5. Commit changes
git add data/intents_v2.csv
git add models/
git commit -m "refactor: retrain intent classifier with new examples"

# 6. Deploy to production
# Push to GitHub, Railway auto-deploys
git push origin main
```

### Add New Knowledge Base Topic

```bash
# 1. Create new JSON file in knowledge_base/
cat > knowledge_base/new_topic.json << 'EOF'
{
  "intent": "new_topic",
  "description": "Information about new topic",
  "items": [
    {
      "title": "First item",
      "content": "Description here"
    },
    {
      "title": "Second item",
      "content": "More info"
    }
  ]
}
EOF

# 2. Add training examples to data/intents_v2.csv
echo "Sample question about new topic,new_topic" >> data/intents_v2.csv

# 3. Retrain classifier
jupyter notebook notebooks/intent_classifier_training_executed_v2.ipynb

# 4. Test it works
python -c "
from intent_classifier import get_intent_classifier
classifier = get_intent_classifier()
result = classifier.predict('Sample question about new topic')
print(f'Intent: {result.intent}')
print(f'Confidence: {result.confidence}')
"

# 5. Commit and deploy
git add knowledge_base/new_topic.json data/intents_v2.csv models/
git commit -m "feat: add new knowledge base topic"
git push origin main
```

### Export and Analyze Data

```bash
# Export training data with feedback
python export_training_data.py

# This creates files:
# - data/exports/training_data_latest.csv
# - data/exports/training_data_reviewed_latest.csv
# - data/exports/all_feedback_TIMESTAMP.csv

# Analyze in Python
import pandas as pd

df = pd.read_csv('data/exports/training_data_latest.csv')

# Distribution of intents
print(df['intent'].value_counts())

# Confidence analysis
print(f"Average confidence: {df['confidence'].mean():.2%}")
print(f"Low confidence (< 0.5): {(df['confidence'] < 0.5).sum()}")
```

### Admin Labeling Interface

```bash
# Label user questions for training
python admin_labeling.py

# Interface allows:
# 1. View logged user questions
# 2. Correct/confirm predicted intent
# 3. Export labeled data
# 4. Review statistics
```

---

## Performance Optimization

### Profile Code

```python
import cProfile
import pstats

# Profile intent classifier
profiler = cProfile.Profile()
profiler.enable()

classifier.predict("Question text")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def predict_cached(question: str) -> IntentPrediction:
    """Cache intent predictions"""
    return classifier.predict(question)
```

### Batch Processing

```python
# Process multiple questions (predict() satu per satu)
questions = [
    "Question 1?",
    "Question 2?",
    "Question 3?"
]

# predict_batch() tidak ada di kode; iterasi manual:
results = [classifier.predict(q) for q in questions]
```

---

## Documentation Guidelines

- Keep README updated with major changes
- Add docstrings to all public functions
- Update architecture docs for major changes
- Keep CHANGELOG.md updated
- Add examples to API docs

---

## Release Process

```bash
# 1. Update version
# In app.py, update version = "1.1.0"

# 2. Update CHANGELOG.md
# Document all changes

# 3. Run full test suite
pytest tests/ --cov=. -v

# 4. Create release branch
git checkout -b release/1.1.0

# 5. Commit
git add .
git commit -m "chore: release version 1.1.0"

# 6. Create git tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# 7. Push and create PR
git push origin release/1.1.0

# 8. Merge to main
# Via GitHub PR

# 9. Push tag
git push origin v1.1.0

# 10. Railway auto-deploys on main push
```

---

## Getting Help

- Check documentation in `/doc`
- Review existing issues on GitHub
- Check test files for examples
- Ask in team Slack/Discord
- Create detailed GitHub issue if stuck

---

**Happy coding! 🚀**
