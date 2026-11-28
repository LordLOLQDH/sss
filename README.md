# SchoolServer Security (SSS)

**SSS 3.2** ist eine lokale Windows-Sicherheitsassistenz in Python. Es wird keine EXE erstellt oder benötigt.

## Projektstruktur

```
sss_main.py
Start-SSS.bat
SSS_Data/
├── assets/
├── modules/
├── tools/
├── requirements.txt
└── version.json
```

## Einfache Einrichtung ohne Administratorrechte

1. Python 3.11 oder neuer für deinen Benutzer installieren. Die normale Benutzerinstallation reicht; SSS braucht keine Adminrechte.
2. [SSS-Windows.zip herunterladen](https://github.com/LordLOLQDH/sss/releases/download/latest/SSS-Windows.zip) und entpacken.
3. **Start-SSS.bat** doppelklicken. Das Skript richtet eine private Python-Umgebung unter `%LOCALAPPDATA%\\SchoolServer Security\\.venv` ein und installiert PySide6 ohne Administratorrechte.
4. Beim ersten Start öffnet sich der Einrichtungsassistent. Wähle Privat oder Schule, Scanordner, Prüfintervall und ob du die lokale KI möchtest.
5. Die Einrichtung ist fertig. Weitere Starts gehen über das Windows-Startmenü.

Schule und Schulserver sind optional. SSS prüft lokal ohne Netzwerk; eine Schulserver-Anbindung ist in dieser Version noch nicht enthalten. Ollama für KI-Erklärungen ist ebenfalls optional.

## Installation und Wartung

SSS kopiert beim ersten Start die Programmdateien in `%LOCALAPPDATA%\\Programs\\SchoolServer Security`. Die Verknüpfungen verwenden die private Python-Umgebung. Der SSS Manager kann die Anwendung reparieren, aktualisieren oder vollständig deinstallieren. Programmupdates ersetzen den Programmordner, lassen Einstellungen, Logs und Quarantäne in deinem Benutzerprofil unangetastet.

## Funktionen

- Lokale Dateiprüfung mit SHA-256 und defensiven Musterprüfungen
- Optionale ClamAV-Prüfung, wenn ClamAV lokal installiert ist
- Quarantäne mit Bestätigung und hash-geprüfter Wiederherstellung
- Optionale lokale KI-Erklärung über Ollama
- Scanordner, Ausschlüsse und Prüfintervall konfigurierbar
- Protokollfenster und lokale Logs
- Update-Prüfung beim Programmstart und bestätigte Installation
- Python-only ZIP-Paket und separater Manager

## Sicherheitshinweis

SSS ist ein Sicherheitsassistenz-Prototyp und kein zertifizierter Virenschutz. Es kann Dateien übersehen und Fehlalarme erzeugen. Untersuchte Dateien werden nicht ausgeführt. Quarantäneaktionen benötigen eine Bestätigung.
