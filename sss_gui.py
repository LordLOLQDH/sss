#!/usr/bin/env python3
"""SchoolServer Security (SSS) modern desktop UI. Read-only scanner frontend."""
from __future__ import annotations
import sys, json, threading
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QLineEdit, QCheckBox,
    QSpinBox, QTextEdit, QProgressBar)

from sss_scanner import load_config, save_config, scan_one, APP, VERSION

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "Sicherheits-Schild mit Servern und Schloss.png"
BG="#f4f7f6"; SURFACE="#ffffff"; INK="#172b22"; MUTED="#6b7c74"
GREEN="#159653"; GREEN_DARK="#08763a"; LINE="#e0e9e3"; PALE="#e8f5ed"

class ScanSignals(QObject):
    done = Signal(list)
    progress = Signal(int, int, str)

class ScannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg=load_config(); self.results=[]; self.busy=False
        self.setWindowTitle(f"{APP} · {VERSION}")
        self.setMinimumSize(960,640); self.resize(1180,760)
        self.setStyleSheet(f"""
            QWidget {{ background:{BG}; color:{INK}; font-family:'Segoe UI'; font-size:13px; }}
            QFrame#surface {{ background:{SURFACE}; border:1px solid {LINE}; border-radius:14px; }}
            QLabel#muted {{ color:{MUTED}; }}
            QPushButton {{ border:1px solid {LINE}; background:white; border-radius:9px; padding:10px 14px; font-weight:600; }}
            QPushButton:hover {{ background:#f0f7f2; }}
            QPushButton#primary {{ background:{GREEN}; color:white; border-color:{GREEN}; }}
            QPushButton#primary:hover {{ background:{GREEN_DARK}; }}
            QTableWidget {{ background:white; border:1px solid {LINE}; border-radius:12px; gridline-color:{LINE}; selection-background-color:#e7f4ec; selection-color:{INK}; }}
            QHeaderView::section {{ background:#f8faf9; border:0; border-bottom:1px solid {LINE}; padding:10px; color:{MUTED}; font-weight:700; }}
            QTableWidget::item {{ padding:8px; border-bottom:1px solid #edf2ef; }}
        """)
        self.signals=ScanSignals(); self.signals.done.connect(self.scan_finished); self.signals.progress.connect(self.progress_update)
        self.build()

    def build(self):
        central=QWidget(); self.setCentralWidget(central)
        outer=QVBoxLayout(central); outer.setContentsMargins(26,22,26,22); outer.setSpacing(16)
        header=QHBoxLayout(); brand=QHBoxLayout()
        logo=QLabel()
        if LOGO.exists():
            pix=QPixmap(str(LOGO))
            if not pix.isNull(): logo.setPixmap(pix.scaled(42,42,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        brand.addWidget(logo)
        titlecol=QVBoxLayout(); titlecol.setSpacing(0)
        name=QLabel("SchoolServer Security"); name.setStyleSheet("font-size:17px;font-weight:800")
        sub=QLabel("SSS · Datei-Sicherheitsprüfung"); sub.setObjectName("muted")
        titlecol.addWidget(name); titlecol.addWidget(sub); brand.addLayout(titlecol)
        header.addLayout(brand); header.addStretch()
        version=QLabel("VERSION "+VERSION); version.setObjectName("muted"); version.setStyleSheet(f"color:{MUTED};font-weight:700;")
        header.addWidget(version); outer.addLayout(header)

        intro=QHBoxLayout()
        textcol=QVBoxLayout(); textcol.setSpacing(5)
        headline=QLabel("Sicherheitsübersicht"); headline.setStyleSheet("font-size:27px;font-weight:800;letter-spacing:-.4px")
        desc=QLabel("Lokale, lesende Dateiprüfung. Dateien werden nicht automatisch verändert oder verschoben.")
        desc.setObjectName("muted"); desc.setWordWrap(True)
        textcol.addWidget(headline); textcol.addWidget(desc); intro.addLayout(textcol); intro.addStretch()
        self.scan_btn=QPushButton("Scan starten"); self.scan_btn.setObjectName("primary"); self.scan_btn.clicked.connect(self.start_scan)
        intro.addWidget(self.scan_btn); outer.addLayout(intro)

        stats=QHBoxLayout(); stats.setSpacing(12)
        self.stat_files=self.stat_card("Geprüfte Dateien","—")
        self.stat_findings=self.stat_card("Prüfung erforderlich","—")
        self.stat_hints=self.stat_card("Hinweise","—")
        for w in [self.stat_files,self.stat_findings,self.stat_hints]: stats.addWidget(w)
        outer.addLayout(stats)

        toolbar=QHBoxLayout()
        toolbar.addWidget(QLabel("Scan-Ergebnisse"))
        toolbar.addStretch()
        self.status=QLabel("Bereit · Noch keine Prüfung durchgeführt"); self.status.setObjectName("muted")
        toolbar.addWidget(self.status)
        self.settings_btn=QPushButton("Einstellungen"); self.settings_btn.clicked.connect(self.open_settings)
        self.export_btn=QPushButton("Bericht exportieren"); self.export_btn.clicked.connect(self.export_report)
        toolbar.addWidget(self.settings_btn); toolbar.addWidget(self.export_btn); outer.addLayout(toolbar)
        self.progress=QProgressBar(); self.progress.setTextVisible(False); self.progress.setFixedHeight(6); self.progress.hide(); outer.addWidget(self.progress)

        self.table=QTableWidget(0,4); self.table.setHorizontalHeaderLabels(["STATUS","DATEI / PFAD","CLAMAV","DETAILS"])
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False); self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows); self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        outer.addWidget(self.table,1)
        footer=QLabel("SSS ist ein Entwicklungsprototyp. Ergebnisse sind Hinweise und keine Malware-Garantie."); footer.setObjectName("muted")
        footer.setStyleSheet(f"font-size:11px;color:{MUTED};"); outer.addWidget(footer)

    def stat_card(self,label,value):
        frame=QFrame(); frame.setObjectName("surface"); frame.setMinimumHeight(82)
        layout=QVBoxLayout(frame); layout.setContentsMargins(16,12,16,12); layout.setSpacing(4)
        l=QLabel(label); l.setObjectName("muted"); l.setStyleSheet(f"color:{MUTED};font-size:12px")
        v=QLabel(value); v.setStyleSheet("font-size:24px;font-weight:800")
        layout.addWidget(l); layout.addWidget(v); frame.value_label=v; return frame

    def start_scan(self):
        if self.busy: return
        paths=self.cfg.get("scan_paths",[])
        if not paths:
            QMessageBox.warning(self,"Keine Scanordner","Bitte unter Einstellungen mindestens einen Ordner hinzufügen."); return
        self.busy=True; self.scan_btn.setEnabled(False); self.progress.show(); self.progress.setRange(0,0)
        self.status.setText("Scan wird vorbereitet…"); self.table.setRowCount(0)
        threading.Thread(target=self.scan_worker,daemon=True).start()

    def scan_worker(self):
        output=[]; excluded=[Path(x).expanduser().resolve() for x in self.cfg.get("exclude_paths",[])]
        for raw in self.cfg.get("scan_paths",[]):
            base=Path(raw).expanduser()
            if not base.exists():
                output.append({"status":"Fehler","path":str(base),"clamav":"—","details":"Pfad existiert nicht"}); continue
            for current,dirs,files in __import__("os").walk(base):
                dirs[:]=[d for d in dirs if not any((Path(current)/d).resolve()==e or e in (Path(current)/d).resolve().parents for e in excluded)]
                for fn in files:
                    p=Path(current)/fn
                    if any(p.resolve()==e or e in p.resolve().parents for e in excluded): continue
                    output.append(scan_one(p,self.cfg))
        self.signals.done.emit(output)

    def progress_update(self,*args): pass

    def scan_finished(self,rows):
        self.results=rows; self.busy=False; self.scan_btn.setEnabled(True); self.progress.hide()
        self.table.setRowCount(len(rows))
        findings=sum(1 for r in rows if r.get("status")=="Prüfung erforderlich")
        hints=sum(1 for r in rows if r.get("status")=="Hinweis")
        self.stat_files.value_label.setText(str(len(rows)))
        self.stat_findings.value_label.setText(str(findings))
        self.stat_hints.value_label.setText(str(hints))
        for i,r in enumerate(rows):
            values=[r.get("status",""),r.get("path",""),r.get("clamav","—"),r.get("details","")]
            for j,value in enumerate(values):
                item=QTableWidgetItem(str(value)); item.setToolTip(str(value))
                if j==0:
                    if value=="Prüfung erforderlich": item.setForeground(Qt.darkRed)
                    elif value=="Kein Treffer durch aktivierte Prüfungen": item.setForeground(Qt.darkGreen)
                self.table.setItem(i,j,item)
        self.status.setText(f"Abgeschlossen · {len(rows)} Dateien untersucht")

    def open_settings(self):
        dialog=SettingsDialog(self.cfg,self)
        if dialog.exec()==QDialog.Accepted:
            self.cfg=dialog.get_config()
            save_config(self.cfg)
            QMessageBox.information(self,"SSS","Einstellungen gespeichert.")

    def export_report(self):
        if not self.results:
            QMessageBox.information(self,"SSS","Es liegen noch keine Ergebnisse vor."); return
        path, _=QFileDialog.getSaveFileName(self,"Bericht speichern",f"sss-report-{datetime.now():%Y%m%d-%H%M%S}.json","JSON (*.json)")
        if not path: return
        Path(path).write_text(json.dumps({"version":VERSION,"created":datetime.now().isoformat(),"results":self.results},indent=2,ensure_ascii=False),encoding="utf-8")
        QMessageBox.information(self,"Bericht gespeichert",f"Bericht gespeichert:\n{path}")

