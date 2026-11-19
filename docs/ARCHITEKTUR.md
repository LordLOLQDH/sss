# SSS Plattformarchitektur

**SchoolServer Security (SSS) · Konzept und Implementierungsplan**

SSS wird zu einer zentral verwalteten Sicherheitsplattform für autorisierte Schul-IT. Diese Architektur beschreibt das Zielsystem und ist kein Nachweis, dass alle Funktionen bereits implementiert sind.

## Produkteditionen

### SSS Standard
- Client für registrierte Schulserver/Arbeitsstationen
- Regelmäßige lokale Prüfungen und Ereignisberichte
- Datei-, Prozess-/System- und Log-Analyse, soweit technisch und rechtlich freigegeben
- Web-Dashboard mit verständlichen Statusmeldungen
- Update-Prüfung und kontrollierter Client-Updateprozess
- Basis-Benutzerrollen und Benachrichtigungen

### SSS Professional
Enthält Standard sowie:
- Multi-Server-/Multi-Standortverwaltung
- Erweiterte Regeln und Analyseberichte
- Erweiterte Audit- und Logansichten
- Integrationen und individuell konfigurierbare Alarmregeln
- Rollen-/Rechteverwaltung für größere IT-Teams
- Erweiterte Ereigniszusammenfassung und Trendanalysen

Editionen werden durch serverseitige Berechtigungen und Feature-Flags kontrolliert. Clientseitige UI-Schalter allein sind keine Berechtigungsgrenze.

## Systemkomponenten

1. **SSS Client:** Lokaler Dienst/Agent. Scannt nur ausdrücklich konfigurierte Bereiche, läuft mit minimalen Rechten und meldet Ereignisse über eine authentifizierte Verbindung.
2. **SSS Backend/API:** Authentifizierung, Schul-/Mandantenisolation, Geräteeinbindung, Ereignisaufnahme, Richtlinien, Nachrichten, Audit und Update-Metadaten.
3. **SSS Control Center:** Weboberfläche für Schulleitung, IT-Team und SSS-Plattformadministration. Rollenabhängige Ansichten.
4. **SSS Update Service:** Prüft Releases, verifiziert Signaturen, lädt Pakete kontrolliert, unterstützt Rollback und protokolliert Updates.
5. **Analyse-Engine:** Klassische Signaturen/Regeln, lokale Tools wie ClamAV (optional), sichere Parser und optional lokale KI. KI-Ergebnisse sind Empfehlungen und dürfen nicht allein irreversible Maßnahmen auslösen.

## Backend / Daten

Vorgeschlagener Start: Supabase (Postgres, Auth, RLS, Edge Functions) als Backend. Die finale Wahl und die Datenschutz-/Hostingprüfung muss vor Pilotbetrieb erfolgen.

Grundlegende Datenbereiche:
- schools (Mandanten/Schulen)
- school_memberships (Mitglieder, Rollen, Status)
- clients (registrierte Geräte, Edition, Softwareversion, letzter Kontakt)
- enrollments (einmalige, kurzlebige Registrierungstoken; nur Hashes speichern)
- events (Ereignisse und Risiko-/Schweregrad)
- scan_runs (Prüfungen, Dauer, Zusammenfassung)
- policies (Schulregeln und Konfiguration)
- notifications (Nachrichten, Empfänger, Zustellung, gelesen/acknowledged)
- update_releases (Version, Kanal, Paket-URL, SHA-256, Signatur, Mindestversion)
- audit_log (Admin- und Sicherheitsaktionen)
- quarantined_items (Metadaten, Hash, Originalpfad, Status, Restore-Referenz; keine Dateien in Webspeicher legen)

Jede school-spezifische Tabelle braucht tenant_id/school_id und passende Row Level Security (RLS)-Policies. Keine Service-Role- oder Admin-Secrets in Clients oder generierten Downloads.

## Accounts und Installation

- Schulleitung: übersichtliche Sicherheitslage, verständliche Meldungen, Berichte, keine technischen Rohdaten standardmäßig.
- Schul-IT: verwaltete Geräte, Prüfungen, Richtlinien, Detailereignisse und bestätigte Maßnahmen.
- SSS Plattformadministrator: getrennte Betreiberverwaltung für Editionen, Schulen, Release-Metadaten, Support-Status und Audit.
- Registrierung: Schule registriert einen Account, bestätigt die Organisation und erstellt ein Enrollment für einen Client.
- Client-Konfiguration: generierte Konfiguration enthält nur öffentliche/kurzlebige, eingeschränkte Enrollment-Daten. Keine dauerhaft gültigen Accountpasswörter, Backend-Service-Secrets oder privaten Signierschlüssel werden eingebettet.
- Enrollment-Codes sind einmalig, zeitlich begrenzt, widerrufbar und serverseitig nur gehasht gespeichert.

