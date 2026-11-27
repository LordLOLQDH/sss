# SchoolServer Security (SSS)

**Lokaler Sicherheitsassistent für Windows**  
Entwickelt von Adam Gabriel Kraus.

SSS ist eine eigenständige Desktop-App mit lokaler Datei-Prüfung, nachvollziehbaren Hinweisen und optionalen KI-Erklärungen. Es gibt derzeit **keinen Installer**.

## Download und Start

1. Lade das aktuelle Paket **SSS-Windows.zip** von der [SSS-Downloadseite](https://lordlolqdh.github.io/sss/download.html) oder aus den [GitHub Releases](https://github.com/LordLOLQDH/sss/releases).
2. Entpacke die ZIP-Datei in einen eigenen Ordner.
3. Starte **SSS.exe**.
4. Beim ersten Start öffnet sich automatisch der Einrichtungsassistent. Name, optional Schule/Gerät, KI und Scanordner werden eingerichtet; es gibt keine Rollenabfrage.
5. Bei späteren Starts erkennt SSS das gespeicherte Profil und öffnet direkt die Anwendung.

Profil und Einstellungen werden lokal unter **%LOCALAPPDATA%\\SchoolServer Security\\settings.json** gespeichert.

## Erste Einrichtung

### 1. Profil
Name ist optional eingetragen, Schule und Gerätename sind optional. Eine Rollenabfrage gibt es nicht; im Profil wird intern IT Manager gespeichert. Diese Angaben bleiben lokal auf dem Gerät. Eine zentrale Schulserver-Anbindung ist noch nicht implementiert.

### 2. Lokale KI mit Ollama
SSS unterstützt aktuell Ollama. Andere KI-Anbieter und Cloud-APIs sind noch nicht integriert.

1. Öffne https://ollama.com/download/windows und installiere Ollama.
2. Öffne PowerShell oder Windows Terminal.
3. Führe **ollama pull qwen2.5:3b** aus.
4. Warte, bis der Modell-Download abgeschlossen ist.
5. Klicke im SSS-Assistenten auf **Verbindung testen**.

Die KI läuft lokal. Die KI-Erklärung ist eine ergänzende Einschätzung und kann Scannerergebnisse nicht überschreiben.

### 3. Scanordner
Wähle die zu prüfenden Ordner und das Prüfintervall. Scanordner, Ausschlüsse, Prüfintervall und Dateigrößenlimit können später im übersichtlichen Einstellungen-Fenster geändert werden.

## Funktionen

- PySide6-Desktopoberfläche
- Konfigurierbare Scanordner und Ausschlüsse
- SHA-256-Dateihashes
- Optionale ClamAV-Erkennung, sofern clamscan installiert ist
- Defensive Musterprüfungen für ausgewählte Skriptdateien
- Nutzerbestätigte, reversible Quarantäne
- Hash-geprüfte Wiederherstellung aus der Quarantäne
- Optionale lokale KI-Erklärungen via Ollama\n- Modell-Download direkt über den KI-Dialog\n- Einstellungen mit Scan- und KI-Bereichen\n- Windows-EXE-Updater, der die veröffentlichte ZIP lädt, die neue EXE nach dem Beenden einsetzt und neu startet

## Entwicklerstart

Python 3.10+:

**py -3 -m pip install -r requirements.txt**  
**py -3 sss_gui.py**

Alternativ unter Windows **Start-SSS.bat** starten. Das Skript richtet eine lokale virtuelle Python-Umgebung ein und startet SSS. Es ist kein Installationsassistent.

## Windows-Build

GitHub Actions baut nach Änderungen auf main eine eigenständige Windows-Anwendung und veröffentlicht **SSS-Windows.zip** als Vorab-Release. Das Paket enthält **SSS.exe**; ein Setup- oder Installationsprogramm wird nicht verwendet.

## Update\n\nDer Updater ist für die portable Windows-EXE gedacht. Er prüft die veröffentlichte Version und lädt das Windows-ZIP. Die EXE wird erst nach dem Schließen des laufenden Programms ersetzt und anschließend neu gestartet.\n\n## Sicherheitshinweise

SSS ist ein Entwicklungsprojekt und **kein zertifizierter Virenschutz oder Endpoint-Protection-Ersatz**. Es kann Schadsoftware übersehen und Fehlalarme erzeugen. Untersuchte Dateien werden nicht ausgeführt. Quarantäneaktionen erfordern eine Bestätigung. Der Einsatz auf Schulgeräten benötigt die Freigabe der zuständigen IT.
