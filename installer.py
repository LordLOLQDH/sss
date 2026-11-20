#!/usr/bin/env python3
"""SSS 3.0 graphical Windows installer. Bootstrap GUI packages quietly."""
import os,sys,subprocess,shutil,tempfile,urllib.request,zipfile,pathlib,time,base64

REPO="https://github.com/LordLOLQDH/sss/archive/refs/heads/main.zip"
OLLAMA_URL="https://ollama.com/download/OllamaSetup.exe"
MODEL="qwen2.5:3b"
APP=pathlib.Path(os.environ.get("LOCALAPPDATA",str(pathlib.Path.home())))/"SchoolServerSecurity"
HIDDEN=getattr(subprocess,"CREATE_NO_WINDOW",0)
def run_hidden(args,**kw):
    kw.setdefault("creationflags",HIDDEN)
    return subprocess.run(args,**kw)
def start_gui():
    py=pathlib.Path(sys.executable)
    candidates=[py.with_name("pythonw.exe")] if py.name.lower()=="python.exe" else []
    candidates.append(py)
    for exe in candidates:
        if exe.exists():
            subprocess.Popen([str(exe),str(pathlib.Path(__file__).resolve()),"--gui"],creationflags=HIDDEN,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return 0
    return 1
def bootstrap():
    try:
        import PySide6
    except ImportError:
        log=pathlib.Path(tempfile.gettempdir())/"sss3_gui_bootstrap.log"
        with log.open("w",encoding="utf-8") as f:
            p=run_hidden([sys.executable,"-m","pip","install","--user","--quiet","PySide6"],stdout=f,stderr=subprocess.STDOUT)
            if p.returncode:
                f.write("\nTrying ensurepip fallback…\n")
                run_hidden([sys.executable,"-m","ensurepip","--upgrade"],stdout=f,stderr=subprocess.STDOUT)
                p=run_hidden([sys.executable,"-m","pip","install","--user","--quiet","PySide6"],stdout=f,stderr=subprocess.STDOUT)
        if p.returncode:
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0,"PySide6 konnte nicht automatisch installiert werden. Protokoll: "+str(log),"SSS Installer 3.0",0x10)
            except Exception: print("PySide6 installation failed:",log)
            return 1
    return start_gui()

