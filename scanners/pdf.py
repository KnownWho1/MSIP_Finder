from pathlib import Path
from typing import Dict, Any
from .base import BaseScanner
from pypdf import PdfReader

class PDFScanner(BaseScanner):
    SUPPORTED_EXTENSIONS = {'.pdf'}
    
    def scan(self, file_path: Path, file_path_display: str = None, archive_source: str = None) -> Dict[str, Any]:
        result = {
            "fileName": file_path.name,
            "filePath": file_path_display or str(file_path.name),
            "archiveSource": archive_source,
            "fileExtension": file_path.suffix.lower(),
            "status": "no_label_detected",
            "labelEntries": [],
            "scanNotes": [],
            "scannedAt": self.scanned_at
        }
        
        try:
            reader = PdfReader(file_path)
            # Check document info
            if reader.metadata:
                meta = dict(reader.metadata)
                for k, v in meta.items():
                    kstr = str(k).lower()
                    if any(x in kstr for x in ['msip', 'sensitivity', 'label', 'mip', 'classification']):
                        entry = {
                            "labelId": None,
                            "labelName": str(v) if v is not None else None,
                            "description": None,
                            "parentLabels": [],
                            "whereItCameFrom": f"pdf:metadata:{k}",
                            "rawFieldValue": {str(k): str(v)},
                            "appliedAt": None,
                            "previousLabelId": None,
                            "previousLabelName": None,
                        }
                        import re
                        if v:
                            guids = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', str(v))
                            if guids:
                                entry['labelId'] = guids[0]
                        result['labelEntries'].append(entry)
            
            # Try to look in XMP if available
            try:
                if reader.xmp_metadata:
                    xmp = reader.xmp_metadata
                    # Basic check
                    xmp_str = str(dir(xmp))
                    if any(x in xmp_str.lower() for x in ['msip', 'label', 'sensitivity']):
                        result['scanNotes'].append('XMP metadata present with potential label references')
            except Exception:
                pass
                
        except Exception as e:
            result['status'] = 'scan_error'
            result['scanNotes'].append(f"Failed to parse PDF: {str(e)}")
            return result
        
        if result['labelEntries']:
            result['status'] = 'labelled'
        else:
            result['status'] = 'no_label_detected'
        
        return result
