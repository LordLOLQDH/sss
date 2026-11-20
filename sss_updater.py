"""Repository-based updater for SchoolServer Security."""
from __future__ import annotations
import json, urllib.request, zipfile, tempfile, os, shutil, pathlib
REPO="LordLOLQDH/sss"
RAW="https://raw.githubusercontent.com/"+REPO+"/main/"
ZIP_URL="https://github.com/"+REPO+"/archive/refs/heads/main.zip"
ROOT=pathlib.Path(__file__).resolve().parent
FILES=("sss_gui.py","sss_core.py","sss_ai.py","sss_updater.py","sss_scanner.py","version.json","requirements.txt")
def fetch(url,timeout=30):
 req=urllib.request.Request(url,headers={"User-Agent":"SSS-Updater"})
 with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
def vt(v):
 try:return tuple(int(x) for x in str(v).strip().lstrip("v").split("."))
 except:return (0,)
def check(current):
 try:
  meta=json.loads(fetch(RAW+"version.json",15).decode("utf-8"))
  latest=str(meta.get("version","0.0.0"))
  return {"ok":True,"current":str(current),"latest":latest,"update_available":vt(latest)>vt(current),"notes":meta.get("notes",""),"url":"https://github.com/"+REPO}
 except Exception as e:return {"ok":False,"error":str(e)}
def install_update():
 """Fetch source ZIP, path-check it, then replace app code with rollback on failure."""
 temp=pathlib.Path(tempfile.mkdtemp(prefix="sss_update_"));backup=temp/"backup";stage=temp/"stage"
 try:
  zpath=temp/"source.zip";zpath.write_bytes(fetch(ZIP_URL,90));stage.mkdir()
  with zipfile.ZipFile(zpath) as z:
   root=stage.resolve()
   for info in z.infolist():
    target=(root/info.filename).resolve()
    if not target.is_relative_to(root):raise RuntimeError("Unsafe archive path blocked.")
   z.extractall(stage)
  folders=[p for p in stage.iterdir() if p.is_dir()];source=folders[0] if folders else stage
  missing=[n for n in FILES if not (source/n).is_file()]
  if missing:raise RuntimeError("Archive missing: "+", ".join(missing))
  meta=json.loads((source/"version.json").read_text(encoding="utf-8"));latest=str(meta.get("version",""))
  if not latest or vt(latest)<vt("2.0.0"):raise RuntimeError("Invalid version metadata.")
  backup.mkdir();done=[]
  try:
   for name in FILES:
    dst=ROOT/name
    if dst.exists():shutil.copy2(dst,backup/name)
    temp_file=ROOT/(name+".sss-update-tmp");shutil.copy2(source/name,temp_file);os.replace(temp_file,dst);done.append(name)
  except Exception:
   for name in reversed(done):
    old=backup/name
    if old.exists():shutil.copy2(old,ROOT/name)
    else:(ROOT/name).unlink(missing_ok=True)
   raise
  return {"ok":True,"version":latest,"files":done}
 except Exception as e:return {"ok":False,"error":str(e)}
 finally:shutil.rmtree(temp,ignore_errors=True)
def download_and_launch(asset=None,checksum_asset=None):
 return install_update()
