# AgentDaf1.1 - AGENTS.md

## Project Overview

AgentDaf1.1 is a comprehensive Excel data processing and dashboard generation platform with advanced AI capabilities, real-time WebSocket communication, and enterprise-grade features.

## Architecture

### Core Components

- **Flask Web Application**: Main API server with authentication
- **Excel Processing Engine**: Advanced data extraction and analysis
- **Dashboard Generator**: Dynamic HTML dashboard creation
- **WebSocket Service**: Real-time updates and notifications
- **Database Layer**: SQLite with comprehensive data management
- **Authentication System**: JWT-based security with role management

### Advanced Features

- **AI Tools**: Code analysis, test generation, performance profiling
- **Memory Management**: Working, episodic, and semantic memory systems
- **Task Management**: Async task scheduling and execution
- **Performance Monitoring**: Real-time system metrics and alerting
- **Auto-Repair**: Self-healing capabilities for common issues

## Development Status

### ✅ Working Components
- Basic Flask application with routes
- SQLite database with full CRUD operations
- JWT authentication system
- Excel file processing with pandas/openpyxl
- WebSocket service for real-time updates
- Configuration management system

### ❌ Issues to Fix
- Missing core modules (dashboard_generator, task_manager, performance_monitor)
- Import errors in main application
- Docker deployment complexity
- API integration gaps
- Test suite failures

## Task Management

### High Priority Tasks
1. Fix critical import errors
2. Create missing core modules
3. Integrate WebSocket service
4. Simplify Docker setup
5. Implement security fixes

### Medium Priority Tasks
- Add comprehensive error handling
- Implement caching layer
- Add API documentation
- Performance optimization
- Monitoring and health checks

### Future Enhancements
- Advanced AI features
- Quantum computing integration
- Metaverse capabilities
- Consciousness uploading (theoretical)

## Configuration

### Environment Variables
```
SECRET_KEY=your-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=8080
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-repo
JWT_SECRET_KEY=your-jwt-secret
```

### Database Setup
- SQLite database: `data/agentdaf1.db`
- Automatic table creation on startup
- Sample data initialization available

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info

### Data Processing
- `POST /api/upload` - Excel file upload
- `GET /api/dashboards` - List dashboards
- `GET /api/stats` - System statistics
- `GET /api/processed-data` - Processed data

### WebSocket
- `ws://localhost:8081` - Real-time updates
- Authentication required for private channels

## Development Guidelines

### Code Structure
```
src/
├── api/           # API endpoints
├── core/          # Core business logic
├── tools/         # Utility tools
├── config/        # Configuration
└── web/           # Web assets

services/          # Microservices
tools/             # Development tools
tests/             # Test suites
config/            # Configuration files
```

### Best Practices
- Use type hints for all functions
- Implement comprehensive error handling
- Add logging for debugging
- Write unit tests for new features
- Follow PEP 8 style guidelines

## Deployment

### Docker Setup
```bash
# Build and run
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.production.yml up -d
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py

# Start application
python app.py
```

## Monitoring

### Health Checks
- `/api/health` - Application health
- WebSocket connection status
- Database connectivity
- System resource usage

### Performance Metrics
- CPU and memory usage
- Request response times
- Database query performance
- Error rates and alerts

## Security

### Authentication
- JWT tokens with expiration
- Role-based access control
- Password hashing with bcrypt
- Session management

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

## Testing

### Test Coverage
- Unit tests for core components
- Integration tests for API endpoints
- Performance tests for data processing
- Security tests for authentication

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Run test suite
4. Update documentation
5. Submit pull request

### Code Review
- Ensure all tests pass
- Check code quality with flake8
- Verify security implications
- Update documentation as needed

## Troubleshooting

### Common Issues
- Import errors: Check Python path and module installation
- Database errors: Verify SQLite file permissions
- WebSocket issues: Check port availability
- Docker errors: Verify Docker daemon status

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose output
python app.py --verbose
```

## Future Roadmap

### Phase 1: Core Fixes (Week 1-2)
- Fix import errors
- Complete missing modules
- Integrate components
- Basic testing

### Phase 2: Enhancement (Week 3-4)
- Performance optimization
- Security improvements
- Advanced features
- Documentation

### Phase 3: Advanced Features (Month 2)
- AI integration
- Advanced analytics
- Real-time collaboration
- Enterprise features

### Phase 4: Future Tech (Month 3+)
- Quantum computing
- Metaverse integration
- Advanced AI capabilities
- Consciousness features

## Support

### Documentation
- `README.md` - General information
- `COMPLETE_SETUP_GUIDE.md` - Setup instructions
- `PRODUCTION_DEPLOYMENT.md` - Deployment guide
- `TESTING_STRATEGY.md` - Testing guidelines

### Contact
- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Documentation: Project Wiki

---

**Note**: This document is a living document and will be updated as the project evolves. Last updated: 2025-11-27