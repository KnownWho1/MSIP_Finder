from pathlib import Path
from typing import Dict, Any
from .base import BaseScanner

class MSGEMLScanner(BaseScanner):
    SUPPORTED_EXTENSIONS = {'.msg', '.eml'}
    
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
            if file_path.suffix.lower() == '.msg':
                try:
                    import extract_msg
                    msg = extract_msg.Message(str(file_path))
                    # Check properties
                    try:
                        props = msg.props
                        for k, v in props.items():
                            kstr = str(k).lower()
                            if any(x in kstr for x in ['msip', 'sensitivity', 'label', 'mip', 'classification']):
                                entry = {
                                    "labelId": None,
                                    "labelName": str(v) if v is not None else None,
                                    "description": None,
                                    "parentLabels": [],
                                    "whereItCameFrom": f"msg:properties:{k}",
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
                    except Exception as e:
                        result['scanNotes'].append(f"MSG props error: {str(e)}")
                    try:
                        msg.close()
                    except:
                        pass
                except Exception as e:
                    result['scanNotes'].append(f"Failed to parse MSG: {str(e)}")
            elif file_path.suffix.lower() == '.eml':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    # Look for headers/properties
                    for line in content.splitlines():
                        lline = line.lower()
                        if any(x in lline for x in ['msip', 'sensitivity', 'label', 'mip']):
                            entry = {
                                "labelId": None,
                                "labelName": line.strip()[:200],
                                "description": None,
                                "parentLabels": [],
                                "whereItCameFrom": "eml:header",
                                "rawFieldValue": {"header": line.strip()},
                                "appliedAt": None,
                                "previousLabelId": None,
                                "previousLabelName": None,
                            }
                            import re
                            guids = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', line)
                            if guids:
                                entry['labelId'] = guids[0]
                            result['labelEntries'].append(entry)
                            break  # just first match to avoid duplicates
                except Exception as e:
                    result['scanNotes'].append(f"Failed to parse EML: {str(e)}")
        except Exception as e:
            result['status'] = 'scan_error'
            result['scanNotes'].append(f"Failed to parse email: {str(e)}")
            return result
        
        if result['labelEntries']:
            result['status'] = 'labelled'
        else:
            result['status'] = 'no_label_detected'
        
        return result
