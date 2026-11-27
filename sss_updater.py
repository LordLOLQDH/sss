"""Safe source updater for the Python SSS project."""
from __future__ import annotations
import json, pathlib, shutil, subprocess, tempfile, urllib.request, zipfile, sys

REPO="LordLOLQDH/sss"
ROOT=pathlib.Path(__file__).resolve().parent
RAW="https://raw.githubusercontent.com/"+REPO+"/main/"
ARCHIVE="https://github.com/"+REPO+"/archive/refs/heads/main.zip"
ALLOWED={"sss_gui.py","sss_core.py","sss_ai.py","sss_updater.py","sss_setup.py","version.json","requirements.txt","Start-SSS.bat","README.md"}
def fetch(url,timeout=60):
    req=urllib.request.Request(url,headers={"User-Agent":"SchoolServer-Security-Updater"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return response.read()
def version_tuple(v):
    try:return tuple(int(p) for p in str(v).strip().lstrip("v").split("."))
    except Exception:return (0,)
def check(current):
    try:
        meta=json.loads(fetch(RAW+"version.json",20).decode("utf-8"))
        latest=str(meta.get("version","0.0.0"))
        return {"ok":True,"current":str(current),"latest":latest,"update_available":version_tuple(latest)>version_tuple(current),"notes":meta.get("notes",""),"download_url":ARCHIVE,"release_url":"https://github.com/"+REPO}
    except Exception as e:
        return {"ok":False,"error":"Updateprüfung fehlgeschlagen: "+str(e)}
def install_update():
    if getattr(sys,"frozen",False):
        return {"ok":False,"error":"Bitte SSS über Start-SSS.bat starten, damit der Quellcode-Updater funktioniert."}
    temp=pathlib.Path(tempfile.mkdtemp(prefix="sss_source_update_"))
    try:
        archive=temp/"source.zip"
        archive.write_bytes(fetch(ARCHIVE,120))
        extract=temp/"extract"
        extract.mkdir()
        with zipfile.ZipFile(archive) as z:
            rootname=z.namelist()[0].split("/")[0]
            for member in z.namelist():
                rel=member[len(rootname)+1:] if member.startswith(rootname+"/") else ""
                if not rel:continue
                dest=extract/rel
                if rel in ALLOWED or rel.startswith("assets/"):
                    if member.endswith("/"):
                        dest.mkdir(parents=True,exist_ok=True)
                    else:
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        with z.open(member) as src,dest.open("wb") as out:
                            shutil.copyfileobj(src,out)
        required={"sss_gui.py","sss_core.py","sss_ai.py","sss_updater.py","sss_setup.py","version.json","requirements.txt","Start-SSS.bat"}
        if not required.issubset({p.name for p in extract.iterdir() if p.is_file()}):
            raise RuntimeError("Quellcode-Archiv unvollständig, Update abgebrochen.")
        if not (extract/"assets").is_dir():
            raise RuntimeError("Logo/Assets fehlen, Update abgebrochen.")
        staged=temp/"new"
        shutil.copytree(extract,staged)
        helper=temp/"apply_update.cmd"
        helper.write_text(
            '@echo off\r\nsetlocal\r\nset "SOURCE='+str(staged)+'"\r\nset "TARGET='+str(ROOT)+'"\r\n:wait\r\ntimeout /t 2 /nobreak >nul\r\nrobocopy "%SOURCE%" "%TARGET%" /E /NFL /NDL /NJH /NJS >nul\r\nif errorlevel 8 goto wait\r\nstart "" "%TARGET%\\Start-SSS.bat"\r\nexit /b 0\r\n',
            encoding="utf-8")
        subprocess.Popen(["cmd.exe","/c","start","",str(helper)],creationflags=getattr(sys,"DETACHED_PROCESS",8)|getattr(sys,"CREATE_NEW_PROCESS_GROUP",512),cwd=str(ROOT))
        return {"ok":True,"message":"Update wird nach dem Schließen installiert. SSS startet anschließend neu."}
    except Exception as e:
        shutil.rmtree(temp,ignore_errors=True)
        return {"ok":False,"error":str(e)}
