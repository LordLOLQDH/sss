"""First-run profile and connection wizard for SchoolServer Security."""
from __future__ import annotations
import json, socket, webbrowser
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QLabel, QLineEdit, QComboBox, QVBoxLayout,
    QFormLayout, QHBoxLayout, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QSpinBox
)
from sss_core import DATA_DIR
from sss_ai import status as ai_status, DEFAULT_MODEL

CONFIG = DATA_DIR / "settings.json"
DEFAULT_DIRS = [str(Path.home() / "Downloads"), str(Path.home() / "Desktop"), str(Path.home() / "Documents")]
STYLE = """
QWizard,QWidget{background:#f5f8f6;color:#172b22;font-family:'Segoe UI';font-size:13px}
QLabel#heading{font-size:23px;font-weight:800;color:#172b22}
QLabel#muted{color:#66776d}
QLineEdit,QComboBox,QListWidget,QSpinBox{background:white;border:1px solid #dce7df;border-radius:8px;padding:9px;min-height:20px}
QPushButton{background:white;border:1px solid #dce7df;border-radius:9px;padding:9px 13px;font-weight:650}
QPushButton:hover{background:#edf5ef}
QPushButton#primary{background:#16884b;color:white;border-color:#16884b}
QWizard QAbstractButton{min-width:92px;padding:9px 15px}
"""

