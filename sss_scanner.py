#!/usr/bin/env python3
"""SchoolServer Security (SSS) — defensive file audit prototype.
Developed by Adam Gabriel Kraus. Read-only scanning; no files are modified.
"""
from __future__ import annotations
import hashlib, json, os, platform, shutil, subprocess, sys, threading, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP="SchoolServer Security"
VERSION="0.1.0"
ROOT=Path(__file__).resolve().parent
CONFIG=ROOT/"sss-settings.json"
VERSION_URL="https://raw.githubusercontent.com/LordLOLQDH/sss/main/version.json"
RELEASES="https://github.com/LordLOLQDH/sss/archive/refs/heads/main.zip"
DEFAULT={"scan_paths":[],"exclude_paths":[],"interval_minutes":10,"scan_on_start":False,"inspect_source_files":True,"use_clamav":True,"max_file_mb":100,"report_dir":"reports"}

def load_config():
    try:
        data=json.loads(CONFIG.read_text(encoding="utf-8"))
        return {**DEFAULT,**data}
    except Exception:
        return DEFAULT.copy()

def save_config(cfg):
    CONFIG.write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding="utf-8")

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

SOURCE_EXT={".py",".js",".ts",".jsx",".tsx",".java",".c",".h",".cpp",".cs",".php",".html",".htm",".ps1",".bat",".cmd",".sh",".vbs",".wsf",".jar"}
SUSPICIOUS_TEXT=[b"powershell -enc",b"invoke-expression",b"eval(base64_decode",b"wget http",b"curl http"]
EICAR=b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

def scan_one(path,cfg):
    try:
        size=path.stat().st_size
        if size>cfg["max_file_mb"]*1024*1024: return {"path":str(path),"status":"Übersprungen","reason":"Datei größer als Größenlimit"}
        digest=sha256_file(path)
        with path.open("rb") as f: head=f.read(2*1024*1024)
        reasons=[]
        if EICAR in head: reasons.append("EICAR-Testsignatur erkannt")
        if cfg["inspect_source_files"] and path.suffix.lower() in SOURCE_EXT:
            reasons.append("Quellcode/Skript: erhöhte Prüfpriorität")
            low=head.lower()
            for marker in SUSPICIOUS_TEXT:
                if marker in low: reasons.append("Verdächtiges Muster: "+marker.decode("ascii","ignore"))
        clam="nicht verfügbar"
        if cfg["use_clamav"] and shutil.which("clamscan"):
            try:
                p=subprocess.run(["clamscan","--no-summary",str(path)],capture_output=True,text=True,timeout=30)
                clam="Fund" if p.returncode==1 else ("Sauber" if p.returncode==0 else "Fehler")
                if p.returncode==1: reasons.append("ClamAV meldet einen Fund")
            except Exception: clam="Prüfung fehlgeschlagen"
        status="Prüfung erforderlich" if any("Fund" in x or "EICAR" in x or "Verdächtiges" in x for x in reasons) else "Hinweis" if reasons else "Kein Treffer durch aktivierte Prüfungen"
        return {"path":str(path),"status":status,"sha256":digest,"bytes":size,"clamav":clam,"details":"; ".join(reasons) or "Keine aktivierte Regel hat angeschlagen"}
    except Exception as e: return {"path":str(path),"status":"Fehler","details":str(e)}

