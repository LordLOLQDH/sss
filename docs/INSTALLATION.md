# SSS – Installations- und Nutzungshinweise

**SchoolServer Security (SSS)**  
Entwickelt von Adam Gabriel Kraus

## Entwicklungsstatus

SSS befindet sich in der Entwicklung. Dieses Repository enthält derzeit die Projektwebsite und die technische Planung. Es gibt noch keinen produktionsreifen Scanner, keinen getesteten Dienst und keinen freigegebenen Installer.

**Nicht auf einem echten Schulserver installieren oder automatische Dateiaktionen aktivieren, bevor die zuständige Schul-IT den Code geprüft und den Einsatz ausdrücklich freigegeben hat.**

## Quellcode beziehen

```bash
git clone https://github.com/LordLOLQDH/sss.git
cd sss
```

Alternativ kann über GitHub **Code → Download ZIP** das Repository als ZIP-Datei heruntergeladen werden.

## Geplante Komponenten

- Konfigurierbare Laufwerke und Ordner
- Regelmäßiger Scan (Standardziel: alle 10 Minuten)
- Inhaltsanalyse abhängig vom tatsächlichen Dateityp
- Intensivprüfung von Quellcode und Skripten
- Malware-Signaturen und YARA-Regeln
- Lokale KI-gestützte Analyse, sofern datenschutzrechtlich freigegeben
- Geschützte Quarantäne außerhalb normaler Freigaben
- Administratorprüfung, Freigabe und Audit-Protokoll
- SHA-256-basierte Wiedererkennung unveränderter Dateien

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
