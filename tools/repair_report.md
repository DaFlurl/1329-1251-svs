# AgentDaf1.1 Auto-Repair Report
Generated: 2025-11-27 07:52:54

## 📊 Summary
- Total Issues: 10
- Critical Issues: 4
- Warnings: 6

## 🔍 Docker Services
🔴 **Docker Error**
   - Message: Error checking Docker services: 404 Client Error for http+docker://localnpipe/v1.52/containers/7d992032bb79bfbaa1abb60226fff390f940e35c272f827f1d698dc695fe368b/json: Not Found ("No such container: 7d992032bb79bfbaa1abb60226fff390f940e35c272f827f1d698dc695fe368b")
   - Fix: Check Docker daemon status

## 🔍 Python Deps
🟡 **Missing Package**
   - Message: Package opentelemetry-api is not installed
   - Fix: Run: pip install opentelemetry-api

🟡 **Missing Package**
   - Message: Package opentelemetry-sdk is not installed
   - Fix: Run: pip install opentelemetry-sdk

🟡 **Missing Package**
   - Message: Package opentelemetry-exporter-jaeger is not installed
   - Fix: Run: pip install opentelemetry-exporter-jaeger

🟡 **Missing Package**
   - Message: Package opentelemetry-exporter-prometheus is not installed
   - Fix: Run: pip install opentelemetry-exporter-prometheus

🟡 **Missing Package**
   - Message: Package asyncpg is not installed
   - Fix: Run: pip install asyncpg

🟡 **Missing Package**
   - Message: Package scikit-learn is not installed
   - Fix: Run: pip install scikit-learn

## 🔍 Config
🔴 **Missing Config**
   - Message: Configuration file docker-compose.messaging.yml is missing
   - Fix: Create or restore docker-compose.messaging.yml

🔴 **Missing Config**
   - Message: Configuration file shared/monitoring/telemetry.py is missing
   - Fix: Create or restore shared/monitoring/telemetry.py

🔴 **Missing Config**
   - Message: Configuration file shared/events/event_bus.py is missing
   - Fix: Create or restore shared/events/event_bus.py

## 🔧 Auto-Fix Results
- Fixes Attempted: 10
- Fixes Successful: 6
- Fixes Failed: 4
