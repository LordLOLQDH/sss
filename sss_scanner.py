"""SSS 2.0 compatibility facade; the legacy Tkinter UI has been retired."""
import json
from pathlib import Path
from sss_core import APP_NAME as APP, VERSION, DATA_DIR, inspect
CONFIG=DATA_DIR/"settings.json"
def load_config():
 try:return json.loads(CONFIG.read_text(encoding="utf-8"))
 except:return {"scan_dirs":[],"excluded_dirs":[],"interval_minutes":10,"max_file_mb":200}
def save_config(config):
 DATA_DIR.mkdir(parents=True,exist_ok=True);CONFIG.write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding="utf-8")
def scan_one(path,cfg=None):return inspect(Path(path),int((cfg or {}).get("max_file_mb",200)))
