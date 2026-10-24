from pathlib import Path
from typing import Dict, Any
from .base import BaseScanner
import re

class GenericScanner(BaseScanner):
    SUPPORTED_EXTENSIONS = set()  # used as fallback
    
    def can_scan(self, file_path: Path) -> bool:
        return True  # try all files as fallback
    
    def scan(self, file_path: Path, file_path_display: str = None, archive_source: str = None) -> Dict[str, Any]:
        result = {
            "fileName": file_path.name,
            "filePath": file_path_display or str(file_path.name),
            "archiveSource": archive_source,
            "fileExtension": file_path.suffix.lower() or '(no ext)',
            "status": "no_label_detected",
            "labelEntries": [],
            "scanNotes": [],
            "scannedAt": self.scanned_at
        }
        
        try:
            # Try to read as text for common label patterns
            try:
                with open(file_path, 'rb') as f:
                    data = f.read(4096)  # read first 4KB
                text = data.decode('utf-8', errors='ignore')
                if any(x in text.lower() for x in ['msip_label', 'sensitivitylabel', 'msip label']):
                    entry = {
                        "labelId": None,
                        "labelName": None,
                        "description": None,
                        "parentLabels": [],
                        "whereItCameFrom": "generic:binary/text-scan",
                        "rawFieldValue": {"snippet": text[:200]},
                        "appliedAt": None,
                        "previousLabelId": None,
                        "previousLabelName": None,
                    }
                    guids = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', text)
                    if guids:
                        entry['labelId'] = guids[0]
                    result['labelEntries'].append(entry)
            except Exception as e:
                result['scanNotes'].append(f"Binary scan issue: {str(e)}")
        except Exception as e:
            result['status'] = 'scan_error'
            result['scanNotes'].append(f"Failed to scan: {str(e)}")
            return result
        
        if result['labelEntries']:
            result['status'] = 'labelled'
        else:
            # Check if it's a known unscannable binary type
            ext = file_path.suffix.lower()
            if ext in ['.exe', '.dll', '.bin']:
                result['status'] = 'unsupported_for_scan'
                result['scanNotes'].append('Binary executable type - not scanned for metadata')
            else:
                result['status'] = 'no_label_detected'
        
        return result
