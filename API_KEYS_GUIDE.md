# 🔑 API Keys Guide

## API Keys Used in This Project

This document explains all API keys used in the Marketing AI Platform, what they're for, and how to configure them.

---

## 📋 Quick Summary

| API Key | Required? | Purpose | Cost |
|---------|-----------|---------|------|
| **OPENAI_API_KEY** | ❌ Optional | Cloud AI fallback | Paid (per token) |
| **SECRET_KEY** | ✅ Required | Flask session security | Free |

---

## 1️⃣ SECRET_KEY (Required)

### Purpose
Flask's session encryption and security token generation.

### Required?
✅ **YES** - Required for the application to run securely.

### Where It's Used
- Session cookie encryption
- CSRF token generation
- Security features

### How to Set
```bash
# In .env file
SECRET_KEY=your-super-secret-random-key-here
```

### How to Generate
```bash
# Python method
python -c "import secrets; print(secrets.token_hex(32))"

# Output example:
# 4f3a8b2e9d1c7a6b5e4f3a2d1c9b8a7e6f5d4c3b2a1e9d8c7b6a5f4e3d2c1b0
```

### Security Notes
- ⚠️ **Never commit this to Git**
- ⚠️ **Change it in production**
- ⚠️ **Use different keys for dev/prod**
- ✅ Keep it secret and random
- ✅ Minimum 32 characters recommended

### Default Value
```
quantum-antigrav-secret-9000
```
⚠️ **Change this immediately for production!**

---

## 2️⃣ OPENAI_API_KEY (Optional)

### Purpose
OpenAI API access for **fallback** when local Ollama is unavailable.

### Required?
❌ **NO** - The application works perfectly without it!

### Primary AI: Ollama (Local)
The application **primarily uses Ollama** (local AI) which requires:
- ✅ No API key
- ✅ No internet connection
- ✅ No usage costs
- ✅ Privacy-focused (data stays local)

### When OpenAI is Used
OpenAI is only used as a **fallback** in this order:

```
1. Try Ollama (Local AI) ✅ FREE
   ↓ (if fails)
2. Try OpenAI (Cloud AI) 💰 PAID
   ↓ (if fails)
3. Use Mock Data ✅ FREE
```

### Where It's Used
OpenAI API is used as fallback in:
- `/api/generate-caption` - Caption generation
- `/api/generate-hashtags` - Hashtag generation
- `/api/ai-chat` - AI chat responses

### How to Set
```bash
# In .env file
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

### How to Get
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create new secret key
5. Copy and paste into `.env`

### Cost
OpenAI charges per token:
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **GPT-4o**: ~$5.00 per 1M input tokens, ~$15.00 per 1M output tokens

### Do You Need It?
**NO!** Here's why:

✅ **Ollama works perfectly** for:
- Caption generation
- Hashtag generation
- AI chat (with detailed 400-900 word responses)
- Ad link analysis
- All AI features

❌ **You only need OpenAI if**:
- Ollama service is down
- You don't have Ollama installed
- You prefer cloud AI

### Cost Comparison
| Solution | Setup | Cost | Privacy | Speed |
|----------|-------|------|---------|-------|
| **Ollama (Local)** | Install Ollama | FREE | 100% Private | Fast |
| **OpenAI (Cloud)** | API Key | $$ per use | Data sent to OpenAI | Very Fast |
| **Mock Data** | None | FREE | 100% Private | Instant |

### Recommendation
💡 **Use Ollama** (the default setup) - It's free, private, and works great!

---

## 🔧 Configuration Guide

### Step 1: Create .env File
```bash
# Copy the example file
cp .env.example .env
```

### Step 2: Set Required Keys
```bash
# Edit .env file
nano .env

# Or on Windows
notepad .env
```

### Step 3: Update SECRET_KEY
```bash
# Generate a new secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste in .env:
SECRET_KEY=your-generated-key-here
```

### Step 4: (Optional) Add OpenAI Key
```bash
# Only if you want OpenAI fallback
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

## 📝 Complete .env Template

### Minimal Configuration (Recommended)
```bash
# Required
FLASK_ENV=development
SECRET_KEY=your-generated-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///database/marketing.db

# Ollama (Local AI - Free)
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=90
OLLAMA_MAX_TOKENS=2048

# OpenAI (Optional - Skip this if using Ollama)
# OPENAI_API_KEY=your-key-here
```

### Full Configuration (With All Options)
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_APP=backend/app.py
SECRET_KEY=your-generated-secret-key-here
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///database/marketing.db

# Ollama Configuration (Local AI)
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b
OLLAMA_TIMEOUT=90
OLLAMA_MAX_TOKENS=2048

# OpenAI Configuration (Optional Fallback)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Upload Configuration
MAX_UPLOAD_SIZE=10485760
UPLOAD_FOLDER=frontend/static/uploads

# Logging
LOG_LEVEL=INFO

