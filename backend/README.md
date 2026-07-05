# Backend Application

## Overview

This is the refactored backend application with a modular, production-ready structure.

## Structure

```
backend/
├── app.py          # Main application factory
├── config.py       # Configuration management
├── wsgi.py         # WSGI entry point for production
└── README.md       # This file
```

## Running the Application

### Development Mode

```bash
python backend/app.py
```

### Production Mode (with Gunicorn)

```bash
gunicorn -c deployment/gunicorn/gunicorn_config.py backend.wsgi:application
```

### Docker

```bash
docker-compose -f deployment/docker/docker-compose.yml up
```

## Features

- **Modular Architecture**: Clear separation of concerns with blueprints
- **Configuration Management**: Environment-based configuration
- **Database Integration**: SQLAlchemy ORM with migrations
- **AI Integration**: Ollama service for intelligent features
- **Authentication**: Secure login/logout with session management
- **RESTful API**: Well-organized API routes

## API Routes

All API routes are organized in `api/routes/`:

- `auth.py` - Authentication (login, signup, logout)
- `views.py` - HTML page rendering
- `profile.py` - User profile management
- `posts.py` - Social feed posts, likes, comments
- `network.py` - User connections and networking
- `messages.py` - Direct messaging
- `campaigns.py` - Campaign management and analytics
- `ai.py` - AI features (captions, hashtags, chat, link analysis)
- `admin.py` - Admin dashboard

## Configuration

Configuration is managed through environment variables and the `backend/config.py` file.

Create a `.env` file in the project root:

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=sqlite:///database/marketing.db

# Ollama
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=90

# OpenAI (Optional fallback)
OPENAI_API_KEY=your-key-here
```

## Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

Main dependencies:
- Flask
- SQLAlchemy
- Requests (for Ollama API)
- Werkzeug (for security)
- Gunicorn (for production)

## Development

### Adding New Routes

1. Create a new file in `api/routes/`
2. Define a Blueprint
3. Register the blueprint in `backend/app.py`

Example:

```python
# api/routes/my_feature.py
from flask import Blueprint, jsonify

my_feature_bp = Blueprint('my_feature', __name__, url_prefix='/api')

@my_feature_bp.route('/my-endpoint')
def my_endpoint():
    return jsonify({'message': 'Hello'}), 200
```

```python
# backend/app.py
from api.routes.my_feature import my_feature_bp

def create_app():
    # ...
    app.register_blueprint(my_feature_bp)
    # ...
```

### Adding New Services

1. Create a new file in `api/services/`
2. Implement your service class
3. Export it in `api/services/__init__.py`

## Testing

Run tests:

```bash
python tests/test_ollama.py
python tests/test_detailed_responses.py
```

## Troubleshooting

### Import Errors

Make sure you're running from the project root:

```bash
cd /path/to/project
python backend/app.py
```

### Database Not Found

Check the database path in `backend/config.py` and ensure the database directory exists.

### Templates Not Found

Verify the template folder path in `backend/app.py`:

```python
template_folder='../frontend/templates'
```

## Migration from Old Structure

If migrating from the old monolithic `app.py`:

1. The database remains compatible
2. All API endpoints remain unchanged
3. Update any external scripts to use `backend/app.py` instead of `app.py`

See `docs/MIGRATION_GUIDE.md` for detailed migration instructions.
