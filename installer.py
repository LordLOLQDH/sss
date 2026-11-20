#!/usr/bin/env python3
"""SSS Windows setup: installs SSS, Ollama, and a local AI model."""
import os,sys,shutil,tempfile,urllib.request,zipfile,subprocess,pathlib,time,base64
REPO="https://github.com/LordLOLQDH/sss/archive/refs/heads/main.zip"
OLLAMA="https://ollama.com/download/OllamaSetup.exe"
MODEL="qwen2.5:3b"
ROOT=pathlib.Path(os.environ.get("LOCALAPPDATA",pathlib.Path.home()))/"SchoolServerSecurity"
MENU=pathlib.Path(os.environ.get("APPDATA",pathlib.Path.home()))/"Microsoft"/"Windows"/"Start Menu"/"Programs"
DESK=pathlib.Path.home()/"Desktop"
def say(s):print(s,flush=True)
def safe_unzip(z,d):
 d=d.resolve()
 with zipfile.ZipFile(z) as f:
  for i in f.infolist():
   if not (d/i.filename).resolve().is_relative_to(d):raise RuntimeError("Unsafe ZIP path")
  f.extractall(d)
def ollama_path():
 for p in [pathlib.Path(os.environ.get("LOCALAPPDATA",""))/"Programs"/"Ollama"/"ollama.exe",pathlib.Path(os.environ.get("ProgramFiles",r"C:\Program Files"))/"Ollama"/"ollama.exe"]:
  if p.is_file():return p
 x=shutil.which("ollama");return pathlib.Path(x) if x else None
def psq(s):return str(s).replace("'","''")
def link(path,exe,gui):
 path.parent.mkdir(parents=True,exist_ok=True)
 cmd="$w=New-Object -ComObject WScript.Shell;$s=$w.CreateShortcut('{}');$s.TargetPath='{}';$s.Arguments='"{}"';$s.WorkingDirectory='{}';$s.Save()".format(psq(path),psq(exe),psq(gui),psq(ROOT))
 subprocess.run(["powershell","-NoProfile","-Command",cmd],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def wait_api(exe):
 try:subprocess.Popen([str(exe),"serve"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 except:pass
 for _ in range(40):
  try:
   with urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=2):return True
  except Exception:time.sleep(3)
 return False
def main():
 if sys.platform!="win32":print("Windows only.");input("Enter");return 1
 print("SchoolServer Security installer\nThis installs SSS, Ollama, and model "+MODEL+" (several GB download).")
 if input("Proceed [Y/n]? ").lower().strip() not in ("","y","yes"):return 0
 tmp=pathlib.Path(tempfile.mkdtemp(prefix="sss_install_"))
 try:
  say("[1/5] Downloading app source…")
  z=tmp/"source.zip"
  with urllib.request.urlopen(urllib.request.Request(REPO,headers={"User-Agent":"SSS-Installer"}),timeout=120) as r,z.open("wb") as f:shutil.copyfileobj(r,f)
  stage=tmp/"stage";stage.mkdir();safe_unzip(z,stage)
  src=next((p for p in stage.iterdir() if p.is_dir()),stage)
  if not (src/"sss_gui.py").exists():raise RuntimeError("GUI source missing from archive")
  say("[2/5] Install SSS files (preserving data/quarantine)")
  saved=tmp/"saved"
  for n in ("data","quarantine"):
   if (ROOT/n).exists():shutil.copytree(ROOT/n,saved/n,dirs_exist_ok=True)
  if ROOT.exists():shutil.rmtree(ROOT)
  shutil.copytree(src,ROOT)
  for n in ("data","quarantine"):
   if (saved/n).exists():shutil.copytree(saved/n,ROOT/n,dirs_exist_ok=True)
  say("[3/5] Create app virtual environment and install dependencies")
  v=ROOT/"venv";subprocess.run([sys.executable,"-m","venv",str(v)],check=True)
  py=v/"Scripts"/"python.exe";pip=v/"Scripts"/"pip.exe"
  req=ROOT/"requirements.txt"
  if req.exists():subprocess.run([str(pip),"install","-r",str(req)],check=True)
  say("[4/5] Install Ollama if needed")
  ol=ollama_path()
  if not ol:
   setup=tmp/"OllamaSetup.exe"
   with urllib.request.urlopen(OLLAMA,timeout=180) as r,setup.open("wb") as f:shutil.copyfileobj(r,f)
   sig=subprocess.run(["powershell","-NoProfile","-Command",'(Get-AuthenticodeSignature -FilePath "{}").Status'.format(psq(setup))],capture_output=True,text=True)
   if sig.returncode!=0 or "Valid" not in sig.stdout:raise RuntimeError("Ollama signature verification failed.")
   p=subprocess.Popen([str(setup),"/VERYSILENT","/NORESTART","/SUPPRESSMSGBOXES"]);p.wait()
   if p.returncode:raise RuntimeError("Ollama installer returned exit code "+str(p.returncode))
   for _ in range(30):
    ol=ollama_path()
    if ol:break
    time.sleep(2)
   if not ol:raise RuntimeError("Ollama CLI not found after install")
  say("[5/5] Start local Ollama and download model "+MODEL)
  if not wait_api(ol):raise RuntimeError("Ollama API failed to start")
  subprocess.run([str(ol),"pull",MODEL],check=True)
  gui=ROOT/"sss_gui.py";link(MENU/"SchoolServer Security.lnk",py,gui);link(DESK/"SchoolServer Security.lnk",py,gui)
  (ROOT/"uninstall_sss.py").write_text("import pathlib,os,shutil\na=pathlib.Path(os.environ.get('LOCALAPPDATA',pathlib.Path.home()))/'SchoolServerSecurity'\nm=pathlib.Path(os.environ.get('APPDATA',pathlib.Path.home()))/'Microsoft'/'Windows'/'Start Menu'/'Programs'/'SchoolServer Security.lnk'\nd=pathlib.Path.home()/'Desktop'/'SchoolServer Security.lnk'\nprint('Remove SSS app, settings and quarantine? Ollama/model stay installed.')\nif input('Type REMOVE: ').strip()=='REMOVE':\n m.unlink(missing_ok=True);d.unlink(missing_ok=True);shutil.rmtree(a,ignore_errors=True);print('SSS removed')\ninput('Enter to close')\n",encoding="utf-8")
  say("Done. SSS, Ollama, and "+MODEL+" installed. Local AI requires no cloud account/API key.")
 except Exception as e:say("Installation failed: "+str(e));return 1
 finally:shutil.rmtree(tmp,ignore_errors=True)
 input("Enter to exit");return 0
if __name__=="__main__":raise SystemExit(main())
