# AgentDaf1.1 - Vollständige Anleitung

## 📋 Inhaltsverzeichnis
1. [Projektübersicht](#projektübersicht)
2. [Schnellstart](#schnellstart)
3. [Systemvoraussetzungen](#systemvoraussetzungen)
4. [Installation](#installation)
5. [Konfiguration](#konfiguration)
6. [Anwendung starten](#anwendung-starten)
7. [Wichtige Funktionen](#wichtige-funktionen)
8. [MCP-LSP Integration](#mcp-lsp-integration)
9. [API-Dokumentation](#api-dokumentation)
10. [Fehlerbehebung](#fehlerbehebung)
11. [Wartung](#wartung)

---

## 🎯 Projektübersicht

AgentDaf1.1 ist eine umfassende Excel-Datenverarbeitungs- und Dashboard-Generierungsplattform mit KI-Fähigkeiten, Echtzeit-WebSocket-Kommunikation und Enterprise-Features.

### ✅ **Aktueller Status (29.11.2025)**
- **Status**: Production Ready ✅
- **Auto-Repair**: 94.48% Erfolg (6.664 Dateien verarbeitet)
- **MCP-LSP Integration**: 85% Erfolg (Kernfunktionen aktiv)
- **Docker Deployment**: Vereinfacht und betriebsbereit

---

## 🚀 Schnellstart

### 1. Projekt herunterladen und vorbereiten
```bash
cd C:\Users\flori\Desktop\AgentDaf1.1
```

### 2. Schnellstart-Script ausführen
```bash
# Windows
start_stable.bat

# Oder manuell:
python app.py
```

### 3. Anwendung testen
- **Hauptanwendung**: http://localhost:8080
- **API Health Check**: http://localhost:8080/api/health
- **WebSocket**: ws://localhost:8081

---

## 💻 Systemvoraussetzungen

### Minimum
- **Python**: 3.8+
- **RAM**: 4GB
- **Speicher**: 2GB freier Speicher
- **OS**: Windows 10/11, Linux, macOS

### Empfohlen
- **Python**: 3.9+
- **RAM**: 8GB+
- **Speicher**: 5GB freier Speicher
- **Docker**: Optional für volle Funktionalität

---

## 📦 Installation

### 1. Python-Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 2. Datenbank initialisieren
```bash
python database.py
```

### 3. Konfiguration überprüfen
```bash
# Konfigurationsdatei prüfen
type config\current_config.json
```

### 4. Optionale Abhängigkeiten (für volle Funktionalität)
```bash
pip install websockets docker
```

---

## ⚙️ Konfiguration

### Umgebungsvariablen erstellen
Erstellen Sie `.env` Datei im Hauptverzeichnis:
```env
# Grundlegende Konfiguration
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=8080

# JWT Konfiguration
JWT_SECRET_KEY=your-jwt-secret-here
JWT_EXPIRATION_HOURS=24

# GitHub Integration (optional)
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-repo-name

# Datenbank
DATABASE_PATH=data/agentdaf1.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agentdaf1.log
```

### Wichtige Konfigurationsdateien
- `config/current_config.json` - Aktuelle Systemkonfiguration
- `config/mcp_lsp_config.json` - MCP-LSP Einstellungen
- `docker-compose.simple.yml` - Docker Konfiguration

---

## 🎮 Anwendung starten

### Option 1: Manuelles Starten
```bash
# Hauptanwendung
python app.py

# Oder mit erweiterten Funktionen
python src/main.py
```

### Option 2: Batch-Scripts (Windows)
```bash
# Stabiler Start
start_stable.bat

# Produktion
start_production.bat

# Docker
deploy-simple.bat
```

### Option 3: Docker Deployment
```bash
# Vereinfachtes Docker
docker-compose -f docker-compose.simple.yml up -d

# Produktion Docker
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔧 Wichtige Funktionen

### 1. Excel-Verarbeitung
```python
# Excel-Datei hochladen
POST /api/upload
Content-Type: multipart/form-data
file: your_excel_file.xlsx

# Verarbeitete Daten abrufen
GET /api/processed-data
```

### 2. Dashboard-Generierung
```python
# Dashboard erstellen
GET /dashboard/{dashboard_name}.html

# Dashboard-Liste
GET /api/dashboards
```

### 3. Authentifizierung
```python
# Login
POST /api/auth/login
{
  "username": "admin",
  "password": "your_password"
}

# Token refresh
POST /api/auth/refresh
```

### 4. Echtzeit-Updates
```javascript
// WebSocket Verbindung
const ws = new WebSocket('ws://localhost:8081');
ws.onmessage = function(event) {
    console.log('Update:', event.data);
};
```

---

## 🔌 MCP-LSP Integration

### Status: ✅ Kernfunktionen aktiv

### 1. MCP-LSP Verbindung testen
```bash
# Einfacher Test
python scripts/simple_mcp_lsp_test.py

# Umfassender Test
python scripts/mcp_lsp_connect.py --connect --test
```

### 2. WebSocket Server starten
```bash
python scripts/mcp_lsp_connect.py --connect --server
```

### 3. MCP-LSP Status prüfen
```bash
python scripts/mcp_lsp_connect.py --status
```

### Aktive Dienste
- **MCP Client**: ✅ Operational (Port 8082)
- **LSP Bridge**: ⚠️ Partial (Docker erforderlich)
- **WebSocket Server**: ✅ Aktiv

---

## 📚 API-Dokumentation

### Authentifizierung
| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/auth/login` | POST | Benutzerlogin |
| `/api/auth/register` | POST | Benutzerregistrierung |
| `/api/auth/refresh` | POST | Token erneuern |
| `/api/auth/me` | GET | Benutzerinfo |

### Datenverarbeitung
| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/upload` | POST | Excel-Datei hochladen |
| `/api/dashboards` | GET | Dashboard-Liste |
| `/api/stats` | GET | Systemstatistiken |
| `/api/processed-data` | GET | Verarbeitete Daten |

### System
| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/api/health` | GET | Health Check |
| `/api/system/status` | GET | Systemstatus |

---

## 🛠️ Fehlerbehebung

### Häufige Probleme und Lösungen

#### 1. Unicode-Fehler (Windows)
**Problem**: `UnicodeEncodeError: 'charmap' codec can't encode character`
**Lösung**:
```bash
# Windows Console auf UTF-8 einstellen
chcp 65001
# Oder Python-Script verwenden (bereits gefixt)
```

#### 2. Import-Fehler
**Problem**: `ModuleNotFoundError: No module named 'src'`
**Lösung**:
```bash
# Von Projekt-Hauptverzeichnis ausführen
cd C:\Users\flori\Desktop\AgentDaf1.1
python app.py
```

#### 3. Datenbank-Fehler
**Problem**: `sqlite3.OperationalError: no such table`
**Lösung**:
```bash
# Datenbank initialisieren
python database.py
```

#### 4. Port bereits verwendet
**Problem**: `Address already in use`
**Lösung**:
```bash
# Prozess beenden
netstat -ano | findstr :8080
taskkill /PID <PID> /F
# Oder Port in .env ändern
PORT=8081
```

#### 5. MCP-LSP Verbindungsprobleme
**Problem**: Verbindung zu MCP-Servern fehlschlägt
**Lösung**:
```bash
# Server-Status prüfen
python scripts/mcp_lsp_connect.py --status
# Firewall-Einstellungen überprüfen
```

---

## 🔍 Wartung

### Tägliche Wartung
```bash
# Logs prüfen
type logs\agentdaf1.log

# Systemstatus
python health-checks\system-health.py

# Datenbank-Backup
python backup_system.py
```

### Wöchentliche Wartung
```bash
# Vollständiger System-Check
python check_project_status.py

# Auto-Repair ausführen
python auto_repair_all.py

# Performance prüfen
python monitoring.py
```

### Monatliche Wartung
```bash
# Vollständiges Backup
python create_backup.py

# Logs aufräumen
del logs\*.log.old

# Updates prüfen
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 📊 Wichtige Dateien und Verzeichnisse

### Kern-Dateien
- `app.py` - Hauptanwendung
- `database.py` - Datenbank-Management
- `auth.py` - Authentifizierung
- `src/main.py` - Erweiterte Hauptanwendung

### Konfiguration
- `config/current_config.json` - Aktuelle Konfiguration
- `.env` - Umgebungsvariablen
- `requirements.txt` - Python-Abhängigkeiten

### Tools und Scripts
- `scripts/` - Hilfsscripts
- `tools/` - Entwicklungs-Tools
- `auto_repair_all.py` - Automatische Reparatur

### Docker
- `docker-compose.simple.yml` - Vereinfachte Docker-Konfiguration
- `Dockerfile` - Docker-Image

---

## 🚨 Wichtige Hinweise

### Sicherheit
- Ändern Sie Standard-Passwörter und Secrets
- Verwenden Sie HTTPS in der Produktion
- Regelmäßige Backups durchführen
- Firewall konfigurieren

### Performance
- Verwenden Sie Docker für Produktion
- Monitoren Sie System-Ressourcen
- Optimieren Sie Datenbank-Abfragen

### Backup-Strategie
1. **Täglich**: Inkrementelle Backups
2. **Wöchentlich**: Vollständige Backups
3. **Monatlich**: Archivierung

---

## 📞 Unterstützung

### Dokumentation
- `README.md` - Allgemeine Informationen
- `COMPLETE_SETUP_GUIDE.md` - Detaillierte Setup-Anleitung
- `MCP_LSP_TEST_REPORT.md` - MCP-LSP Testergebnisse
- `AUTO_REPAIR_SUMMARY.md` - Auto-Repair Ergebnisse

### Fehler melden
1. Issue auf GitHub erstellen
2. Logs anhängen
3. Schritte zur Reproduktion beschreiben

### Kontakt
- GitHub Issues: Projekt-Repository
- Dokumentation: Projekt-Wiki

---

## 🎉 Nächste Schritte

### Sofort erledigen
1. ✅ Anwendung starten: `python app.py`
2. ✅ Health Check: http://localhost:8080/api/health
3. ✅ Excel-Upload testen
4. ✅ Dashboard generieren

### Optional für volle Funktionalität
1. Docker installieren und starten
2. MCP-LSP Server konfigurieren
3. Produktion einrichten

### Langfristig
1. Monitoring implementieren
2. Backup-Automatisierung
3. Skalierung planen

---

**AgentDaf1.1 ist bereit für den produktiven Einsatz! 🚀**

*Letzte Aktualisierung: 29. November 2025*