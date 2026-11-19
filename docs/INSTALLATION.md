# SSS – Installations- und Nutzungshinweise

**SchoolServer Security (SSS)**  
Entwickelt von Adam Gabriel Kraus

## Aktueller Desktop-Client

Der Desktop-Prototyp verwendet PySide6 und startet über die Launcher. Python 3.10+ wird benötigt. Beim ersten Start installieren die Startskripte PySide6 via pip (Internetverbindung nötig).

- Windows: start_sss.bat
- Linux/macOS: start_sss.sh
- Alternativ: pip install -r requirements.txt und python sss_gui.py

ClamAV ist optional. Es muss separat installiert sein und der Befehl clamscan im PATH verfügbar sein. Das Programm zeigt in der GUI das vorhandene Scanresultat, es führt ClamAV nicht mit.


## Projektstatus und Sicherheitswarnung

SSS ist ein Entwicklungsprototyp. Die aktuelle Scannerlogik prüft lesend auf EICAR, SHA-256 und einfache verdächtige Textmuster; bei Quellcode-Dateien werden Prüfhinweise markiert. Es kann Fehlalarme geben und Malware übersehen. Kein produktiver Virenschutz.


## Schul-Konfiguration ZIP

Das Control Center erzeugt lokal ein ZIP-Starterpaket mit Konfigurationsdatei, GUI, Scanner, Logo und Startskripten. Standard und Professional sind momentan Konfigurationsprofile; sie unterscheiden sich noch nicht in Scannerfunktionen.


## Geplanter Plattformausbau

Zentrale Plattform, Accounts, Client-Enrollment, Backend/API, automatische Updateinstallation und rollenbasierte Dashboards sind noch nicht vollständig implementiert.


## Testempfehlung

1. Nur einen eigenen, eigens angelegten Testordner scannen.
2. Scanordner und Ausschlüsse vor dem Scan kontrollieren.
3. Keine echten Schulserver oder sensible Daten einbinden.
4. Erst nach Prüfung und Freigabe durch die zuständige Schul-IT einen Testbetrieb erwägen.

Repository: https://github.com/LordLOLQDH/sss