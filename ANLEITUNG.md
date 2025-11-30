# AgentDaf1.1 - Ordneranleitung und Hinweise

## 📁 Ordnerstruktur

```
AgentDaf1.1/
├── 📁 data/                    # Datienspeicherung (persistent)
│   ├── uploads/               # Temporäre Excel-Uploads
│   └── processed/             # Verarbeitete Ergebnisse
│
├── 📁 logs/                     # Logdateien (persistent)
│   ├── app.log                # Anwendungs-Logs
│   ├── docker_startup.log       # Docker-Startskript-Logs
│   └── error.log              # Fehler-Logs
│
├── 📁 docs/                     # Dokumentation
│   ├── README.md               # Projektdokumentation
│   ├── API.md                # API-Referenz
│   ├── DEPLOYMENT.md          # Bereitstellungsanleitung
│   └── user_manual.md         # Benutzerhandbuch
│
├── 🔧 src/                      # Quellcode
│   ├── config/               # Konfigurationsmodule
│   │   ├── settings.py          # App-Einstellungen
│   │   └── logging.py           # Logging-Konfiguration
│   │
│   ├── core/                  # Kernfunktionen
│   │   ├── excel_workflow.py     # Excel-Verarbeitungs-Engine
│   │   ├── dashboard_generator.py # Dashboard-Generator
│   │   └── github_integration.py # GitHub-Integration
│   │
│   ├── api/                   # Flask-API
│   │   ├── routes.py            # Endpunkte
│   │   ├── models.py            # Datenmodelle
│   │   └── middleware.py        # Middleware (CORS, etc.)
│   │
│   ├── web/                   # Web-Oberfläche
│   │   ├── static/             # CSS/JS/Assets
│   │   │   ├── css/
│   │   │   │   └── dashboard.css
│   │   │   └── js/
│   │   │       └── dashboard.js
│   │   │
│   │   └── templates/           # HTML-Vorlagen
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       └── components/
│   │           ├── charts.html
│   │           ├── tables.html
│   │           └── filters.html
│   │
│   └── utils/                  # Hilfsmodule
│       ├── file_utils.py          # Dateioperationen
│       ├── date_utils.py          # Datumsfunktionen
│       └── validation.py        # Validierung
│
├── 🧪 tests/                     # Testdateien
│   ├── test_excel_processor.py
│   ├── test_dashboard_generator.py
│   ├── test_workflow_engine.py
│   └── test_memory_manager.py
│
├── 📋 requirements.txt            # Python-Abhängigkeiten
├── 🐳 Dockerfile                 # Docker-Image-Definition
├── 🔄 docker-compose.yml          # Container-Orchestrierung
├── 🚀 docker_startup.py           # Docker-Management-Skript
├── 📄 PROJECT_PLAN.md            # Projektplan
├── 📖 README.md                 # Hauptdokumentation
└── 📄 PROJEKT_PLAN.md           # Detaillierte Struktur
```

## 🎯 Wichtige Ordner und ihre Verwendung