class SettingsDialog(QDialog):
    def __init__(self,cfg,parent=None):
        super().__init__(parent); self.cfg=dict(cfg); self.setWindowTitle("SSS · Einstellungen"); self.resize(680,560)
        self.setStyleSheet(parent.styleSheet())
        layout=QVBoxLayout(self); form=QFormLayout(); form.setSpacing(12)
        self.paths=QTextEdit(); self.paths.setPlainText("\n".join(cfg.get("scan_paths",[]))); self.paths.setPlaceholderText("Ein Ordnerpfad pro Zeile")
        self.excludes=QTextEdit(); self.excludes.setPlainText("\n".join(cfg.get("exclude_paths",[]))); self.excludes.setMaximumHeight(90)
        self.interval=QSpinBox(); self.interval.setRange(1,1440); self.interval.setValue(int(cfg.get("interval_minutes",10)))
        self.maxmb=QSpinBox(); self.maxmb.setRange(1,10000); self.maxmb.setValue(int(cfg.get("max_file_mb",100)))
        self.source=QCheckBox("Quellcode-/Skriptdateien mit erhöhtem Prüfhinweis markieren"); self.source.setChecked(cfg.get("inspect_source_files",True))
        self.clam=QCheckBox("ClamAV verwenden, sofern clamscan installiert ist"); self.clam.setChecked(cfg.get("use_clamav",True))
        self.startup=QCheckBox("Beim Programmstart automatisch prüfen"); self.startup.setChecked(cfg.get("scan_on_start",False))
        form.addRow("Scanordner (je eine Zeile)",self.paths); form.addRow("Ausgeschlossene Pfade",self.excludes)
        form.addRow("Prüfintervall (Minuten)",self.interval); form.addRow("Max. Dateigröße (MB)",self.maxmb)
        layout.addLayout(form); layout.addWidget(self.source); layout.addWidget(self.clam); layout.addWidget(self.startup)
        buttons=QHBoxLayout(); buttons.addStretch(); cancel=QPushButton("Abbrechen"); save=QPushButton("Speichern"); save.setObjectName("primary")
        cancel.clicked.connect(self.reject); save.clicked.connect(self.accept); buttons.addWidget(cancel); buttons.addWidget(save); layout.addLayout(buttons)

    def get_config(self):
        return {**self.cfg,"scan_paths":[x.strip() for x in self.paths.toPlainText().splitlines() if x.strip()],
                "exclude_paths":[x.strip() for x in self.excludes.toPlainText().splitlines() if x.strip()],
                "interval_minutes":self.interval.value(),"max_file_mb":self.maxmb.value(),
                "inspect_source_files":self.source.isChecked(),"use_clamav":self.clam.isChecked(),
                "scan_on_start":self.startup.isChecked()}

if __name__=="__main__":
    app=QApplication(sys.argv); app.setApplicationName(APP); app.setFont(QFont("Segoe UI",10))
    win=ScannerWindow(); win.show(); sys.exit(app.exec())
