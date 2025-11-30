# Verwenden einer offiziellen Python-Laufzeitumgebung als Basis-Image
FROM python:3.12-slim

# Metadaten für das Docker-Projekt
LABEL maintainer="Docker Performance Monitor" \
      version="1.0.0" \
      description="Erweitertes Docker-Container-Performance-Überwachungssystem"

# Umgebungsvariablen für Python festlegen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Systemabhängigkeiten und Python-Pakete installieren
RUN apt-get update && apt-get install -y \
    procps \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Python-Pakete installieren
RUN pip install --no-cache-dir \
    psutil==6.1.0 \
    requests==2.32.3 \
    flask==3.1.0 \
    py-cpuinfo==9.0.0

# Anwendungsverzeichnis erstellen
WORKDIR /app

# Nicht-root-Benutzer für Sicherheit erstellen
RUN groupadd -r monitor && useradd -r -g monitor monitor
RUN chown -R monitor:monitor /app
RUN chmod -R 755 /app

# Anwendungsdateien kopieren
COPY --chown=monitor:monitor src/ /app/src/
COPY --chown=monitor:monitor scripts/ /app/scripts/
COPY --chown=monitor:monitor docker_startup.py /app/
COPY --chown=monitor:monitor requirements.txt /app/

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Notwendige Verzeichnisse erstellen
RUN mkdir -p /app/logs /app/data /app/backups /app/configs && \
    chown -R monitor:monitor /app/logs /app/data /app/backups /app/configs

# Zu nicht-root-Benutzer wechseln
USER monitor

# Überwachungs-Dashboard-Port freigeben
EXPOSE 8080

# Gesundheitsprüfung
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Standardbefehl festlegen
CMD ["/app/scripts/start.sh"]