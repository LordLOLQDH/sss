# SchoolServer Security (SSS)

**SSS 2.2.0 ist eine Python-Anwendung mit einer zentralen Hauptdatei.** Keine EXE, kein Installer und keine BAT-Datei zum Starten.

## Start

1. Python 3.11 oder neuer installieren.
2. Repository-ZIP herunterladen und entpacken.
3. Im SSS-Ordner ein Terminal öffnen.
4. Einmalig Abhängigkeiten installieren:

```powershell
py -3 -m pip install -r requirements.txt
```

5. Hauptprogramm starten:

```powershell
py -3 sss_gui.py
```

**Hauptdatei: `sss_gui.py`**. Scanner, Ollama-Anbindung, Quarantäne, Logs, Einstellungen und Updater sind darin integriert. `version.json` enthält die Versionsanzeige und Updatehinweise. Die weiteren alten Moduldateien sind für den Start der neuen Hauptdatei nicht erforderlich.

## Funktionen

- Lokale Dateiprüfung mit SHA-256 und defensiven Musterprüfungen
- Optionale ClamAV-Prüfung, wenn ClamAV lokal installiert ist
- Quarantäne mit Bestätigung und Hash-geprüfter Wiederherstellung
- Lokale KI-Erklärung über Ollama
- GUI-Einstellungen für Scanordner, Ausschlüsse und Prüfintervall
- Protokollfenster und Logdatei
- Updates direkt über die GUI; vor dem Ersetzen wird eine Sicherung der Hauptdatei angelegt

## Hinweise

Beim ersten Start kann SSS nach Scanordnern fragen. Ollama ist optional. Installiere Ollama separat und lade das konfigurierte Modell im KI-Fenster.

SSS ist ein Sicherheitsassistenz-Prototyp, kein zertifizierter Virenschutz. Es kann Dateien übersehen und Fehlalarme erzeugen. Untersuchte Dateien werden nicht ausgeführt. Quarantäneaktionen benötigen eine Bestätigung.
