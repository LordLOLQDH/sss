# Sicherheits- und Datenschutzkonzept

SSS ist für die Unterstützung autorisierter Schul-IT gedacht. Es darf nicht heimlich oder ohne Zustimmung der verantwortlichen Administratoren auf Schulservern eingesetzt werden.

## Grundprinzipien

- Standardmäßig lesende Analyse; Dateiaktionen erst nach validierter Konfiguration.
- Keine Ausführung analysierter Dateien.
- Inhaltsanalyse mit typgerechten Parsern, Signaturen und optionaler lokaler KI.
- Unvertrauenswürdige Dokumentinhalte gelten auch gegenüber KI-Modellen als Daten, niemals als Anweisungen.
- Analyseprozesse laufen isoliert, ohne unnötige Netzwerkrechte und mit CPU-, Speicher- und Zeitlimits.
- Quarantäne liegt außerhalb normaler Benutzerfreigaben und verwendet restriktive ACLs.
- Freigaben erfordern eine authentifizierte, autorisierte Person und werden protokolliert.
- Hashes dienen zur Wiedererkennung; eine frühere Freigabe ist kein dauerhafter Sicherheitsbeweis, wenn sich die Datei verändert.
- Externe KI-Übertragung ist standardmäßig deaktiviert und erfordert eine Datenschutzprüfung.

## Schutz vor Fehlalarmen und Datenverlust

Vor dem Verschieben einer Datei müssen Originalpfad, Metadaten, SHA-256-Hash und Wiederherstellungsinformationen gesichert werden. Verschiebungen müssen atomar oder anderweitig gegen Teilfehler abgesichert sein. Freigabe bedeutet kontrollierte Wiederherstellung an den ursprünglichen Speicherort, sofern dieser noch verfügbar und berechtigt ist.

Programmierdateien erhalten eine erhöhte Prüfpriorität, werden aber nicht allein wegen ihrer Endung als Malware behandelt.

## Einsatzfreigabe

Vor einem realen Einsatz sind eine Prüfung durch die zuständige Schul-IT, Datenschutzprüfung, Rechteprüfung, Test mit harmlosen Testdateien und ein dokumentierter Wiederherstellungstest erforderlich.
