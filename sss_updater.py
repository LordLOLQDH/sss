"""SSS release updater: only downloads checksum-verified official GitHub installers."""
import json,urllib.request,hashlib,os,subprocess,platform,tempfile
API="https://api.github.com/repos/LordLOLQDH/sss/releases/latest"
def latest_release():
 req=urllib.request.Request(API,headers={"Accept":"application/vnd.github+json","User-Agent":"SchoolServer-Security-Updater"})
 with urllib.request.urlopen(req,timeout=15) as r:return json.loads(r.read())
def vt(v):
 try:return tuple(int(x) for x in str(v).lstrip("v").split("."))
 except:return (0,)
def check(current):
 try:
  rel=latest_release();tag=rel.get("tag_name","").lstrip("v");assets=rel.get("assets",[])
  exe=next((a for a in assets if a.get("name","").startswith("SSS-Setup-") and a.get("name","").endswith(".exe")),None)
  checksum=next((a for a in assets if a.get("name","").endswith(".exe.sha256")),None)
  return {"ok":True,"current":current,"latest":tag,"update_available":vt(tag)>vt(current),"installer":exe,"checksum":checksum,"url":rel.get("html_url",""),"notes":rel.get("body","")}
 except Exception as e:return {"ok":False,"error":str(e)}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"SSS-Updater"})
 with urllib.request.urlopen(req,timeout=60) as r:return r.read()
def download_and_launch(asset,checksum_asset):
 if platform.system()!="Windows":return {"ok":False,"error":"Windows installer updater only."}
 if not asset or not checksum_asset:return {"ok":False,"error":"Release installer or SHA-256 checksum asset missing. Update blocked."}
 name=asset.get("name","")
 if not name.startswith("SSS-Setup-") or not name.endswith(".exe"):return {"ok":False,"error":"Unexpected installer filename blocked."}
 try:
  checksum_text=get(checksum_asset["browser_download_url"]).decode("ascii","ignore")
  expected=next((line.split()[0].lower() for line in checksum_text.splitlines() if line.split() and len(line.split()[0])==64 and all(c in "0123456789abcdefABCDEF" for c in line.split()[0])),None)
  if not expected:return {"ok":False,"error":"Checksum file has invalid format."}
  binary=get(asset["browser_download_url"])
  actual=hashlib.sha256(binary).hexdigest()
  if actual.lower()!=expected:return {"ok":False,"error":"Installer SHA-256 mismatch. Download rejected."}
  target=os.path.join(tempfile.gettempdir(),name)
  with open(target,"wb") as f:f.write(binary)
  if os.path.getsize(target)<1_000_000:return {"ok":False,"error":"Installer size sanity check failed."}
  subprocess.Popen([target],shell=False);return {"ok":True,"path":target}
 except Exception as e:return {"ok":False,"error":str(e)}
