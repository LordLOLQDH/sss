# SchoolServer Security (SSS)

**Schulserver-Sicherheit. Entwickelt von Adam Gabriel Kraus.**

SchoolServer Security ist ein Entwicklungsprojekt für die Überwachung und Sicherheitsanalyse von Dateien auf Schulservern.

🌐 **Projektwebsite:** https://lordlolqdh.github.io/sss/  
📦 **Quellcode:** https://github.com/LordLOLQDH/sss

## Projektziele

- Konfigurierbare Laufwerke und Ordner überwachen
- Regelmäßige Scans (geplantes Standardintervall: 10 Minuten)
- Dateien anhand ihres tatsächlichen Inhalts analysieren
- Programmierdateien und Skripte besonders intensiv prüfen
- Verdächtige Dateien in einer geschützten Quarantäne isolieren
- Manuelle Prüfung, Freigabe und nachvollziehbare Protokollierung
- SHA-256-Prüfsummen zur Wiedererkennung unveränderter Dateien

## Desktop-Programm\n\nVersion 0.1.0 enthält einen Python-Desktop-Prototyp unter `sss_scanner.py`. Er bietet manuelle, lesende Ordnerscans, bearbeitbare Einstellungen, optionale ClamAV-Anbindung und JSON-Berichte.\n\nStart: `python sss_scanner.py` (Python 3.10+). Eine ausführliche Anleitung steht in [docs/PROGRAMM.md](docs/PROGRAMM.md). Die Updateprüfung zeigt aktuell nur die verfügbare Versionsnummer; sie installiert noch keine Updates.\n\n## Dokumentation

- [Installations- und Nutzungshinweise](docs/INSTALLATION.md)
- [Programm-Anleitung](docs/PROGRAMM.md)\n- [Updater-Status](docs/UPDATER.md)\n- [Sicherheits- und Datenschutzkonzept](docs/SECURITY.md)

## Entwicklungsstatus

**Prototyp 0.1.0 – nicht produktionsbereit.** Ein einfacher Desktop-Scanner ist vorhanden. Er ersetzt keinen Virenschutz. Automatische Zeitplanung, automatische Updates, Installer, geschützte Quarantäne und produktionsreife Erkennung sind noch nicht enthalten.

Bitte nicht auf einem echten Schulserver einsetzen, bevor die zuständige Schul-IT den Code geprüft und den Einsatz ausdrücklich freigegeben hat.

## Technische Leitlinien

- Keine Ausführung unbekannter Dateien während der Analyse
- Isolierte Parser und Analyseprozesse
- Klassische Erkennung (z. B. ClamAV/YARA) ergänzend zur KI
- Lokale Analyse als Datenschutzstandard
- Restriktive, serverseitige Rechte für die Quarantäne
- Dokumentierte und wiederherstellbare Dateiaktionen

---

**SchoolServer Security (SSS)**  
*by Adam Gabriel Kraus*
