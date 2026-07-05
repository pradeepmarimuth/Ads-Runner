# 📂 API Key Storage Locations

## Where API Keys Are Stored in This Project

---

## 📍 File Structure

```
D:\SEO-marketing\
│
├── 🔐 .env                    ← YOUR API KEYS GO HERE (create this file)
├── 📋 .env.example            ← Template file (already exists)
├── 🚫 .gitignore              ← Protects .env from Git
│
├── backend/
│   └── ⚙️ config.py           ← Reads API keys from .env
│
└── api/routes/
    └── 🤖 ai.py               ← Uses API keys for AI features
```

---

## 1️⃣ Primary Storage: `.env` file

### Location
```
D:\SEO-marketing\.env
```

### Status
❌ **NOT CREATED YET** - You need to create this file!

### Purpose
- Stores your actual API keys securely
- Not committed to Git (protected by .gitignore)
- Read by the application at runtime

### How to Create
```bash
# Option 1: Copy from template
copy .env.example .env

# Option 2: Create manually
notepad .env
```

### What Goes Inside
```bash
SECRET_KEY=your-generated-secret-key-here
OPENAI_API_KEY=sk-proj-your-key-here
```

---

## 2️⃣ Template: `.env.example` file

### Location
```
D:\SEO-marketing\.env.example
```

### Status
✅ **EXISTS** - Template file with examples

### Purpose
- Shows what variables are needed
- Provides example values
- Committed to Git (safe to share)
- Used as template for creating `.env`

### Current Contents
```bash
# Flask Configuration
SECRET_KEY=change-this-to-random-secret-key

# Ollama Configuration
OLLAMA_URL=http://localhost:11434/api
OLLAMA_MODEL=qwen2.5:0.5b

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

---

## 3️⃣ Configuration Module: `backend/config.py`

### Location
```
D:\SEO-marketing\backend\config.py
```

### Status
✅ **EXISTS** - Reads API keys from .env

### Purpose
- Loads environment variables from `.env`
- Provides configuration to the application
- Handles different environments (dev/prod/test)

### Key Code
```python
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'quantum-antigrav-secret-9000')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api')
```

---

## 4️⃣ Protection: `.gitignore` file

### Location
```
D:\SEO-marketing\.gitignore
```

### Status
✅ **EXISTS** - Protects sensitive files

### Purpose
- Prevents `.env` from being committed to Git
- Keeps API keys private
- Essential for security

### Relevant Lines
```gitignore
.env
.env.local
.env.*.local
*.key
secrets/
```

---

## 5️⃣ Usage: `api/routes/ai.py`

### Location
```
D:\SEO-marketing\api\routes\ai.py
```

### Status
✅ **EXISTS** - Uses API keys

### Purpose
- Uses OPENAI_API_KEY for AI features
- Falls back to Ollama if OpenAI not available

### Key Code
```python
import os

# Read API key from environment
api_key = os.getenv('OPENAI_API_KEY', '').strip()
if api_key and api_key != 'your-openai-api-key-here':
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
```

---

## 📊 File Comparison

| File | Location | Purpose | Contains Real Keys? | In Git? |
|------|----------|---------|---------------------|---------|
| `.env` | Root | Store real API keys | ✅ YES | ❌ NO |
| `.env.example` | Root | Template/example | ❌ NO | ✅ YES |
| `backend/config.py` | Backend | Read API keys | ❌ NO | ✅ YES |
| `.gitignore` | Root | Protect secrets | ❌ NO | ✅ YES |
| `api/routes/ai.py` | API | Use API keys | ❌ NO | ✅ YES |

---

## 🎯 Current Status

### What EXISTS ✅
```
✅ .env.example       (template file)
✅ backend/config.py  (configuration loader)
✅ .gitignore         (security protection)
✅ api/routes/ai.py   (API key usage)
```

### What's MISSING ❌
```
❌ .env               (your actual API keys)
```

---

## 🚀 Quick Setup Guide

### Step 1: Create .env file
```bash
# Copy from template
copy .env.example .env
```

### Step 2: Edit .env file
```bash
# Open in notepad
notepad .env
```

### Step 3: Add your keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Paste in .env
SECRET_KEY=4f3a8b2e9d1c7a6b5e4f3a2d1c9b8a7e6f5d4c3b2a1e9d8c7b6a5f4e3d2c1b0

# Optional: Add OpenAI key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### Step 4: Verify .env is ignored
```bash
# Check git status
git status

