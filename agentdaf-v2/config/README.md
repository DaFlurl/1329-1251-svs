# AgentDaf1.1 Configuration

## Overview
This directory contains configuration files for the AgentDaf1.1 dashboard system.

## Configuration Files

### 1. Main Configuration (`config.json`)
Primary configuration for the dashboard system including:
- Project settings (name, version, environment)
- Server configuration (host, port, debug)
- Database paths and file locations
- Feature toggles and options
- GitHub integration settings
- API configuration
- Logging configuration

### 2. Repository Configuration (`repo_config.txt`)
Git repository and deployment settings:
- Private and public repository names
- Local directory paths
- File deployment rules
- Branch configuration

### 3. Application Settings (`settings.py`)
Python application configuration:
- Flask settings and security
- File upload restrictions
- Path configurations
- Environment variables

## Configuration Structure

```
config/
├── config.json              # Main dashboard configuration
├── repo_config.txt           # Repository deployment settings
├── settings.py              # Python application settings
├── dashboard.json           # Dashboard-specific settings
├── database.json            # Database configuration
└── deployment.json          # Deployment settings
```

## Usage

### Loading Configuration
```python
# Load main configuration
import json
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Load application settings
from config.settings import app_config
```

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DEBUG`: Enable/disable debug mode
- `GITHUB_TOKEN`: GitHub API token
- `GITHUB_REPO`: Repository name for deployment

## Configuration Categories

### Dashboard Settings
- Auto-refresh interval
- Theme preferences
- Display options
- Player limits

### Data Settings
- File paths
- Backup settings
- History retention
- Export formats

### Server Settings
- Host and port
- CORS configuration
- Rate limiting
- Timeouts

### GitHub Integration
- Repository information
- Deployment settings
- API configuration
- Branch management

## Security Notes

⚠️ **Important**: 
- Never commit sensitive data like API keys
- Use environment variables for secrets
- Keep `.env` files out of version control
- Regularly rotate secret keys

## Deployment Configuration

The dashboard supports multiple deployment methods:
1. **GitHub Pages** (Primary)
2. **Docker Container**
3. **Direct Server**
4. **Development Mode**

Each method has specific configuration requirements documented in the respective files.