# OpenCode Konfigurationsdokumentation

## Überblick
Dieses Dokument enthält die gelernten Informationen über die OpenCode JSON-Konfiguration für das AgentDaf1.1 Projekt.

## Konfigurationsformat
OpenCode unterstützt sowohl JSON als auch JSONC (JSON mit Kommentaren).

### Beispielkonfiguration (opencode.jsonc)
```json
{
  "$schema": "https://opencode.ai/config.json",
  // Theme configuration
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
}
```

## Konfigurationsstandorte und Priorität

### 1. Globale Konfiguration
- **Pfad**: `~/.config/opencode/opencode.json`
- **Verwendung**: Für globale Einstellungen wie Themes, Provider, Tastenkombinationen

### 2. Projektkonfiguration
- **Pfad**: `opencode.json` im Projektstammverzeichnis
- **Verwendung**: Projektspezifische Anbieter oder Modi
- **Git**: Kann bedenkenlos in Git eingecheckt werden

### 3. Benutzerdefinierter Pfad
- **Umgebungsvariable**: `OPENCODE_CONFIG`
- **Beispiel**: `export OPENCODE_CONFIG=/path/to/my/custom-config.json`

### 4. Benutzerdefiniertes Verzeichnis
- **Umgebungsvariable**: `OPENCODE_CONFIG_DIR`
- **Beispiel**: `export OPENCODE_CONFIG_DIR=/path/to/my/config-directory`

## Konfigurationszusammenführung
- Konfigurationen werden **zusammengeführt**, nicht ersetzt
- Tiefe Zusammenführung mit Konfliktauflösung
- Spätere Konfigurationen überschreiben frühere bei Schlüsselkonflikten
- Nicht konfliktbehaftete Einstellungen bleiben erhalten

### Beispiel der Zusammenführung
Globale Konfiguration:
```json
{
  "theme": "opencode",
  "autoupdate": true
}
```

Projektkonfiguration:
```json
{
  "model": "anthropic/claude-sonnet-4-5"
}
```

Finale Konfiguration (alle drei Einstellungen):
```json
{
  "theme": "opencode",
  "autoupdate": true,
  "model": "anthropic/claude-sonnet-4-5"
}
```

## Wichtige Konfigurationsabschnitte

### TUI-Konfiguration
```json
{
  "tui": {
    "scroll_speed": 3,
    "scroll_acceleration": {
      "enabled": true
    }
  }
}
```

### Tools-Konfiguration
```json
{
  "tools": {
    "write": false,
    "bash": false
  }
}
```

### Modell-Provider
```json
{
  "provider": {},
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

### Theme-Konfiguration
```json
{
  "theme": "dark"
}
```

### Agenten-Konfiguration
```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

### Share-Konfiguration
```json
{
  "share": "manual"  // "manual", "auto", "disabled"
}
```

### Benutzerdefinierte Befehle
```json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5"
    }
  }
}
```

### Tastenkombinationen
```json
{
  "keybinds": {}
}
```

### Automatische Aktualisierung
```json
{
  "autoupdate": false  // false, "notify", true
}
```

### Formatierer
```json
{
  "formatter": {
    "prettier": {
      "disabled": true
    },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```

### Berechtigungen
```json
{
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

### MCP-Server
```json
{
  "mcp": {}
}
```

### Anweisungen
```json
{
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]
}
```

### Deaktivierte Provider
```json
{
  "disabled_providers": ["openai", "gemini"]
}
```

## Variablenersetzung

### Umgebungsvariablen
Format: `{env:VARIABLE_NAME}`
```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### Dateiinhalte
Format: `{file:path/to/file}`
```json
{
  "instructions": ["./custom-instructions.md"],
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

## Dateipfad-Regeln
- Relativ zum Konfigurationsdateiverzeichnis
- Absolute Pfade mit `/` oder `~` Beginn

## Verwendungszwecke für Variablen
- Sensitive Daten (API-Schlüssel) in separaten Dateien speichern
- Große Anweisungsdateien einbinden
- Gemeinsame Konfigurationsabschnitte wiederverwenden

## Schema-Validierung
- Schema definiert in: `https://opencode.ai/config.json`
- Editoren sollten Autovervollständigungen und Validierung bereitstellen

## Best Practices für AgentDaf1.1

1. **Projektkonfiguration** im Stammverzeichnis platzieren
2. **Sensible Daten** mit `{file:}` Referenzen speichern
3. **Modell-Konfiguration** projektspezifisch anpassen
4. **Tools** entsprechend Projektanforderungen aktivieren/deaktivieren
5. **Git-Kompatibilität** sicherstellen (keine sensiblen Daten direkt in JSON)

## Aktuelle AgentDaf1.1 Konfiguration
Die erstellte `opencode.json` enthält:
- Projektspezifische Service-Konfigurationen
- Aktivierte/Deaktivierte Tools
- Docker- und Deployment-Einstellungen
- Sicherheits- und Monitoring-Konfigurationen
- Pfad- und Abhängigkeitsdefinitionen