# .env should NOT appear in the list
```

### Step 5: Restart application
```bash
python backend/app.py
```

---

## 📁 Visual Directory Structure

```
D:\SEO-marketing\
│
├── 🔐 .env                          ← CREATE THIS! (your real keys)
│   ├── SECRET_KEY=xxx...
│   └── OPENAI_API_KEY=sk-proj-xxx...
│
├── 📋 .env.example                  ← Template (already exists)
│   ├── SECRET_KEY=change-this...
│   └── OPENAI_API_KEY=your-key...
│
├── 🚫 .gitignore                    ← Security (already exists)
│   └── .env  ← prevents Git tracking
│
├── backend/
│   ├── ⚙️ config.py                 ← Loads from .env
│   │   ├── os.getenv('SECRET_KEY')
│   │   └── os.getenv('OPENAI_API_KEY')
│   │
│   └── app.py                       ← Main application
│
├── api/
│   └── routes/
│       └── 🤖 ai.py                 ← Uses API keys
│           └── os.getenv('OPENAI_API_KEY')
│
└── requirements.txt
```

---

## 🔒 Security Best Practices

### DO ✅
- ✅ Store keys in `.env` file
- ✅ Keep `.env` in `.gitignore`
- ✅ Use `.env.example` for sharing structure
- ✅ Generate strong SECRET_KEY
- ✅ Use different keys for dev/prod

### DON'T ❌
- ❌ Never commit `.env` to Git
- ❌ Never share `.env` publicly
- ❌ Never hardcode keys in source code
- ❌ Never use default keys in production
- ❌ Never log API keys

---

## 🔍 How to View Current Keys

### Check if .env exists
```bash
dir .env
```

### View .env contents (if it exists)
```bash
type .env
```

### View template
```bash
type .env.example
```

### Test if keys are loaded
```python
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SECRET_KEY:', os.getenv('SECRET_KEY'))"
```

---

## 🆘 Troubleshooting

### Issue: Application can't find API keys
**Solution:**
1. Check `.env` file exists in project root
2. Verify file is named exactly `.env` (not `.env.txt`)
3. Restart application after creating `.env`

### Issue: Keys not loading
**Solution:**
```python
# Add to backend/app.py
from dotenv import load_dotenv
load_dotenv()
```

### Issue: .env tracked by Git
**Solution:**
```bash
# Remove from Git
git rm --cached .env

# Verify .gitignore has .env
type .gitignore | findstr .env
```

---

## 📚 Related Files

### Configuration
- `backend/config.py` - Configuration class
- `.env.example` - Template file
- `API_KEYS_GUIDE.md` - Detailed API key guide

### Usage
- `api/routes/ai.py` - AI features using OpenAI
- `backend/app.py` - Application initialization

### Documentation
- `API_KEYS_GUIDE.md` - Complete API key guide
- `QUICK_REFERENCE.md` - Quick reference
- `README.md` - Project overview

---

## ✅ Summary

### API Keys Storage Location
```
📍 D:\SEO-marketing\.env
```

### Status
```
❌ Not created yet - YOU NEED TO CREATE IT
```

### Template Available
```
✅ .env.example exists - use as template
```

### Next Steps
```
1. Create .env file
2. Generate SECRET_KEY
3. (Optional) Add OPENAI_API_KEY
4. Restart application
```

---

**Last Updated**: July 5, 2026  
**Project Root**: `D:\SEO-marketing\`  
**Action Required**: Create `.env` file with your API keys
