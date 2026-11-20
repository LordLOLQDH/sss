"""SSS 2.0 local file inspection engine. Defensive, non-executing checks."""
from pathlib import Path
from datetime import datetime
import hashlib, os, re, shutil, subprocess, time
APP_NAME="SchoolServer Security"
VERSION="2.0.0"
DATA_DIR=Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"SchoolServer Security"
QUARANTINE=DATA_DIR/"Quarantine"
SCRIPT_EXT={".ps1",".bat",".cmd",".vbs",".js",".py",".hta",".scr",".jse",".vbe"}
RULES=[
 (r"powershell.{0,80}-(enc|encodedcommand)","PowerShell encoded command"),
 (r"\b(eval|exec)\s*\(","Dynamic code execution"),
 (r"\b(shell=True|os\.system\s*\()","Shell execution"),
 (r"frombase64string.{0,100}(invoke|exec|eval)","Decode-and-execute pattern"),
]
def sha256(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def inspect(path,max_mb=200):
 p=Path(path); start=time.time()
 try:
  if not p.is_file(): return {"path":str(p),"risk":"Info","reasons":["Not a regular file"]}
  size=p.stat().st_size
  if size>max_mb*1024*1024: return {"path":str(p),"risk":"Info","size":size,"reasons":[f"Skipped: larger than {max_mb} MB"]}
  digest=sha256(p); reasons=[]; clam="Unavailable"
  clamscan=shutil.which("clamscan")
  if clamscan:
   try:
    result=subprocess.run([clamscan,"--no-summary",str(p)],capture_output=True,text=True,timeout=40)
    if "FOUND" in result.stdout+result.stderr: reasons.append("ClamAV detection")
    clam="Detection" if reasons else "Clean"
   except Exception: clam="Scan error"
  if p.suffix.lower() in SCRIPT_EXT: reasons.append(f"Script/executable-related file type: {p.suffix}")
  if p.suffix.lower() in {".py",".js",".ps1",".bat",".cmd",".vbs"} and size<2*1024*1024:
   content=p.read_text(encoding="utf-8",errors="ignore")
   for pattern,reason in RULES:
    if re.search(pattern,content,re.I|re.S): reasons.append(reason)
  risk="Critical" if "ClamAV detection" in reasons else ("Review" if reasons else "Low")
  return {"path":str(p),"risk":risk,"reasons":reasons,"sha256":digest,"size":size,"clamav":clam,"elapsed":round(time.time()-start,2),"checked_at":datetime.now().isoformat()}
 except PermissionError: return {"path":str(p),"risk":"Review","reasons":["Access denied"]}
 except Exception as e: return {"path":str(p),"risk":"Review","reasons":[str(e)]}
def iter_files(scan_dirs,excluded=()):
 excludes=[Path(x).resolve() for x in excluded]
 for root in scan_dirs:
  base=Path(root).expanduser()
  if not base.exists(): continue
  for current,dirs,files in os.walk(base):
   here=Path(current)
   dirs[:]=[d for d in dirs if not any((here/d).resolve()==x or x in (here/d).resolve().parents for x in excludes)]
   for name in files:
    p=here/name
    try:
     q=p.resolve()
     if not any(q==x or x in q.parents for x in excludes): yield p
    except OSError: continue