# Security
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600
```

---

## 🚀 Quick Start Configurations

### For Local Development (Recommended)
```bash
SECRET_KEY=quantum-antigrav-secret-9000
OLLAMA_URL=http://localhost:11434/api
# No OpenAI key needed!
```

### For Production
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=postgresql://user:pass@localhost/dbname
OLLAMA_URL=http://ollama-service:11434/api
# Optional: Add OpenAI for redundancy
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### For Testing Without Ollama
```bash
SECRET_KEY=test-secret-key
# Skip Ollama, use OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

## 🔒 Security Best Practices

### Do's ✅
- ✅ Use environment variables for all secrets
- ✅ Generate random SECRET_KEY
- ✅ Use different keys for dev/staging/prod
- ✅ Rotate keys regularly
- ✅ Use `.env` files (not committed to Git)
- ✅ Restrict API key permissions

### Don'ts ❌
- ❌ Never commit API keys to Git
- ❌ Never hardcode keys in source code
- ❌ Never share keys in public
- ❌ Never use default/example keys in production
- ❌ Never expose keys in client-side code
- ❌ Never log API keys

### .gitignore Configuration
```bash
# Already configured in the project
.env
.env.local
.env.*.local
*.key
secrets/
```

---

## 🧪 Testing API Keys

### Test SECRET_KEY
```python
# Should be set and not default
python -c "import os; from backend.config import get_config; c=get_config(); print('✅ OK' if c.SECRET_KEY != 'quantum-antigrav-secret-9000' else '⚠️  Using default key!')"
```

### Test Ollama
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Or use Python
python -c "import requests; r=requests.get('http://localhost:11434/api/tags'); print('✅ Ollama running' if r.status_code==200 else '❌ Ollama not running')"
```

### Test OpenAI (if configured)
```python
# Test OpenAI API key
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    client.models.list()
    print('✅ OpenAI API key valid')
except:
    print('❌ OpenAI API key invalid or not set')
"
```

---

## ❓ Frequently Asked Questions

### Q: Do I need an OpenAI API key?
**A:** No! The application works perfectly with Ollama (local AI) which is free.

### Q: What happens if I don't set OPENAI_API_KEY?
**A:** The app will:
1. Try Ollama first (works great!)
2. If Ollama fails, use mock data
3. Everything still works!

### Q: How much does OpenAI cost?
**A:** GPT-4o-mini costs about $0.15-$0.60 per 1M tokens. For typical usage:
- 100 AI chat responses: ~$0.01-0.05
- 1000 caption generations: ~$0.05-0.20

But remember: **Ollama is FREE!**

### Q: Is Ollama as good as OpenAI?
**A:** For this application, yes! Ollama provides:
- ✅ Detailed responses (400-900 words)
- ✅ Good quality captions and hashtags
- ✅ Fast response times
- ✅ No cost
- ✅ Privacy

### Q: Can I use both Ollama and OpenAI?
**A:** Yes! The application will:
1. Try Ollama first
2. Fall back to OpenAI if Ollama fails
3. This provides redundancy

### Q: How do I change the SECRET_KEY?
**A:** 
```bash
# Generate new key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env file
SECRET_KEY=your-new-key-here

# Restart application
python backend/app.py
```

### Q: Where should I store API keys?
**A:** 
- **Development**: `.env` file (not committed to Git)
- **Production**: Environment variables or secrets manager
- **Docker**: Docker secrets or environment variables
- **Kubernetes**: Kubernetes secrets

### Q: What if someone gets my SECRET_KEY?
**A:** 
1. Generate a new key immediately
2. Update `.env` file
3. Restart the application
4. All users will be logged out (sessions invalidated)

---

## 🎯 Summary

### Required API Keys
| Key | Required | Default | Action Needed |
|-----|----------|---------|---------------|
| **SECRET_KEY** | ✅ Yes | `quantum-antigrav-secret-9000` | ⚠️ Change for production |

### Optional API Keys
| Key | Required | Purpose | Cost |
|-----|----------|---------|------|
| **OPENAI_API_KEY** | ❌ No | Cloud AI fallback | $$ per use |

### Recommendation
✅ **For most users**: Just set SECRET_KEY and use Ollama (free!)
✅ **For production**: Generate secure SECRET_KEY
❌ **OpenAI key**: Only needed if you want cloud AI fallback

---

## 📚 Related Documentation

- **Ollama Setup**: `docs/OLLAMA_INTEGRATION.md`
- **Environment Config**: `backend/config.py`
- **Security Guide**: `docs/SECURITY.md` (if exists)
- **Deployment**: `docs/DEPLOYMENT_GUIDE.md`

---

## 🆘 Support

If you have issues with API keys:

1. Check `.env` file exists and is properly formatted
2. Verify API keys don't have extra spaces
3. Ensure `.env` is in project root
4. Restart application after changing `.env`
5. Check application logs for errors

---

**Last Updated**: July 5, 2026  
**Project Version**: 2.0  
**Status**: ✅ Complete
