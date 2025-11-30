# OpenCode Tools Konfigurationsdokumentation

## Überblick
Dieses Dokument enthält die gelernten Informationen über die Tool-Konfiguration in OpenCode für das AgentDaf1.1 Projekt.

## Tool-Konfigurationshierarchie

### 1. Globale Tool-Konfiguration
Standardmäßig sind alle Tools aktiviert (`true`). Tools können global deaktiviert werden:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "write": false,
    "bash": false,
    "webfetch": true
  }
}
```

### 2. Platzhalter für mehrere Tools
MCP-Server-Tools können mit Platzhaltern gesteuert werden:

```json
{
  "tools": {
    "mymcp_*": false
  }
}
```

### 3. Agentenspezifische Tool-Konfiguration
Globale Einstellungen können pro Agent überschrieben werden:

```json
{
  "tools": {
    "write": true,
    "bash": true
  },
  "agent": {
    "plan": {
      "tools": {
        "write": false,
        "bash": false
      }
    }
  }
}
```

### 4. Markdown-Agenten-Konfiguration
Tools können auch in Markdown-Dateien konfiguriert werden:

**~/.config/opencode/agent/readonly.md**
```markdown
---
description: Read-only analysis agent
mode: subagent
tools:
  write: false
  edit: false
  bash: false
---
Analyze code without making any modifications.
```

## Verfügbare Built-in Tools

### bash
- **Zweck**: Shell-Befehle in der Projektumgebung ausführen
- **Beispiele**: `npm install`, `git status`, beliebige Shell-Befehle
- **Konfiguration**:
```json
{
  "tools": {
    "bash": true
  }
}
```

### edit
- **Zweck**: Vorhandene Dateien durch exakte Zeichenkettenersetzungen modifizieren
- **Verwendung**: Präzise Änderungen durch Textersetzung
- **Konfiguration**:
```json
{
  "tools": {
    "edit": true
  }
}
```

### write
- **Zweck**: Neue Dateien erstellen oder bestehende überschreiben
- **Warnung**: Vorhandene Dateien werden überschrieben
- **Konfiguration**:
```json
{
  "tools": {
    "write": true
  }
}
```

### read
- **Zweck**: Inhalt von Dateien aus der Codebasis lesen
- **Funktion**: Unterstützt Lesen bestimmter Zeilenbereiche bei großen Dateien
- **Konfiguration**:
```json
{
  "tools": {
    "read": true
  }
}
```

### grep
- **Zweck**: Dateiinhalte mit regulären Ausdrücken durchsuchen
- **Funktion**: Volle Regex-Syntax und Dateimusterfilterung
- **Konfiguration**:
```json
{
  "tools": {
    "grep": true
  }
}
```

### glob
- **Zweck**: Dateien durch Mustervergleich finden
- **Beispiele**: `**/*.js`, `src/**/*.ts`
- **Funktion**: Gibt übereinstimmende Dateipfade sortiert nach Änderungsdatum zurück
- **Konfiguration**:
```json
{
  "tools": {
    "glob": true
  }
}
```

### list
- **Zweck**: Dateien und Verzeichnisse in einem angegebenen Pfad auflisten
- **Funktion**: Akzeptiert Glob-Muster zum Filtern der Ergebnisse
- **Konfiguration**:
```json
{
  "tools": {
    "list": true
  }
}
```

### patch
- **Zweck**: Patches auf Dateien anwenden
- **Verwendung**: Nützlich für Änderungen und Patches aus verschiedenen Quellen
- **Konfiguration**:
```json
{
  "tools": {
    "patch": true
  }
}
```

### todowrite
- **Zweck**: Aufgabenlisten während Programmiersitzungen verwalten
- **Funktion**: Organisation mehrstufiger Aufgaben
- **Konfiguration**:
```json
{
  "tools": {
    "todowrite": true
  }
}
```

### todoread
- **Zweck**: Vorhandene Aufgabenlisten lesen
- **Funktion**: Verfolgen von ausstehenden oder erledigten Aufgaben
- **Konfiguration**:
```json
{
  "tools": {
    "todoread": true
  }
}
```

### webfetch
- **Zweck**: Webinhalte abrufen
- **Verwendung**: Dokumentationen nachschlagen, Online-Ressourcen recherchieren
- **Konfiguration**:
```json
{
  "tools": {
    "webfetch": true
  }
}
```

## Interne Tools und ripgrep Integration

### ripgrep-basierte Tools
Tools wie `grep`, `glob` und `list` verwenden intern `ripgrep`:

- **Standardverhalten**: Berücksichtigt `.gitignore`-Suchmuster
- **Ignorierte Dateien**: In `.gitignore` aufgeführte Dateien/Verzeichnisse werden ausgeschlossen

### .ignore Datei
Um normalerweise ignorierte Dateien einzuschließen:

**.ignore im Projektstammverzeichnis:**
```
!node_modules/
!dist/
!build/
```

**Beispiel**: Ermöglicht Suche in `node_modules/`, `dist/`, `build/`, selbst wenn diese in `.gitignore` stehen.

## Benutzerdefinierte Tools

### Eigene Funktionen definieren
Benutzerdefinierte Tools ermöglichen eigene Funktionen, die vom LLM aufgerufen werden können:

- **Definition**: In der Konfigurationsdatei
- **Fähigkeit**: Beliebigen Code ausführen
- **Dokumentation**: Siehe "Erstellung benutzerdefinierter Tools"

## MCP-Server Integration

### Model Context Protocol
MCP-Server ermöglichen Integration externer Tools und Dienste:

- **Datenbankzugriffe**
- **API-Integrationen** 
- **Dienste von Drittanbietern**
- **Dokumentation**: Siehe "Konfiguration von MCP-Servern"

## Best Practices für AgentDaf1.1

### 1. Sicherheitskonfiguration
```json
{
  "tools": {
    "write": true,
    "edit": true,
    "bash": true,
    "webfetch": true
  }
}
```

### 2. Agentenspezifische Einschränkungen
```json
{
  "agent": {
    "code-reviewer": {
      "tools": {
        "write": false,
        "bash": false
      }
    }
  }
}
```

### 3. Projektoptimierung
Für Excel-Dashboard-Projekt relevante Tools aktivieren:
- `write` - Für neue Dashboard-Dateien
- `edit` - Für Code-Modifikationen
- `read` - Für Excel-Datei-Analyse
- `bash` - Für Deployment und Tests
- `webfetch` - Für Dokumentationsabruf

### 4. .ignore Konfiguration
Für AgentDaf1.1 Projekt:
```
# Build-Outputs ignorieren
!build/
!dist/

# Node-Module für Entwicklung
!node_modules/

# Backup-Dateien
!backups/

# Temporäre Dateien
!temp/
```

## Tool-Konfiguration für Entwicklungsumgebung

### Vollständige Entwicklungskonfiguration
```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "write": true,
    "edit": true,
    "read": true,
    "bash": true,
    "grep": true,
    "glob": true,
    "list": true,
    "webfetch": true,
    "todowrite": true,
    "todoread": true,
    "patch": false
  },
  "agent": {
    "security-reviewer": {
      "tools": {
        "write": false,
        "bash": false,
        "edit": false
      }
    }
  }
}
```

Diese Konfiguration ermöglicht:
- Vollständige Entwicklungsfähigkeiten
- Sicherheitsbeschränkungen für Review-Aufgaben
- Projektmanagement mit Todo-Listen
- Code-Analyse und -Modifikation