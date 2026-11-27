"""First-run setup wizard for SchoolServer Security."""
from __future__ import annotations

import json
import socket
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout, QFormLayout,
    QHBoxLayout, QPushButton, QListWidget, QFileDialog, QMessageBox, QSpinBox
)

from sss_core import DATA_DIR
from sss_ai import status as ai_status, DEFAULT_MODEL

CONFIG = DATA_DIR / "settings.json"
DEFAULT_DIRS = [
    str(Path.home() / "Downloads"),
    str(Path.home() / "Desktop"),
    str(Path.home() / "Documents"),
]

STYLE = """
QWizard, QWidget {
    background: #f5f8f6;
    color: #172b22;
    font-family: "Segoe UI";
    font-size: 13px;
}
QWizardPage { background: #f5f8f6; }
QLabel#heading { font-size: 23px; font-weight: 800; color: #172b22; }
QLabel#muted { color: #66776d; }
QLineEdit, QListWidget, QSpinBox {
    background: white; border: 1px solid #dce7df;
    border-radius: 8px; padding: 9px; min-height: 20px;
}
QPushButton {
    background: white; border: 1px solid #dce7df;
    border-radius: 9px; padding: 9px 15px; font-weight: 650;
}
QPushButton:hover { background: #edf5ef; }
QPushButton#primary { background: #16884b; color: white; border-color: #16884b; }
QWizard QPushButton { min-width: 100px; }
"""

def read_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}


