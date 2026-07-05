# Quick Start Guide - Ollama Chatbot

## 5-Minute Setup

### 1. Install Ollama

**Option A: Using the included installer**
```bash
# Run the setup file in your project folder
.\OllamaSetup.exe
```

**Option B: Download from website**
- Visit: https://ollama.ai
- Download and install for Windows

### 2. Pull the AI Model

Open a new terminal and run:
```bash
ollama pull qwen2.5:0.5b
```

Wait for the download to complete (~380MB).

### 3. Install Dependencies

```bash
# Make sure you're in the project directory
cd D:\SEO-marketing

# Activate virtual environment (if not already active)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Start the Application

```bash
python app.py
```

You should see:
```
Seeding system with default accounts...
Seeding complete.
 * Running on http://127.0.0.1:5000
```

### 5. Test the Chatbot

1. Open browser: http://127.0.0.1:5000
2. Login:
   - Email: `customer@antigravity.io`
   - Password: `pass123`
3. Click **"AI Copywriter"** in the sidebar
4. Try the chatbot:
   - Type: "Suggest an ad campaign for hover shoes"
   - Click "Send Query"

## Verify Ollama is Working

### Check Service Status
```bash
curl http://localhost:11434/api/tags
```

Expected output:
```json
{
  "models": [
    {
      "name": "qwen2.5:0.5b",
      "modified_at": "2024-...",
      ...
    }
  ]
}
```

### List Installed Models
```bash
ollama list
```

Expected output:
```
NAME              ID            SIZE
qwen2.5:0.5b      abc123...     380 MB
```

## Test Each Feature

### 1. Slogan Generator
- Input: `Hover Boots 3000`
- Click "Generate Slogans"
- See 3 creative slogans appear

### 2. Hashtag Generator
- Input: `Zero-Gravity Flight`
- Click "Create Hashtags"
- See 3 hashtags with # symbols

### 3. Link Analyzer
- Input: `https://instagram.com/hover-boots-promo`
- Click "Analyze URL"
- See predicted CTR, engagement, and insights

### 4. Chatbot
- Ask: "How can I improve my Instagram ad performance?"
- See AI response with personalized advice

## Troubleshooting

### Problem: "Ollama query failed"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

### Problem: "No model found"

**Solution:**
```bash
ollama pull qwen2.5:0.5b
```

### Problem: Slow responses

**Try a smaller model:**
```bash
ollama pull tinyllama
```

### Problem: Port 5000 already in use

**Solution:**
```bash
# Edit app.py last line:
app.run(host='127.0.0.1', port=5001, debug=True)

# Then access: http://127.0.0.1:5001
```

## What's Next?

✅ **Your chatbot is working!**

Try these features:
- Generate marketing slogans
- Create campaign hashtags
- Analyze ad URLs
- Chat with AI about your campaigns
- Toggle dark/light theme

## Quick Command Reference

```bash
# Check Ollama status
ollama list

# Pull a different model
ollama pull llama3.2:1b

# Run Python app
python app.py

# Install new dependency
pip install package-name

# Activate virtual environment
.\venv\Scripts\activate
```

## Support

- Full documentation: `OLLAMA_INTEGRATION.md`
- Ollama docs: https://ollama.ai/docs
- Open an issue if you encounter problems

---

**Enjoy your AI-powered marketing assistant!** 🚀
