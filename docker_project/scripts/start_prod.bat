@echo off
echo Starting AgentDaf1.1 Production Server...
cd /d "C:\Users\flori\Desktop\AgentDaf1.1\docker_project"
set HOST=0.0.0.0
set PORT=8080
set DEBUG=False
python src/main.py
pause
