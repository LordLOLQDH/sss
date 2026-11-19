# SSS – Installations- und Nutzungshinweise

**SchoolServer Security (SSS)**  
Entwickelt von Adam Gabriel Kraus

## Entwicklungsstatus

SSS ist ein umfangreiches Entwicklungsprojekt. Der vorhandene Scanner ist ein Prototyp; die zentrale Plattform, Schul-Accounts, Client-Enrollment, Updateinstallation und rollenbasierte Dashboards sind Zielkomponenten und noch nicht vollständig implementiert.

**Keine Installation auf echten Schulservern ohne ausdrückliche Freigabe durch die zuständige Schul-IT.** Aktuelle Versionen nicht mit produktiver Schutzsoftware verwechseln.


## Quellcode beziehen

```bash
git clone https://github.com/LordLOLQDH/sss.git
cd sss
```

Alternativ kann über GitHub **Code → Download ZIP** das Repository als ZIP-Datei heruntergeladen werden.

## Zielplattform

Die geplante Plattform besteht aus SSS Client, Backend/API, Web-Control-Center, Update-Service und Analyse-Engine. Zwei Editionen sind vorgesehen: SSS Standard und SSS Professional.

- [Architektur und Roadmap](ARCHITEKTUR.md)
- [Updater-Konzept](UPDATER.md)

## Geplanter Ablauf für einen späteren Testbetrieb

1. Testumgebung ohne echte Schülerdaten einrichten.
2. Nur eigens dafür erstellte Testordner konfigurieren.
3. Zunächst ausschließlich lesenden Scanmodus verwenden.
4. Ergebnisse und Fehlalarme prüfen.
5. Quarantäne und Wiederherstellung mit Testdateien validieren.
6. Rechte, Protokollierung, Datenschutz und Notfall-Wiederherstellung durch die Schul-IT prüfen lassen.
7. Erst nach formaler Freigabe einen begrenzten Pilotbetrieb starten.

## Sicherheit und Datenschutz

- Unbekannte Dateien niemals zur Analyse ausführen.
- Parser und Analysewerkzeuge in einer isolierten Umgebung mit Ressourcenlimits betreiben.
- Externe KI-Dienste nicht mit Schüler- oder Lehrerdokumenten füttern, solange keine ausdrückliche Datenschutzfreigabe vorliegt.
- Quarantäne mit restriktiven serverseitigen Zugriffsrechten absichern.
- Jede Verschiebung und Freigabe protokollieren.
- Vor Quarantäneaktionen Dateihash, ursprünglichen Pfad und Wiederherstellungsinformationen sichern.
- Keine automatische Löschung als Standardaktion verwenden.

## Projekt

**SchoolServer Security (SSS)**  
by Adam Gabriel Kraus

Repository: https://github.com/LordLOLQDH/sss
