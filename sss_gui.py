#!/usr/bin/env python3
"""SSS 2.0 modern GUI. Single supported desktop client."""
import sys,json,time,threading,shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt,QObject,Signal,QThread,QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import *
from sss_core import APP_NAME,VERSION,DATA_DIR,QUARANTINE,inspect,iter_files
from sss_ai import status as ai_status,explain as ai_explain,DEFAULT_MODEL
CONFIG=DATA_DIR/"settings.json"
DEFAULT={"scan_dirs":[str(Path.home()/"Downloads"),str(Path.home()/"Desktop")],"excluded_dirs":[],"interval_minutes":10,"max_file_mb":200,"ai_enabled":True,"ai_model":DEFAULT_MODEL}
STYLE="""QWidget{background:#f4f7f6;color:#172b22;font-family:'Segoe UI';font-size:13px} QFrame#card{background:white;border:1px solid #dfe8e2;border-radius:14px} QPushButton{background:white;border:1px solid #dfe8e2;border-radius:9px;padding:9px 13px;font-weight:600} QPushButton:hover{background:#edf5ef} QPushButton#primary{background:#159653;color:white;border-color:#159653} QTableWidget{background:white;border:1px solid #dfe8e2;border-radius:12px;selection-background-color:#e7f4eb} QHeaderView::section{background:#f8faf9;border:0;padding:10px;color:#718078;font-weight:700}"""
def load_cfg():
 DATA_DIR.mkdir(parents=True,exist_ok=True)
 try:return {**DEFAULT,**json.loads(CONFIG.read_text(encoding="utf-8"))}
 except:return DEFAULT.copy()
def save_cfg(c): DATA_DIR.mkdir(parents=True,exist_ok=True); CONFIG.write_text(json.dumps(c,indent=2,ensure_ascii=False),encoding="utf-8")
class ScanWorker(QObject):
 done=Signal(list)
 def __init__(self,c):super().__init__();self.c=c
 def run(self):
  rows=[]
  for p in iter_files(self.c["scan_dirs"],self.c.get("excluded_dirs",[])):rows.append(inspect(p,int(self.c["max_file_mb"])))
  self.done.emit(rows)
class AIWorker(QObject):
 done=Signal(dict)
 def __init__(self,r,m):super().__init__();self.r=r;self.m=m
 def run(self):self.done.emit(ai_explain(self.r,self.m))