def gui():
    from PySide6.QtCore import QObject,Signal,QThread
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QProgressBar,QTextEdit,QFrame
    class Installer(QObject):
        status=Signal(str);progress=Signal(int);finished=Signal(bool,str)
        def run(self):
            try: self.install();self.finished.emit(True,"SSS 3.1 wurde erfolgreich installiert.")
            except Exception as e:self.finished.emit(False,str(e))
        def say(self,s):self.status.emit(s)
        def pct(self,n):self.progress.emit(n)
        def ollama_path(self):
            paths=[pathlib.Path(os.environ.get("LOCALAPPDATA",""))/"Programs"/"Ollama"/"ollama.exe",pathlib.Path(os.environ.get("ProgramFiles",r"C:\Program Files"))/"Ollama"/"ollama.exe"]
            for p in paths:
                if p.exists():return p
            q=shutil.which("ollama")
            return pathlib.Path(q) if q else None
        def shortcut(self,path,exe,target):
            path.parent.mkdir(parents=True,exist_ok=True)
            quote=lambda s:"'"+str(s).replace("'","''")+"'"
            script="$w=New-Object -ComObject WScript.Shell;$s=$w.CreateShortcut({});$s.TargetPath={};$s.Arguments={};$s.WorkingDirectory={};$s.Save()".format(quote(path),quote(exe),quote('"'+str(target)+'"'),quote(APP))
            encoded=base64.b64encode(script.encode("utf-16le")).decode("ascii")
            run_hidden(["powershell","-NoProfile","-EncodedCommand",encoded],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        def install(self):
            if sys.platform!="win32":raise RuntimeError("SSS Setup unterstützt Windows 10/11.")
            tmp=pathlib.Path(tempfile.mkdtemp(prefix="sss3_setup_"))
            try:
                self.say("1/6 · SSS-Programmdateien werden geladen…");self.pct(8)
                z=tmp/"sss.zip"
                with urllib.request.urlopen(urllib.request.Request(REPO,headers={"User-Agent":"SSS-Setup-3.0"}),timeout=180) as r,z.open("wb") as f:shutil.copyfileobj(r,f)
                stage=tmp/"extract";stage.mkdir()
                with zipfile.ZipFile(z) as zipf:
                    for item in zipf.infolist():
                        if not (stage/item.filename).resolve().is_relative_to(stage.resolve()):raise RuntimeError("Archiv enthält einen ungültigen Pfad.")
                    zipf.extractall(stage)
                src=next((p for p in stage.iterdir() if p.is_dir()),stage)
                if not (src/"sss_gui.py").exists():raise RuntimeError("sss_gui.py fehlt im Archiv.")
                self.pct(18);self.say("2/6 · Dateien werden installiert, vorhandene Daten bleiben erhalten…")
                backup=tmp/"backup"
                for name in ("data","quarantine"):
                    if (APP/name).exists():shutil.copytree(APP/name,backup/name,dirs_exist_ok=True)
                shutil.rmtree(APP,ignore_errors=True);shutil.copytree(src,APP)
                for name in ("data","quarantine"):
                    if (backup/name).exists():shutil.copytree(backup/name,APP/name,dirs_exist_ok=True)
                self.pct(28);self.say("3/6 · Python-Umgebung wird erstellt…")
                venv=APP/"venv"
                run_hidden([sys.executable,"-m","venv","--copies",str(venv)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                py=venv/"Scripts"/"python.exe"
                if not py.is_file() or not (venv/"pyvenv.cfg").is_file():raise RuntimeError("Virtuelle Python-Umgebung unvollständig: python.exe oder pyvenv.cfg fehlt.")
                self.say("4/6 · GUI- und Programm-Pakete werden still im Hintergrund installiert…")
                piplog=tmp/"pip-install.log"
                # Bootstrap pip inside the venv without invoking the fragile pip.exe launcher.
                with piplog.open("w",encoding="utf-8") as log:
                    ensure=run_hidden([str(py),"-m","ensurepip","--upgrade"],stdout=log,stderr=subprocess.STDOUT)
                    if ensure.returncode:
                        raise RuntimeError("pip konnte in der Python-Umgebung nicht eingerichtet werden.\\n"+piplog.read_text(encoding="utf-8",errors="replace")[-3500:])
                    requirements=APP/"requirements.txt"
                    if requirements.exists():
                        p=run_hidden([str(py),"-m","pip","install","--disable-pip-version-check","-r",str(requirements)],stdout=log,stderr=subprocess.STDOUT)
                        if p.returncode:
                            raise RuntimeError("Paketinstallation fehlgeschlagen (Code "+str(p.returncode)+").\\nDetails:\\n"+piplog.read_text(encoding="utf-8",errors="replace")[-3500:])
                # Verify the required GUI import explicitly before continuing.
                check=run_hidden([str(py),"-c","import PySide6"],capture_output=True,text=True)
                if check.returncode:
                    raise RuntimeError("PySide6 fehlt nach der Paketinstallation.\\n"+(check.stderr or check.stdout))
                self.pct(48);self.say("5/6 · Ollama wird geprüft / installiert…")
                ollama=self.ollama_path()
                if not ollama:
                    setup=tmp/"OllamaSetup.exe"
                    with urllib.request.urlopen(OLLAMA_URL,timeout=180) as r,setup.open("wb") as f:shutil.copyfileobj(r,f)
                    signature=run_hidden(["powershell","-NoProfile","-Command","(Get-AuthenticodeSignature -FilePath '"+str(setup).replace("'","''")+"').Status"],capture_output=True,text=True)
                    if signature.returncode or "Valid" not in signature.stdout:raise RuntimeError("Ollama-Signaturprüfung fehlgeschlagen.")
                    self.say("Ollama wird im Hintergrund installiert…")
                    p=run_hidden([str(setup),"/VERYSILENT","/NORESTART","/SUPPRESSMSGBOXES"])
                    if p.returncode:raise RuntimeError("Ollama Setup Fehlercode "+str(p.returncode))
                    for _ in range(30):
                        ollama=self.ollama_path()
                        if ollama:break
                        time.sleep(2)
                    if not ollama:raise RuntimeError("Ollama-Programm konnte nicht gefunden werden.")
                self.pct(60);self.say("Ollama-Dienst wird gestartet…")
                try:subprocess.Popen([str(ollama),"serve"],creationflags=HIDDEN,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                except Exception:pass
                ready=False
                for _ in range(45):
                    try:
                        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=2):ready=True;break
                    except Exception:time.sleep(2)
                if not ready:raise RuntimeError("Ollama API ist nicht erreichbar.")
                self.say("6/6 · Lokales KI-Modell "+MODEL+" wird heruntergeladen (mehrere GB)…");self.pct(70)
                run_hidden([str(ollama),"pull",MODEL],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                self.pct(94);self.say("Desktop- und Startmenü-Verknüpfungen werden angelegt…")
                menu=pathlib.Path(os.environ.get("APPDATA",str(pathlib.Path.home())))/"Microsoft"/"Windows"/"Start Menu"/"Programs"
                self.shortcut(menu/"SchoolServer Security.lnk",py,APP/"sss_gui.py")
                self.shortcut(pathlib.Path.home()/"Desktop"/"SchoolServer Security.lnk",py,APP/"sss_gui.py")
                self.pct(100)
            finally:shutil.rmtree(tmp,ignore_errors=True)
    app=QApplication(sys.argv);app.setFont(QFont("Segoe UI",10))
    w=QWidget();w.setWindowTitle("SchoolServer Security · Setup 3.1");w.setFixedSize(620,420)
    w.setStyleSheet("QWidget{background:#f4f7f6;color:#183126;font-family:'Segoe UI'} QLabel#title{font-size:24px;font-weight:800} QLabel#muted{color:#6c7b72} QFrame#panel{background:white;border:1px solid #e0e8e2;border-radius:14px} QPushButton{background:#159653;color:white;border:0;border-radius:9px;padding:11px 18px;font-weight:700} QPushButton:disabled{background:#b8c8be} QProgressBar{height:13px;border:0;border-radius:6px;background:#e8eeea} QProgressBar::chunk{background:#159653;border-radius:6px}")
    layout=QVBoxLayout(w);layout.setContentsMargins(26,24,26,24);layout.setSpacing(13)
    brand=QLabel("SCHOOLSERVER SECURITY · SETUP 3.1");brand.setStyleSheet("color:#159653;font-size:11px;font-weight:900")
    layout.addWidget(brand);title=QLabel("SSS wird installiert");title.setObjectName("title");layout.addWidget(title)
    intro=QLabel("Grafische Installation. Benötigte Komponenten, Ollama und das lokale KI-Modell werden automatisch eingerichtet.");intro.setWordWrap(True);intro.setObjectName("muted");layout.addWidget(intro)
    panel=QFrame();panel.setObjectName("panel");p=QVBoxLayout(panel);p.setContentsMargins(16,16,16,16);p.setSpacing(10)
    state=QLabel("Bereit");state.setStyleSheet("font-weight:700")
    bar=QProgressBar();bar.setRange(0,100);bar.setValue(0);bar.setTextVisible(False)
    logs=QTextEdit();logs.setReadOnly(True);logs.setFixedHeight(112);logs.setStyleSheet("border:0;background:transparent;color:#68786f")
    p.addWidget(state);p.addWidget(bar);p.addWidget(logs);layout.addWidget(panel)
    row=QHBoxLayout();row.addStretch();button=QPushButton("Installation starten");row.addWidget(button);layout.addLayout(row)
    worker=Installer();thread=QThread();worker.moveToThread(thread);thread.started.connect(worker.run)
    worker.status.connect(state.setText);worker.status.connect(logs.append);worker.progress.connect(bar.setValue)
    def completed(ok,msg):
        state.setText("Installation abgeschlossen" if ok else "Installation fehlgeschlagen");logs.append(msg);button.setEnabled(True);button.setText("SSS starten" if ok else "Schließen")
        try:button.clicked.disconnect()
        except:pass
        if ok:
            button.clicked.connect(lambda: subprocess.Popen([str(APP/"venv"/"Scripts"/"python.exe"),str(APP/"sss_gui.py")],creationflags=HIDDEN))
        else:button.clicked.connect(w.close)
    worker.finished.connect(completed)
    def start():
        button.setEnabled(False);button.setText("Installiert wird…")
        if not thread.isRunning():thread.start()
    button.clicked.connect(start)
    w.show();sys.exit(app.exec())
if __name__=="__main__":
    if "--gui" in sys.argv:gui()
    else:bootstrap()
