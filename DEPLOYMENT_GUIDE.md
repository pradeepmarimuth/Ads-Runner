# 🚀 Deployment Guide — SEO Marketing AI

## Why API Keys Fail After Deployment

Your `.env` file is in `.gitignore` — it is **never pushed to your server**.
On cloud platforms, you must set environment variables manually in their dashboard.

---

## ✅ Production Environment Variables to Set

Set ALL of these in your hosting platform's dashboard:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Any long random string (generate: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `FLASK_ENV` | `production` |
| `DEBUG` | `False` |
| `OPENAI_API_KEY` | `sk-...` (your real OpenAI key from https://platform.openai.com/api-keys) |
| `OPENAI_MODEL` | `gpt-4o-mini` |
| `SESSION_COOKIE_SECURE` | `True` |
| `SESSION_COOKIE_HTTPONLY` | `True` |
| `SESSION_COOKIE_SAMESITE` | `Lax` |
| `PERMANENT_SESSION_LIFETIME` | `3600` |
| `MAX_UPLOAD_SIZE` | `10485760` |

> **Note:** `DATABASE_URL` does NOT need to be set unless you upgrade from SQLite to PostgreSQL.

---

## Platform-Specific Instructions

### 🔵 Render (render.com)

1. Go to your **Dashboard** → Select your Web Service → **Environment**
2. Click **Add Environment Variable**
3. Add each variable from the table above
4. Click **Save Changes** → Render will auto-redeploy

**Render Settings to check:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Environment:** `Python 3`

---

### 🟣 Railway (railway.app)

1. Go to your project → Select the service → **Variables** tab
2. Click **+ New Variable** and add each from the table above
3. Railway auto-redeploys after saving

---

### 🟡 Heroku (heroku.com)

**Via Dashboard:**
1. Go to your app → **Settings** → **Config Vars** → **Reveal Config Vars**
2. Add each variable from the table above

**Via CLI (faster):**
```bash
heroku config:set SECRET_KEY="your-random-secret-key"
heroku config:set FLASK_ENV=production
heroku config:set DEBUG=False
heroku config:set OPENAI_API_KEY="sk-..."
heroku config:set SESSION_COOKIE_SECURE=True
```

---

### 🔵 Fly.io (fly.io)

```bash
fly secrets set SECRET_KEY="your-random-secret-key"
fly secrets set FLASK_ENV=production
fly secrets set DEBUG=False
fly secrets set OPENAI_API_KEY="sk-..."
fly secrets set SESSION_COOKIE_SECURE=True
```

---

## 🔑 Getting a Valid OpenAI API Key

Your current key (`AQ.Ab8RN6...`) is **invalid**. OpenAI keys always start with `sk-`.

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **+ Create new secret key**
4. Copy the key (starts with `sk-proj-...` or `sk-...`)
5. Set it as `OPENAI_API_KEY` in your platform's dashboard

> **Cost:** `gpt-4o-mini` is very cheap (~$0.15 per million tokens).

---

## 🏗️ How the AI Fallback Chain Works

The app tries AI providers in this order:

```
1. Ollama (local) → Only works on your own machine, NOT on cloud
2. OpenAI (cloud) → Works on deployment IF the API key is set correctly
3. Mock Responses → Always works as a final fallback
```

On cloud deployment: **Ollama will not be available** (it's a desktop app).
The app jumps directly to **OpenAI**, then **Mock** if the key is missing/invalid.

---

## 🧪 Deployment Checklist

- [ ] `SECRET_KEY` is a long random string (not the default)
- [ ] `DEBUG=False` is set on the platform
- [ ] `FLASK_ENV=production` is set on the platform
- [ ] `OPENAI_API_KEY=sk-...` is set on the platform (valid key starting with `sk-`)
- [ ] `SESSION_COOKIE_SECURE=True` is set (requires HTTPS)
- [ ] `Procfile` uses gunicorn (already fixed ✅)
- [ ] `app.py` has `load_dotenv()` at the top (already fixed ✅)

---

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| AI returns mock responses only | `OPENAI_API_KEY` not set or invalid | Set the key in your platform dashboard |
| `500 Internal Server Error` | Missing env var or wrong `SECRET_KEY` | Check platform logs; set all env vars |
| App won't start | Port binding issue | Ensure `Procfile` uses `$PORT` variable |
| Session lost on every request | `SECRET_KEY` differs between deploys | Set a fixed `SECRET_KEY` in the dashboard |
| `AuthenticationError` from OpenAI | Invalid API key | Replace with a valid `sk-...` key |

---

## 📋 Local Development (unchanged)

```bash
# Run locally as before:
python app.py
```
