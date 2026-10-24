# MSIP Label Scanner

A local Flask web app for extracting Microsoft Purview/MSIP sensitivity labels from uploaded files (including ZIP archives). No external connections, no authentication, runs entirely offline.

## Features
- Upload individual files or ZIP archives (recursively scanned)
- Detects embedded MSIP/sensitivity label metadata from common formats
- Shows Label ID, label name, description, where it came from, parent labels (if present in metadata), and flags for multiple labels or potential label changes
- Marks files with no detectable label as "no label detected"
- Per-file error handling
- Runs locally with `python app.py` accessible at http://127.0.0.1:5000

## Supported Formats
- Office Open XML: `.docx`, `.docm`, `.xlsx`, `.xlsm`, `.pptx`, `.pptm`
- OLE2/Compound: `.doc`, `.xls`, `.ppt`
- PDF: `.pdf`
- Email: `.msg`, `.eml`
- Any other file type attempted as fallback

## Installation (local)
```bash
cd MSIP_Finder
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.
Or use `run.bat` / `run.ps1` on Windows.
