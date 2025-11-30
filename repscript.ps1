Write-Host "🚀 Starte AgentDaf1.1 Setup..."

Set-Location "C:\Users\flori\Desktop\AgentDaf1.1"

if (-Not (Test-Path ".venv")) {
    Write-Host "📦 Erstelle virtuelle Umgebung..."
    python -m venv .venv
}

Write-Host "🔑 Aktiviere virtuelle Umgebung..."
& .\.venv\Scripts\Activate.ps1

Write-Host "📥 Installiere Python-Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "🌐 Starte Flask Server auf Port 8080..."
python app.py
