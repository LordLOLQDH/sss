#!/usr/bin/env python3
"""
SchoolServer Security (SSS) - simple Python installer.
Requires Python 3.10+ on Windows.
Downloads the latest repository snapshot, installs dependencies into the user's
local SSS folder, and creates Start Menu/Desktop shortcuts.
"""
from __future__ import annotations
import os, sys, shutil, tempfile, urllib.request, zipfile, subprocess, pathlib

REPO_ZIP = "https://github.com/LordLOLQDH/sss/archive/refs/heads/main.zip"
APP_NAME = "SchoolServer Security"
INSTALL_DIR = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home())) / "SchoolServerSecurity"
START_MENU = pathlib.Path(os.environ.get("APPDATA", pathlib.Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
DESKTOP = pathlib.Path.home() / "Desktop"

def say(text):
    print(text, flush=True)

def safe_extract(zip_path, destination):
    dest = destination.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest) + os.sep) and target != dest:
                raise RuntimeError("Unsicherer Archivpfad erkannt; Abbruch.")
        zf.extractall(destination)

def powershell_shortcut(shortcut_path, target, working_dir, icon=None):
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    escaped_path = str(shortcut_path).replace("'", "''")
    escaped_target = str(target).replace("'", "''")
    escaped_work = str(working_dir).replace("'", "''")
    iconline = f"$s.IconLocation = '{str(icon).replace(chr(39), chr(39)+chr(39))}'" if icon else ""
    script = f"$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('{escaped_path}'); $s.TargetPath='{escaped_target}'; $s.WorkingDirectory='{escaped_work}'; $s.Description='{APP_NAME}'; {iconline}; $s.Save()"
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    if sys.platform != "win32":
        say("Dieser einfache Installer ist aktuell nur für Windows gedacht.")
        input("Enter zum Beenden…")
        return 1
    say("=" * 58)
    say("  SchoolServer Security (SSS) - Python-Installer")
    say("=" * 58)
    say("Zielordner: " + str(INSTALL_DIR))
    say("Der Installer lädt den öffentlichen GitHub-Quellcode und installiert")
    say("die Python-Abhängigkeiten. Er löscht keine persönlichen Dateien.")
    answer = input("Installieren? [J/n] ").strip().lower()
    if answer not in ("", "j", "ja", "y", "yes"):
        say("Installation abgebrochen.")
        return 0
    tmp_root = pathlib.Path(tempfile.mkdtemp(prefix="sss_setup_"))
    try:
        zip_file = tmp_root / "sss-source.zip"
        say("\n[1/4] Lade SSS-Quellcode herunter…")
        request = urllib.request.Request(REPO_ZIP, headers={"User-Agent": "SSS-Python-Installer"})
        with urllib.request.urlopen(request, timeout=60) as response, open(zip_file, "wb") as out:
            shutil.copyfileobj(response, out)
        say("[2/4] Entpacke Dateien…")
        if INSTALL_DIR.exists():
            # Preserve user's config and quarantine directory across updates.
            backup = tmp_root / "preserved"
            for folder in ("data", "quarantine"):
                old = INSTALL_DIR / folder
                if old.exists():
                    shutil.copytree(old, backup / folder, dirs_exist_ok=True)
        stage = tmp_root / "extracted"
        stage.mkdir()
        safe_extract(zip_file, stage)
        roots = [p for p in stage.iterdir() if p.is_dir()]
        source = roots[0] if roots else stage
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR)
        shutil.copytree(source, INSTALL_DIR)
        preserved = tmp_root / "preserved"
        for folder in ("data", "quarantine"):
            saved = preserved / folder
            if saved.exists():
                shutil.copytree(saved, INSTALL_DIR / folder, dirs_exist_ok=True)
        say("[3/4] Installiere Python-Abhängigkeiten…")
        py = sys.executable
        req = INSTALL_DIR / "requirements.txt"
        if req.exists():
            subprocess.run([py, "-m", "pip", "install", "--user", "-r", str(req)], check=True)
        gui = INSTALL_DIR / "sss_gui.py"
        if not gui.exists():
            raise RuntimeError("sss_gui.py wurde im Repository nicht gefunden.")
        say("[4/4] Erstelle Startmenü- und Desktopverknüpfungen…")
        START_MENU.mkdir(parents=True, exist_ok=True)
        link = START_MENU / "SchoolServer Security.lnk"
        powershell_shortcut(link, py, INSTALL_DIR, None)
        # Shortcut points to Python with the GUI script as its argument.
        ps = f"$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('{str(link).replace(chr(39), chr(39)+chr(39))}'); $s.TargetPath='{py.replace(chr(39), chr(39)+chr(39))}'; $s.Arguments='"{str(gui).replace(chr(39), chr(39)+chr(39))}"'; $s.WorkingDirectory='{str(INSTALL_DIR).replace(chr(39), chr(39)+chr(39))}'; $s.Description='{APP_NAME}'; $s.Save()"
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], check=True)
        powershell_shortcut(DESKTOP / "SchoolServer Security.lnk", py, INSTALL_DIR)
        # Correct shortcut arguments explicitly for desktop.
        desk = DESKTOP / "SchoolServer Security.lnk"
        ps2 = f"$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('{str(desk).replace(chr(39), chr(39)+chr(39))}'); $s.TargetPath='{py.replace(chr(39), chr(39)+chr(39))}'; $s.Arguments='"{str(gui).replace(chr(39), chr(39)+chr(39))}"'; $s.WorkingDirectory='{str(INSTALL_DIR).replace(chr(39), chr(39)+chr(39))}'; $s.Description='{APP_NAME}'; $s.Save()"
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps2], check=True)
        # Transparent uninstaller: user runs this to remove app + shortcuts.
        uninstaller = INSTALL_DIR / "uninstall_sss.py"
        uninstaller.write_text("""import pathlib, shutil, os\napp=pathlib.Path(os.environ.get('LOCALAPPDATA',pathlib.Path.home()))/'SchoolServerSecurity'\nmenu=pathlib.Path(os.environ.get('APPDATA',pathlib.Path.home()))/'Microsoft'/'Windows'/'Start Menu'/'Programs'/'SchoolServer Security.lnk'\ndesk=pathlib.Path.home()/'Desktop'/'SchoolServer Security.lnk'\nprint('Remove SSS and its installed files? This also deletes the app data and quarantine folder inside its install directory.')\nif input('Type REMOVE to confirm: ').strip()=='REMOVE':\n    menu.unlink(missing_ok=True); desk.unlink(missing_ok=True); shutil.rmtree(app,ignore_errors=True); print('SSS removed.')\nelse: print('Uninstall cancelled.')\ninput('Press Enter to close…')\n""", encoding="utf-8")
        say("\nInstallation abgeschlossen.")
        say("SSS wurde installiert unter: " + str(INSTALL_DIR))
        say("Desktop- und Startmenüverknüpfungen wurden erstellt.")
        say("Zum Entfernen: uninstall_sss.py im Installationsordner starten.")
        say("Du kannst SSS jetzt über die Verknüpfung öffnen.")
    except Exception as exc:
        say("\nInstallationsfehler: " + str(exc))
        say("Bitte kontrolliere die Fehlermeldung. Installierte Dateien bleiben im Zielordner.")
        return 1
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    input("\nEnter zum Schließen…")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
