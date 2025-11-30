# AgentDaf1.1 User Manual

## Getting Started

### System Requirements
- Python 3.8+ (recommended: 3.14.0)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB RAM minimum
- 1GB disk space

### Quick Start

#### 1. Launch the Application
```bash
# Navigate to project directory
cd AgentDaf1.1

# Install dependencies
pip install flask flask-cors pandas openpyxl

# Start the application
python stable_base.py
```

#### 2. Access the Dashboard
Open your web browser and go to:
- **Local**: http://localhost:8080
- **Network**: http://your-ip:8080

## Dashboard Features

### Main Dashboard View
The main dashboard provides an overview of gaming statistics:

#### 1. **Live Scoreboard**
- Real-time player rankings
- Score updates every 30 seconds
- Sortable columns (Rank, Name, Score, Alliance)

#### 2. **Player Statistics**
- Individual player performance metrics
- Historical data tracking
- Alliance membership information

#### 3. **Alliance Rankings**
- Team-based statistics
- Member count and total scores
- Alliance comparison tools

#### 4. **Navigation Menu**
- **Home**: Main dashboard view
- **Database**: Data management interface
- **Auth**: User authentication
- **Enterprise**: Advanced features
- **Monitoring**: System health
- **Test**: System testing

## Working with Excel Files

### Supported File Formats
- **Excel Files**: .xlsx, .xls
- **Data Structure**: Player names, scores, alliances
- **File Size**: Up to 10MB recommended

### Upload Process

#### 1. Navigate to Upload Section
- Click "Upload Excel" in the navigation menu
- Or access directly at http://localhost:8080/upload

#### 2. Select and Upload File
1. Click "Choose File" button
2. Select your Excel file
3. Click "Upload" to process

#### 3. Processing Results
- **Success**: Data appears in dashboard
- **Errors**: Detailed error messages provided
- **Validation**: Automatic data format checking

### Expected Excel Format

#### Player Data Format
| Column | Required | Format | Example |
|--------|----------|--------|---------|
| Name | Yes | Text | "PlayerName" |
| Score | Yes | Number | 10000 |
| Alliance | No | Text | "AllianceName" |
| Rank | No | Number | 1 |

#### Alliance Data Format
| Column | Required | Format | Example |
|--------|----------|--------|---------|
| Alliance Name | Yes | Text | "AllianceName" |
| Members | Yes | Number | 10 |
| Total Score | Yes | Number | 50000 |

## System Monitoring

### Health Check
Access system health at http://localhost:8080/api/health

**Health Information:**
- System status (healthy/unhealthy)
- Uptime and performance metrics
- Database connection status
- Memory and CPU usage

### Performance Metrics
- **Response Times**: API endpoint performance
- **Request Rates**: System load monitoring
- **Error Rates**: Error tracking and alerts

## Authentication

### User Login
1. Navigate to http://localhost:8080/auth
2. Enter credentials:
   - Username: admin
   - Password: password (change in production)
3. Click "Login"

### JWT Token Usage
After login, you'll receive a JWT token for API access:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/api/data
```

## API Usage

### Basic API Calls

#### Get All Data
```bash
curl http://localhost:8080/api/data
```

#### Get Players Only
```bash
curl http://localhost:8080/api/players
```

#### Get Alliances Only
```bash
curl http://localhost:8080/api/alliances
```

### Upload via API
```bash
curl -X POST -F "file=@your_file.xlsx" http://localhost:8080/api/upload
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
**Problem**: Port 8080 already in use
**Solution**: 
```bash
# Find process using port
netstat -tulpn | grep :8080
# Kill process or change port
export PORT=8081
python stable_base.py
```

#### 2. Excel Upload Fails
**Problem**: Invalid file format
**Solution**: 
- Check file is .xlsx or .xls
- Verify required columns exist
- Ensure file size < 10MB

#### 3. Dashboard Not Loading
**Problem**: Browser cache issue
**Solution**: 
- Clear browser cache
- Try incognito mode
- Check browser console for errors

#### 4. Data Not Displaying
**Problem**: Database connection issue
**Solution**: 
- Check database file exists
- Verify file permissions
- Restart application

### Error Messages

#### File Upload Errors
- **"Invalid file format"**: Use .xlsx or .xls files
- **"Missing required columns"**: Check Excel structure
- **"File too large"**: Reduce file size under 10MB

#### System Errors
- **"Database connection failed"**: Restart application
- **"Authentication failed"**: Check login credentials
- **"Rate limit exceeded"**: Wait before retrying

## Advanced Features

### Real-time Updates
The dashboard automatically refreshes every 30 seconds. You can also:
- Manual refresh with F5
- Disable auto-refresh in settings
- Use WebSocket for instant updates

### Data Export
Export dashboard data in various formats:
- **CSV**: For spreadsheet applications
- **JSON**: For programmatic use
- **PDF**: For reports and printing

### Custom Configuration
Modify application behavior:
```bash
# Edit configuration
nano .env

# Common settings
DEBUG=False
PORT=8080
AUTO_REFRESH=30
MAX_FILE_SIZE=10485760  # 10MB
```

## Security Best Practices

### Production Deployment
1. **Change Default Passwords**: Update admin credentials
2. **Use HTTPS**: Configure SSL/TLS
3. **Firewall**: Restrict access to necessary ports
4. **Regular Updates**: Keep dependencies updated

### Data Protection
- **Regular Backups**: Backup database frequently
- **Access Control**: Limit user permissions
- **Audit Logs**: Monitor system access
- **Data Validation**: Validate all inputs

## Support and Resources

### Getting Help
1. **Documentation**: Read this manual completely
2. **Health Check**: Visit /api/health for system status
3. **Logs**: Check application logs for errors
4. **Tests**: Run test suite for diagnostics

### Contact Information
- **Documentation**: /docs/ folder
- **API Reference**: /docs/API_REFERENCE.md
- **Complete Guide**: /docs/COMPLETE_DOCUMENTATION.md

### Version Information
- **Current Version**: 1.1.0
- **Release Date**: November 27, 2025
- **Compatibility**: Python 3.8+

---

**Last Updated**: November 27, 2025  
**Manual Version**: 1.0  
**For AgentDaf1.1 v1.1.0**