"""SSS release updater: downloads official GitHub release installers only."""
import json, urllib.request, urllib.error, tempfile, os, subprocess, platform
RELEASE_API="https://api.github.com/repos/LordLOLQDH/sss/releases/latest"
def latest_release():
 req=urllib.request.Request(RELEASE_API,headers={"Accept":"application/vnd.github+json","User-Agent":"SchoolServer-Security-Updater"})
 with urllib.request.urlopen(req,timeout=12) as r:return json.loads(r.read())
def version_tuple(v):
 try:return tuple(int(x) for x in str(v).lstrip("v").split("."))
 except:return (0,)
def check(current):
 try:
  release=latest_release();remote=release.get("tag_name","").lstrip("v")
  assets=release.get("assets",[])
  installer=next((a for a in assets if a.get("name","").startswith("SSS-Setup-") and a.get("name","").endswith(".exe")),None)
  return {"ok":True,"current":current,"latest":remote,"update_available":version_tuple(remote)>version_tuple(current),"installer":installer,"release_url":release.get("html_url",""),"notes":release.get("body","")}
 except Exception as e:return {"ok":False,"error":str(e)}
def download_and_launch(asset):
 if platform.system()!="Windows":return {"ok":False,"error":"Updater installer is Windows-only."}
 if not asset or not asset.get("browser_download_url"):return {"ok":False,"error":"Release installer asset missing."}
 name=asset.get("name","")
 if not name.startswith("SSS-Setup-") or not name.endswith(".exe"):return {"ok":False,"error":"Unexpected installer filename; blocked."}
 target=os.path.join(tempfile.gettempdir(),name)
 req=urllib.request.Request(asset["browser_download_url"],headers={"User-Agent":"SchoolServer-Security-Updater"})
 with urllib.request.urlopen(req,timeout=60) as response,open(target,"wb") as f:
  while True:
   block=response.read(1024*1024)
   if not block:break
   f.write(block)
 if not os.path.isfile(target) or os.path.getsize(target)<1_000_000:return {"ok":False,"error":"Downloaded installer failed size sanity check."}
 subprocess.Popen([target],shell=False)
 return {"ok":True,"path":target}
