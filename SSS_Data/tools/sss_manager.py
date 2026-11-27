#!/usr/bin/env python3
"""SchoolServer Security Manager. Standalone repair/update/uninstall utility."""
import os
import sys
import json
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import urllib.error
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
PROGRAMS = ROAMING / "Microsoft" / "Windows" / "Start Menu" / "Programs"
STARTUP = PROGRAMS / "Startup"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SchoolServerSecurity"
MANAGER_VERSION = "1.0.0"


def hidden_run(args, **kwargs):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    return subprocess.run(args, creationflags=flags, **kwargs)


def python_gui():
    candidate = Path(sys.executable).with_name("pythonw.exe")
    return str(candidate if candidate.exists() else Path(sys.executable))


def powershell(script):
    return hidden_run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True, text=True, timeout=30
    )


def make_shortcut(link, target, args=""):
    def q(value):
        return "'" + str(value).replace("'", "''") + "'"
    link = Path(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    script = (
        "$w=New-Object -ComObject WScript.Shell;"
        "$s=$w.CreateShortcut(" + q(link) + ");"
        "$s.TargetPath=" + q(target) + ";"
        "$s.Arguments=" + q(args) + ";"
        "$s.WorkingDirectory=" + q(INSTALL_DIR) + ";"
        "$s.Description=" + q(APP_NAME) + ";$s.Save()"
    )
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
            parts = Path(name).parts
            if name.startswith("/") or ".." in parts:
                raise RuntimeError("Das Downloadpaket enthält einen ungültigen Dateipfad.")
            if not (name == "sss_main.py" or name.startswith("SSS_Data/")):
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
    if not main.is_file() or not requirements.is_file() or not metadata.is_file():
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Das SSS-Paket ist unvollständig. Es wurde nichts installiert.")
    check = hidden_run([sys.executable, "-m", "py_compile", str(main)], capture_output=True, text=True)
    if check.returncode:
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Die Hauptdatei besteht die Python-Syntaxprüfung nicht:\n" + check.stderr)
    version = json.loads(metadata.read_text(encoding="utf-8")).get("version", "unbekannt")
    return stage, payload, str(version)


def install_or_repair():
    stage, payload, version = download_and_validate()
    backup = INSTALL_DIR.with_name(INSTALL_DIR.name + ".manager-backup")
    try:
        INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            shutil.rmtree(backup)
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
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        app = INSTALL_DIR / "sss_main.py"
        make_shortcut(PROGRAMS / "SchoolServer Security.lnk", python_gui(), '"' + str(app) + '"')
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
        return version
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def uninstall():
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    farewell = desktop / "SchoolServer Security - Abschied.log"
    farewell.write_text(
        "SchoolServer Security wurde entfernt.\n\n"
        "Danke, dass du SSS verwendet hast. Wir hoffen, dass es dir gute Dienste geleistet hat.\n\n"
        "Alle zu SSS gehörenden lokalen Programmdateien, Einstellungen, Protokolle und Quarantänedaten wurden entfernt.\n",
        encoding="utf-8"
    )
    for link in (STARTUP / "SchoolServer Security.lnk", PROGRAMS / "SchoolServer Security.lnk"):
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
        return "Installation beschädigt (Versionsdatei fehlt)"


class Manager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SchoolServer Security · Verwaltung")
        self.geometry("590x480")
        self.minsize(540, 440)
        self.configure(bg="#f4f7f6")
        self.busy = False
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f7f6")
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), background="#f4f7f6", foreground="#172b22")
        style.configure("Info.TLabel", font=("Segoe UI", 10), background="#f4f7f6", foreground="#68776e")
        style.configure("Action.TButton", font=("Segoe UI", 11), padding=11)
        frame = ttk.Frame(self, padding=26)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="SchoolServer Security", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Verwaltungs- und Wiederherstellungstool", style="Info.TLabel").pack(anchor="w", pady=(3, 18))
        self.status = ttk.Label(frame, text="", style="Info.TLabel", wraplength=520)
        self.status.pack(anchor="w", pady=(0, 14))
        ttk.Button(frame, text="Installation prüfen", style="Action.TButton", command=self.check).pack(fill="x", pady=4)
        ttk.Button(frame, text="SSS reparieren", style="Action.TButton", command=self.repair).pack(fill="x", pady=4)
        ttk.Button(frame, text="SSS aktualisieren", style="Action.TButton", command=self.update).pack(fill="x", pady=4)
        ttk.Button(frame, text="SSS vollständig deinstallieren", style="Action.TButton", command=self.remove).pack(fill="x", pady=4)
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(18, 8))
        ttk.Label(frame, text="Reparatur und Update laden das offizielle Python-Paket von GitHub.\nPersönliche SSS-Daten werden dabei nicht gelöscht.", style="Info.TLabel").pack(anchor="w")
        self.check()

    def check(self):
        local = installed_version()
        self.status.configure(text=f"Installiert: {local}\nInstallationsordner: {INSTALL_DIR}\nDatenspeicher: {DATA_DIR}")

    def run_action(self, title, action):
        if self.busy:
            return
        self.busy = True
        self.progress.start(12)
        self.status.configure(text=title + "\nBitte warten. Das Fenster geöffnet lassen.")
        self.update_idletasks()
        try:
            result = action()
            self.progress.stop()
            self.busy = False
            self.check()
            messagebox.showinfo("SSS-Verwaltung", f"{title} erfolgreich.\nInstallierte Version: {result}")
        except Exception as exc:
            self.progress.stop()
            self.busy = False
            self.check()
            messagebox.showerror("SSS-Verwaltung", f"{title} fehlgeschlagen:\n\n{exc}")

    def repair(self):
        if messagebox.askyesno("SSS reparieren", "Die Programmdateien werden durch eine frische offizielle Version ersetzt. Einstellungen, Logs und Quarantäne bleiben erhalten. Fortfahren?"):
            self.run_action("Reparatur", install_or_repair)

    def update(self):
        try:
            latest = get_latest_version()
        except Exception as exc:
            messagebox.showerror("Updater", f"GitHub-Version konnte nicht geprüft werden:\n{exc}")
            return
        current = installed_version()
        if current == latest:
            if not messagebox.askyesno("SSS aktualisieren", f"Version {latest} ist bereits installiert. Soll die Installation trotzdem frisch ersetzt werden?"):
                return
        elif not messagebox.askyesno("SSS aktualisieren", f"Installiert: {current}\nVerfügbar: {latest}\n\nJetzt aktualisieren?"):
            return
        self.run_action("Update", install_or_repair)

    def remove(self):
        if not messagebox.askyesno("SSS vollständig entfernen",
            "SSS-Programmordner, Einstellungen, Logs, Quarantäne, Startmenü- und Autostart-Verknüpfungen werden gelöscht.\n\n"
            "Auf dem Desktop bleibt nur eine Abschieds-Logdatei zurück. Ollama als eigenständige Anwendung bleibt installiert.\n\n"
            "Dieser Vorgang kann nicht rückgängig gemacht werden. Wirklich deinstallieren?"):
            return
        errors, farewell = uninstall()
        if errors:
            messagebox.showerror("Deinstallation teilweise fehlgeschlagen",
                "Einige Dateien konnten nicht entfernt werden:\n" + "\n".join(errors) +
                "\n\nBitte SSS schließen und die Deinstallation erneut versuchen.")
        else:
            messagebox.showinfo("SSS entfernt", f"SchoolServer Security wurde entfernt.\n\nAbschiedsdatei:\n{farewell}")
        self.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Windows erforderlich", "Der SSS-Manager ist für Windows vorgesehen.")
        raise SystemExit(1)
    Manager().mainloop()
