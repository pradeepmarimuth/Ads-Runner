# 📦 Migration Guide - Project Restructuring

## Overview

The project has been restructured into a professional, scalable architecture with clear separation of concerns.

## What Changed

### Before (Monolithic)
```
├── app.py (1000+ lines)
├── models.py
├── templates/
├── static/
└── marketing.db
```

### After (Modular)
```
├── backend/          # Application core
├── api/              # API layer with routes & services
├── database/         # Database models & migrations
├── frontend/         # UI templates & static assets
├── deployment/       # Docker, Nginx, Gunicorn configs
├── tests/            # Test suite
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## File Mapping

### Old → New Location

| Old Path | New Path | Purpose |
|----------|----------|---------|
| `app.py` | `backend/app.py` | Main application (refactored) |
| `models.py` | `database/models.py` | Database models |
| `templates/*` | `frontend/templates/*` | HTML templates |
| `static/js/*` | `frontend/static/js/*` | JavaScript files |
| `static/uploads/*` | `frontend/static/uploads/*` | User uploads |
| `marketing.db` | `database/marketing.db` | SQLite database |
| `requirements.txt` | `backend/requirements.txt` | Python dependencies |
| N/A | `backend/config.py` | Configuration (NEW) |
| N/A | `api/services/ollama_service.py` | Ollama service (NEW) |
| N/A | `api/middleware/auth.py` | Auth middleware (NEW) |

## Import Changes

### Before
```python
from models import db, User, Campaign
from app import login_required
```

### After
```python
from database.models import db, User, Campaign
from api.middleware.auth import login_required
from api.services.ollama_service import ollama_service
```

## Configuration Changes

### Before
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketing.db'
app.config['SECRET_KEY'] = 'hardcoded-secret'
```

### After
```python
from backend.config import get_config

config = get_config()
app.config.from_object(config)
```

## Running the Application

### Before
```bash
python app.py
```

### After
```bash
# Development
python backend/app.py

# Production with Gunicorn
gunicorn -c deployment/gunicorn/gunicorn_config.py backend.wsgi:application

# Docker
docker-compose up
```

## Benefits of New Structure

### 1. **Separation of Concerns**
- Backend logic separate from API routes
- Database models in dedicated package
- Frontend assets organized separately

### 2. **Scalability**
- Easy to add new API routes
- Modular services can be scaled independently
- Clear boundaries for microservices migration

### 3. **Maintainability**
- Smaller, focused files instead of one large app.py
- Easier to locate and modify specific functionality
- Better code organization

### 4. **Testability**
- Dedicated tests/ directory
- Can test services independently
- Mock external dependencies easily

### 5. **Deployment Ready**
- Docker configuration included
- Nginx reverse proxy setup
- Gunicorn WSGI configuration
- Environment-based configuration

## Migration Steps

If you have an existing installation:

### Step 1: Backup Database
```bash
cp marketing.db marketing.db.backup
```

### Step 2: Update Git
```bash
git pull origin main
```

### Step 3: Reinstall Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Update Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### Step 5: Move Database
```bash
# If you have an existing database
cp marketing.db database/marketing.db
```

### Step 6: Test the Application
```bash
python backend/app.py
```

## Environment Variables

Create a `.env` file:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///database/marketing.db

# Ollama
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=90

# OpenAI (Optional)
OPENAI_API_KEY=your-key-here
```

## API Changes

### Endpoints Remain the Same
All API endpoints remain unchanged:
- `/api/ai-chat`
- `/api/generate-caption`
- `/api/campaigns`
- etc.

### Internal Structure Changed
The implementation is now modular:
```
/api/ai-chat → api/routes/ai.py → api/services/ollama_service.py
```

## Testing After Migration

### 1. Test Ollama Integration
```bash
python tests/test_ollama.py
```

### 2. Test API Endpoints
```bash
python tests/test_api.py
```

### 3. Test Detailed Responses
```bash
python tests/test_detailed_responses.py
```

### 4. Access the Application
```
http://127.0.0.1:5000
```

## Troubleshooting

### Issue: Import Errors
```
ModuleNotFoundError: No module named 'database'
```

**Solution:** Make sure you're running from the project root:
```bash
cd /path/to/marketing-ai-platform
python backend/app.py
```

### Issue: Database Not Found
```
OperationalError: unable to open database file
```

**Solution:** Update database path in config:
```python
# backend/config.py
DB_PATH = os.path.join(BASE_DIR, 'database', 'marketing.db')
```

### Issue: Templates Not Found
```
TemplateNotFound: ai.html
```

**Solution:** Update Flask template folder:
```python
app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
```

## Rollback Plan

If you need to rollback:

### Step 1: Restore Old Files
```bash
git checkout previous-version
```

### Step 2: Restore Database
```bash
cp marketing.db.backup marketing.db
```

### Step 3: Run Old Version
```bash
python app.py
```

## New Features in Restructured Version

### 1. Configuration Management
- Environment-based configuration
- Separate dev/production settings
- Easy to customize per environment

### 2. Service Layer
- Ollama service encapsulates AI logic
- Easy to swap AI providers
- Testable in isolation

### 3. Middleware
- Reusable auth decorators
- Request validation
- Error handling

### 4. Deployment Ready
- Docker support
- Nginx configuration
- Gunicorn WSGI
- Production-grade setup

## Best Practices

### 1. Always Use Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Keep .env Secure
```bash
# Never commit .env to git
echo ".env" >> .gitignore
```

### 3. Use Configuration Objects
```python
from backend.config import get_config
config = get_config('production')
```

### 4. Follow Import Conventions
```python
# Absolute imports from project root
from database.models import User
from api.services.ollama_service import ollama_service
```

## Support

If you encounter issues during migration:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
3. Open an issue on GitHub
4. Contact support

## Next Steps

After successful migration:

1. ✅ Test all features
2. ✅ Update custom code to use new imports
3. ✅ Configure environment variables
4. ✅ Setup deployment (Docker/Nginx)
5. ✅ Run production tests
6. ✅ Deploy to production

---

**Migration completed! Your application is now production-ready with a professional structure.**
