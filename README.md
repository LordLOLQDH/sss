# SchoolServer Security (SSS)

**Schulserver-Sicherheit. Entwickelt von Adam Gabriel Kraus.**

SchoolServer Security ist ein Entwicklungsprojekt für die lokale Datei-Sicherheitsprüfung.

🌐 **Projektwebsite:** https://lordlolqdh.github.io/sss/  
📦 **Quellcode:** https://github.com/LordLOLQDH/sss

## Aktueller Desktop-Client

Version 0.1.0 enthält:
- Modernes Desktop-GUI auf Basis von PySide6 (sss_gui.py)
- Manuelle, lesende Scans konfigurierter Ordner
- SHA-256-Hashes
- EICAR-Testsignatur und einfache Textmuster
- Optionale ClamAV-Anbindung (wenn clamscan installiert ist)
- Ausschlussordner, Dateigrößenlimit und Scanoptionen
- JSON-Berichtexport
- Logo im Desktopfenster

Die GUI greift auf die vorhandenen Scanfunktionen aus sss_scanner.py zurück. Die alte Tkinter-Oberfläche ist dort weiterhin vorhanden, wird aber durch die Startskripte nicht mehr als Standard gestartet.


## Start

Voraussetzung: Python 3.10 oder neuer. Beim ersten Start wird PySide6 anhand von requirements.txt installiert (Internetverbindung erforderlich).

- Windows: start_sss.bat
- Linux/macOS: start_sss.sh

ClamAV ist optional und muss separat installiert sein, damit clamscan verfügbar ist.


## Editionen und Plattform-Konzept

Standard und Professional sind derzeit Konfigurationsprofile im Control Center. Sie schalten noch keine unterschiedlichen Scanner-Funktionen frei. Backend, Cloud-Synchronisierung, zentrale Liveüberwachung, Multi-Serververwaltung, automatische Updates und echte serverseitige Rollen sind noch nicht implementiert.


## Dokumentation

- [Installations- und Nutzungshinweise](docs/INSTALLATION.md)
- [Programm-Anleitung](docs/PROGRAMM.md)
- [Updater-Status](docs/UPDATER.md)
- [Sicherheits- und Datenschutzkonzept](docs/SECURITY.md)


## Entwicklungsstatus

**Prototyp 0.1.0 – nicht produktionsbereit.** Scans sind lesend. Textmuster können Fehlalarme auslösen und Malware übersehen. Der Scanner ist kein Ersatz für einen professionellen Virenschutz. Bitte nicht auf einem echten Schulserver einsetzen, bevor die zuständige IT den Code geprüft und den Einsatz freigegeben hat.


---

**SchoolServer Security (SSS)**  
*by Adam Gabriel Kraus*
