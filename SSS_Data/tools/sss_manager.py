#!/usr/bin/env python3
"""SchoolServer Security Manager: repair, update and uninstall utility."""
import os
import sys
import json
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "SchoolServer Security"
RELEASE_ZIP = "https://github.com/LordLOLQDH/sss/releases/download/latest/SSS-Windows-Python.zip"
VERSION_URL = "https://raw.githubusercontent.com/LordLOLQDH/sss/main/SSS_Data/version.json"
LOCAL = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
ROAMING = Path(os.environ.get("APPDATA", str(Path.home())))
INSTALL_DIR = LOCAL / "Programs" / APP_NAME
DATA_DIR = LOCAL / APP_NAME
QUARANTINE_DIR = DATA_DIR / "Quarantine"
PROGRAMS = ROAMING / "Microsoft" / "Windows" / "Start Menu" / "Programs"
STARTUP = PROGRAMS / "Startup"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SchoolServerSecurity"
MANAGER_VERSION = "1.1.0"
BG = "#f3f7f4"
PANEL = "#ffffff"
INK = "#183126"
MUTED = "#718078"
GREEN = "#16864b"
GREEN_DARK = "#11683a"
BORDER = "#dce7df"


def hidden_run(args, **kwargs):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    return subprocess.run(args, creationflags=flags, **kwargs)


def python_gui():
    candidate = Path(sys.executable).with_name("pythonw.exe")
    return str(candidate if candidate.exists() else Path(sys.executable))


def powershell(script):
    return hidden_run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                      capture_output=True, text=True, timeout=30)


