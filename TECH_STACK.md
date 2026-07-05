# 🛠️ Technology Stack

## Complete Tech Stack Overview

This document provides a comprehensive overview of all technologies, frameworks, libraries, and tools used in the Marketing AI Platform.

---

## 📋 Table of Contents

1. [Backend Technologies](#backend-technologies)
2. [Frontend Technologies](#frontend-technologies)
3. [Database](#database)
4. [AI/ML Technologies](#aiml-technologies)
5. [DevOps & Deployment](#devops--deployment)
6. [Development Tools](#development-tools)
7. [External Services](#external-services)

---

## 🔙 Backend Technologies

### Core Framework
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Python** | 3.8+ | Programming language | [python.org](https://www.python.org/) |
| **Flask** | 3.0+ | Web framework | [flask.palletsprojects.com](https://flask.palletsprojects.com/) |
| **Flask Blueprints** | Built-in | Modular routing | [Flask Blueprints Docs](https://flask.palletsprojects.com/blueprints/) |

### Database ORM
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **SQLAlchemy** | 2.0+ | ORM (Object-Relational Mapping) | [sqlalchemy.org](https://www.sqlalchemy.org/) |
| **Flask-SQLAlchemy** | 3.0+ | Flask integration for SQLAlchemy | [flask-sqlalchemy.palletsprojects.com](https://flask-sqlalchemy.palletsprojects.com/) |

### Authentication & Security
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Werkzeug** | 3.0+ | Password hashing & security utilities | [werkzeug.palletsprojects.com](https://werkzeug.palletsprojects.com/) |
| **Flask Sessions** | Built-in | Session management | [Flask Sessions](https://flask.palletsprojects.com/sessions/) |

### HTTP Client
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Requests** | 2.31+ | HTTP library for API calls | [requests.readthedocs.io](https://requests.readthedocs.io/) |

---

## 🎨 Frontend Technologies

### Template Engine
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Jinja2** | 3.1+ | HTML templating | [jinja.palletsprojects.com](https://jinja.palletsprojects.com/) |

### JavaScript
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Vanilla JavaScript** | ES6+ | Frontend logic | [MDN JavaScript](https://developer.mozilla.org/docs/Web/JavaScript) |
| **Fetch API** | Built-in | AJAX requests | [MDN Fetch API](https://developer.mozilla.org/docs/Web/API/Fetch_API) |

### CSS Framework
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Tailwind CSS** | 3.4+ | Utility-first CSS framework | [tailwindcss.com](https://tailwindcss.com/) |

### UI Components
| Technology | Purpose |
|------------|---------|
| Custom JavaScript modules | Dashboard, feed, messaging, campaigns, AI workspace |
| Responsive design | Mobile-first approach |
| Real-time updates | AJAX-based dynamic content |

---

## 💾 Database

### Primary Database
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **SQLite** | 3.x | Development database | [sqlite.org](https://www.sqlite.org/) |
| **PostgreSQL** | 14+ | Production database (optional) | [postgresql.org](https://www.postgresql.org/) |

### Database Models
```python
- User (authentication, profiles)
- Post (social feed content)
- PostLike (post likes)
- Comment (post comments)
- Message (direct messaging)
- Connection (user networking)
- Campaign (marketing campaigns)
- CampaignLog (audit logs)
```

### Schema Management
| Technology | Purpose |
|------------|---------|
| **SQLAlchemy Migrations** | Database versioning |
| **Alembic** (optional) | Advanced migrations |

---

## 🤖 AI/ML Technologies

### Local AI
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Ollama** | Latest | Local LLM inference engine | [ollama.ai](https://ollama.ai/) |
| **Qwen 2.5:0.5b** | 0.5b | Small, fast language model | [Qwen Models](https://github.com/QwenLM/Qwen) |

### Supported Models
- **qwen2.5:0.5b** (Default) - Fast, lightweight
- **tinyllama** - Tiny model for testing
- **llama3.2:1b** - Small Llama model
- **llama3.2:3b** - Larger Llama model

### Cloud AI (Fallback)
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **OpenAI API** | Latest | Cloud LLM (optional fallback) | [platform.openai.com](https://platform.openai.com/) |
| **GPT-4o-mini** | Latest | Efficient GPT model | OpenAI Docs |

### AI Features
- **Text Generation** - Captions, hashtags, content
- **Chat** - Context-aware conversational AI (400-900 word responses)
- **Analysis** - Ad link analysis and insights
- **JSON Mode** - Structured output generation

---

## 🚀 DevOps & Deployment

### Containerization
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Docker** | 20.10+ | Containerization | [docker.com](https://www.docker.com/) |
| **Docker Compose** | 2.0+ | Multi-container orchestration | [Docker Compose Docs](https://docs.docker.com/compose/) |

### Web Server
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Nginx** | 1.24+ | Reverse proxy & static files | [nginx.org](https://nginx.org/) |

### WSGI Server
| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Gunicorn** | 21.0+ | Production WSGI server | [gunicorn.org](https://gunicorn.org/) |

### Configuration
```yaml
Docker:
  - Python 3.11 Alpine base image
  - Multi-stage build
  - Production-ready container

Nginx:
  - Reverse proxy configuration
  - Static file serving
  - Load balancing ready

Gunicorn:
  - 4 worker processes
  - Async worker class
  - Auto-restart on failure
```

---

## 🛠️ Development Tools

### Version Control
| Technology | Purpose | Documentation |
|------------|---------|---------------|
| **Git** | Version control | [git-scm.com](https://git-scm.com/) |
| **GitHub** | Code hosting | [github.com](https://github.com/) |

### Package Management
| Technology | Purpose | Documentation |
|------------|---------|---------------|
| **pip** | Python package installer | [pip.pypa.io](https://pip.pypa.io/) |
| **virtualenv/venv** | Virtual environments | [Python venv](https://docs.python.org/3/library/venv.html) |
| **requirements.txt** | Dependency specification | Standard |

### Code Quality
| Technology | Purpose |
|------------|---------|
| **Python Type Hints** | Type checking |
| **Docstrings** | Code documentation |
| **PEP 8** | Code style guide |

---

## 🔌 External Services

### Required Services
| Service | Purpose | Hosting |
|---------|---------|---------|
| **Ollama** | Local AI inference | localhost:11434 |

### Optional Services
| Service | Purpose | Setup Required |
|---------|---------|----------------|
| **OpenAI API** | Cloud AI fallback | API key needed |

---

## 📦 Complete Dependencies List

### Core Dependencies
```txt
Flask==3.0.0              # Web framework
Flask-SQLAlchemy==3.1.1   # Database ORM
SQLAlchemy==2.0.23        # SQL toolkit
Werkzeug==3.0.1           # WSGI utilities
requests==2.31.0          # HTTP library
```

### Optional Dependencies
```txt
gunicorn==21.2.0          # Production server
psycopg2-binary==2.9.9    # PostgreSQL adapter
python-dotenv==1.0.0      # Environment variables
openai==1.3.0             # OpenAI API (optional)
```

### Development Dependencies
```txt
pytest==7.4.3             # Testing framework
pytest-flask==1.3.0       # Flask testing
black==23.12.0            # Code formatter
flake8==6.1.0             # Linter
```

---

## 🏗️ Architecture Stack

### Application Architecture
```
┌─────────────────────────────────────┐
│     Presentation Layer (Frontend)    │
│  Jinja2 Templates + JavaScript       │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│    Application Layer (Backend)       │
│  Flask + Blueprints + Services       │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│       Data Layer (Database)          │
│    SQLAlchemy ORM + SQLite/PG        │
└─────────────────────────────────────┘
```

### Deployment Stack
```
┌─────────────────────────────────────┐
│          Nginx (Port 80)             │
│       Reverse Proxy + Static         │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Gunicorn (Port 5000)            │
│         WSGI Server                  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      Flask Application               │
│     Python Backend Logic             │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│        SQLite/PostgreSQL             │
│         Data Storage                 │
└─────────────────────────────────────┘
```

---

## 🔧 System Requirements

### Development Environment
```
Operating System: Windows, macOS, Linux
Python: 3.8 or higher
Ollama: Latest version (for AI features)
RAM: 4GB minimum, 8GB recommended
Storage: 2GB free space
```

### Production Environment
```
Operating System: Linux (Ubuntu 20.04+)
Python: 3.10+
RAM: 8GB minimum, 16GB recommended
Storage: 20GB free space
Docker: 20.10+
Nginx: 1.20+
```

---

## 📊 Technology Choices - Why?

### Why Flask?
- ✅ Lightweight and flexible
- ✅ Easy to learn and use
- ✅ Extensive ecosystem
- ✅ Perfect for small to medium projects
- ✅ Blueprint support for modularity

### Why SQLAlchemy?
- ✅ Powerful ORM
- ✅ Database agnostic
- ✅ Migration support
- ✅ Excellent documentation
- ✅ Production-ready

### Why Ollama?
- ✅ Local AI inference (privacy)
- ✅ No API costs
- ✅ Fast responses
- ✅ Multiple model support
- ✅ Easy to use

### Why Tailwind CSS?
- ✅ Utility-first approach
- ✅ Fast development
- ✅ Responsive by default
- ✅ Small production bundle
- ✅ Highly customizable

### Why Docker?
- ✅ Consistent environments
- ✅ Easy deployment
- ✅ Isolation
- ✅ Scalability
- ✅ Industry standard

---

## 🔄 Technology Alternatives

| Current | Alternative | Reason for Choice |
|---------|-------------|-------------------|
| Flask | Django | Flask is lighter, more flexible |
| SQLite | PostgreSQL | SQLite for dev, PostgreSQL for prod |
| Ollama | OpenAI API | Ollama is local, no API costs |
| Jinja2 | React | Server-side rendering is simpler |
| Gunicorn | uWSGI | Gunicorn is easier to configure |

---

## 📈 Scalability Considerations

### Current Stack Scaling
| Component | Scaling Strategy |
|-----------|------------------|
| **Flask App** | Horizontal scaling with load balancer |
| **Database** | PostgreSQL with read replicas |
| **Static Files** | CDN (CloudFront, Cloudflare) |
| **Ollama** | Multiple instances with load balancing |
| **Sessions** | Redis for distributed sessions |

### Future Enhancements
- **Message Queue**: Celery + Redis
- **Caching**: Redis/Memcached
- **Search**: Elasticsearch
- **Real-time**: WebSockets (Socket.IO)
- **Monitoring**: Prometheus + Grafana

---

## 🔒 Security Stack

### Security Features
| Feature | Implementation |
|---------|----------------|
| **Password Hashing** | Werkzeug (PBKDF2) |
| **Session Security** | Secure cookies, httponly |
| **SQL Injection** | SQLAlchemy parameterization |
| **XSS Protection** | Jinja2 auto-escaping |
| **CSRF Protection** | Flask-WTF (optional) |
| **File Upload Security** | Extension validation, secure filenames |

---

## 📚 Learning Resources

### Flask
- [Official Flask Tutorial](https://flask.palletsprojects.com/tutorial/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### SQLAlchemy
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/tutorial/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/orm/tutorial.html)

### Ollama
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Python Library](https://github.com/ollama/ollama-python)

### Docker
- [Docker Get Started](https://docs.docker.com/get-started/)
- [Docker Compose Tutorial](https://docs.docker.com/compose/gettingstarted/)

---

## 🎯 Tech Stack Summary

### Programming Languages
- **Python 3.8+** (Backend)
- **JavaScript ES6+** (Frontend)
- **HTML5** (Templates)
- **CSS3** (Styling)

### Frameworks & Libraries
- **Flask 3.0+** (Web framework)
- **SQLAlchemy 2.0+** (ORM)
- **Jinja2 3.1+** (Templating)
- **Tailwind CSS 3.4+** (CSS framework)

### AI & ML
- **Ollama** (Local LLM)
- **Qwen 2.5** (Language model)
- **OpenAI API** (Fallback)

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production)

### Deployment
- **Docker** (Containerization)
- **Nginx** (Web server)
- **Gunicorn** (WSGI server)

### Tools
- **Git** (Version control)
- **pip** (Package management)
- **pytest** (Testing)

---

## 📊 Technology Maturity

| Technology | Maturity | Community | Production Ready |
|------------|----------|-----------|------------------|
| Python | ⭐⭐⭐⭐⭐ | Huge | ✅ Yes |
| Flask | ⭐⭐⭐⭐⭐ | Large | ✅ Yes |
| SQLAlchemy | ⭐⭐⭐⭐⭐ | Large | ✅ Yes |
| Ollama | ⭐⭐⭐⭐ | Growing | ✅ Yes |
| Docker | ⭐⭐⭐⭐⭐ | Huge | ✅ Yes |
| Tailwind | ⭐⭐⭐⭐⭐ | Large | ✅ Yes |

---

## ✅ Conclusion

This project uses a **modern, production-ready tech stack** that combines:

- ✅ **Proven technologies** (Flask, SQLAlchemy, Docker)
- ✅ **Modern AI** (Ollama for local inference)
- ✅ **Scalable architecture** (Three-tier design)
- ✅ **Developer friendly** (Easy to learn and use)
- ✅ **Production ready** (Docker, Nginx, Gunicorn)

The stack is carefully chosen to balance **simplicity, performance, and scalability** while keeping costs low and development fast.

---

**Last Updated**: July 5, 2026  
**Project Version**: 2.0 (Modular Architecture)  
**Tech Stack Status**: ✅ Production Ready
