# AgentDaf1.1 Troubleshooting Guide

## Common Issues and Solutions

### 1. Application Startup Issues

#### Problem: Application Won't Start
**Symptoms:**
- Error messages when running `python stable_base.py`
- Port already in use errors
- Module import errors

**Solutions:**

##### Port Already in Use
```bash
# Find process using port 8080
netstat -tulpn | grep :8080
# or on Windows
netstat -ano | findstr :8080

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or change port
export PORT=8081
python stable_base.py
```

##### Module Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall packages
pip install --force-reinstall flask flask-cors pandas openpyxl
```

##### Permission Issues
```bash
# Check file permissions
ls -la stable_base.py
chmod +x stable_base.py

# Check directory permissions
ls -la data/
chmod 755 data/
```

### 2. Database Issues

#### Problem: Database Connection Failed
**Symptoms:**
- "Database connection failed" errors
- SQLite file not found
- Permission denied errors

**Solutions:**

##### SQLite Database Issues
```bash
# Check if database exists
ls -la data/agentdaf1.db

# Create new database
python -c "
import sqlite3
conn = sqlite3.connect('data/agentdaf1.db')
conn.close()
print('Database created')
"

# Check database integrity
sqlite3 data/agentdaf1.db "PRAGMA integrity_check;"

# Repair corrupted database
sqlite3 data/agentdaf1.db ".recover" | sqlite3 data/agentdaf1_repaired.db
mv data/agentdaf1_repaired.db data/agentdaf1.db
```

##### Database Lock Issues
```bash
# Find and remove lock files
find . -name "*.db-journal" -delete
find . -name "*.db-wal" -delete
find . -name "*.db-shm" -delete

# Restart application
python stable_base.py
```

### 3. Excel Processing Issues

#### Problem: Excel Upload Fails
**Symptoms:**
- "Invalid file format" errors
- "File too large" errors
- Processing timeouts

**Solutions:**

##### File Format Issues
```bash
# Check file format
file your_file.xlsx

# Convert to proper format
libreoffice --headless --convert-to xlsx your_file.xls

# Validate Excel file
python -c "
import pandas as pd
try:
    df = pd.read_excel('your_file.xlsx')
    print('File is valid')
    print('Columns:', df.columns.tolist())
    print('Rows:', len(df))
except Exception as e:
    print('Error:', e)
"
```

##### File Size Issues
```bash
# Check file size
ls -lh your_file.xlsx

# Compress large files
python -c "
import pandas as pd
df = pd.read_excel('large_file.xlsx')
df.to_excel('compressed_file.xlsx', engine='openpyxl')
"

# Increase upload limit in configuration
export MAX_CONTENT_LENGTH=52428800  # 50MB
```

### 4. Web Interface Issues

#### Problem: Dashboard Not Loading
**Symptoms:**
- Blank white page
- JavaScript errors
- CSS not loading

**Solutions:**

##### Browser Issues
```bash
# Clear browser cache
# Chrome: Ctrl+Shift+Del
# Firefox: Ctrl+Shift+Del

# Try incognito mode
# Check browser console for errors (F12)

# Test different browser
```

##### Static File Issues
```bash
# Check static files exist
ls -la static/
ls -la static/css/
ls -la static/js/

# Check file permissions
chmod -R 644 static/
chmod -R 755 static/

# Restart application
python stable_base.py
```

### 5. Performance Issues

#### Problem: Slow Response Times
**Symptoms:**
- Pages loading slowly
- High CPU usage
- Memory leaks

**Solutions:**

##### Monitor Performance
```bash
# Check system resources
top
htop
ps aux | grep python

# Monitor memory usage
python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"

# Check database performance
sqlite3 data/agentdaf1.db "EXPLAIN QUERY PLAN SELECT * FROM players ORDER BY score DESC LIMIT 100;"
```

##### Optimize Database
```sql
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_players_score ON players(score DESC);
CREATE INDEX IF NOT EXISTS idx_players_alliance ON players(alliance);

-- Vacuum database
VACUUM;

-- Analyze statistics
ANALYZE;
```

##### Enable Caching
```python
# Add Redis caching
pip install redis

# Update configuration
export REDIS_URL=redis://localhost:6379

# Restart with caching enabled
python stable_base.py
```

### 6. Authentication Issues

#### Problem: Login Fails
**Symptoms:**
- "Invalid credentials" errors
- JWT token errors
- Session issues

**Solutions:**

##### Reset Authentication
```bash
# Check configuration
cat .env | grep -E "(SECRET|JWT)"

# Reset admin password
python -c "
from auth import create_user
create_user('admin', 'newpassword')
print('Admin user created/reset')
"

# Clear session data
rm -rf sessions/
```

##### JWT Token Issues
```bash
# Generate new JWT secret
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Test token generation
python -c "
import jwt
token = jwt.encode({'user_id': 1}, 'your-secret-key', algorithm='HS256')
print('Token:', token)
"
```

### 7. Docker Issues

#### Problem: Docker Container Fails
**Symptoms:**
- Container won't start
- Port binding errors
- Volume mounting issues

**Solutions:**

##### Container Issues
```bash
# Check container logs
docker logs agentdaf1

