#!/usr/bin/env python3
"""SSS 2.0 modern GUI. Single supported desktop client."""
import sys,json,time,threading,shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt,QObject,Signal,QThread,QTimer
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import *
from sss_core import APP_NAME,VERSION,DATA_DIR,QUARANTINE,inspect,iter_files,sha256
from sss_ai import status as ai_status,explain as ai_explain,DEFAULT_MODEL
from sss_updater import check as update_check,download_and_launch
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
class StatusWorker(QObject):
 done=Signal(dict)
 def run(self):self.done.emit(ai_status())
class UpdateWorker(QObject):
 done=Signal(dict)
 def run(self):self.done.emit(update_check(VERSION))
class Main(QMainWindow):
 def __init__(self):
  super().__init__();self.c=load_cfg();self.rows=[];self.busy=False;self.ai_online=False;self.next=time.monotonic()+self.c["interval_minutes"]*60
  self.setWindowTitle(f"{APP_NAME} 2.0");self.resize(1180,770);self.setMinimumSize(900,620);self.setStyleSheet(STYLE)
  self.build();self.tick_timer=QTimer(self);self.tick_timer.timeout.connect(self.tick);self.tick_timer.start(1000);QTimer.singleShot(1000,self.check_ai);QTimer.singleShot(2500,self.scan)
 def build(self):
  central=QWidget();self.setCentralWidget(central);l=QVBoxLayout(central);l.setContentsMargins(26,22,26,22);l.setSpacing(15)
  header=QHBoxLayout();titles=QVBoxLayout();titles.setSpacing(1);h=QLabel("SchoolServer Security");h.setStyleSheet("font-size:22px;font-weight:850");sub=QLabel(f"SSS 2.0 · Local Security Engine · {VERSION}");sub.setStyleSheet("color:#718078");titles.addWidget(h);titles.addWidget(sub);header.addLayout(titles);header.addStretch();self.ai_label=QLabel("LOCAL KI · wird geprüft");self.ai_label.setStyleSheet("font-weight:750");header.addWidget(self.ai_label);self.ai_setup_btn=QPushButton("KI einrichten");self.ai_setup_btn.clicked.connect(self.ai_setup);header.addWidget(self.ai_setup_btn);l.addLayout(header)
  intro=QHBoxLayout();txt=QVBoxLayout();headline=QLabel("Sicherheitsübersicht");headline.setStyleSheet("font-size:27px;font-weight:850");desc=QLabel("Automatische lokale Prüfungen. Dateiaktionen erfolgen nachvollziehbar und mit Bestätigung.");desc.setStyleSheet("color:#718078");txt.addWidget(headline);txt.addWidget(desc);intro.addLayout(txt);intro.addStretch();self.scan_btn=QPushButton("Jetzt prüfen");self.scan_btn.setObjectName("primary");self.scan_btn.clicked.connect(self.scan);intro.addWidget(self.scan_btn);self.settings_btn=QPushButton("Einstellungen");self.settings_btn.clicked.connect(self.settings);intro.addWidget(self.settings_btn);self.update_btn=QPushButton("Updates");self.update_btn.clicked.connect(self.check_updates);intro.addWidget(self.update_btn);l.addLayout(intro)
  cards=QHBoxLayout();self.files=self.card("Geprüfte Dateien","—");self.flags=self.card("Auffälligkeiten","—");self.countdown=self.card("Nächste Prüfung","—");self.ai_card=self.card("Lokale KI","Status");[cards.addWidget(x) for x in [self.files,self.flags,self.countdown,self.ai_card]];l.addLayout(cards)
  bar=QHBoxLayout();bar.addWidget(QLabel("Prüfergebnisse"));bar.addStretch();self.status=QLabel("Bereit");self.status.setStyleSheet("color:#718078");bar.addWidget(self.status);self.quarantine_btn=QPushButton("In Quarantäne verschieben");self.quarantine_btn.clicked.connect(self.quarantine);bar.addWidget(self.quarantine_btn);self.manage_quarantine_btn=QPushButton("Quarantäne verwalten");self.manage_quarantine_btn.clicked.connect(self.manage_quarantine);bar.addWidget(self.manage_quarantine_btn);self.ai_btn=QPushButton("KI-Erklärung");self.ai_btn.clicked.connect(self.explain);bar.addWidget(self.ai_btn);l.addLayout(bar)
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
 def manage_quarantine(self):
  QUARANTINE.mkdir(parents=True,exist_ok=True)
  d=QDialog(self);d.setWindowTitle("SSS · Quarantäne");d.resize(760,440);layout=QVBoxLayout(d)
  t=QTableWidget(0,3);t.setHorizontalHeaderLabels(["DATEI","RISIKO","ORIGINALPFAD"]);t.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents);t.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents);t.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch);t.setSelectionBehavior(QAbstractItemView.SelectRows);t.setEditTriggers(QAbstractItemView.NoEditTriggers);t.verticalHeader().hide()
  entries=[]
  for f in QUARANTINE.glob("*.quarantined"):
   meta=f.with_suffix(f.suffix+".json")
   try:m=json.loads(meta.read_text(encoding="utf-8"))
   except: m={}
   entries.append((f,m))
  t.setRowCount(len(entries))
  for i,(f,m) in enumerate(entries):
   for j,v in enumerate([f.name,m.get("risk","?"),m.get("source","metadata missing")]):t.setItem(i,j,QTableWidgetItem(str(v)))
  layout.addWidget(t)
  actions=QHBoxLayout();restore=QPushButton("Ausgewählte Datei wiederherstellen");close=QPushButton("Schließen");actions.addWidget(restore);actions.addStretch();actions.addWidget(close);layout.addLayout(actions);close.clicked.connect(d.accept)
  def do_restore():
   row=t.currentRow()
   if row<0:QMessageBox.information(d,"Quarantäne","Eintrag auswählen.");return
   qfile,meta=entries[row];original=Path(meta.get("source",""))
   if not original.is_absolute():QMessageBox.critical(d,"Restore blockiert","Ursprungspfad fehlt in den Metadaten.");return
   if original.exists():QMessageBox.warning(d,"Restore blockiert","Am ursprünglichen Speicherort existiert bereits eine Datei. Sie wird nicht überschrieben.");return
   if QMessageBox.question(d,"Wiederherstellen",f"Datei an den ursprünglichen Ort zurückverschieben?\n\n{original}")!=QMessageBox.Yes:return
   try:
    original.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(qfile),str(original))
    if meta.get("sha256") and sha256(original)!=meta["sha256"]:
     shutil.move(str(original),str(qfile));QMessageBox.critical(d,"Hashprüfung fehlgeschlagen","Datei wurde zurück in Quarantäne verschoben.");return
    qfile.with_suffix(qfile.suffix+".json").unlink(missing_ok=True);QMessageBox.information(d,"SSS","Datei wiederhergestellt.");d.accept()
   except Exception as e:QMessageBox.critical(d,"Restore fehlgeschlagen",str(e))
  restore.clicked.connect(do_restore);d.exec()
 def explain(self):
  r=self.selected()
  if not r:QMessageBox.information(self,"Lokale KI","Datei in der Tabelle auswählen.");return
  if not self.c.get("ai_enabled",True):QMessageBox.information(self,"Lokale KI","KI-Auswertung ist in Einstellungen deaktiviert.");return
  self.ai_btn.setEnabled(False);self.ai_btn.setText("KI analysiert…");self.ai_thread=QThread(self);self.ai_worker=AIWorker(r,self.c.get("ai_model",DEFAULT_MODEL));self.ai_worker.moveToThread(self.ai_thread);self.ai_thread.started.connect(self.ai_worker.run);self.ai_worker.done.connect(self.ai_result);self.ai_worker.done.connect(self.ai_thread.quit);self.ai_worker.done.connect(self.ai_worker.deleteLater);self.ai_thread.finished.connect(self.ai_thread.deleteLater);self.ai_thread.start()
 def ai_result(self,r):
  self.ai_btn.setEnabled(True);self.ai_btn.setText("KI-Erklärung");dlg=QDialog(self);dlg.setWindowTitle("Lokale KI-Erklärung");dlg.resize(650,480);v=QVBoxLayout(dlg);out=QTextEdit();out.setReadOnly(True);out.setPlainText(r.get("text") if r.get("ok") else r.get("error","Keine KI-Antwort"));v.addWidget(out);close=QPushButton("Schließen");close.clicked.connect(dlg.accept);v.addWidget(close);dlg.exec()
 def check_updates(self):
  self.update_btn.setEnabled(False);self.update_btn.setText("Suche Updates…")
  self.up_thread=QThread(self);self.up_worker=UpdateWorker();self.up_worker.moveToThread(self.up_thread)
  self.up_thread.started.connect(self.up_worker.run);self.up_worker.done.connect(self.update_result)
  self.up_worker.done.connect(self.up_thread.quit);self.up_worker.done.connect(self.up_worker.deleteLater);self.up_thread.finished.connect(self.up_thread.deleteLater);self.up_thread.start()
 def update_result(self,result):
  self.update_btn.setEnabled(True);self.update_btn.setText("Updates")
  if not result.get("ok"):QMessageBox.warning(self,"Update-Prüfung",result.get("error","Updateprüfung fehlgeschlagen"));return
  if not result.get("update_available"):QMessageBox.information(self,"SSS Update",f"SSS ist aktuell. Installierte Version: {VERSION}");return
  latest=result.get("latest","?")
  if QMessageBox.question(self,"Update verfügbar",f"Version {latest} ist verfügbar.\n\nJetzt herunterladen und installieren?\n\n{result.get('notes','')}")!=QMessageBox.Yes:return
  download=download_and_launch(result.get("installer"),result.get("checksum"))
  if download.get("ok"):QMessageBox.information(self,"Updater","Installer gestartet. SSS wird geschlossen.");self.close()
  else:QMessageBox.critical(self,"Update",download.get("error","Update fehlgeschlagen"))
 def ai_setup(self):
  d=QDialog(self);d.setWindowTitle("SSS · Lokale KI einrichten");d.resize(540,420);layout=QVBoxLayout(d)
  title=QLabel("Lokale KI aktivieren");title.setStyleSheet("font-size:21px;font-weight:800");layout.addWidget(title)
  guide=QLabel("SSS verwendet Ollama und ein lokales Modell. Die KI-Anfragen bleiben auf diesem Gerät.\n\n1. Ollama für Windows herunterladen und installieren.\n2. Ollama starten (läuft im Hintergrund).\n3. Terminal/PowerShell öffnen und diesen Befehl ausführen:\n\nollama pull qwen2.5:3b\n\n4. Nach dem Download in SSS auf „KI-Status prüfen“ bzw. das Programm neu öffnen.\n\nHinweis: Das Modell benötigt mehrere GB Speicherplatz und RAM. KI-Ausgaben sind nur unterstützende Einschätzungen.");guide.setWordWrap(True);guide.setStyleSheet("font-size:14px;line-height:1.6");layout.addWidget(guide)
  link=QPushButton("Offizielle Ollama-Downloadseite öffnen");link.setObjectName("primary");link.clicked.connect(lambda:QDesktopServices.openUrl(QUrl("https://ollama.com/download/windows")));layout.addWidget(link)
  cmds=QLabel("ollama pull qwen2.5:3b");cmds.setTextInteractionFlags(Qt.TextSelectableByMouse);cmds.setStyleSheet("background:white;border:1px solid #dfe8e2;border-radius:8px;padding:10px;font-family:Consolas");layout.addWidget(cmds)
  actions=QHBoxLayout();refresh=QPushButton("KI-Status erneut prüfen");refresh.clicked.connect(lambda:(d.accept(),self.check_ai()));close=QPushButton("Schließen");close.clicked.connect(d.accept);actions.addWidget(refresh);actions.addWidget(close);layout.addLayout(actions);d.exec()
 def check_ai(self):
  self.status_thread=QThread(self);self.status_worker=StatusWorker();self.status_worker.moveToThread(self.status_thread)
  self.status_thread.started.connect(self.status_worker.run);self.status_worker.done.connect(self.ai_status_result)
  self.status_worker.done.connect(self.status_thread.quit);self.status_worker.done.connect(self.status_worker.deleteLater);self.status_thread.finished.connect(self.status_thread.deleteLater);self.status_thread.start()
 def ai_status_result(self,result):
  self.ai_online=result.get("online",False)
  self.ai_label.setText("LOCAL KI · "+("ONLINE" if self.ai_online else "OFFLINE"))
  self.ai_card.value.setText("Online" if self.ai_online else "Offline")
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
