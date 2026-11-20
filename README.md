# SchoolServer Security (SSS) 2.0

**Local-first file security assistant**  
Developed by Adam Gabriel Kraus.

SSS 2.0 replaces the previous Tkinter prototype with a single PySide6 desktop GUI and a separate non-executing file inspection engine.

## Current 2.0 scope
- New desktop UI (single supported GUI)
- Scheduled recurring local scan with countdown
- Configurable scan folders and exclusions
- SHA-256 file hashes
- Optional ClamAV detection if clamscan is installed
- Basic defensive script-pattern checks
- Explicit user-confirmed reversible quarantine move for flagged files
- Optional local AI explanations via Ollama; no external AI calls

## Local AI setup
1. Install Ollama from its official website.
2. Start Ollama locally.
3. Pull the configured model, for example `ollama pull qwen2.5:3b`.
4. Open SSS and select a scan result, then choose **KI-Erklärung**.

AI status is shown as local online/offline. AI output is advisory and cannot override the scanner findings. The scanner does not execute analyzed files.

## Developer run
Python 3.10+ is recommended.

```powershell
py -3 -m pip install -r requirements.txt
py -3 sss_gui.py
```

## Build standalone executable
Install PyInstaller and run:
```powershell
py -3 -m pip install -r requirements.txt pyinstaller
py -3 -m PyInstaller --noconfirm --clean --windowed --onefile --name SSS sss_gui.py
```
The standalone EXE does not include the local AI model. Ollama and a model must be installed separately.

## Safety limitations
SSS 2.0 is a development project and is **not a certified antivirus/endpoint protection product**. It can miss malware and generate false positives. Quarantine moves are user-confirmed. Do not use it as your sole security control on school or production systems. Deployment on school computers requires approval from authorized IT staff.