# Check container status
docker ps -a

# Restart container
docker restart agentdaf1

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

##### Volume Issues
```bash
# Check volume mounts
docker inspect agentdaf1 | grep -A 10 "Mounts"

# Fix permissions
sudo chown -R 1000:1000 data/
sudo chown -R 1000:1000 logs/

# Create missing directories
mkdir -p data/uploads logs
```

### 8. Network Issues

#### Problem: Cannot Access Application
**Symptoms:**
- Connection refused errors
- Timeout errors
- Firewall blocking

**Solutions:**

##### Local Network Issues
```bash
# Check if application is listening
netstat -tulpn | grep :8080

# Test local connection
curl http://localhost:8080/api/health

# Check firewall
sudo ufw status
sudo iptables -L
```

##### Remote Access Issues
```bash
# Check if binding to all interfaces
# In stable_base.py, ensure: app.run(host='0.0.0.0')

# Check router port forwarding
# Forward port 8080 to your machine

# Test remote access
curl http://your-ip:8080/api/health
```

### 9. Memory Issues

#### Problem: Out of Memory Errors
**Symptoms:**
- Application crashes
- "MemoryError" in logs
- System becomes unresponsive

**Solutions:**

##### Monitor Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Monitor Python process
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

##### Optimize Memory Usage
```python
# Add memory optimization to stable_base.py
import gc

# Force garbage collection
gc.collect()

# Limit data processing
def process_large_file(file_path):
    chunk_size = 1000
    for chunk in pd.read_excel(file_path, chunksize=chunk_size):
        process_chunk(chunk)
        gc.collect()
```

### 10. SSL/HTTPS Issues

#### Problem: HTTPS Not Working
**Symptoms:**
- Certificate errors
- Mixed content warnings
- HTTPS redirect loops

**Solutions:**

##### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# Generate new certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

##### Nginx Configuration
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

## Debugging Tools

### 1. Application Debugging
```python
# Enable debug mode
export DEBUG=True
export FLASK_ENV=development

# Add debug endpoints
@app.route('/debug/info')
def debug_info():
    import sys
    import os
    return {
        'python_version': sys.version,
        'environment': dict(os.environ),
        'working_directory': os.getcwd(),
        'modules': list(sys.modules.keys())
    }
```

### 2. Logging Configuration
```python
# Enhanced logging
import logging
from logging.handlers import RotatingFileHandler

def setup_debug_logging(app):
    """Setup detailed logging for debugging."""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    )
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/debug.log', maxBytes=10485760, backupCount=5
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)
```

### 3. Health Check Script
```bash
#!/bin/bash
# health_check.sh - Comprehensive health check

echo "=== AgentDaf1.1 Health Check ==="
echo "Time: $(date)"
echo

# Check if application is running
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "✅ Application: Running"
else
    echo "❌ Application: Not responding"
fi

# Check database
if [ -f "data/agentdaf1.db" ]; then
    echo "✅ Database: Exists"
    sqlite3 data/agentdaf1.db "PRAGMA integrity_check;" | grep -q "ok" && echo "✅ Database: Integrity OK" || echo "❌ Database: Corrupted"
else
    echo "❌ Database: Missing"
fi

# Check memory
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE < 80" | bc -l) )); then
    echo "✅ Memory: ${MEMORY_USAGE}%"
else
    echo "⚠️  Memory: ${MEMORY_USAGE}% (High)"
fi

# Check disk space
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk: ${DISK_USAGE}%"
else
    echo "⚠️  Disk: ${DISK_USAGE}% (High)"
fi

echo
echo "=== Health Check Complete ==="
```

## Getting Help

### 1. Log Analysis
```bash
# Monitor application logs in real-time
tail -f logs/agentdaf1.log

# Search for errors
grep -i error logs/agentdaf1.log

# Find recent issues
tail -100 logs/agentdaf1.log | grep -i error
```

### 2. System Information Collection
```bash
# Create system report
{
    echo "=== System Information ==="
    uname -a
    echo
    echo "=== Python Environment ==="
    python --version
    pip list
    echo
    echo "=== Application Status ==="
    ps aux | grep python
    echo
    echo "=== Network Status ==="
    netstat -tulpn | grep :8080
    echo
    echo "=== Disk Usage ==="
    df -h
    echo
    echo "=== Memory Usage ==="
    free -h
} > system_report.txt
```

### 3. Contact Support
If issues persist:
1. Collect logs and system information
2. Document error messages
3. Note steps to reproduce
4. Check documentation in `/docs/` folder
5. Review GitHub issues (if available)

---

**Troubleshooting Guide Version**: 1.0  
**Last Updated**: November 27, 2025  
**For AgentDaf1.1 v1.1.0**