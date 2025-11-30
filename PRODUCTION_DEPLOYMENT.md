# AgentDaf1.1 Production Deployment Guide
## Complete Production Setup Instructions

### 🚀 Quick Production Deployment

#### 1. Install Dependencies
```bash
pip install -r requirements-production.txt
```

#### 2. Set Up Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit with your actual values
notepad .env
```

#### 3. Create Logs Directory
```bash
mkdir logs
```

#### 4. Start Production Server

**Option A: Direct Gunicorn (Linux/Mac)**
```bash
gunicorn --config gunicorn.conf.py wsgi:app
```

**Option B: Direct Python (Windows)**
```bash
python simple_app.py
```

**Option C: Systemd Service (Linux)**
```bash
# Copy service file
sudo cp agentdaf1.service /etc/systemd/system/

# Enable and start
sudo systemctl enable agentdaf1
sudo systemctl start agentdaf1

# Check status
sudo systemctl status agentdaf1
```

### 🌐 Nginx Configuration (Optional)

#### Install Nginx
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Configure Nginx
```bash
# Copy configuration
sudo cp nginx-production.conf /etc/nginx/sites-available/agentdaf1

# Enable site
sudo ln -s /etc/nginx/sites-available/agentdaf1 /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### 📊 Monitoring & Health Checks

#### Application Endpoints
- **Dashboard**: http://localhost:8080
- **Health Check**: http://localhost:8080/api/health
- **Metrics**: http://localhost:8080/api/metrics

#### System Monitoring
```bash
# Check logs
tail -f logs/access.log
tail -f logs/error.log

# Check service status
sudo systemctl status agentdaf1

# Check processes
ps aux | grep gunicorn
```

### 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `wsgi.py` | Production WSGI entry point |
| `gunicorn.conf.py` | Gunicorn server configuration |
| `nginx-production.conf` | Nginx reverse proxy setup |
| `.env.production` | Production environment template |
| `agentdaf1.service` | Systemd service file |
| `requirements-production.txt` | Production dependencies |

### 🛡️ Security Considerations

1. **Change Default Secrets**
   - Update `SECRET_KEY` in `.env`
   - Update `JWT_SECRET_KEY` in `.env`

2. **Firewall Configuration**
   ```bash
   # Allow HTTP/HTTPS
   sudo ufw allow 80
   sudo ufw allow 443
   
   # Allow application port (if direct access)
   sudo ufw allow 8000
   ```

3. **SSL Certificate (Optional)**
   ```bash
   # Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### 📈 Performance Optimization

1. **Database Connection Pooling** (if using database)
2. **Redis Caching** (if using cache)
3. **CDN for Static Assets**
4. **Load Balancing** (multiple instances)

### 🔄 Deployment Commands

#### Start/Stop/Restart
```bash
# Systemd
sudo systemctl start agentdaf1
sudo systemctl stop agentdaf1
sudo systemctl restart agentdaf1

# Direct Gunicorn
pkill -f gunicorn
gunicorn --config gunicorn.conf.py wsgi:app &

# Python Direct
pkill -f simple_app
python simple_app.py &
```

#### Update Deployment
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements-production.txt

# Restart service
sudo systemctl restart agentdaf1
```

### 🐛 Troubleshooting

#### Common Issues
1. **Port Already in Use**
   ```bash
   # Find process
   sudo lsof -i :8000
   # Kill process
   sudo kill -9 <PID>
   ```

2. **Permission Issues**
   ```bash
   # Fix ownership
   sudo chown -R www-data:www-data /path/to/AgentDaf1.1
   # Fix permissions
   sudo chmod -R 755 /path/to/AgentDaf1.1
   ```

3. **Module Not Found**
   ```bash
   # Reinstall dependencies
   pip install -r requirements-production.txt
   ```

### 📋 Production Checklist

- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Logs directory created
- [ ] Service enabled (if using systemd)
- [ ] Nginx configured (if using reverse proxy)
- [ ] Firewall configured
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Health checks configured

---

## 🎯 Production Ready!

Your AgentDaf1.1 gaming dashboard is now configured for production deployment with:
- ✅ High-performance WSGI server
- ✅ Reverse proxy configuration
- ✅ Security headers and rate limiting
- ✅ Systemd auto-start service
- ✅ Production logging
- ✅ Environment management
- ✅ Monitoring endpoints

**Access**: http://localhost (or your domain)
**API**: http://localhost/api/health