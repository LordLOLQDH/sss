#!/usr/bin/env python3
"""SSS 2.0 modern GUI. Single supported desktop client."""
import sys,json,time,threading,shutil,subprocess,logging,os
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt,QObject,Signal,QThread,QTimer
from PySide6.QtGui import QFont, QDesktopServices, QPixmap, QIcon
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import *
from sss_core import APP_NAME,VERSION,DATA_DIR,QUARANTINE,inspect,iter_files,sha256
from sss_ai import status as ai_status,explain as ai_explain,DEFAULT_MODEL
from sss_updater import check as update_check,install_update
CONFIG=DATA_DIR/"settings.json"
LOGFILE=DATA_DIR/"sss.log"
DATA_DIR.mkdir(parents=True,exist_ok=True)
logging.basicConfig(filename=str(LOGFILE),level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s",encoding="utf-8")
logger=logging.getLogger("SSS")
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
class PullWorker(QObject):
 done=Signal(dict)
 def __init__(self,model):super().__init__();self.model=model
 def run(self):
  try:
   p=subprocess.run(["ollama","pull",self.model],capture_output=True,text=True,timeout=900)
   self.done.emit({"ok":p.returncode==0,"output":(p.stdout or "")+"\n"+(p.stderr or "")})
  except Exception as e:self.done.emit({"ok":False,"output":str(e)})
def autostart_enabled():
 try:
  import winreg
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",0,winreg.KEY_READ) as key:
   try: value,_=winreg.QueryValueEx(key,"SchoolServer Security")
   except FileNotFoundError:return False
   return bool(value)
 except Exception:return False
def set_autostart(enabled):
 try:
  import winreg
  keypath=r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keypath,0,winreg.KEY_SET_VALUE) as key:
   if enabled:
    executable='"'+str(Path(sys.executable).resolve())+'"'
    winreg.SetValueEx(key,"SchoolServer Security",0,winreg.REG_SZ,executable)
   else:
    try:winreg.DeleteValue(key,"SchoolServer Security")
    except FileNotFoundError:pass
  return True,""
 except Exception as exc:return False,str(exc)
