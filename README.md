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

## Dokumentation

- [Installations- und Nutzungshinweise](docs/INSTALLATION.md)
- [Sicherheits- und Datenschutzkonzept](docs/SECURITY.md)

## Entwicklungsstatus

**Noch nicht produktionsbereit.** Aktuell enthält das Repository die Projektwebsite und die technische Planung. Ein fertiger Scanner, ein getesteter Installer und eine produktionsreife Quarantänefunktion sind noch nicht veröffentlicht.

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
