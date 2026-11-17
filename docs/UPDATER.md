# SSS Updater

Version 0.1.0 enthält eine Updateprüfung: Das Programm liest die veröffentlichte Versionsnummer aus `version.json`. Ein automatischer Download und Austausch der Programmdateien ist noch nicht implementiert.

Geplanter sicherer Updateprozess für eine spätere Version:
1. Release-Metadaten vom offiziellen GitHub-Projekt abrufen.
2. Nur signierte Release-Artefakte akzeptieren.
3. Signatur und SHA-256-Prüfsumme lokal validieren.
4. Vor Änderungen ein Backup der Programmdateien erstellen.
5. Einstellungen und Berichte niemals überschreiben.
6. Update in einem separaten Prozess installieren und bei Fehlern zurückrollen.

Bis dahin Updates manuell über GitHub beziehen und die Versionshinweise prüfen. Keine unbekannten Update-Server verwenden.
