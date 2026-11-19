# SchoolServer Security (SSS)

**Schulserver-Sicherheit. Entwickelt von Adam Gabriel Kraus.**

SchoolServer Security ist ein Entwicklungsprojekt für die Überwachung und Sicherheitsanalyse von Dateien auf Schulservern.

🌐 **Projektwebsite:** https://lordlolqdh.github.io/sss/  
📦 **Quellcode:** https://github.com/LordLOLQDH/sss

## Zielplattform

SSS entwickelt sich von einem lokalen Scanner zu einer zentral verwalteten Schul-Sicherheitsplattform mit Web-Control-Center, Backend, Client-Agent, Ereignissen, Updates und zwei Editionen: **SSS Standard** und **SSS Professional**.


## Editionen

- **SSS Standard:** lokaler Client, regelmäßige Prüfungen, Datei-/Log-Ereignisse, Dashboard, Status und Updates.
- **SSS Professional:** Standard plus Multi-Server-/Standortverwaltung, erweiterte Regeln, Audit, Analyse und Integrationen.

Details und Abgrenzung stehen in [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md). Funktionen in dieser Zielarchitektur sind noch nicht automatisch implementiert.


## Aktueller Client-Prototyp

Version 0.1.0 enthält einen Python-Desktop-Prototyp unter `sss_scanner.py`. Er bietet manuelle, lesende Ordnerscans, optionale ClamAV-Anbindung und JSON-Berichte. Die Intervall-Einstellung ist noch kein aktiver Scheduler. Die automatische Installation von Updates ist noch nicht vorhanden.

## Dokumentation

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