class Main(QMainWindow):
 def __init__(self):
  super().__init__();self.c=load_cfg();self.rows=[];self.busy=False;self.ai_online=False;self.next=time.monotonic()+self.c["interval_minutes"]*60
  self.setWindowTitle(f"{APP_NAME} 2.0");self.resize(1180,770);
  logo_icon=Path(__file__).resolve().parent/"assets"/"Sicherheits-Schild mit Servern und Schloss.png"
  if logo_icon.exists():self.setWindowIcon(QIcon(str(logo_icon)))
  logger.info("Programmstart Version %s",VERSION)self.setMinimumSize(900,620);self.setStyleSheet(STYLE)
  self.build();self.tick_timer=QTimer(self);self.tick_timer.timeout.connect(self.tick);self.tick_timer.start(1000);QTimer.singleShot(1000,self.check_ai);QTimer.singleShot(2500,self.scan)
 def build(self):
  central=QWidget();self.setCentralWidget(central);l=QVBoxLayout(central);l.setContentsMargins(26,22,26,22);l.setSpacing(15)
  header=QHBoxLayout();logo=QLabel();logo_path=Path(__file__).resolve().parent/"assets"/"Sicherheits-Schild mit Servern und Schloss.png"
  if logo_path.exists():
   pix=QPixmap(str(logo_path))
   if not pix.isNull():logo.setPixmap(pix.scaled(54,54,Qt.KeepAspectRatio,Qt.SmoothTransformation))
  header.addWidget(logo);titles=QVBoxLayout();titles.setSpacing(1);h=QLabel("SchoolServer Security");h.setStyleSheet("font-size:22px;font-weight:850");sub=QLabel(f"SSS 2.0 · Local Security Engine · {VERSION}");sub.setStyleSheet("color:#718078");titles.addWidget(h);titles.addWidget(sub);header.addLayout(titles);header.addStretch();self.ai_label=QLabel("LOCAL KI · wird geprüft");self.ai_label.setStyleSheet("font-weight:750");header.addWidget(self.ai_label);self.ai_setup_btn=QPushButton("KI einrichten");self.ai_setup_btn.clicked.connect(self.ai_setup);header.addWidget(self.ai_setup_btn);l.addLayout(header)
  intro=QHBoxLayout();txt=QVBoxLayout();headline=QLabel("Sicherheitsübersicht");headline.setStyleSheet("font-size:27px;font-weight:850");desc=QLabel("Automatische lokale Prüfungen. Dateiaktionen erfolgen nachvollziehbar und mit Bestätigung.");desc.setStyleSheet("color:#718078");txt.addWidget(headline);txt.addWidget(desc);intro.addLayout(txt);intro.addStretch();self.scan_btn=QPushButton("Jetzt prüfen");self.scan_btn.setObjectName("primary");self.scan_btn.clicked.connect(self.scan);intro.addWidget(self.scan_btn);self.settings_btn=QPushButton("Einstellungen");self.settings_btn.clicked.connect(self.settings);intro.addWidget(self.settings_btn);self.update_btn=QPushButton("Updates");self.update_btn.clicked.connect(self.check_updates);intro.addWidget(self.update_btn);self.logs_btn=QPushButton("Logs");self.logs_btn.clicked.connect(self.show_logs);intro.addWidget(self.logs_btn)

  l.addLayout(intro)
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
  self.rows=rows;self.busy=False;logger.info("Scan abgeschlossen: %d Dateien",len(rows));self.scan_btn.setEnabled(True);self.progress.hide();self.next=time.monotonic()+self.c["interval_minutes"]*60
  flagged=[x for x in rows if x.get("risk") in ("Critical","Review")];self.files.value.setText(str(len(rows)));self.flags.value.setText(str(len(flagged)));self.status.setText(f"Scan beendet · {len(rows)} Dateien · {len(flagged)} Hinweise")
  self.table.setRowCount(len(rows))
  for i,r in enumerate(rows):
   logger.info("Ergebnis %s | %s | %s",r.get("risk"),r.get("path"),"; ".join(r.get("reasons",[])))
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
   shutil.move(str(src),str(target));logger.warning("Datei isoliert: %s -> %s",src,target);metadata={"source":str(src),"target":str(target),"sha256":r.get("sha256"),"risk":r.get("risk"),"reasons":r.get("reasons"),"date":datetime.now().isoformat()}
   target.with_suffix(target.suffix+".json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding="utf-8");QMessageBox.information(self,"SSS","Datei in Quarantäne verschoben.");self.scan()
  except Exception as e:QMessageBox.critical(self,"Fehler",str(e))
 def manage_quarantine(self):
  QUARANTINE.mkdir(parents=True,exist_ok=True)
  d=QDialog(self);d.setWindowTitle("SSS · Quarantäne");d.resize(760,440);layout=QVBoxLayout(d);path_label=QLabel("Quarantäne-Ordner: "+str(QUARANTINE));path_label.setWordWrap(True);path_label.setTextInteractionFlags(Qt.TextSelectableByMouse);layout.addWidget(path_label);open_folder=QPushButton("Ordner im Explorer öffnen");open_folder.clicked.connect(lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(QUARANTINE))));layout.addWidget(open_folder)
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
  if not result.get("ok"):
   QMessageBox.warning(self,"Update-Prüfung",result.get("error","Updateprüfung fehlgeschlagen"));return
  if not result.get("update_available"):
   QMessageBox.information(self,"SSS Update",f"SSS ist aktuell. Installierte Version: {VERSION}");return
  if not result.get("asset_url"):
   QMessageBox.warning(self,"Update",f"Version {result.get('latest')} ist angekündigt, aber das Windows-ZIP wurde nicht gefunden.\n\n{result.get('release_url','')}");return
  latest=result.get("latest","?")
  answer=QMessageBox.question(self,"Update verfügbar",f"SSS {latest} ist verfügbar (installiert: {VERSION}).\n\n{result.get('notes','')}\n\nJetzt herunterladen und nach dem Schließen installieren?")
  if answer!=QMessageBox.Yes:return
  download=install_update()
  if download.get("ok"):
   QMessageBox.information(self,"Updater",download.get("message","Update wird vorbereitet."));self.close()
  else:QMessageBox.critical(self,"Update fehlgeschlagen",download.get("error","Update fehlgeschlagen"))
 def ai_setup(self):
  d=QDialog(self);d.setWindowTitle("SSS · KI verbinden");d.resize(580,460);layout=QVBoxLayout(d);layout.setSpacing(12)
  title=QLabel("Lokale KI mit Ollama");title.setStyleSheet("font-size:21px;font-weight:800");layout.addWidget(title)
  desc=QLabel("SSS nutzt Ollama lokal. Erst Ollama installieren, danach das Modell direkt hier laden und Verbindung testen.");desc.setWordWrap(True);layout.addWidget(desc)
  model_name=self.c.get("ai_model",DEFAULT_MODEL)
  guide=QLabel("1. Ollama für Windows installieren.\\n2. Danach unten „Modell installieren / aktualisieren“ klicken. SSS führt den Download aus.\\n3. Sobald der Modell-Download fertig ist, Verbindung prüfen.\\n\\nModell: "+model_name+"\\nDer Modell-Download kann mehrere GB groß sein.")
  guide.setWordWrap(True);guide.setStyleSheet("background:white;border:1px solid #dfe8e2;border-radius:12px;padding:14px");layout.addWidget(guide)
  link=QPushButton("Ollama für Windows installieren");link.clicked.connect(lambda:QDesktopServices.openUrl(QUrl("https://ollama.com/download/windows")));layout.addWidget(link)
  self.ai_setup_status=QLabel("Status wird geprüft …");self.ai_setup_status.setWordWrap(True);layout.addWidget(self.ai_setup_status)
  buttons=QHBoxLayout();self.pull_btn=QPushButton("Modell installieren / aktualisieren");self.pull_btn.setObjectName("primary");test=QPushButton("Verbindung testen");close=QPushButton("Schließen");buttons.addWidget(self.pull_btn);buttons.addWidget(test);buttons.addWidget(close);layout.addLayout(buttons)
  self.pull_btn.clicked.connect(lambda:self.pull_ai_model(d));test.clicked.connect(lambda:self.check_ai_for_dialog(d));close.clicked.connect(d.accept)
  self.ai_setup_dialog=d;self.check_ai_for_dialog(d);d.exec()
 def check_ai_for_dialog(self,d):
  result=ai_status()
  if not result.get("online"):
   self.ai_setup_status.setText("Ollama offline. Installiere Ollama und starte es, danach erneut prüfen.")
   self.ai_setup_status.setStyleSheet("color:#a45b18;font-weight:700");return
  models=result.get("models",[])
  model_name=self.c.get("ai_model",DEFAULT_MODEL)
  if any(model_name in name for name in models):
   self.ai_setup_status.setText("Verbunden. Modell "+model_name+" ist installiert.")
   self.ai_setup_status.setStyleSheet("color:#16884b;font-weight:750")
  else:
   self.ai_setup_status.setText("Ollama erreichbar, Modell fehlt noch. Klicke auf „Modell installieren / aktualisieren“.")
   self.ai_setup_status.setStyleSheet("color:#a45b18;font-weight:700")
  self.ai_status_result(result)
 def pull_ai_model(self,d):
  if not ai_status().get("online"):
   QMessageBox.warning(d,"Ollama nicht gefunden","Installiere zuerst Ollama für Windows und öffne es.");return
  self.pull_btn.setEnabled(False);self.pull_btn.setText("Modell wird geladen …");self.ai_setup_status.setText("Modell-Download läuft. Das kann einige Minuten dauern.")
  model_name=self.c.get("ai_model",DEFAULT_MODEL)
  self.pull_thread=QThread(d);self.pull_worker=PullWorker(model_name);self.pull_worker.moveToThread(self.pull_thread)
  self.pull_thread.started.connect(self.pull_worker.run);self.pull_worker.done.connect(self.pull_result)
  self.pull_worker.done.connect(self.pull_thread.quit);self.pull_worker.done.connect(self.pull_worker.deleteLater);self.pull_thread.finished.connect(self.pull_thread.deleteLater);self.pull_thread.start()
 def pull_result(self,result):
  self.pull_btn.setEnabled(True);self.pull_btn.setText("Modell installieren / aktualisieren")
  if result.get("ok"):
   self.ai_setup_status.setText("Modell "+self.c.get("ai_model",DEFAULT_MODEL)+" erfolgreich geladen. KI ist einsatzbereit.")
   self.ai_setup_status.setStyleSheet("color:#16884b;font-weight:750");self.check_ai()
  else:
   self.ai_setup_status.setText("Modell-Download fehlgeschlagen: "+result.get("output","Unbekannter Fehler")[-1200:])
   self.ai_setup_status.setStyleSheet("color:#a45b18;font-weight:700")
 def check_ai(self):
  self.status_thread=QThread(self);self.status_worker=StatusWorker();self.status_worker.moveToThread(self.status_thread)
  self.status_thread.started.connect(self.status_worker.run);self.status_worker.done.connect(self.ai_status_result)
  self.status_worker.done.connect(self.status_thread.quit);self.status_worker.done.connect(self.status_worker.deleteLater);self.status_thread.finished.connect(self.status_thread.deleteLater);self.status_thread.start()
 def ai_status_result(self,result):
  self.ai_online=result.get("online",False)
  self.ai_label.setText("LOCAL KI · "+("ONLINE" if self.ai_online else "OFFLINE"))
  self.ai_card.value.setText("Online" if self.ai_online else "Offline")
 def settings(self):
  d=QDialog(self);d.setWindowTitle("SSS · Einstellungen");d.resize(760,560);outer=QVBoxLayout(d)
  tabs=QTabWidget();outer.addWidget(tabs)
  scan_tab=QWidget();scan_layout=QVBoxLayout(scan_tab);scan_layout.setSpacing(10)
  dirs=QPlainTextEdit();dirs.setPlaceholderText("Ein Ordnerpfad pro Zeile");dirs.setPlainText("\n".join(self.c["scan_dirs"]));dirs.setMinimumHeight(130)
  exclude=QPlainTextEdit();exclude.setPlainText("\n".join(self.c.get("excluded_dirs",[])));exclude.setMinimumHeight(90)
  scan_layout.addWidget(QLabel("Zu prüfende Ordner"));scan_layout.addWidget(dirs)
  row=QHBoxLayout();add=QPushButton("Ordner auswählen …");remove=QPushButton("Ausgewählten Pfad entfernen");row.addWidget(add);row.addWidget(remove);scan_layout.addLayout(row)
  add.clicked.connect(lambda:self.pick_scan_folder(dirs));remove.clicked.connect(lambda:self.remove_scan_path(dirs))
  scan_layout.addWidget(QLabel("Ausgeschlossene Pfade"));scan_layout.addWidget(exclude)
  autostart=QCheckBox("SSS beim Windows-Anmelden automatisch starten");autostart.setChecked(autostart_enabled());scan_layout.addWidget(autostart)
  numeric=QFormLayout();interval=QSpinBox();interval.setRange(1,360);interval.setValue(int(self.c["interval_minutes"]));interval.setSuffix(" Minuten")
  size=QSpinBox();size.setRange(1,5000);size.setValue(int(self.c["max_file_mb"]));size.setSuffix(" MB")
  numeric.addRow("Automatisches Prüfintervall",interval);numeric.addRow("Maximale Dateigröße",size);scan_layout.addLayout(numeric);scan_layout.addStretch()
  tabs.addTab(scan_tab,"Scans")
  ai_tab=QWidget();ai_layout=QVBoxLayout(ai_tab);ai_layout.setSpacing(10
  )
  enabled=QCheckBox("KI-Auswertung für ausgewählte Dateien aktivieren");enabled.setChecked(self.c.get("ai_enabled",True))
  model=QLineEdit(self.c.get("ai_model",DEFAULT_MODEL));model.setPlaceholderText(DEFAULT_MODEL)
  ai_layout.addWidget(enabled);ai_layout.addWidget(QLabel("Ollama-Modellname"));ai_layout.addWidget(model)
  ai_text=QLabel("Ollama muss installiert und gestartet sein. Die Verbindung und das Modell lassen sich im Fenster „KI verbinden“ prüfen und laden.");ai_text.setWordWrap(True);ai_layout.addWidget(ai_text)
  connect=QPushButton("KI verbinden / Modell verwalten");connect.setObjectName("primary");connect.clicked.connect(self.ai_setup);ai_layout.addWidget(connect);ai_layout.addStretch()
  tabs.addTab(ai_tab,"KI")
  buttons=QHBoxLayout();buttons.addStretch();cancel=QPushButton("Abbrechen");save=QPushButton("Änderungen speichern");save.setObjectName("primary");buttons.addWidget(cancel);buttons.addWidget(save);outer.addLayout(buttons);cancel.clicked.connect(d.reject)
  def save_settings():
   ok,msg=set_autostart(autostart.isChecked())
   if not ok:QMessageBox.warning(d,"Autostart","Autostart konnte nicht gesetzt werden: "+msg)
   self.c.update({"autostart":autostart.isChecked(),"scan_dirs":[x.strip() for x in dirs.toPlainText().splitlines() if x.strip()],"excluded_dirs":[x.strip() for x in exclude.toPlainText().splitlines() if x.strip()],"interval_minutes":interval.value(),"max_file_mb":size.value(),"ai_enabled":enabled.isChecked(),"ai_model":model.text().strip() or DEFAULT_MODEL})
   save_cfg(self.c);logger.info("Einstellungen gespeichert");self.next=time.monotonic()+self.c["interval_minutes"]*60;d.accept();self.status.setText("Einstellungen gespeichert")
  save.clicked.connect(save_settings);d.exec()
 def pick_scan_folder(self,editor):
  folder=QFileDialog.getExistingDirectory(self,"Scanordner hinzufügen",str(Path.home()))
  if folder:
   existing={p.strip().casefold() for p in editor.toPlainText().splitlines() if p.strip()}
   if folder.casefold() not in existing:editor.appendPlainText(folder)
 def remove_scan_path(self,editor):
  text=editor.toPlainText().splitlines()
  if not text:return
  cursor=editor.textCursor()
  selected_line=cursor.block().text().strip()
  if selected_line and selected_line in text:text.remove(selected_line)
  else:text.pop(-1)
  editor.setPlainText("\n".join(text))
 def show_logs(self):
  d=QDialog(self);d.setWindowTitle("SSS · Protokolle");d.resize(850,560);layout=QVBoxLayout(d)
  path=QLabel("Logdatei: "+str(LOGFILE));path.setTextInteractionFlags(Qt.TextSelectableByMouse);layout.addWidget(path)
  box=QPlainTextEdit();box.setReadOnly(True)
  try:box.setPlainText(LOGFILE.read_text(encoding="utf-8")[-250000:])
  except Exception as e:box.setPlainText("Log nicht verfügbar: "+str(e))
  layout.addWidget(box);buttons=QHBoxLayout();refresh=QPushButton("Aktualisieren");open_btn=QPushButton("Logdatei öffnen");close=QPushButton("Schließen");buttons.addWidget(refresh);buttons.addWidget(open_btn);buttons.addStretch();buttons.addWidget(close);layout.addLayout(buttons)
  refresh.clicked.connect(lambda:box.setPlainText(LOGFILE.read_text(encoding="utf-8")[-250000:] if LOGFILE.exists() else ""));open_btn.clicked.connect(lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOGFILE))));close.clicked.connect(d.accept);d.exec()
if __name__=="__main__":
 app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setFont(QFont("Segoe UI",10))
 from sss_setup import run_first_setup, read_config
 if not read_config().get("profile_completed"):
  if not run_first_setup():sys.exit(0)
 w=Main();w.show()
 cfg=load_cfg()
 if cfg.get("seen_version")!=VERSION:
  try:
   meta=json.loads((Path(__file__).resolve().parent/"version.json").read_text(encoding="utf-8"))
   notes=meta.get("notes","")
  except Exception:notes="Neue Funktionen und Verbesserungen."
  def show_whats_new():
   QMessageBox.information(w,"SSS wurde aktualisiert",f"Version {VERSION} ist jetzt installiert.\\n\\nNeu in dieser Version:\\n{notes}\\n\\nLogs und Quarantäneverwaltung findest du direkt in SSS.")
   cfg["seen_version"]=VERSION;save_cfg(cfg)
  QTimer.singleShot(900,show_whats_new)
 sys.exit(app.exec())