class Main(QMainWindow):
 def __init__(self):
  super().__init__();self.c=load_cfg();self.rows=[];self.busy=False;self.ai_online=False;self.next=time.monotonic()+self.c["interval_minutes"]*60
  self.setWindowTitle(f"{APP_NAME} 2.0");self.resize(1180,770);self.setMinimumSize(900,620);self.setStyleSheet(STYLE)
  self.build();self.tick_timer=QTimer(self);self.tick_timer.timeout.connect(self.tick);self.tick_timer.start(1000);QTimer.singleShot(1000,self.check_ai);QTimer.singleShot(2500,self.scan)
 def build(self):
  central=QWidget();self.setCentralWidget(central);l=QVBoxLayout(central);l.setContentsMargins(26,22,26,22);l.setSpacing(15)
  header=QHBoxLayout();titles=QVBoxLayout();titles.setSpacing(1);h=QLabel("SchoolServer Security");h.setStyleSheet("font-size:22px;font-weight:850");sub=QLabel(f"SSS 2.0 · Local Security Engine · {VERSION}");sub.setStyleSheet("color:#718078");titles.addWidget(h);titles.addWidget(sub);header.addLayout(titles);header.addStretch();self.ai_label=QLabel("LOCAL KI · wird geprüft");self.ai_label.setStyleSheet("font-weight:750");header.addWidget(self.ai_label);l.addLayout(header)
  intro=QHBoxLayout();txt=QVBoxLayout();headline=QLabel("Sicherheitsübersicht");headline.setStyleSheet("font-size:27px;font-weight:850");desc=QLabel("Automatische lokale Prüfungen. Dateiaktionen erfolgen nachvollziehbar und mit Bestätigung.");desc.setStyleSheet("color:#718078");txt.addWidget(headline);txt.addWidget(desc);intro.addLayout(txt);intro.addStretch();self.scan_btn=QPushButton("Jetzt prüfen");self.scan_btn.setObjectName("primary");self.scan_btn.clicked.connect(self.scan);intro.addWidget(self.scan_btn);self.settings_btn=QPushButton("Einstellungen");self.settings_btn.clicked.connect(self.settings);intro.addWidget(self.settings_btn);l.addLayout(intro)
  cards=QHBoxLayout();self.files=self.card("Geprüfte Dateien","—");self.flags=self.card("Auffälligkeiten","—");self.countdown=self.card("Nächste Prüfung","—");self.ai_card=self.card("Lokale KI","Status");[cards.addWidget(x) for x in [self.files,self.flags,self.countdown,self.ai_card]];l.addLayout(cards)
  bar=QHBoxLayout();bar.addWidget(QLabel("Prüfergebnisse"));bar.addStretch();self.status=QLabel("Bereit");self.status.setStyleSheet("color:#718078");bar.addWidget(self.status);self.quarantine_btn=QPushButton("In Quarantäne verschieben");self.quarantine_btn.clicked.connect(self.quarantine);bar.addWidget(self.quarantine_btn);self.ai_btn=QPushButton("KI-Erklärung");self.ai_btn.clicked.connect(self.explain);bar.addWidget(self.ai_btn);l.addLayout(bar)
  self.progress=QProgressBar();self.progress.setTextVisible(False);self.progress.setFixedHeight(5);self.progress.hide();l.addWidget(self.progress)
  self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(["RISIKO","DATEIPFAD","SHA-256","PRÜFHINWEISE"]);self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents);self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch);self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents);self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch);self.table.verticalHeader().hide();self.table.setSelectionBehavior(QAbstractItemView.SelectRows);self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);l.addWidget(self.table,1)
  foot=QLabel("Hinweis: SSS ist ein Sicherheitsassistenz-Prototyp und kein zertifizierter Virenschutz. Keine Datei wird ausgeführt.");foot.setStyleSheet("color:#718078;font-size:11px");l.addWidget(foot)
 def card(self,name,value):
  f=QFrame();f.setObjectName("card");f.setMinimumHeight(88);x=QVBoxLayout(f);x.setContentsMargins(15,12,15,12);a=QLabel(name);a.setStyleSheet("color:#718078");b=QLabel(value);b.setStyleSheet("font-size:22px;font-weight:800");x.addWidget(a);x.addWidget(b);f.value=b;return f
 def tick(self):
  secs=max(0,int(self.next-time.monotonic()));self.countdown.value.setText("Scan läuft…" if self.busy else f"{secs//60:02d}:{secs%60:02d}")
  if secs<=0 and not self.busy:self.scan()
 def scan(self):
  if self.busy:return
  roots=[p for p in self.c["scan_dirs"] if Path(p).exists()]
  if not roots:self.status.setText("Scanordner in Einstellungen auswählen");return
  self.busy=True;self.scan_btn.setEnabled(False);self.progress.show();self.progress.setRange(0,0);self.status.setText("Prüfung läuft…")
  self.thread=QThread(self);self.worker=ScanWorker(self.c);self.worker.moveToThread(self.thread);self.thread.started.connect(self.worker.run);self.worker.done.connect(self.finished);self.worker.done.connect(self.thread.quit);self.worker.done.connect(self.worker.deleteLater);self.thread.finished.connect(self.thread.deleteLater);self.thread.start()
 def finished(self,rows):
  self.rows=rows;self.busy=False;self.scan_btn.setEnabled(True);self.progress.hide();self.next=time.monotonic()+self.c["interval_minutes"]*60
  flagged=[x for x in rows if x.get("risk") in ("Critical","Review")];self.files.value.setText(str(len(rows)));self.flags.value.setText(str(len(flagged)));self.status.setText(f"Scan beendet · {len(rows)} Dateien · {len(flagged)} Hinweise")
  self.table.setRowCount(len(rows))
  for i,r in enumerate(rows):
   values=[r.get("risk","?"),r.get("path",""),r.get("sha256","—"),"; ".join(r.get("reasons",[])) or "Keine Auffälligkeiten"]
   for j,v in enumerate(values):
    item=QTableWidgetItem(str(v));item.setToolTip(str(v))
    if j==0 and v in ("Critical","Review"):item.setForeground(Qt.red if v=="Critical" else Qt.darkYellow)
    self.table.setItem(i,j,item)
 def selected(self):
  i=self.table.currentRow()
  return self.rows[i] if 0<=i<len(self.rows) else None
 def quarantine(self):
  r=self.selected()
  if not r:QMessageBox.information(self,"SSS","Bitte Datei auswählen.");return
  if r.get("risk") not in ("Critical","Review"):QMessageBox.warning(self,"SSS","Nur auffällige Dateien können isoliert werden.");return
  src=Path(r["path"])
  if QMessageBox.question(self,"Datei isolieren",f"Datei wird verschoben, nicht gelöscht.\n\n{src}\n\nWeiter?")!=QMessageBox.Yes:return
  try:
   QUARANTINE.mkdir(parents=True,exist_ok=True);target=QUARANTINE/(src.name+"_"+r.get("sha256","")[:12]+".quarantined")
   shutil.move(str(src),str(target));metadata={"source":str(src),"target":str(target),"sha256":r.get("sha256"),"risk":r.get("risk"),"reasons":r.get("reasons"),"date":datetime.now().isoformat()}
   target.with_suffix(target.suffix+".json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding="utf-8");QMessageBox.information(self,"SSS","Datei in Quarantäne verschoben.");self.scan()
  except Exception as e:QMessageBox.critical(self,"Fehler",str(e))
 def explain(self):
  r=self.selected()
  if not r:QMessageBox.information(self,"Lokale KI","Datei in der Tabelle auswählen.");return
  self.ai_btn.setEnabled(False);self.ai_btn.setText("KI analysiert…");self.ai_thread=QThread(self);self.ai_worker=AIWorker(r,self.c.get("ai_model",DEFAULT_MODEL));self.ai_worker.moveToThread(self.ai_thread);self.ai_thread.started.connect(self.ai_worker.run);self.ai_worker.done.connect(self.ai_result);self.ai_worker.done.connect(self.ai_thread.quit);self.ai_worker.done.connect(self.ai_worker.deleteLater);self.ai_thread.finished.connect(self.ai_thread.deleteLater);self.ai_thread.start()
 def ai_result(self,r):
  self.ai_btn.setEnabled(True);self.ai_btn.setText("KI-Erklärung");dlg=QDialog(self);dlg.setWindowTitle("Lokale KI-Erklärung");dlg.resize(650,480);v=QVBoxLayout(dlg);out=QTextEdit();out.setReadOnly(True);out.setPlainText(r.get("text") if r.get("ok") else r.get("error","Keine KI-Antwort"));v.addWidget(out);close=QPushButton("Schließen");close.clicked.connect(dlg.accept);v.addWidget(close);dlg.exec()
 def check_ai(self):
  def probe():
   result=ai_status();self.ai_online=result.get("online",False)
   QTimer.singleShot(0,lambda:self.ai_label.setText("LOCAL KI · "+("ONLINE" if self.ai_online else "OFFLINE")))
   QTimer.singleShot(0,lambda:self.ai_card.value.setText("Online" if self.ai_online else "Offline"))
  threading.Thread(target=probe,daemon=True).start()
 def settings(self):
  d=QDialog(self);d.setWindowTitle("SSS Einstellungen");d.resize(620,460);layout=QVBoxLayout(d);form=QFormLayout()
  dirs=QPlainTextEdit();dirs.setPlainText("\n".join(self.c["scan_dirs"]));exclude=QPlainTextEdit();exclude.setMaximumHeight(90);exclude.setPlainText("\n".join(self.c.get("excluded_dirs",[])))
  interval=QSpinBox();interval.setRange(1,360);interval.setValue(int(self.c["interval_minutes"]));size=QSpinBox();size.setRange(1,5000);size.setValue(int(self.c["max_file_mb"]))
  enabled=QCheckBox("KI-Auswertung aktivieren");enabled.setChecked(self.c.get("ai_enabled",True));model=QLineEdit(self.c.get("ai_model",DEFAULT_MODEL))
  form.addRow("Scanordner (ein Pfad je Zeile)",dirs);form.addRow("Ausgeschlossene Pfade",exclude);form.addRow("Prüfintervall (Minuten)",interval);form.addRow("Max. Dateigröße (MB)",size);form.addRow(enabled);form.addRow("Ollama-Modell",model);layout.addLayout(form)
  buttons=QHBoxLayout();buttons.addStretch();cancel=QPushButton("Abbrechen");save=QPushButton("Speichern");buttons.addWidget(cancel);buttons.addWidget(save);layout.addLayout(buttons);cancel.clicked.connect(d.reject)
  def save():
   self.c.update({"scan_dirs":[x.strip() for x in dirs.toPlainText().splitlines() if x.strip()],"excluded_dirs":[x.strip() for x in exclude.toPlainText().splitlines() if x.strip()],"interval_minutes":interval.value(),"max_file_mb":size.value(),"ai_enabled":enabled.isChecked(),"ai_model":model.text().strip() or DEFAULT_MODEL});save_cfg(self.c);self.next=time.monotonic()+self.c["interval_minutes"]*60;d.accept()
  save.clicked.connect(save);d.exec()
if __name__=="__main__":
 app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setFont(QFont("Segoe UI",10));w=Main();w.show();sys.exit(app.exec())
