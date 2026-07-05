# 🚀 Marketing AI Platform

A comprehensive marketing automation platform with AI-powered chatbot using Ollama, campaign management, social networking, and analytics.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)

## ✨ Features

### Core Features
- **AI Chatbot**: Powered by Ollama with comprehensive, detailed responses
- **Campaign Management**: Track clicks, conversions, spend, and ROI
- **Social Networking**: Connect with influencers, publishers, and customers
- **Analytics Dashboard**: Real-time performance metrics
- **Content Generation**: AI-powered slogans and hashtags
- **URL Analyzer**: Analyze marketing URLs and predict performance

### AI Capabilities
- Context-aware responses using campaign data
- Markdown-formatted detailed answers (400-900 words)
- Fallback to OpenAI when Ollama is unavailable
- Chat history management
- Real-time content generation

### User Roles
- **Customer**: View campaigns, connect with others
- **Influencer**: Create content, partner with brands
- **Ad Publisher**: Manage ad slots and campaigns
- **Admin**: Full platform management

## 📁 Project Structure

```
marketing-ai-platform/
├── backend/                    # Backend application core
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── wsgi.py                # WSGI entry point
│   └── requirements.txt       # Python dependencies
│
├── api/                        # API layer
│   ├── routes/                # API route handlers
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── posts.py          # Posts/feed endpoints
│   │   ├── campaigns.py      # Campaign endpoints
│   │   ├── messages.py       # Messaging endpoints
│   │   ├── network.py        # Network endpoints
│   │   ├── ai.py             # AI chatbot endpoints
│   │   └── admin.py          # Admin endpoints
│   │
│   ├── middleware/            # Request middleware
│   │   └── auth.py           # Authentication middleware
│   │
│   └── services/              # Business logic services
│       ├── ollama_service.py # Ollama AI service
│       └── analytics_service.py # Analytics calculations
│
├── database/                   # Database layer
│   ├── models.py              # SQLAlchemy models
│   ├── migrations/            # Database migrations
│   ├── seeders.py             # Seed data
│   └── marketing.db           # SQLite database
│
├── frontend/                   # Frontend layer
│   ├── static/               # Static assets
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   └── uploads/         # User uploads
│   │
│   └── templates/            # HTML templates
│       ├── admin.html
│       ├── ai.html
│       ├── dashboard.html
│       └── ...
│
├── tests/                      # Test suite
│   ├── test_api.py
│   ├── test_ollama.py
│   └── test_auth.py
│
├── deployment/                 # Deployment configurations
│   ├── docker/
│   ├── nginx/
│   └── gunicorn/
│
├── docs/                       # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── HOW_TO_USE.md
│
└── scripts/                    # Utility scripts
    ├── setup.sh
    └── deploy.sh
```

## 🔧 Prerequisites

### Required
- Python 3.8+
- Ollama (for local AI)
- pip (Python package manager)

### Optional
- PostgreSQL (for production)
- Docker & Docker Compose (for containerized deployment)
- Nginx (for production web server)
- OpenAI API key (for AI fallback)

## 📥 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/marketing-ai-platform.git
cd marketing-ai-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Install Ollama
**Windows:**
```bash
# Run the included installer
OllamaSetup.exe

# Or download from https://ollama.ai
```

**Linux/Mac:**
```bash
curl https://ollama.ai/install.sh | sh
```

### 5. Pull AI Model
```bash
ollama pull qwen2.5:0.5b
```

### 6. Setup Database
```bash
# The database will be created automatically on first run
# Or run the setup script
python scripts/setup_db.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///database/marketing.db

# Ollama Configuration
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=90
OLLAMA_MAX_TOKENS=2048

# OpenAI (Optional - Fallback)
OPENAI_API_KEY=your-openai-key-here
OPENAI_MODEL=gpt-4o-mini

# Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
```

### Configuration Files

- `backend/config.py`: Main configuration
- `deployment/docker/docker-compose.yml`: Docker configuration
- `deployment/nginx/nginx.conf`: Nginx configuration
- `deployment/gunicorn/gunicorn_config.py`: Gunicorn configuration

## 🚀 Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the application
python backend/app.py
```

The application will be available at: http://127.0.0.1:5000

### Demo Accounts

```
Customer:
  Email: customer@antigravity.io
  Password: pass123

Influencer:
  Email: influencer@antigravity.io
  Password: pass123

Ad Publisher:
  Email: adpub@antigravity.io
  Password: pass123

Admin:
  Email: admin@antigravity.io
  Password: adminpassword
```

### Production Mode

```bash
# Using Gunicorn
gunicorn -c deployment/gunicorn/gunicorn_config.py backend.wsgi:application

# Using Docker
docker-compose -f deployment/docker/docker-compose.yml up -d
```

## 🐳 Deployment

### Docker Deployment

```bash
# Build and start containers
cd deployment/docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Manual Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions on:
- Server setup
- Nginx configuration
- SSL/HTTPS setup
- Database migration
- Environment configuration

## 📚 API Documentation

### Authentication Endpoints
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### AI Endpoints
- `POST /api/ai-chat` - Send message to AI chatbot
- `POST /api/ai-chat/clear` - Clear chat history
- `POST /api/generate-caption` - Generate product slogans
- `POST /api/generate-hashtags` - Generate hashtags
- `POST /api/analyze-link` - Analyze marketing URL

### Campaign Endpoints
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaign-logs` - Get analysis logs
- `POST /api/analyze-performance` - Analyze performance

### Social Endpoints
- `GET /api/posts` - List posts
- `POST /api/posts` - Create post
- `POST /api/posts/:id/like` - Like post
- `GET /api/network` - List network connections
- `POST /api/connect/:id` - Send connection request

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference.

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Tests
```bash
# Test Ollama integration
python tests/test_ollama.py

# Test API endpoints
pytest tests/test_api.py

# Test authentication
pytest tests/test_auth.py

# Test detailed responses
python tests/test_detailed_responses.py
```

### Test Coverage
```bash
pytest --cov=backend --cov=api --cov=database tests/
```

## 📊 Performance

### Response Times
- AI Chatbot: 15-30 seconds for detailed responses
- API Endpoints: < 200ms
- Database Queries: < 50ms
- Page Load: < 2 seconds

### Scalability
- Supports 100+ concurrent users
- Database: SQLite (dev), PostgreSQL (production)
- Caching: Redis (optional)
- Load Balancing: Nginx

## 🔒 Security

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection
- SQL injection prevention
- XSS protection
- File upload validation
- Rate limiting (production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Ollama team for the local AI framework
- Flask team for the web framework
- Tailwind CSS for the UI framework
- Contributors and testers

## 📞 Support

- Documentation: `/docs` folder
- Issues: GitHub Issues
- Email: support@yourcompany.com

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] API rate limiting
- [ ] Webhook integrations
- [ ] Export/Import campaigns
- [ ] A/B testing framework

---

**Built with ❤️ using Flask, Ollama, and Tailwind CSS**
