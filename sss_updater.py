"""Safe updater for the packaged Windows one-file SSS executable."""
from __future__ import annotations
import json, os, pathlib, subprocess, tempfile, urllib.request, zipfile, shutil, time
REPO="LordLOLQDH/sss"
API="https://api.github.com/repos/"+REPO
ROOT=pathlib.Path(__file__).resolve().parent
def fetch(url,timeout=45):
 req=urllib.request.Request(url,headers={"User-Agent":"SchoolServer-Security-Updater","Accept":"application/vnd.github+json"})
 with urllib.request.urlopen(req,timeout=timeout) as response:return response.read()
def version_tuple(v):
 try:return tuple(int(p) for p in str(v).strip().lstrip("v").split("."))
 except:return (0,)
def check(current):
 try:
  meta=json.loads(fetch("https://raw.githubusercontent.com/"+REPO+"/main/version.json",20).decode("utf-8"))
  latest=str(meta.get("version","0.0.0"))
  release=json.loads(fetch(API+"/releases/tags/latest",20).decode("utf-8"))
  asset=next((a for a in release.get("assets",[]) if a.get("name")=="SSS-Windows.zip" and a.get("state")=="uploaded" and a.get("size",0)>100000),None)
  return {"ok":True,"current":str(current),"latest":latest,"update_available":version_tuple(latest)>version_tuple(current),"notes":meta.get("notes",""),"asset_url":asset.get("browser_download_url") if asset else None,"asset_size":asset.get("size",0),"release_url":release.get("html_url","https://github.com/"+REPO+"/releases")}
 except Exception as e:return {"ok":False,"error":"Updateprüfung fehlgeschlagen: "+str(e)}
def install_update():
 if not getattr(__import__("sys"),"frozen",False):return {"ok":False,"error":"Automatisches EXE-Update funktioniert nur in der installierten Paketversion."}
 exe=pathlib.Path(__import__("sys").executable).resolve()
 temp=pathlib.Path(tempfile.mkdtemp(prefix="sss_update_"))
 try:
  release=json.loads(fetch(API+"/releases/tags/latest",20).decode("utf-8"))
  asset=next((a for a in release.get("assets",[]) if a.get("name")=="SSS-Windows.zip" and a.get("state")=="uploaded" and a.get("size",0)>100000),None)
  if not asset:raise RuntimeError("Das Windows-ZIP ist im Release nicht verfügbar.")
  archive=temp/"SSS-Windows.zip";archive.write_bytes(fetch(asset["browser_download_url"],120))
  with zipfile.ZipFile(archive) as z:
   names=z.namelist()
   exe_entry=next((n for n in names if n.lower().endswith("/sss.exe") or n.lower()=="sss.exe"),None)
   if not exe_entry:raise RuntimeError("Im Update-ZIP wurde keine SSS.exe gefunden.")
   staged=temp/"SSS-new.exe"
   with z.open(exe_entry) as src, staged.open("wb") as dst:shutil.copyfileobj(src,dst)
  if staged.stat().st_size<10_000_000:raise RuntimeError("Update-EXE wirkt unvollständig (zu klein).")
  # Detached helper retries replacement after current process exits, then relaunches.
  helper=temp/"apply_update.cmd"
  helper.write_text("@echo off\r\nsetlocal\r\nset TARGET="+str(exe)+"\r\nset SOURCE="+str(staged)+"\r\nset APPDIR="+str(exe.parent)+"\r\n:retry\r\ntimeout /t 2 /nobreak >nul\r\ncopy /y \"%SOURCE%\" \"%TARGET%\" >nul 2>&1\r\nif errorlevel 1 goto retry\r\nstart \"\" \"%TARGET%\"\r\nexit /b 0\r\n",encoding="utf-8")
  subprocess.Popen(["cmd.exe","/c","start","",str(helper)],creationflags=getattr(subprocess,"DETACHED_PROCESS",0x00000008)|getattr(subprocess,"CREATE_NEW_PROCESS_GROUP",0x00000200),cwd=str(exe.parent))
  return {"ok":True,"message":"Update wird nach dem Schließen von SSS installiert und anschließend neu gestartet."}
 except Exception as e:
  shutil.rmtree(temp,ignore_errors=True)
  return {"ok":False,"error":str(e)}
