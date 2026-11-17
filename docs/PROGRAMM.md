# SSS Desktop-Programm

**SchoolServer Security (SSS) · Entwickelt von Adam Gabriel Kraus**

## Status und Zweck

Version 0.1.0 ist ein lauffähiger Desktop-Prototyp für Windows, macOS und Linux mit Python 3.10 oder neuer. Er bietet eine grafische Oberfläche, konfigurierbare Ordner, lesende Datei-Scans, SHA-256-Prüfsummen und JSON-Berichte.

**Dies ist kein vollständiger Virenschutz und keine produktionsreife Schulserverlösung.** Die einfachen Inhaltsmuster sind nur Demonstrationen. Ein „kein Treffer“ bedeutet nicht, dass eine Datei sicher ist. Quarantäne, Freigabe-Workflow, dauerhafter Hintergrunddienst, signierte Updates und ein Installer sind noch nicht enthalten.

Nur mit Zustimmung der zuständigen Schul-IT und zunächst in einem Testordner verwenden. Keine echten Schüler- oder Lehrerdaten als Testmaterial verwenden.

## Installation

1. Python 3.10 oder neuer von https://www.python.org/downloads/ installieren.
2. Das Repository als ZIP herunterladen und entpacken.
3. Im entpackten Ordner ein Terminal öffnen.
4. Programm starten:

```bash
python sss_scanner.py
```

Unter manchen Linux/macOS-Systemen lautet der Befehl `python3 sss_scanner.py`.

Es werden keine zusätzlichen Python-Pakete benötigt. Die grafische Oberfläche verwendet Tkinter, das bei manchen Linux-Distributionen separat installiert werden muss.

## Erste Einrichtung

1. Programm öffnen und **Einstellungen** auswählen.
2. Einen eigens angelegten Testordner unter „Zu überwachende Ordner“ eintragen, z. B. `/home/user/sss-test` oder `C:\\SSS-Test`.
3. Optional ausgeschlossene Unterordner eintragen.
4. Intervall, maximale Dateigröße und Prüfoptionen anpassen.
5. Einstellungen speichern.
6. **Scan starten** auswählen.
7. Ergebnisse prüfen und über **Bericht exportieren** als JSON speichern.

Die Intervall-Einstellung ist bereits in der Konfiguration vorgesehen, löst in Version 0.1.0 aber noch keinen automatischen Zeitplan aus. Der Scan wird manuell gestartet.

## ClamAV (optional)

Wenn ClamAV installiert und `clamscan` im Systempfad verfügbar ist, kann SSS es zusätzlich aufrufen. Ohne ClamAV wird diese Teilprüfung als „nicht verfügbar“ angezeigt. ClamAV-Signaturen müssen separat aktuell gehalten werden.

## Einstellungen

Die Datei `sss-settings.json` wird nach dem ersten Speichern im Programmordner angelegt. Sie kann auch mit einem Texteditor bearbeitet werden. Beispiel:

```json
{
  "scan_paths": ["C:/SSS-Test"],
  "exclude_paths": [],
  "interval_minutes": 10,
  "scan_on_start": false,
  "inspect_source_files": true,
  "use_clamav": true,
  "max_file_mb": 100,
  "report_dir": "reports"
}
```

## Updateprüfung

Die Schaltfläche **Updater** prüft die veröffentlichte Versionsnummer über `version.json`. In diesem Prototyp werden Updates noch nicht automatisch heruntergeladen oder installiert. Vor einem Update die eigenen Einstellungen und Berichte sichern und nur Quellcode aus dem offiziellen Repository verwenden.

## Projekt

Repository: https://github.com/LordLOLQDH/sss  
Website: https://lordlolqdh.github.io/sss/

**Entwickelt von Adam Gabriel Kraus.**