def write_config(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Dein SSS-Profil")
        self.setSubTitle("Einmal einrichten. Dein Profil wird lokal auf diesem Gerät gespeichert.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(16)

        logo = QLabel()
        logo.setFixedHeight(82)
        logo_path = Path(__file__).resolve().parent / "assets" / "Sicherheits-Schild mit Servern und Schloss.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                logo.setPixmap(pixmap.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo, alignment=Qt.AlignLeft)

        self.name = QLineEdit()
        self.name.setPlaceholderText("z. B. Adam")
        self.school = QLineEdit()
        self.school.setPlaceholderText("Optional")
        self.device = QLineEdit(socket.gethostname())

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.addRow("Dein Name", self.name)
        form.addRow("Schule / Organisation (optional)", self.school)
        form.addRow("Gerätename", self.device)
        layout.addLayout(form)

        note = QLabel(
            "Keine Rollenabfrage, kein Schulserver und keine Administratorrechte erforderlich. "
            "SSS verwendet intern das Profil „IT Manager“. Schule und Gerätename kannst du "
            "anpassen oder leer lassen."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch(1)

        self.registerField("person", self.name)
        self.registerField("school", self.school)
        self.registerField("device", self.device)


class AIPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("KI-Verbindung")
        self.setSubTitle("Die lokale KI ist optional. Du kannst diesen Schritt jederzeit überspringen.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        title = QLabel("Lokale KI mit Ollama")
        title.setObjectName("heading")
        layout.addWidget(title)

        instructions = QLabel(
            "1. Öffne die offizielle Ollama-Seite und lade Ollama für Windows herunter.\n"
            "2. Installiere Ollama mit den Standardeinstellungen.\n"
            "3. Öffne PowerShell und führe diesen Befehl aus:\n\n"
            "   ollama pull qwen2.5:3b\n\n"
            "4. Warte, bis das Modell vollständig geladen ist.\n"
            "5. Klicke auf „Verbindung testen“.\n\n"
            "Ollama läuft lokal auf deinem Gerät. Die KI-Einrichtung ist freiwillig."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "background:white; border:1px solid #dce7df; border-radius:12px; padding:16px;"
        )
        layout.addWidget(instructions)

        buttons = QHBoxLayout()
        open_button = QPushButton("Ollama herunterladen")
        open_button.clicked.connect(
            lambda: webbrowser.open("https://ollama.com/download/windows")
        )
        test_button = QPushButton("Verbindung testen")
        test_button.setObjectName("primary")
        test_button.clicked.connect(self.test_connection)
        buttons.addWidget(open_button)
        buttons.addWidget(test_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.status = QLabel("Noch nicht geprüft. Du kannst ohne KI fortfahren.")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def test_connection(self):
        try:
            result = ai_status()
        except Exception as exc:
            self.status.setText(f"Ollama-Prüfung fehlgeschlagen: {exc}")
            self.status.setStyleSheet("color:#a45b18;font-weight:650")
            return

        if not result.get("online"):
            self.status.setText(
                "Ollama ist nicht erreichbar. Prüfe die Installation und versuche es erneut."
            )
            self.status.setStyleSheet("color:#a45b18;font-weight:650")
            return

        models = result.get("models", [])
        if any(DEFAULT_MODEL in name for name in models):
            self.status.setText(f"Verbunden. {DEFAULT_MODEL} ist verfügbar.")
            self.status.setStyleSheet("color:#16884b;font-weight:750")
        else:
            self.status.setText(
                f"Ollama ist online, aber {DEFAULT_MODEL} fehlt. "
                f"Führe in PowerShell „ollama pull {DEFAULT_MODEL}“ aus."
            )
            self.status.setStyleSheet("color:#a45b18;font-weight:650")


class FoldersPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Scanordner auswählen")
        self.setSubTitle("Wähle die Ordner, die SSS regelmäßig lokal prüfen soll.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)

        self.folders = QListWidget()
        self.folders.addItems([p for p in DEFAULT_DIRS if Path(p).exists()])
        layout.addWidget(self.folders, 1)

        actions = QHBoxLayout()
        add_button = QPushButton("Ordner hinzufügen")
        remove_button = QPushButton("Auswahl entfernen")
        add_button.clicked.connect(self.add_folder)
        remove_button.clicked.connect(self.remove_folder)
        actions.addWidget(add_button)
        actions.addWidget(remove_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        form = QFormLayout()
        self.interval = QSpinBox()
        self.interval.setRange(1, 360)
        self.interval.setValue(10)
        self.interval.setSuffix(" Minuten")
        form.addRow("Automatische Prüfung", self.interval)
        layout.addLayout(form)

        note = QLabel(
            "Du kannst die Auswahl später in den Einstellungen ändern. "
            "Systemordner wie Windows oder Program Files sind nicht als Startauswahl gedacht."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Scanordner auswählen", str(Path.home()))
        if folder:
            existing = {
                self.folders.item(i).text().casefold()
                for i in range(self.folders.count())
            }
            if folder.casefold() not in existing:
                self.folders.addItem(folder)

    def remove_folder(self):
        row = self.folders.currentRow()
        if row >= 0:
            self.folders.takeItem(row)

    def values(self):
        return [
            self.folders.item(i).text()
            for i in range(self.folders.count())
            if Path(self.folders.item(i).text()).exists()
        ]


class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SchoolServer Security · Erste Einrichtung")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(720, 600)
        self.resize(760, 640)
        self.setStyleSheet(STYLE)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)

        self.addPage(IntroPage())
        self.addPage(AIPage())
        self.folders_page = FoldersPage()
        self.addPage(self.folders_page)

        self.setButtonText(QWizard.NextButton, "Weiter")
        self.setButtonText(QWizard.BackButton, "Zurück")
        self.setButtonText(QWizard.FinishButton, "SSS einrichten")
        self.setButtonText(QWizard.CancelButton, "Abbrechen")

    def accept(self):
        person = self.field("person").strip() or "SSS-Nutzer/in"
        school = self.field("school").strip()
        device = self.field("device").strip() or socket.gethostname()

        config = read_config()
        config.update({
            "profile_completed": True,
            "profile": {
                "person": person,
                "school": school,
                "role": "IT Manager",
                "device": device,
                "server": ""
            },
            "scan_dirs": self.folders_page.values(),
            "interval_minutes": self.folders_page.interval.value(),
            "ai_enabled": True,
            "ai_provider": "ollama",
            "ai_model": DEFAULT_MODEL
        })
        config.setdefault("excluded_dirs", [])
        config.setdefault("max_file_mb", 200)

        try:
            write_config(config)
        except OSError as exc:
            QMessageBox.critical(
                self, "Einrichtung konnte nicht gespeichert werden",
                f"SSS konnte dein Profil nicht speichern.\n\n{exc}"
            )
            return

        super().accept()


def run_first_setup():
    wizard = SetupWizard()
    return wizard.exec() == QWizard.Accepted
