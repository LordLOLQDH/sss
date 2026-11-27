# SchoolServer Security (SSS)

**Lokaler Sicherheitsassistent für Windows, als Python-Projekt.** Keine EXE und kein Installer.

## Download und Start

1. Lade das [Python-Quellcode-ZIP](https://github.com/LordLOLQDH/sss/archive/refs/heads/main.zip) oder die [Downloadseite](https://lordlolqdh.github.io/sss/download.html).
2. ZIP in einen eigenen Ordner entpacken.
3. **Start-SSS.bat** starten. Beim ersten Start erstellt das Skript eine lokale virtuelle Umgebung und installiert die Abhängigkeiten.
4. SSS öffnet den Einrichtungsdialog.

Python 3.10+ muss installiert sein. Beim Windows-Python-Setup die Option "Add Python to PATH" aktivieren.

## Updates

SSS kann unter **Updates** die Version auf GitHub prüfen. Bei einem neuen Stand lädt der Updater das Quellcode-ZIP herunter, prüft die benötigten Dateien und legt das Update bereit. Nach dem Schließen des Programms werden die Dateien kopiert und SSS über Start-SSS.bat erneut gestartet.

## Lokale KI

SSS unterstützt lokale Ollama-Modelle. Installiere Ollama über https://ollama.com/download/windows, öffne es und lade das in SSS ausgewählte Modell über **KI einrichten**. KI-Analyse ist optional. Wenn Ollama oder das Modell nicht erreichbar ist, zeigt SSS einen konkreten Fehler.

## Funktionen

- Lokale Prüfungen und SHA-256
- Defensive Mustererkennung für ausgewählte Scriptdateien
- Optional ClamAV, falls lokal installiert
- Nutzerbestätigte Quarantäne und Hash-geprüfte Wiederherstellung
- Lokale KI-Erklärung via Ollama
- Konfigurierbare Scanordner, Ausschlüsse und Zeitintervalle
- Logs und kontrollierbarer Windows-Anmeldeautostart
- Quellcode-Updater

## Entwicklerstart

```bat
py -3 -m pip install -r requirements.txt
py -3 sss_gui.py
```

SSS ist ein Prototyp, kein zertifizierter Virenschutz. Es kann Dateien übersehen und Fehlalarme erzeugen. Untersuchte Dateien werden nicht ausgeführt. Quarantäneaktionen benötigen eine Bestätigung.