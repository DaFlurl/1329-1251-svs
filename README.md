# AgentDaf1.1 Gaming Dashboard

Live Gaming Dashboard mit erweiterten Analytics und Team-Statistiken.

## 🚀 Features
- **Live Gaming Dashboard** - Echtzeit-Spieler-Ranglisten
- **GitStyle Design** - Modernes dunkles Theme mit Neon-Akzenten
- **PWA Support** - Installierbare Web-App mit Offline-Funktion
- **Responsive Design** - Mobile-First Ansicht für alle Geräte
- **Advanced Analytics** - Interaktive Diagramme und Statistiken
- **Real-time Updates** - Automatische Datenaktualisierung

## 📊 Daten
- **Monday Data** - 412 Spieler (101 Positive, 66 Negative, 115 Combined)
- **Sunday Data** - 472 Spieler (104 Positive, 91 Negative, 129 Combined)
- **Total Records** - 884 Spielerdatensätze

## 🛠️ Technologie
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Frameworks**: Bootstrap 5.3.0, Chart.js 4.4.0
- **PWA**: Service Worker, Web App Manifest
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Inter)

## 📁 Struktur
```
├── index.html                 # Haupt-Dashboard
├── components/                # JavaScript Komponenten
│   ├── theme-manager.js      # Theme-Wechsel
│   ├── data-loader.js       # Daten-Ladung
│   ├── scoreboard.js        # Spieler-Rangliste
│   └── charts.js           # Analytics-Diagramme
├── scripts/
│   └── main.js             # Haupt-Anwendung
├── styles/                  # CSS Stylesheets
│   ├── variables.css        # Design-System
│   ├── dashboard.css       # Haupt-Layout
│   ├── themes.css          # Theme-Variationen
│   └── mobile.css         # Responsive Design
├── data/                    # JSON Datendateien
│   ├── monday_data.json    # Montag-Daten
│   └── scoreboard-data.json # Sonntag-Daten
├── manifest.json            # PWA Manifest
├── service-worker.js        # Offline-Funktionalität
└── convert_excel_to_json.py # Daten-Konverter
```

## 🎯 Installation
```bash
git clone https://github.com/DaFlurl/1329-1251-svs.git
cd 1329-1251-svs
```

## 🔄 Daten-Update
```bash
# Excel zu JSON konvertieren
python convert_excel_to_json.py

# Änderungen deployen
git add .
git commit -m "Update gaming data"
git push origin main
```

## 🌐 Deployment
- **Live URL**: https://daflurl.github.io/1329-1251-svs/
- **GitHub Pages**: Automatischer Deployment von `main` Branch
- **PWA**: Kann als native App installiert werden

## 📱 Features
- **Theme Switching**: Light/Dark/High-Contrast
- **Search & Filter**: Spieler-Suche und Allianz-Filter
- **Export**: CSV-Export für Datenanalyse
- **Fullscreen**: Immersive Dashboard-Erfahrung
- **Offline**: Gecachte Daten für Offline-Nutzung
- **Keyboard Shortcuts**: Power-User Features

## 🎮 Dashboard Tabs
1. **Übersicht** - Top Spieler, Allianz-Ranking, Schnellstatistiken
2. **Spieler** - Vollständige Rangliste mit Suche/Filter
3. **Allianzen** - Detaillierte Allianz-Statistiken
4. **Analytics** - Punkteverteilung, Performance-Trends

## ⌨️ Keyboard Shortcuts
- `Ctrl+Shift+T` - Theme wechseln
- `Ctrl+Shift+D` - Dunkles Theme
- `Ctrl+Shift+L` - Helles Theme
- `Ctrl+R` - Daten aktualisieren
- `Ctrl+E` - Daten exportieren
- `F11` - Vollbild umschalten

## 🤖 Contributing
1. Repository forken
2. Feature Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## 📄 Lizenz
MIT License - Siehe LICENSE Datei für Details.

## 👥 Team
- **Development**: AgentDaf1.1
- **Design**: GitStyle Framework
- **Data**: Gaming Community

---
*Zuletzt aktualisiert: 27. November 2025*