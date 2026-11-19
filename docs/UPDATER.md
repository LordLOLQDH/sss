# SSS Update-System

## Updateprüfungen

Der Client prüft auf neue Releases:
- automatisch beim Start (nicht blockierend für den Start der Oberfläche)
- alle 24 Stunden
- über „Jetzt nach Updates suchen“

## Updateprozess (Ziel)

1. Abruf des Release-Manifests über HTTPS.
2. Validierung des Schemas, Editions-/Channel-Zuordnung und Mindestversion.
3. Paketdownload in einen temporären Ordner.
4. SHA-256-Prüfung.
5. Prüfung der kryptografischen Signatur mit einem im Client eingebetteten öffentlichen Schlüssel.
6. Prüfung auf unterstützte Plattform und Paketgröße.
7. Installation nur in einem kontrollierten Updateprozess; vorher Backup/rollback-fähige Version sichern.
8. Start-/Health-Check und Ergebnisbericht.
9. Bei fehlgeschlagenem Start: Rollback und Fehlerbericht.

## Manifest (konzeptionelles Beispiel)

```json
{
  "version": "0.2.0",
  "edition": "standard",
  "channel": "stable",
  "platform": "windows-x64",
  "minimum_version": "0.1.0",
  "package_url": "HTTPS release asset URL",
  "sha256": "package checksum",
  "signature": "release signature"
}
```

Beispielwerte sind Platzhalter. Das Manifest darf keine Shell-Befehle, beliebigen Installationsskripte oder ausführbaren Updateanweisungen enthalten.

## Schlüssel und Freigaben

- Private Signierschlüssel liegen außerhalb GitHub, außerhalb des Backends und außerhalb der Clientinstallation.
- Der Client enthält nur den öffentlichen Verifikationsschlüssel.
- Release-Pakete und Manifest werden vor Veröffentlichung signiert.
- Unsignierte, ungültige, veraltete oder nicht passende Updates werden abgelehnt.
- Administratoren können in Schulen Updatekanäle und Wartungsfenster festlegen; wichtige Sicherheitsupdates werden deutlich markiert.

## Status

Die automatische Installation, Signaturprüfung, Paketprüfung, Rollback und das 24-Stunden-Scheduling sind noch zu implementieren und zu testen. Eine bloße Versionsabfrage ist kein sicherer Updater.
