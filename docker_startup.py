#!/usr/bin/env python3
"""
Docker Start- und Testskript für AgentDaf1.1

Automatisches Starten, Testen und Überwachen der Docker-Container
mit Health-Checks und Performance-Monitoring.
"""

import subprocess
import time
import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docker_startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DockerManager:
    """Klasse für Docker-Container-Management."""
    
    def __init__(self, project_dir: str):
        """Initialisiere Docker Manager."""
        self.project_dir = Path(project_dir)
        self.compose_file = self.project_dir / 'docker-compose.yml'
        self.dockerfile = self.project_dir / 'Dockerfile'
        self.container_name = 'agentdaf1.1'
        self.nginx_container = 'agentdaf1.1-nginx'
        
    def check_docker_installation(self):
        """Überprüfe Docker-Installation."""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Docker Version: {version}")
                return {
                    'installed': True,
                    'version': version,
                    'message': 'Docker ist korrekt installiert'
                }
            else:
                return {
                    'installed': False,
                    'error': 'Docker konnte nicht ausgeführt werden',
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'installed': False,
                'error': 'Docker-Check timeout'
            }
        except FileNotFoundError:
            return {
                'installed': False,
                'error': 'Docker ist nicht installiert'
            }
        except Exception as e:
            logger.error(f"Docker-Check fehlgeschlagen: {str(e)}")
            return {
                'installed': False,
                'error': str(e)
            }
    
    def build_images(self):
        """Baue Docker-Images."""
        logger.info("Baue Docker-Images...")
        
        try:
            # Haupt-Image bauen
            result = subprocess.run(
                ['docker', 'build', '-t', 'agentdaf1.1', '.'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Haupt-Image erfolgreich gebaut")
                build_success = True
            else:
                logger.error(f"Fehler beim Bauen der Haupt-Image: {result.stderr}")
                build_success = False
            
            # Test-Image für Integrationstests bauen
            test_result = subprocess.run(
                ['docker', 'build', '-t', 'agentdaf1.1-test', '-f', 'docker-compose.yml', '--target', 'app'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if test_result.returncode == 0:
                logger.info("Test-Image erfolgreich gebaut")
                test_success = True
            else:
                logger.error(f"Fehler beim Bauen der Test-Image: {test_result.stderr}")
                test_success = False
            
            return {
                'main_image': build_success,
                'test_image': test_success,
                'main_build_output': result.stdout if build_success else result.stderr,
                'test_build_output': test_result.stdout if test_success else test_result.stderr
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Build timeout")
            return {
                'main_image': False,
                'test_image': False,
                'error': 'Build timeout nach 300 Sekunden'
            }
        except Exception as e:
            logger.error(f"Build fehlgeschlagen: {str(e)}")
            return {
                'main_image': False,
                'test_image': False,
                'error': str(e)
            }
    
    def start_containers(self):
        """Starte Docker-Container."""
        logger.info("Starte Docker-Container...")
        
        try:
            # Container im Hintergrund starten
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("Container erfolgreich gestartet")
                return {
                    'started': True,
                    'message': 'Container laufen im Hintergrund',
                    'compose_output': result.stdout
                }
            else:
                logger.error(f"Fehler beim Starten: {result.stderr}")
                return {
                    'started': False,
                    'error': result.stderr,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Start timeout")
            return {
                'started': False,
                'error': 'Start timeout nach 60 Sekunden'
            }
        except Exception as e:
            logger.error(f"Start fehlgeschlagen: {str(e)}")
            return {
                'started': False,
                'error': str(e)
            }
    
    def stop_containers(self):
        """Stoppe Docker-Container."""
        logger.info("Stoppe Docker-Container...")
        
        try:
            result = subprocess.run(
                ['docker-compose', 'down'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Container erfolgreich gestoppt")
                return {
                    'stopped': True,
                    'message': 'Container gestoppt'
                }
            else:
                logger.error(f"Fehler beim Stoppen: {result.stderr}")
                return {
                    'stopped': False,
                    'error': result.stderr,
                    'returncode': result.returncode
                }
                
        except Exception as e:
            logger.error(f"Stop fehlgeschlagen: {str(e)}")
            return {
                'stopped': False,
                'error': str(e)
            }
    
    def check_container_health(self, max_attempts: int = 5, delay: int = 10):
        """Überprüfe Container-Health."""
        logger.info("Überprüfe Container-Health...")
        
        for attempt in range(max_attempts):
            try:
                # Health-Check für Haupt-Container
                app_health = subprocess.run(
                    ['docker', 'ps', '-f', f"name={self.container_name}", '--format', '"{{.Status}}"'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Health-Check für Nginx-Container
                nginx_health = subprocess.run(
                    ['docker', 'ps', '-f', f"name={self.nginx_container}", '--format', '"{{.Status}}"'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                app_running = 'running' in app_health.stdout.lower()
                nginx_running = 'running' in nginx_health.stdout.lower()
                
                if app_running and nginx_running:
                    # HTTP-Health-Check
                    http_check = subprocess.run(
                        ['curl', '-f', '-s', 'http://localhost:8080/health'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if http_check.returncode == 0 and 'healthy' in http_check.stdout.lower():
                        logger.info(f"Container sind gesund (Versuch {attempt + 1})")
                        return {
                            'healthy': True,
                            'app_status': 'running',
                            'nginx_status': 'running',
                            'http_status': 'healthy'
                        }
                    else:
                        logger.warning(f"HTTP-Health-Check fehlgeschlagen (Versuch {attempt + 1})")
                
                else:
                    logger.warning(f"Container nicht vollständig laufend (Versuch {attempt + 1})")
                
                if attempt < max_attempts - 1:
                    logger.info(f"Warte {delay} Sekunden vor nächstem Versuch...")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Health-Check fehlgeschlagen: {str(e)}")
        
        return {
            'healthy': False,
            'error': 'Maximale Versuche erreicht ohne Erfolg'
        }
    
    def get_container_logs(self, lines: int = 50):
        """Hole Container-Logs."""
        try:
            result = subprocess.run(
                ['docker-compose', 'logs', '--tail', str(lines)],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                'success': result.returncode == 0,
                'logs': result.stdout,
                'lines': lines
            }
            
        except Exception as e:
            logger.error(f"Log-Abruf fehlgeschlagen: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_container_stats(self):
        """Hole Container-Statistiken."""
        try:
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', '"table"', self.container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'success': result.returncode == 0,
                'stats': result.stdout,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stats-Abruf fehlgeschlagen: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_test(self):
        """Führe umfassende Tests durch."""
        logger.info("Starte umfassende Docker-Tests...")
        
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': []
        }
        
        # Test 1: Docker-Installation
        logger.info("Test 1: Docker-Installation")
        docker_check = self.check_docker_installation()
        test_results['tests'].append({
            'name': 'Docker-Installation',
            'result': docker_check,
            'status': 'PASS' if docker_check.get('installed') else 'FAIL'
        })
        
        # Test 2: Image-Build
        logger.info("Test 2: Image-Build")
        build_result = self.build_images()
        test_results['tests'].append({
            'name': 'Image-Build',
            'result': build_result,
            'status': 'PASS' if build_result.get('main_image') and build_result.get('test_image') else 'FAIL'
        })
        
        # Test 3: Container-Start
        logger.info("Test 3: Container-Start")
        start_result = self.start_containers()
        test_results['tests'].append({
            'name': 'Container-Start',
            'result': start_result,
            'status': 'PASS' if start_result.get('started') else 'FAIL'
        })
        
        # Warte für Start
        if start_result.get('started'):
            logger.info("Warte 5 Sekunden für Health-Check...")
            time.sleep(5)
        
        # Test 4: Health-Check
        logger.info("Test 4: Health-Check")
        health_result = self.check_container_health()
        test_results['tests'].append({
            'name': 'Health-Check',
            'result': health_result,
            'status': 'PASS' if health_result.get('healthy') else 'FAIL'
        })
        
        # Test 5: Log-Abruf
        logger.info("Test 5: Log-Abruf")
        log_result = self.get_container_logs(10)
        test_results['tests'].append({
            'name': 'Log-Abruf',
            'result': log_result,
            'status': 'PASS' if log_result.get('success') else 'FAIL'
        })
        
        # Test 6: Stats-Abruf
        logger.info("Test 6: Stats-Abruf")
        stats_result = self.get_container_stats()
        test_results['tests'].append({
            'name': 'Stats-Abruf',
            'result': stats_result,
            'status': 'PASS' if stats_result.get('success') else 'FAIL'
        })
        
        # Test 7: Container-Stop
        logger.info("Test 7: Container-Stop")
        stop_result = self.stop_containers()
        test_results['tests'].append({
            'name': 'Container-Stop',
            'result': stop_result,
            'status': 'PASS' if stop_result.get('stopped') else 'FAIL'
        })
        
        # Ergebnisse speichern
        results_file = self.project_dir / 'docker_test_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test-Ergebnisse gespeichert: {results_file}")
        
        # Zusammenfassung
        passed_tests = sum(1 for test in test_results['tests'] if test['status'] == 'PASS')
        total_tests = len(test_results['tests'])
        
        logger.info("/n" + "="*60)
        logger.info("DOCKER TEST ZUSAMMENFASSUNG")
        logger.info("="*60)
        
        for i, test in enumerate(test_results['tests'], 1):
            status_icon = "✅" if test['status'] == 'PASS' else "❌"
            print(f"{i}. {test['name']}: {status_icon} {test['status']}")
            
            if test['status'] == 'FAIL' and 'error' in test['result']:
                print(f"   Fehler: {test['result']['error']}")
        
        print(f"/nGesamt: {passed_tests}/{total_tests} Tests bestanden")
        logger.info("="*60)
        
        return test_results
    
    def save_test_results(self, results: dict):
        """Speichere Test-Ergebnisse."""
        results_file = self.project_dir / 'docker_test_results.json'
        
        # Erstelle Verzeichnis falls nötig
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test-Ergebnisse gespeichert: {results_file}")

def main():
    """Hauptfunktion."""
    logger.info("AgentDaf1.1 Docker Start- und Testskript")
    logger.info("="*60)
    
    # Projektverzeichnis ermitteln
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    if not project_dir.exists():
        logger.info(f"Fehler: Projektverzeichnis nicht gefunden: {project_dir}")
        sys.exit(1)
    
    logger.info(f"Projektverzeichnis: {project_dir}")
    
    # Docker Manager initialisieren
    docker_manager = DockerManager(project_dir)
    
    # Menü anzeigen
    logger.info("/nVerfügbare Aktionen:")
    logger.info("1. Docker-Installation überprüfen")
    logger.info("2. Images bauen")
    logger.info("3. Container starten")
    logger.info("4. Health-Check durchführen")
    logger.info("5. Logs abrufen")
    logger.info("6. Statistiken abrufen")
    logger.info("7. Container stoppen")
    logger.info("8. Umfassende Tests durchführen")
    logger.info("9. Test-Ergebnisse anzeigen")
    logger.info("0. Beenden")
    
    while True:
        try:
            choice = input("/nBitte wählen Sie eine Aktion (0-9): ").strip()
            
            if choice == '0':
                logger.info("Beende...")
                break
            
            elif choice == '1':
                result = docker_manager.check_docker_installation()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '2':
                result = docker_manager.build_images()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '3':
                result = docker_manager.start_containers()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '4':
                result = docker_manager.check_container_health()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '5':
                result = docker_manager.get_container_logs(20)
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '6':
                result = docker_manager.get_container_stats()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '7':
                result = docker_manager.stop_containers()
                logger.info(f"Ergebnis: {result}")
            
            elif choice == '8':
                result = docker_manager.run_comprehensive_test()
                print(f"Ergebnisse gespeichert in: docker_test_results.json")
            
            elif choice == '9':
                # Test-Ergebnisse anzeigen
                results_file = project_dir / 'docker_test_results.json'
                if results_file.exists():
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                        
                        logger.info("/n" + "="*60)
                        logger.info("LETZTE TEST-ERGEBNISSE")
                        logger.info("="*60)
                        
                        if 'tests' in results:
                            for i, test in enumerate(results['tests'], 1):
                                status_icon = "✅" if test['status'] == 'PASS' else "❌"
                                print(f"{i}. {test['name']}: {status_icon} {test['status']}")
                                
                                if test['status'] == 'FAIL' and 'error' in test.get('result', {}):
                                    print(f"   Fehler: {test['result']['error']}")
                        else:
                            logger.info("Keine Test-Ergebnisse gefunden")
                else:
                    logger.info("Keine Test-Ergebnisse gefunden")
            
            else:
                logger.info("Ungültige Auswahl!")
                
        except KeyboardInterrupt:
            logger.info("/nProgramm wird beendet...")
            break
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {str(e)}")
            logger.info(f"Fehler: {str(e)}")

if __name__ == '__main__':
    main()