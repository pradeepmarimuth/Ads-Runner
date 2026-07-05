# Ollama Chatbot Integration - Complete Guide

## Overview

Your project now has a **fully functional Ollama chatbot** integration! The AI assistant is embedded in the `/ai` route and provides intelligent marketing advice, campaign analysis, and creative content generation.

## Features Implemented

### 1. **AI Marketing Chatbot** 💬
- **Location**: `/ai` page (AI Workspace)
- **Functionality**: 
  - Conversational AI assistant for marketing queries
  - Context-aware responses using user's campaign data
  - Maintains chat history (last 10 messages)
  - Provides personalized campaign recommendations

### 2. **Slogan Generator** 🎯
- Generates 3 anti-gravity marketing slogans
- Uses Ollama for creative content generation
- Falls back to OpenAI, then mock data

### 3. **Hashtag Generator** #️⃣
- Creates trending social media hashtags
- Keyword-based generation
- Smart formatting (adds # if missing)

### 4. **Smart Ad Link Analyzer** 🔗
- Analyzes marketing URLs
- Extracts keywords from URLs
- Predicts CTR and engagement rates
- Generates campaign insights
- Logs all analyses to database

## How It Works

### Ollama Integration Architecture

```
User Query → Flask API → Ollama (Local) → Response
                      ↓ (fallback)
                   OpenAI API
                      ↓ (fallback)
                   Mock Data
```

### Key API Endpoints

#### 1. **Chat Endpoint**
```
POST /api/ai-chat
Body: { "message": "Your marketing question" }
Response: { "response": "AI answer", "ai_source": "Ollama" }
```

#### 2. **Clear Chat History**
```
POST /api/ai-chat/clear
Response: { "message": "Chat history cleared successfully" }
```

#### 3. **Generate Caption**
```
POST /api/generate-caption
Body: { "productName": "Hover Boots 3000" }
Response: { "captions": [...], "ai_source": "Ollama" }
```

#### 4. **Generate Hashtags**
```
POST /api/generate-hashtags
Body: { "keyword": "Zero-Gravity Flight" }
Response: { "hashtags": [...], "ai_source": "Ollama" }
```

#### 5. **Analyze Link**
```
POST /api/analyze-link
Body: { "adLink": "https://instagram.com/campaign" }
Response: { "log": {...}, "campaign": {...} }
```

## Setup Instructions

### Step 1: Install Ollama

**Windows:**
1. Download Ollama from: https://ollama.ai
2. Run `OllamaSetup.exe` (already in your project folder)
3. Ollama will start automatically as a service

**Verify Installation:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### Step 2: Pull the AI Model

```bash
# Pull the default model (qwen2.5:0.5b - lightweight, fast)
ollama pull qwen2.5:0.5b

# OR pull other models:
ollama pull tinyllama        # 637MB, very fast
ollama pull llama3.2:1b      # 1.3GB, better quality
ollama pull llama3.2:3b      # 2GB, high quality
```

### Step 3: Install Python Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The app will:
- Create the database (`marketing.db`)
- Seed default accounts
- Start on http://127.0.0.1:5000

### Step 5: Test the Chatbot

1. Navigate to: http://127.0.0.1:5000/login
2. Login with:
   - **Customer Account**: `customer@antigravity.io` / `pass123`
   - **Influencer Account**: `influencer@antigravity.io` / `pass123`
3. Go to **AI Copywriter** section
4. Try the chatbot with queries like:
   - "Suggest an ad campaign strategy for Hover Shoes"
   - "Write an engaging Instagram caption for eco-friendly water bottle launch"
   - "Give me 3 tips to improve my ad click-through rate"

## Model Selection Logic

The app automatically selects the best available model:

```python
Preferred Models (in order):
1. qwen2.5:0.5b   # Default, optimized for speed
2. tinyllama      # Fast alternative
3. llama3.2:1b    # Better quality
4. [First available model]  # Fallback to any model
```

## Chat History Management

- **Storage**: In-memory dictionary `CHAT_HISTORIES`
- **Scope**: Per-user (keyed by user_id)
- **Limit**: Last 10 messages (prevents memory overflow)
- **Context**: Includes user profile, campaigns, and audit logs

### Chat Context Example

```python
Context provided to AI:
- User Profile: Name, Role, Email, Tagline
- Active Campaigns: Name, Platform, Clicks, Conversions, ROI
- Recent URL Audits: Ad Links, Verdict, Insights
```

## Fallback Strategy

### 3-Tier Fallback System:

1. **Ollama (Local)** - Primary, no cost, fast
2. **OpenAI API** - Fallback, requires API key
3. **Mock Data** - Last resort, deterministic

### Setting OpenAI API Key (Optional):

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "your-openai-api-key"

# OR add to .env file
OPENAI_API_KEY=your-openai-api-key
```

## Frontend Integration

### Chatbot UI Components

**HTML Template**: `templates/ai.html`
- Chat message container with scrolling
- User/AI message bubbles
- Quick prompt buttons
- Clear chat button

**JavaScript**: `static/js/ai.js`
- `sendChatMessage()` - Sends message to API
- `clearChatHistory()` - Clears conversation
- `setChatPrompt()` - Fills input with quick prompts

### Styling

- **Dark Mode**: Space-themed with cyan/purple accents
- **Light Mode**: Clean slate theme
- **Theme Toggle**: Persistent localStorage
- **Animations**: Typing indicators, pulse effects

## Database Schema

### CampaignLog Model
Stores ad link analysis results:
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- ad_link: String (URL analyzed)
- analysis_result: JSON (Insights, hashtags, verdict)
- timestamp: DateTime
```

## Troubleshooting

### Issue: Ollama not responding

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service (Windows)
# Open Task Manager → Services → Restart Ollama

# OR manually start Ollama
ollama serve
```

### Issue: "No model found"

**Solution:**
```bash
# List installed models
ollama list

# Pull a model if none installed
ollama pull qwen2.5:0.5b
```

### Issue: Slow responses

**Solutions:**
1. Use smaller models: `qwen2.5:0.5b` or `tinyllama`
2. Increase timeout in `query_ollama()` function
3. Check system resources (CPU/RAM usage)

### Issue: Chat context not working

**Solution:**
- Chat history is stored in memory (resets on server restart)
- Use "Clear Chat" button to reset conversation
- Check that user has campaigns/logs for context

## Performance Optimization

### Model Recommendations by Hardware:

| RAM   | CPU Cores | Recommended Model      | Response Time |
|-------|-----------|------------------------|---------------|
| 4GB   | 2-4       | tinyllama             | ~2-5s         |
| 8GB   | 4-8       | qwen2.5:0.5b          | ~3-8s         |
| 16GB+ | 8+        | llama3.2:1b or 3b     | ~5-15s        |

### Tips:
- Keep chat history limit low (currently 10 messages)
- Use JSON mode for structured responses
- Implement request timeout (currently 40s)

## Advanced Configuration

### Custom Model Selection

Edit `query_ollama()` in `app.py`:

```python
preferred = ['your-model:tag', 'fallback-model', 'qwen2.5:0.5b']
```

### Adjust Timeout

```python
res = requests.post(f"{ollama_url}/chat", json=payload, timeout=60)  # Increase from 40s
```

### Change Chat History Limit

```python
CHAT_HISTORIES[uid] = CHAT_HISTORIES[uid][-20:]  # Keep last 20 messages
```

## Testing Checklist

- [ ] Ollama service running
- [ ] Model pulled successfully
- [ ] Flask app starts without errors
- [ ] Can access `/ai` page
- [ ] Chatbot responds to queries
- [ ] Slogan generator works
- [ ] Hashtag generator works
- [ ] Link analyzer saves to database
- [ ] Chat history persists during session
- [ ] Clear chat button works
- [ ] Theme toggle works

## Demo Accounts

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

## Next Steps

### Enhancements You Can Add:

1. **Streaming Responses**: Real-time token streaming from Ollama
2. **Voice Input**: Speech-to-text for queries
3. **Image Analysis**: Upload campaign images for AI feedback
4. **Multi-language**: Support for different languages
5. **Custom Prompts**: User-defined system prompts
6. **Export Chat**: Download conversation history
7. **Suggested Replies**: AI-generated quick responses

## Resources

- **Ollama Docs**: https://ollama.ai/docs
- **Ollama Models**: https://ollama.ai/library
- **Flask Docs**: https://flask.palletsprojects.com/
- **Tailwind CSS**: https://tailwindcss.com/

## Support

If you encounter issues:
1. Check Ollama is running: `ollama list`
2. Verify model is installed: `ollama list`
3. Check Flask logs in terminal
4. Inspect browser console for JavaScript errors
5. Review database logs: `marketing.db`

---

**Your Ollama chatbot is now fully operational!** 🚀

Test it by asking marketing questions, generating content, or analyzing ad links. The AI will provide personalized recommendations based on your campaign data.
