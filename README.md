# SchoolServer Security (SSS)

**SSS 2.3.0** ist eine Python-Desktopanwendung mit einer zentralen Hauptdatei. Es gibt keine EXE und keine BAT-Datei.

## Projektstruktur

```text
sss_main.py
SSS_Data/
├── assets/
├── modules/
├── requirements.txt
└── version.json
```

Die Anwendung installiert sich beim ersten Start in das Benutzerprofil unter `%LOCALAPPDATA%\\Programs\\SchoolServer Security`. Sie erstellt eine Verknüpfung im Windows-Startmenü und einen Eintrag im Autostart-Ordner. Im Startmenü ist sie unter **SchoolServer Security** auffindbar.

## Erster Start

1. Python 3.11 oder neuer installieren.
2. [Python-App-Paket herunterladen](https://github.com/LordLOLQDH/sss/releases/download/latest/SSS-Windows-Python.zip) und entpacken.
3. Im SSS-Ordner ein Terminal öffnen.
4. Abhängigkeiten installieren:

```powershell
py -3 -m pip install -r SSS_Data\\requirements.txt
```

5. Starten:

```powershell
py -3 sss_main.py
```

Beim ersten Start wird die App in den Benutzerordner kopiert und von dort gestartet. Weitere Starts erfolgen über das Windows-Startmenü.

## Funktionen

- Lokale Dateiprüfung mit SHA-256 und defensiven Musterprüfungen
- Optionale ClamAV-Prüfung, wenn ClamAV lokal installiert ist
- Quarantäne mit Bestätigung und Hash-geprüfter Wiederherstellung
- Optionale lokale KI-Erklärung über Ollama
- GUI-Einstellungen für Scanordner, Ausschlüsse und Prüfintervall
- Protokollfenster und lokale Logs
- Automatische Update-Prüfung beim Programmstart
- ZIP-Updater für die Hauptdatei und den gesamten Ordner `SSS_Data`
- Vollständige Deinstallation mit Entfernung der SSS-Dateien, Einstellungen, Quarantäne, Startmenü- und Autostart-Verknüpfungen

Bei der Deinstallation bleibt auf dem Desktop eine einzelne Abschiedsdatei zurück. Eine separat installierte Ollama-Anwendung wird nicht entfernt.

## Sicherheitshinweis

SSS ist ein Sicherheitsassistenz-Prototyp und kein zertifizierter Virenschutz. Es kann Dateien übersehen und Fehlalarme erzeugen. Untersuchte Dateien werden nicht ausgeführt. Quarantäneaktionen benötigen eine Bestätigung.
