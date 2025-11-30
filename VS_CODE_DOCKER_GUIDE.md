# Docker Container Steuerung über VS Code

## 1. Docker Extension für VS Code installieren
- Öffne VS Code
- Gehe zu Extensions (Ctrl+Shift+X)
- Suche nach "Docker"
- Installiere "Docker" von Microsoft

## 2. Docker Container in VS Code verwalten

### Container starten/stoppen:
```bash
# Im VS Code Terminal
docker-compose up -d          # Container starten
docker-compose down            # Container stoppen
docker-compose ps             # Container Status anzeigen
```

### Container logs anzeigen:
```bash
docker-compose logs agentdaf1-app      # Logs der App
docker-compose logs -f agentdaf1-app   # Live Logs
```

### In Container reinconnecten:
```bash
docker exec -it agentdaf1-app bash     # Bash im Container
```

## 3. VS Code Docker Extension Features:
- 🐳 **Container Liste**: Alle Container anzeigen
- 📊 **Container Status**: Running/Stopped/Restarting
- 📋 **Logs**: Direkt in VS Code anzeigen
- 🖥️ **Terminal**: In Container öffnen
- 📁 **Volumes**: Dateien im Container durchsuchen

## 4. Docker Compose in VS Code:
- Rechtsklick auf `docker-compose.yml`
- "Compose Up" wählen
- Oder "Compose Down" zum stoppen

## 5. Debugging im Container:
- Füge `.vscode/launch.json` hinzu
- Konfiguriere Remote Debugging
- Setze Breakpoints im Code

## 6. Dateien im Container bearbeiten:
- Rechtsklick auf Container → "Attach Visual Studio Code"
- Oder: VS Code Remote Development Extension

## 7. Nützliche VS Code Befehle:
- `Ctrl+Shift+P` → "Docker: "
- "Docker: Show Logs"
- "Docker: Restart Container"
- "Docker: Remove Container"

## 8. Hot Reload für Entwicklung:
```yaml
# docker-compose.yml für Entwicklung
volumes:
  - .:/app  # Lokalen Code einbinden
  - /app/node_modules  # Node Module nicht überschreiben
```

## 9. Environment Variablen in VS Code:
- Erstelle `.vscode/settings.json`
```json
{
    "docker.composeFile": "docker-compose.yml",
    "docker.host": "npipe:////./pipe/docker_engine"
}
```

## 10. Troubleshooting in VS Code:
- Docker Panel → Problems
- Container Logs prüfen
- Port Konflikte checken
- Environment Variablen verifizieren