def read_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_config(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Dein SSS-Profil")
        self.setSubTitle("Einmal einrichten. SSS speichert das Profil lokal auf diesem Gerät.")
        layout = QVBoxLayout(self)
        logo = QLabel()
        logo_path = Path(__file__).resolve().parent / "assets" / "Sicherheits-Schild mit Servern und Schloss.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo.setPixmap(pix.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo, 0, Qt.AlignLeft)
        self.name = QLineEdit()
        self.name.setPlaceholderText("z. B. Adam")
        self.school = QLineEdit()
        self.school.setPlaceholderText("Optional, kann leer bleiben")
        self.role = QComboBox()
        self.role.addItems(["Schüler/in", "Privatperson", "Lehrkraft", "Schul-IT (optional)"])
        self.device = QLineEdit(socket.gethostname())
        self.server = QLineEdit()
        self.server.setPlaceholderText("Optional, z. B. server.schule.local")
        form = QFormLayout()
        form.addRow("Dein Name", self.name)
        form.addRow("Schule (optional)", self.school)
        form.addRow("Rolle", self.role)
        form.addRow("Gerätename", self.device)
        form.addRow("Schulserver (nur falls bekannt)", self.server)
        layout.addLayout(form)
        note = QLabel("Du kannst SSS ganz normal als Schüler/in oder privat nutzen. Du brauchst keine Administratorrechte, keinen Schulserver und keine IT-Kenntnisse. Schule und Server sind freiwillige Angaben. Dein Profil bleibt zunächst auf diesem Gerät.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.registerField("person", self.name)
        self.registerField("school", self.school)
        self.registerField("role", self.role, "currentText")
        self.registerField("device", self.device)
        self.registerField("server", self.server)

class AIPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("KI-Verbindung")
        self.setSubTitle("SSS unterstützt aktuell Ollama als lokale KI. Deine Dateien müssen dafür nicht in eine Cloud hochgeladen werden.")
        layout = QVBoxLayout(self)
        title = QLabel("Lokale KI mit Ollama")
        title.setObjectName("heading")
        layout.addWidget(title)
        text = QLabel(
            "1. Öffne die offizielle Ollama-Seite und lade Ollama für Windows herunter.\n"
            "2. Installiere Ollama mit den Standardeinstellungen. Ollama läuft danach lokal im Hintergrund.\n"
            "3. Öffne PowerShell oder Windows Terminal und führe diesen Befehl aus:\n\n"
            "   ollama pull qwen2.5:3b\n\n"
            "4. Warte, bis der Modell-Download abgeschlossen ist. Das Modell benötigt mehrere GB Speicherplatz.\n"
            "5. Klicke hier auf Verbindung testen. SSS prüft, ob Ollama erreichbar ist und das Modell vorhanden ist."
        )
        text.setWordWrap(True)
        text.setStyleSheet("background:white;border:1px solid #dce7df;border-radius:12px;padding:16px;line-height:1.55")
        layout.addWidget(text)
        row = QHBoxLayout()
        self.open_btn = QPushButton("Offizielle Ollama-Seite öffnen")
        self.open_btn.clicked.connect(lambda: webbrowser.open("https://ollama.com/download/windows"))
        self.test_btn = QPushButton("Verbindung testen")
        self.test_btn.setObjectName("primary")
        self.test_btn.clicked.connect(self.test_connection)
        row.addWidget(self.open_btn)
        row.addWidget(self.test_btn)
        layout.addLayout(row)
        self.status = QLabel("Noch nicht geprüft. Du kannst diesen Schritt überspringen und die KI später einrichten.")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()
        self.connected = False
    def test_connection(self):
        result = ai_status()
        if not result.get("online"):
            self.connected = False
            self.status.setText("Ollama ist noch nicht erreichbar. Prüfe, ob es installiert ist und im Hintergrund läuft. Danach erneut testen.")
            self.status.setStyleSheet("color:#a45b18;font-weight:650")
            return
        models = result.get("models", [])
        found = any(DEFAULT_MODEL in name or name.startswith(DEFAULT_MODEL + ":") for name in models)
        if found:
            self.connected = True
            self.status.setText("Verbunden. Ollama ist online und qwen2.5:3b ist verfügbar.")
            self.status.setStyleSheet("color:#16884b;font-weight:750")
        else:
            self.connected = False
            self.status.setText("Ollama ist online, aber das Modell fehlt. Führe in PowerShell ollama pull qwen2.5:3b aus und teste erneut.")
            self.status.setStyleSheet("color:#a45b18;font-weight:650")

class FoldersPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Scanordner auswählen")
        self.setSubTitle("Lege fest, welche Ordner SSS lokal prüfen darf. Du kannst die Auswahl später in den Einstellungen ändern.")
        layout = QVBoxLayout(self)
        self.folders = QListWidget()
        self.folders.addItems(DEFAULT_DIRS)
        layout.addWidget(self.folders)
        row = QHBoxLayout()
        add = QPushButton("Ordner hinzufügen")
        remove = QPushButton("Auswahl entfernen")
        add.clicked.connect(self.add_folder)
        remove.clicked.connect(lambda: self.folders.takeItem(self.folders.currentRow()) if self.folders.currentRow() >= 0 else None)
        row.addWidget(add)
        row.addWidget(remove)
        layout.addLayout(row)
        form = QFormLayout()
        self.interval = QSpinBox()
        self.interval.setRange(1, 360)
        self.interval.setValue(10)
        self.interval.setSuffix(" Minuten")
        form.addRow("Automatische Prüfung", self.interval)
        layout.addLayout(form)
        note = QLabel("Tipp: Wähle zunächst Downloads und Dokumente. Systemordner wie Windows oder Program Files sind nicht als Startauswahl gedacht.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Scanordner auswählen", str(Path.home()))
        if folder and not any(self.folders.item(i).text().lower() == folder.lower() for i in range(self.folders.count())):
            self.folders.addItem(folder)
    def values(self):
        return [self.folders.item(i).text() for i in range(self.folders.count())]

class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SchoolServer Security · Erste Einrichtung")
        self.setMinimumSize(760, 680)\n        self.resize(800, 720)
        self.setStyleSheet(STYLE)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)\n        self.setOption(QWizard.HaveNextButtonOnLastPage, False)
        self.addPage(IntroPage())
        self.addPage(AIPage())
        self.folders_page = FoldersPage()
        self.addPage(self.folders_page)
        self.setButtonText(QWizard.FinishButton, "SSS einrichten")
        self.setButtonText(QWizard.CancelButton, "Abbrechen")
        self.setButtonText(QWizard.NextButton, "Weiter  ›")
        self.setButtonText(QWizard.BackButton, "Zurück")
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
                "role": self.field("role"),
                "device": device,
                "server": self.field("server").strip()
            },
            "scan_dirs": self.folders_page.values(),
            "interval_minutes": self.folders_page.interval.value(),
            "ai_enabled": True,
            "ai_provider": "ollama",
            "ai_model": DEFAULT_MODEL
        })
        config.setdefault("excluded_dirs", [])
        config.setdefault("max_file_mb", 200)
        write_config(config)
        super().accept()

def run_first_setup():
    wizard = SetupWizard()
    return wizard.exec() == QWizard.Accepted