## Client Updates

Der Client prüft Updates:
- bei jedem Start,
- im 24-Stunden-Intervall,
- auf manuelle Anforderung.

Der Client fragt ein Release-Manifest ab, prüft Edition/Kanal/Kompatibilität, Signatur und Hash, lädt das Paket in einen temporären Bereich, prüft es, installiert mit sicherem Austausch, behält ein Rollback und meldet Ergebnis. Fehlerhafte oder nicht signierte Updates werden nicht installiert. Updates dürfen keine unkontrollierten Befehle oder beliebigen Skripte aus einem Manifest ausführen. Release-Signaturen werden mit einem privaten Schlüssel erstellt, der nicht im Repository oder Client liegt.

## Log- und Benutzerkontext

Log-Prüfung umfasst zunächst definierte, administrativ freigegebene Quellen. Benutzername, Raum, WLAN/Netzwerk und Gerät sind Kontextinformationen und nur dann sichtbar, wenn die Schule diese Daten rechtmäßig und technisch bereitstellt.

- Nicht standardmäßig den Standort einzelner Schüler live verfolgen.
- Keine Bewertung einzelner Schüler aus WLAN-/Raumdaten.
- Identitäts-/Standortinformationen minimieren, Zugriff begrenzen und Aufbewahrungsfristen konfigurieren.
- Sicherheitsstatus beschreibt das Gerät/System und konkrete Ereignisse, nicht den Charakter oder die Vertrauenswürdigkeit einer Person.
- Fehlende Daten werden als „nicht verfügbar“ angezeigt, nicht geraten.

## Nachrichten und Maßnahmen

Nachrichten müssen als SSS-Mitteilung erkennbar sein, einen Grund, Zeitstempel, Absender/Automationsquelle und zuständige Stelle zeigen. Keine gefälschten Drohungen oder irreführenden „Account wird gesperrt“-Nachrichten.

KI darf Meldungen zusammenfassen und Vorschläge erzeugen. Automatische Kontosperren, WLAN-Sperren, Nutzerrestriktionen oder andere punitive Maßnahmen sind in der ersten Version nicht erlaubt. Kritische Maßnahmen erfordern eine nachvollziehbare Bestätigung durch einen autorisierten Schuladministrator und eine Auditspur. Für Routinewarnungen können vorab freigegebene, sachliche Templates verwendet werden.

## Rollen und Rechte

- Platform Owner (SSS Betreiber): Plattformweite Administration; MFA, getrennte Admin-Identität, Auditpflicht.
- School Admin: nur eigene Schule, Benutzer, Clients, Richtlinien und Benachrichtigungen.
- IT Operator: technische Untersuchung und begrenzte Aktionen.
- Leadership Viewer: Dashboard, Lage, freigegebene Berichte.
- Client Service: nur zugewiesenes Gerät, begrenzte Event- und Statusübertragung.
- Optional Auditor: lesender Zugriff auf Audit und Reports.

## UX-Prinzipien

- Light mode, klare Hierarchie, barrierearme Kontraste, responsive Layout
- Verständliche Zusammenfassungen, technische Details optional
- Keine falschen Statusanzeigen: „unbekannt“/„nicht geprüft“ bleibt ausdrücklich so
- SSS-Logo als dezentes Wasserzeichen, niemals auf Kosten der Lesbarkeit
- Jede Aktion zeigt Wirkung, Fehler und nächsten Schritt
- Security status basiert auf dokumentierten Regeln und wird erklärbar

## Projektphasen

1. **Fundament:** Architektur, Backend, Tenant-Modell, Auth, Rollen, Audit und API.
2. **Control Center:** Login, Schulen, Übersicht, Client-Status, Events, Benachrichtigungen.
3. **Client 0.2:** stabile UI, Scheduler, Scan-Lock, strukturierte Logs und Report-Format.
4. **Enrollment & Downloads:** Edition wählen, kurzlebigen Registrierungscode erzeugen, Client-Konfiguration beziehen.
5. **Update-Service:** signierte Releases, 24h/start/manual checks, staged install und rollback.
6. **Log-Analyse:** freigegebene Quellen, sichere Parser, Kontextfelder und Regelwerk.
7. **Professional:** Multi-Standort, erweiterte Berichte, Policy-Management und Integrationen.
8. **Pilot:** Testschule/Testdaten, Datenschutz- und Security-Review, Wiederherstellungsübungen, erst danach begrenzter Einsatz.

## Pilot-Grenze

SSS ist ein Entwicklungsprojekt und keine zertifizierte Endpoint-Protection. Der erste Pilot muss in einer isolierten Testumgebung, mit schriftlicher Freigabe der zuständigen Schul-IT und ohne echte Schülerdaten stattfinden.