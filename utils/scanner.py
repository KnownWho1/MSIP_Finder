import os
import tempfile
import zipfile
from pathlib import Path
from typing import List, Dict, Any
from scanners.ooxml import OOXMLScanner
from scanners.ole import OLEScanner
from scanners.pdf import PDFScanner
from scanners.msg_eml import MSGEMLScanner
from scanners.generic import GenericScanner
from scanners.base import normalize_result
from datetime import datetime
import shutil

class LabelScanner:
    def __init__(self):
        self.scanners = [
            OOXMLScanner(),
            OLEScanner(),
            PDFScanner(),
            MSGEMLScanner(),
        ]
        self.generic = GenericScanner()
    
    def scan_files_flask(self, uploaded_files, base_temp_dir=None) -> List[Dict[str, Any]]:
        results = []
        if base_temp_dir:
            temp_dir = Path(base_temp_dir)
        else:
            temp_dir = Path(tempfile.mkdtemp(prefix='msip_scan_'))
        
        try:
            for uploaded in uploaded_files:
                filename = uploaded.filename
                if not filename or filename == '':
                    continue
                # Use secure filename to avoid issues
                from werkzeug.utils import secure_filename
                safe_name = secure_filename(filename) or filename
                file_path = temp_dir / safe_name
                uploaded.save(str(file_path))
                
                if filename.lower().endswith('.zip'):
                    results.extend(self._scan_zip(file_path, temp_dir))
                else:
                    res = self._scan_single_file(file_path, filename, None)
                    if res:
                        results.append(normalize_result(res))
            return results
        finally:
            # Clean up all temp files after scanning
            try:
                if not base_temp_dir:
                    shutil.rmtree(temp_dir)
            except Exception:
                pass
    
    def scan_files(self, uploaded_files) -> List[Dict[str, Any]]:
        return self.scan_files_flask(uploaded_files)
    
    def _scan_zip(self, zip_path: Path, temp_dir: Path) -> List[Dict[str, Any]]:
        results = []
        extract_dir = temp_dir / 'extracted'
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for member in z.namelist():
                    member_path = Path(member)
                    if member_path.is_absolute() or '..' in member_path.parts:
                        continue
                    try:
                        z.extract(member, extract_dir)
                    except Exception:
                        continue
        except Exception as e:
            return [{
                "fileName": zip_path.name,
                "filePath": zip_path.name,
                "archiveSource": None,
                "fileExtension": ".zip",
                "status": "scan_error",
                "labelEntries": [],
                "labelCount": 0,
                "hasMultipleLabels": False,
                "potentialChange": False,
                "changeDetails": {"detected": False, "evidence": None, "from": None, "to": None},
                "scanNotes": [f"Failed to extract ZIP: {str(e)}"],
                "scannedAt": datetime.utcnow().isoformat() + "Z"
            }]
        
        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                full_path = Path(root) / fname
                rel_path = full_path.relative_to(extract_dir)
                archive_source = f"zip:{rel_path.as_posix()}"
                res = self._scan_single_file(full_path, fname, archive_source, str(rel_path))
                if res:
                    results.append(normalize_result(res))
        
        # Clean up extracted files
        try:
            shutil.rmtree(extract_dir)
        except Exception:
            pass
        
        return results
    
    def _scan_single_file(self, file_path: Path, display_name: str, archive_source: str = None, display_path: str = None):
        if not file_path.exists():
            return None
        
        for scanner in self.scanners:
            if scanner.can_scan(file_path):
                try:
                    res = scanner.scan(file_path, file_path_display=display_path or display_name, archive_source=archive_source)
                    return res
                except Exception as e:
                    return {
                        "fileName": display_name,
                        "filePath": display_path or display_name,
                        "archiveSource": archive_source,
                        "fileExtension": file_path.suffix.lower(),
                        "status": "scan_error",
                        "labelEntries": [],
                        "scanNotes": [f"Scanner error: {str(e)}"],
                        "scannedAt": datetime.utcnow().isoformat() + "Z"
                    }
        
        try:
            res = self.generic.scan(file_path, file_path_display=display_path or display_name, archive_source=archive_source)
            return res
        except Exception as e:
            return {
                "fileName": display_name,
                "filePath": display_path or display_name,
                "archiveSource": archive_source,
                "fileExtension": file_path.suffix.lower() or '(no ext)',
                "status": "scan_error",
                "labelEntries": [],
                "scanNotes": [f"Generic scanner error: {str(e)}"],
                "scannedAt": datetime.utcnow().isoformat() + "Z"
            }