def make_shortcut(link, target, args=""):
    def q(value):
        return "'" + str(value).replace("'", "''") + "'"
    link = Path(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    script = ("$w=New-Object -ComObject WScript.Shell;"
              "$s=$w.CreateShortcut(" + q(link) + ");"
              "$s.TargetPath=" + q(target) + ";"
              "$s.Arguments=" + q(args) + ";"
              "$s.WorkingDirectory=" + q(Path.home()) + ";"
              "$s.Description=" + q(APP_NAME + " Manager") + ";$s.Save()")
    result = powershell(script)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Windows konnte die Verknüpfung nicht erstellen.")


def fetch_bytes(url, timeout=90):
    request = urllib.request.Request(url, headers={"User-Agent": "SchoolServer-Security-Manager"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def get_latest_version():
    metadata = json.loads(fetch_bytes(VERSION_URL, 20).decode("utf-8"))
    return str(metadata.get("version", "unbekannt"))


def download_and_validate():
    archive = fetch_bytes(RELEASE_ZIP, 120)
    stage = Path(tempfile.mkdtemp(prefix="sss_manager_"))
    zip_path = stage / "package.zip"
    payload = stage / "payload"
    payload.mkdir()
    zip_path.write_bytes(archive)
    with zipfile.ZipFile(zip_path) as package:
        for info in package.infolist():
            name = info.filename.replace("\\", "/")
            parts = name.split("/")
            if name.startswith("/") or ".." in parts:
                raise RuntimeError("Das Downloadpaket enthält einen ungültigen Dateipfad.")
            if not (name.endswith("/sss_main.py") or name == "sss_main.py" or
                    name.startswith("SSS_Data/") or "/SSS_Data/" in name):
                continue
            if "SSS_Data" in parts:
                parts = parts[parts.index("SSS_Data"):]
            elif parts[-1] == "sss_main.py":
                parts = ["sss_main.py"]
            else:
                continue
            destination = payload.joinpath(*parts)
            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with package.open(info) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
    main = payload / "sss_main.py"
    requirements = payload / "SSS_Data" / "requirements.txt"
    metadata = payload / "SSS_Data" / "version.json"
    manager = payload / "SSS_Data" / "tools" / "sss_manager.py"
    if not all(path.is_file() for path in (main, requirements, metadata, manager)):
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Das Paket ist unvollständig. Hauptprogramm, Manager oder Metadaten fehlen.")
    check = hidden_run([sys.executable, "-m", "py_compile", str(main), str(manager)],
                       capture_output=True, text=True)
    if check.returncode:
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Die Python-Syntaxprüfung ist fehlgeschlagen:\n" + check.stderr)
    version = json.loads(metadata.read_text(encoding="utf-8")).get("version", "unbekannt")
    return stage, payload, str(version)


def sss_processes():
    if os.name != "nt":
        return []
    script = ("Get-CimInstance Win32_Process | Where-Object {"
              "$_.Name -match '^pythonw?\\.exe$' -and $_.CommandLine -and "
              "$_.CommandLine -match 'sss_main\\.py' -and $_.CommandLine -match 'SchoolServer Security'} | "
              "Select-Object -ExpandProperty ProcessId")
    result = powershell(script)
    if result.returncode:
        return []
    return [x.strip() for x in result.stdout.splitlines() if x.strip().isdigit() and int(x) != os.getpid()]


def install_or_repair():
    running = sss_processes()
    if running:
        raise RuntimeError("SSS läuft noch. Bitte zuerst SchoolServer Security vollständig schließen und danach die Reparatur erneut starten.")
    stage, payload, version = download_and_validate()
    backup = INSTALL_DIR.with_name(INSTALL_DIR.name + ".manager-backup")
    try:
        INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        if INSTALL_DIR.exists():
            INSTALL_DIR.rename(backup)
        try:
            shutil.copytree(payload, INSTALL_DIR)
        except Exception:
            if INSTALL_DIR.exists():
                shutil.rmtree(INSTALL_DIR, ignore_errors=True)
            if backup.exists():
                backup.rename(INSTALL_DIR)
            raise
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        app = INSTALL_DIR / "sss_main.py"
        manager = INSTALL_DIR / "SSS_Data" / "tools" / "sss_manager.py"
        make_shortcut(PROGRAMS / "SchoolServer Security.lnk", python_gui(), '"' + str(app) + '"')
        make_shortcut(PROGRAMS / "SchoolServer Security Manager.lnk", python_gui(), '"' + str(manager) + '"')
        make_shortcut(STARTUP / "SchoolServer Security.lnk", python_gui(), '"' + str(app) + '"')
        req = INSTALL_DIR / "SSS_Data" / "requirements.txt"
        pip = hidden_run([sys.executable, "-m", "pip", "install", "-r", str(req)],
                         capture_output=True, text=True, timeout=600)
        if pip.returncode:
            raise RuntimeError("SSS-Dateien wurden installiert, aber Python-Abhängigkeiten konnten nicht repariert werden:\n" + pip.stderr[-2500:])
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(INSTALL_DIR))
        except Exception:
            pass
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        return version
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def uninstall():
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    farewell = desktop / "SchoolServer Security - Abschied.log"
    farewell.write_text("SchoolServer Security wurde entfernt.\n\n"
                        "Danke, dass du SSS verwendet hast.\n\n"
                        "Programmdateien, Einstellungen, Logs und Quarantänedaten wurden entfernt.\n",
                        encoding="utf-8")
    for link in (STARTUP / "SchoolServer Security.lnk",
                 PROGRAMS / "SchoolServer Security.lnk",
                 PROGRAMS / "SchoolServer Security Manager.lnk"):
        try:
            link.unlink(missing_ok=True)
        except OSError:
            pass
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    except Exception:
        pass
    errors = []
    for path in (INSTALL_DIR, DATA_DIR):
        try:
            if path.exists():
                shutil.rmtree(path)
        except Exception as exc:
            errors.append(str(exc))
    return errors, farewell


def installed_version():
    metadata = INSTALL_DIR / "SSS_Data" / "version.json"
    if not (INSTALL_DIR / "sss_main.py").is_file():
        return "Nicht installiert"
    try:
        return str(json.loads(metadata.read_text(encoding="utf-8")).get("version", "unbekannt"))
    except Exception:
        return "Installation beschädigt"


class Manager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SSS Manager")
        self.geometry("680x570")
        self.minsize(620, 520)
        self.configure(bg=BG)
        self.busy = False
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL, relief="flat")
        style.configure("TLabel", background=BG, foreground=INK)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=INK, font=("Segoe UI", 23, "bold"))
        style.configure("Section.TLabel", background=PANEL, foreground=INK, font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 11),
                        background=PANEL, foreground=INK, bordercolor=BORDER)
        style.map("TButton", background=[("active", "#eaf3ed"), ("disabled", "#edf0ee")])
        style.configure("Primary.TButton", background=GREEN, foreground="white",
                        bordercolor=GREEN, padding=(14, 12))
        style.map("Primary.TButton", background=[("active", GREEN_DARK), ("disabled", "#9ab9a5")],
                  foreground=[("disabled", "white")])
        style.configure("Danger.TButton", foreground="#a33b35")
        style.configure("Horizontal.TProgressbar", troughcolor="#e7eee9",
                        background=GREEN, bordercolor="#e7eee9", lightcolor=GREEN, darkcolor=GREEN)

        outer = tk.Frame(self, bg=BG, padx=26, pady=24)
        outer.pack(fill="both", expand=True)
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="SSS", bg=GREEN, fg="white",
                 font=("Segoe UI", 16, "bold"), width=4, height=2).pack(side="left", padx=(0, 14))
        titles = tk.Frame(header, bg=BG)
        titles.pack(side="left", fill="x", expand=True)
        ttk.Label(titles, text="SchoolServer Security", style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text="MANAGER  ·  REPARATUR UND SYSTEMVERWALTUNG",
                  style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

        panel = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER,
                         highlightthickness=1, padx=18, pady=17)
        panel.pack(fill="x")
        ttk.Label(panel, text="Installationsstatus", style="Section.TLabel").pack(anchor="w")
        self.status = tk.Label(panel, text="", bg=PANEL, fg=MUTED,
                               justify="left", anchor="w", wraplength=560,
                               font=("Segoe UI", 9))
        self.status.pack(fill="x", pady=(8, 2))

        ttk.Label(outer, text="Aktionen", style="Section.TLabel").pack(anchor="w", pady=(20, 9))
        actions = tk.Frame(outer, bg=BG)
        actions.pack(fill="x")
        self.check_button = ttk.Button(actions, text="Status aktualisieren", command=self.check)
        self.check_button.pack(fill="x", pady=4)
        self.repair_button = ttk.Button(actions, text="SSS reparieren", style="Primary.TButton",
                                        command=self.repair)
        self.repair_button.pack(fill="x", pady=4)
        self.update_button = ttk.Button(actions, text="Nach Updates suchen", command=self.update_app)
        self.update_button.pack(fill="x", pady=4)
        self.remove_button = ttk.Button(actions, text="SSS vollständig deinstallieren",
                                        style="Danger.TButton", command=self.remove)
        self.remove_button.pack(fill="x", pady=4)
        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill="x", pady=(17, 8))
        ttk.Label(outer, text="Reparatur und Update laden das offizielle Python-Paket von GitHub. "
                              "Einstellungen, Protokolle und Quarantäne bleiben bei einer Reparatur erhalten.",
                  style="Muted.TLabel", wraplength=610).pack(anchor="w")
        self.check()

    def check(self):
        self.status.configure(text=f"Installiert: {installed_version()}\n"
                                   f"Programm: {INSTALL_DIR}\n"
                                   f"Daten: {DATA_DIR}\n"
                                   f"Quarantäne: {QUARANTINE_DIR}")
        self.check_button.configure(state="normal")

    def set_busy(self, busy, label=""):
        self.busy = busy
        state = "disabled" if busy else "normal"
        for button in (self.check_button, self.repair_button, self.update_button, self.remove_button):
            button.configure(state=state)
        if busy:
            self.progress.start(12)
            self.status.configure(text=label + "\nBitte warten. Dieses Fenster geöffnet lassen.")
        else:
            self.progress.stop()
            self.check()

    def run_action(self, title, action):
        if self.busy:
            return
        self.set_busy(True, title)

        def work():
            try:
                result = action()
                self.after(0, lambda: self.action_done(title, result, None))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self.action_done(title, None, error))
        threading.Thread(target=work, daemon=True).start()

    def action_done(self, title, result, error):
        self.set_busy(False)
        if error:
            messagebox.showerror("SSS Manager", f"{title} fehlgeschlagen:\n\n{error}", parent=self)
        else:
            messagebox.showinfo("SSS Manager", f"{title} erfolgreich.\nInstallierte Version: {result}", parent=self)

    def repair(self):
        if messagebox.askyesno("SSS reparieren",
            "Die Programmdateien werden durch eine frische offizielle Version ersetzt. "
            "Einstellungen, Logs und Quarantäne bleiben erhalten.\n\nFortfahren?", parent=self):
            self.run_action("Reparatur", install_or_repair)

    def update_app(self):
        if self.busy:
            return
        self.set_busy(True, "Suche nach einer neuen Version …")

        def check_latest():
            try:
                latest = get_latest_version()
                current = installed_version()
                self.after(0, lambda: self.confirm_update(current, latest))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self.action_done("Updateprüfung", None, error))
        threading.Thread(target=check_latest, daemon=True).start()

    def confirm_update(self, current, latest):
        self.set_busy(False)
        if current == latest:
            question = f"Version {latest} ist bereits installiert. Soll die Installation trotzdem repariert werden?"
        else:
            question = f"Installiert: {current}\nVerfügbar: {latest}\n\nJetzt aktualisieren?"
        if messagebox.askyesno("SSS aktualisieren", question, parent=self):
            self.run_action("Update", install_or_repair)

    def remove(self):
        if self.busy:
            return
        if not messagebox.askyesno("SSS vollständig entfernen",
            "Programmordner, Einstellungen, Logs, Quarantäne und Verknüpfungen werden gelöscht.\n"
            "Ollama bleibt installiert. Auf dem Desktop bleibt eine Abschiedsdatei zurück.\n\n"
            "Dieser Vorgang kann nicht rückgängig gemacht werden. Wirklich deinstallieren?", parent=self):
            return
        errors, farewell = uninstall()
        if errors:
            messagebox.showerror("Deinstallation teilweise fehlgeschlagen",
                                 "\n".join(errors), parent=self)
        else:
            messagebox.showinfo("SSS entfernt", f"SSS wurde entfernt.\n\nAbschiedsdatei:\n{farewell}", parent=self)
        self.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Windows erforderlich", "Der SSS Manager ist für Windows vorgesehen.")
        raise SystemExit(1)
    try:
        os.chdir(Path.home())
    except OSError:
        pass
    Manager().mainloop()
