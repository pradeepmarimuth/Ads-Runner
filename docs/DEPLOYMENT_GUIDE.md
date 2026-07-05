# 🚀 Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Development Deployment](#development-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

### Required
- Python 3.8+
- Ollama installed and running
- Git
- 2GB RAM minimum (4GB recommended)
- 10GB disk space

### Optional (for production)
- Docker & Docker Compose
- Nginx
- PostgreSQL
- Redis
- SSL certificate

## Development Deployment

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/marketing-ai-platform.git
cd marketing-ai-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Install Ollama
```bash
# Download from https://ollama.ai
# Or use the included installer
./OllamaSetup.exe  # Windows

# Pull the AI model
ollama pull qwen2.5:0.5b
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Initialize Database
```bash
python backend/app.py
# Database will be created automatically
```

### 5. Run Development Server
```bash
python backend/app.py
```

Access at: http://127.0.0.1:5000

## Docker Deployment

### 1. Install Docker
```bash
# Install Docker and Docker Compose
# https://docs.docker.com/get-docker/
```

### 2. Build and Run
```bash
cd deployment/docker

# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Pull Ollama Model
```bash
# After services are running
docker exec -it marketing-ai-ollama ollama pull qwen2.5:0.5b
```

Access at: http://localhost

## Production Deployment

### Option 1: Manual Deployment (Ubuntu/Debian)

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql redis-server

# Install Ollama
curl https://ollama.ai/install.sh | sh
```

#### 2. Create Application User
```bash
sudo useradd -m -s /bin/bash marketing
sudo su - marketing
```

#### 3. Deploy Application
```bash
cd /home/marketing
git clone https://github.com/yourusername/marketing-ai-platform.git
cd marketing-ai-platform

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install gunicorn
```

#### 4. Configure Environment
```bash
cp .env.example .env
nano .env

# Set production values:
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/marketing_ai
```

#### 5. Setup PostgreSQL
```bash
sudo -u postgres psql

CREATE DATABASE marketing_ai;
CREATE USER marketing_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE marketing_ai TO marketing_user;
\q
```

#### 6. Setup Systemd Service
```bash
sudo nano /etc/systemd/system/marketing-ai.service
```

Content:
```ini
[Unit]
Description=Marketing AI Platform
After=network.target postgresql.service

[Service]
Type=notify
User=marketing
Group=marketing
WorkingDirectory=/home/marketing/marketing-ai-platform
Environment="PATH=/home/marketing/marketing-ai-platform/venv/bin"
ExecStart=/home/marketing/marketing-ai-platform/venv/bin/gunicorn \
    -c deployment/gunicorn/gunicorn_config.py \
    backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable marketing-ai
sudo systemctl start marketing-ai
sudo systemctl status marketing-ai
```

#### 7. Setup Nginx
```bash
sudo nano /etc/nginx/sites-available/marketing-ai
```

Content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/marketing/marketing-ai-platform/frontend/static/;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/marketing-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 2: Docker Production Deployment

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/marketing-ai-platform.git
cd marketing-ai-platform
```

#### 2. Configure Production Environment
```bash
cp .env.example .env
nano .env

# Set production values
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-random-secret-key
```

#### 3. Start with Docker Compose
```bash
cd deployment/docker
docker-compose -f docker-compose.yml up -d

# Pull Ollama model
docker exec -it marketing-ai-ollama ollama pull qwen2.5:0.5b

# View logs
docker-compose logs -f web
```

#### 4. Setup SSL
```bash
# Using Certbot with Docker
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
    certbot/certbot certonly --standalone \
    -d your-domain.com

# Update docker-compose.yml to mount certificates
```

## Cloud Deployment

### AWS Elastic Beanstalk

#### 1. Install EB CLI
```bash
pip install awsebcli
```

#### 2. Initialize EB
```bash
eb init -p python-3.11 marketing-ai-platform
```

#### 3. Create Environment
```bash
eb create production-env
```

#### 4. Deploy
```bash
eb deploy
```

### Heroku

#### 1. Create Procfile
```
web: gunicorn -c deployment/gunicorn/gunicorn_config.py backend.wsgi:application
```

#### 2. Deploy
```bash
heroku create marketing-ai-platform
git push heroku main
```

### DigitalOcean App Platform

#### 1. Connect Repository
- Go to DigitalOcean App Platform
- Connect GitHub repository

#### 2. Configure Build
```yaml
name: marketing-ai-platform
services:
  - name: web
    build_command: pip install -r backend/requirements.txt
    run_command: gunicorn -c deployment/gunicorn/gunicorn_config.py backend.wsgi:application
```

### Google Cloud Run

#### 1. Build Image
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/marketing-ai
```

#### 2. Deploy
```bash
gcloud run deploy marketing-ai \
    --image gcr.io/PROJECT-ID/marketing-ai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## Monitoring & Maintenance

### Logging

#### Application Logs
```bash
# Systemd service
sudo journalctl -u marketing-ai -f

# Docker
docker-compose logs -f web

# Log files
tail -f /var/log/marketing-ai/app.log
```

### Monitoring Tools

#### 1. Setup Prometheus
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'marketing-ai'
    static_configs:
      - targets: ['localhost:5000']
```

#### 2. Setup Grafana
```bash
docker run -d -p 3000:3000 grafana/grafana
```

### Health Checks

```bash
# HTTP health check
curl http://your-domain.com/health

# Docker health check
docker ps | grep marketing-ai-web
```

### Backup

#### Database Backup
```bash
# PostgreSQL
pg_dump marketing_ai > backup_$(date +%Y%m%d).sql

# SQLite
cp database/marketing.db database/backup_$(date +%Y%m%d).db
```

#### Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### Updates

#### Application Update
```bash
# Pull latest code
git pull origin main

# Install new dependencies
pip install -r backend/requirements.txt

# Restart service
sudo systemctl restart marketing-ai

# Or with Docker
docker-compose pull
docker-compose up -d
```

### Performance Tuning

#### Gunicorn Workers
```python
# deployment/gunicorn/gunicorn_config.py
workers = (CPU_COUNT * 2) + 1
worker_class = "gevent"  # For async
```

#### Nginx Caching
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache my_cache;
```

#### Database Optimization
```sql
-- PostgreSQL
ANALYZE;
VACUUM;
REINDEX DATABASE marketing_ai;
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u marketing-ai -n 50

# Check permissions
ls -la /home/marketing/marketing-ai-platform

# Check ports
sudo netstat -tulpn | grep 5000
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U marketing_user -d marketing_ai

# Check credentials in .env
cat .env | grep DATABASE_URL
```

### Ollama Not Working
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama

# Pull model again
ollama pull qwen2.5:0.5b
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS/SSL in production
- [ ] Configure firewall (ufw/iptables)
- [ ] Set DEBUG=False
- [ ] Use strong database passwords
- [ ] Regular security updates
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Regular backups

## Support

For deployment issues:
1. Check logs
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Open GitHub issue
4. Contact support

---

**Deployment completed! Your Marketing AI Platform is now live.** 🚀