class SSSApp:
    def __init__(self,root):
        self.root=root; self.root.title(f"{APP} · {VERSION}"); self.root.geometry("1050x700"); self.root.minsize(800,560)
        self.cfg=load_config(); self.results=[]
        self.style=ttk.Style(); self.style.theme_use("clam")
        self.style.configure("TFrame",background="#f4f6f8"); self.style.configure("TLabel",background="#f4f6f8",foreground="#172536",font=("Segoe UI",10))
        self.style.configure("Title.TLabel",font=("Segoe UI",22,"bold")); self.style.configure("Sub.TLabel",foreground="#647386")
        self.style.configure("TButton",padding=8); self.style.configure("Treeview",rowheight=29,font=("Segoe UI",9)); self.style.configure("Treeview.Heading",font=("Segoe UI",9,"bold"))
        self.build()
        if self.cfg.get("scan_on_start"): self.root.after(500,self.start_scan)

    def build(self):
        shell=ttk.Frame(self.root,padding=22); shell.pack(fill="both",expand=True)
        head=ttk.Frame(shell); head.pack(fill="x")
        ttk.Label(head,text="SSS",font=("Segoe UI",17,"bold")).pack(side="left")
        ttk.Label(head,text="SCHOOLSERVER SECURITY",font=("Segoe UI",9,"bold")).pack(side="left",padx=12)
        ttk.Label(head,text=f"Version {VERSION}",style="Sub.TLabel").pack(side="right")
        ttk.Label(shell,text="Datei-Sicherheitsprüfung",style="Title.TLabel").pack(anchor="w",pady=(28,3))
        ttk.Label(shell,text="Lokale, lesende Analyse konfigurierter Ordner. Keine Datei wird verändert oder automatisch verschoben.",style="Sub.TLabel").pack(anchor="w")
        bar=ttk.Frame(shell); bar.pack(fill="x",pady=18)
        ttk.Button(bar,text="Scan starten",command=self.start_scan).pack(side="left")
        ttk.Button(bar,text="Einstellungen",command=self.settings).pack(side="left",padx=8)
        ttk.Button(bar,text="Updater",command=self.update_check).pack(side="left")
        ttk.Button(bar,text="Bericht exportieren",command=self.export).pack(side="left",padx=8)
        self.state=ttk.Label(shell,text="Bereit · Es wurden noch keine Dateien geprüft.",style="Sub.TLabel"); self.state.pack(anchor="w",pady=(0,10))
        cols=("status","path","clamav","details")
        self.tree=ttk.Treeview(shell,columns=cols,show="headings")
        for c,t,w in [("status","Ergebnis",180),("path","Dateipfad",340),("clamav","ClamAV",110),("details","Details",320)]:
            self.tree.heading(c,text=t); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True)
        ttk.Label(shell,text="Entwickelt von Adam Gabriel Kraus  ·  SSS ist ein Prototyp und nicht für den produktiven Schulserverbetrieb freigegeben.",style="Sub.TLabel").pack(anchor="w",pady=(12,0))

    def settings(self):
        win=tk.Toplevel(self.root); win.title("SSS · Einstellungen"); win.geometry("720x570"); win.transient(self.root)
        frame=ttk.Frame(win,padding=18); frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="Überwachung konfigurieren",style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame,text="Ein Ordnerpfad pro Zeile. Unterordner werden automatisch einbezogen.",style="Sub.TLabel").pack(anchor="w",pady=(2,12))
        ttk.Label(frame,text="Zu überwachende Ordner").pack(anchor="w")
        paths=tk.Text(frame,height=7,font=("Consolas",10)); paths.pack(fill="x",pady=5); paths.insert("1.0","\\n".join(self.cfg["scan_paths"]))
        ttk.Label(frame,text="Ausgeschlossene Ordner (optional)").pack(anchor="w",pady=(10,0))
        excludes=tk.Text(frame,height=4,font=("Consolas",10)); excludes.pack(fill="x",pady=5); excludes.insert("1.0","\\n".join(self.cfg["exclude_paths"]))
        row=ttk.Frame(frame); row.pack(fill="x",pady=7)
        ttk.Label(row,text="Intervall (Minuten)").pack(side="left")
        interval=tk.StringVar(value=str(self.cfg["interval_minutes"])); ttk.Entry(row,textvariable=interval,width=7).pack(side="left",padx=8)
        maxmb=tk.StringVar(value=str(self.cfg["max_file_mb"])); ttk.Label(row,text="Max. Dateigröße (MB)").pack(side="left",padx=(20,5)); ttk.Entry(row,textvariable=maxmb,width=7).pack(side="left")
        source=tk.BooleanVar(value=self.cfg["inspect_source_files"]); clam=tk.BooleanVar(value=self.cfg["use_clamav"]); startup=tk.BooleanVar(value=self.cfg["scan_on_start"])
        ttk.Checkbutton(frame,text="Quellcode und Skripte mit erhöhter Priorität markieren",variable=source).pack(anchor="w",pady=3)
        ttk.Checkbutton(frame,text="ClamAV verwenden, falls installiert",variable=clam).pack(anchor="w",pady=3)
        ttk.Checkbutton(frame,text="Beim Programmstart automatisch scannen",variable=startup).pack(anchor="w",pady=3)
        def save():
            try:
                cfg={**self.cfg,"scan_paths":[x.strip() for x in paths.get("1.0","end").splitlines() if x.strip()],"exclude_paths":[x.strip() for x in excludes.get("1.0","end").splitlines() if x.strip()],"interval_minutes":max(1,int(interval.get())),"max_file_mb":max(1,int(maxmb.get())),"inspect_source_files":source.get(),"use_clamav":clam.get(),"scan_on_start":startup.get()}
                save_config(cfg); self.cfg=cfg; win.destroy(); messagebox.showinfo("SSS","Einstellungen gespeichert.")
            except ValueError: messagebox.showerror("Ungültige Eingabe","Intervall und Dateigröße müssen ganze Zahlen sein.")
        ttk.Button(frame,text="Einstellungen speichern",command=save).pack(anchor="e",pady=14)

    def start_scan(self):
        if not self.cfg["scan_paths"]:
            messagebox.showwarning("Keine Ordner konfiguriert","Öffne Einstellungen und füge mindestens einen Testordner hinzu."); return
        self.state.config(text="Scan läuft …"); self.tree.delete(*self.tree.get_children()); threading.Thread(target=self.scan_worker,daemon=True).start()

    def scan_worker(self):
        out=[]; excluded=[Path(x).resolve() for x in self.cfg["exclude_paths"]]
        for raw in self.cfg["scan_paths"]:
            base=Path(raw).expanduser()
            if not base.exists(): out.append({"status":"Fehler","path":str(base),"clamav":"—","details":"Pfad existiert nicht"}); continue
            for current,dirs,files in os.walk(base):
                dirs[:]=[d for d in dirs if not any((Path(current)/d).resolve()==e or e in (Path(current)/d).resolve().parents for e in excluded)]
                for name in files:
                    p=Path(current)/name
                    if any(p.resolve()==e or e in p.resolve().parents for e in excluded): continue
                    out.append(scan_one(p,self.cfg))
        self.results=out
        self.root.after(0,self.show_results)

    def show_results(self):
        for r in self.results: self.tree.insert("","end",values=(r.get("status"),r.get("path"),r.get("clamav","—"),r.get("details","")))
        self.state.config(text=f"Scan abgeschlossen · {len(self.results)} Dateien geprüft. Ergebnisse sind Hinweise, keine Malware-Garantie.")

    def export(self):
        if not self.results: messagebox.showinfo("SSS","Noch keine Ergebnisse vorhanden."); return
        folder=Path(self.cfg["report_dir"]); folder.mkdir(exist_ok=True)
        from datetime import datetime
        target=folder/f"sss-report-{datetime.now():%Y%m%d-%H%M%S}.json"
        target.write_text(json.dumps({"version":VERSION,"results":self.results},indent=2,ensure_ascii=False),encoding="utf-8")
        messagebox.showinfo("Bericht gespeichert",str(target.resolve()))

    def update_check(self):
        def worker():
            try:
                with urllib.request.urlopen(VERSION_URL,timeout=10) as r: remote=json.loads(r.read().decode())
                latest=remote.get("version","unbekannt")
                msg=f"Installierte Version: {VERSION}\\nVerfügbare Version: {latest}\\n\\nDer Updater lädt keine Änderungen automatisch. Öffne die Projektseite für geprüfte Updates."
                self.root.after(0,lambda:messagebox.showinfo("SSS · Updateprüfung",msg))
            except Exception as e: self.root.after(0,lambda:messagebox.showerror("Updateprüfung fehlgeschlagen",str(e)))
        threading.Thread(target=worker,daemon=True).start()

if __name__=="__main__":
    root=tk.Tk(); app=SSSApp(root); root.mainloop()