### 📁 **data/** - Datienspeicherung
- **uploads/** - Temporäre Excel-Dateien von Benutzern
  - Automatisches Bereinigen nach 7 Tagen
  - Dateigrößenlimit: 16MB
- **processed/** - Verarbeitete Ergebnisse und Dashboards
  - Permanente Speicherung von Analyseergebnissen
  - HTML-Dashboards werden hier abgelegt

### 📁 **logs/** - Protokollierung
- **app.log** - Anwendungsprotokolle mit Rotation
- **docker_startup.log** - Docker-Management-Aktivitäten
- **error.log** - Zentralisierte Fehlerprotokollierung

### 🔧 **src/** - Quellcode
#### **config/** - Konfiguration
- **settings.py** - Zentrale App-Konfiguration
  - Datenbankpfade, API-Schlüssel, Debug-Modus
- **logging.py** - Logging-Konfiguration
  - Verschiedene Log-Level (DEBUG, INFO, WARNING, ERROR)

#### **core/** - Geschäftslogik
- **excel_workflow.py** - Haupt-Engine für Excel-Verarbeitung
- **dashboard_generator.py** - HTML-Dashboard-Generierung
- **github_integration.py** - GitHub-API-Integration

#### **api/** - REST-API
- **routes.py** - Flask-Endpunkte und Request-Handler
- **models.py** - Datenstrukturen und JSON-Schemas
- **middleware.py** - Authentifizierung, CORS, Fehlerbehandlung

#### **web/** - Web-Oberfläche
- **static/** - Frontend-Assets
  - **css/dashboard.css** - Modernes responsives Design
  - **js/dashboard.js** - Interaktive Charts mit Chart.js
- **templates/** - HTML-Vorlagen
  - **dashboard.html** - Hauptdashboard mit Tabben
  - **components/** - Wiederverwendbare Komponenten

#### **utils/** - Hilfsfunktionen
- **file_utils.py** - Sichere Dateioperationen
- **date_utils.py** - Datumsformatierung (DE/EN)
- **validation.py** - Eingabevalidierung und Bereinigung

### 🧪 **tests/** - Qualitätssicherung
- Unit-Tests für alle Kernmodule
- Integrationstests für Workflows

### 📋 **Konfigurationsdateien**
- **requirements.txt** - Python-Abhängigkeiten mit Versionen
- **Dockerfile** - Multi-Stage-Build für optimale Performance
- **docker-compose.yml** - Container-Orchestrierung mit Health-Checks

### 📖 **Dokumentation**
- **README.md** - Übersicht und Quick-Start
- **docs/user_manual.md** - Detailliertes Benutzerhandbuch
- **docs/API.md** - Technische API-Referenz
- **docs/DEPLOYMENT.md** - Schritt-für-Schritt Bereitstellungsanleitung

## 🚀 Optimierungshinweise

### 1. **Performance-Optimierungen**
- **Docker-Image**: python:3.11-slim (Kleine Basis, nur benötigte Pakete)
- **Multi-Stage-Build**: Reduziert Image-Größe durch Caching
- **Resource-Limits**: CPU/Memory-Limits verhindern Systemüberlastung

### 2. **Sicherheitsmaßnahmen**
- **Non-Root-User**: Container läuft als unprivilegierter Benutzer
- **Dateigrößen-Limit**: 16MB für Uploads verhindert DoS-Angriffe
- **Input-Validierung**: Alle Benutzereingaben werden validiert und bereinigt

### 3. **Monitoring- und Logging**
- **Health-Checks**: Container- und HTTP-Health-Checks
- **Strukturierte Logs**: Verschiedene Log-Level für bessere Fehlersuche
- **Performance-Metriken**: Docker-Stats und Ressourcennutzung

## 🔧 Wichtige Skripte und Befehle

### Docker-Management
```bash
# Container starten
python docker_startup.py

# Interaktives Menü (Option 1)
python docker_startup.py

# Umfassende Tests (Option 8)
python docker_startup.py
```

### Anwendung starten
```bash
# Entwicklungsmodus
python src/main.py

# Produktionsmodus
export DEBUG=false PORT=8080
python src/main.py
```

### Wichtige Konfiguration
```yaml
# config/app_config.yaml
debug: false
port: 8080
github:
  token: "IHR_GITHUB_TOKEN"
  repo: "username/repository"
```

## 📊 Dashboard-Funktionen

### Hauptfeatures
- **📊 Excel-Upload**: Drag & Drop oder Dateiauswahl
- **📈 Multi-Tab-Dashboard**: Verschiedene Ansichten in Tabs
- **📈 Interaktive Charts**: Chart.js mit Zoom/Filter
- **🔍 Echtzeit-Suche**: Live-Suche in Daten
- **📤 Daten-Export**: PDF, Excel, CSV
- **🔄 Auto-Refresh**: Automatische Datenaktualisierung
- **🔗 GitHub-Integration**: 1-Klick-Updates

### API-Endpunkte
- `POST /upload` - Excel-Datei hochladen
- `GET /dashboard/<filename>` - Dashboard anzeigen
- `POST /api/github/update` - GitHub-Integration
- `GET /health` - Health-Check

## 🛠️ Fehlerbehandlung

### Log-Level
- **DEBUG**: Detaillierte Informationen für Entwicklung
- **INFO**: Normale Operationsprotokollierung
- **WARNING**: Warnungen bei Problemen
- **ERROR**: Kritische Fehler

### Log-Dateien
- **app.log** - Anwendungsprotokolle
- **docker_startup.log** - Docker-Management-Aktivitäten
- **error.log** - Alle kritischen Fehler

## 🌐 Web-Zugriff

### Entwicklungsumgebung
```
http://localhost:8080
```

### Produktionsumgebung
```
http://localhost:8080
```

## 🔐 Sicherheitshinweise

1. **API-Schlüssel** in Environment-Variablen speichern
2. **Datei-Uploads** immer validieren (Größe, Typ)
3. **Container** nicht als root laufen lassen
4. **Regelmäßige Updates** durchführen

## 📞 Häufige Probleme

### Container startet nicht?
```bash
# Docker prüfen
docker --version

# Container neu bauen
docker-compose down
docker-compose up --build
```

### Dashboard nicht erreichbar?
```bash
# Port prüfen
netstat -tulpn | grep 8080

# Logs prüfen
python docker_startup.py  # Option 5 für Logs
```

---
**Hinweis**: Diese Anleitung bietet einen Überblick über die vollständige Projektstruktur und die wichtigsten Funktionen für die tägliche Arbeit mit dem AgentDaf1.1 System.