# Optimierter Dockerfile für AgentDaf1.1
FROM python:3.11-slim

# Metadaten
LABEL maintainer="AgentDaf1.1 Dashboard System"
LABEL description="Excel Dashboard mit Web-Interface und GitHub Integration"
LABEL version="2.0"

# Arbeitsverzeichnis
WORKDIR /app

# System-Updates und Abhängigkeiten
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY src/ ./src/
COPY requirements.txt .

# Nicht-root-Benutzer für Sicherheit erstellen
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Volume für persistente Daten
VOLUME ["/app/data", "/app/logs"]

# Exposed Port
EXPOSE 8080

# Health-Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Startup-Command
CMD ["python", "src/main.py"]