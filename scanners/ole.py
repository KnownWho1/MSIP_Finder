from pathlib import Path
from typing import Dict, Any
from .base import BaseScanner
import olefile

class OLEScanner(BaseScanner):
    SUPPORTED_EXTENSIONS = {'.doc', '.xls', '.ppt'}
    
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
            if not olefile.isOleFile(file_path):
                result['status'] = 'scan_error'
                result['scanNotes'].append('Not a valid OLE2 file')
                return result
            
            ole = olefile.OleFileIO(file_path)
            try:
                # Try DocumentSummaryInformation
                for prop in ole.get_properties(['\x05DocumentSummaryInformation']):
                    # Check all properties
                    for k, v in prop.items():
                        kstr = str(k).lower()
                        if any(x in kstr for x in ['msip', 'sensitivity', 'label', 'mip']):
                            entry = {
                                "labelId": None,
                                "labelName": str(v) if v is not None else None,
                                "description": None,
                                "parentLabels": [],
                                "whereItCameFrom": f"ole:DocumentSummaryInformation:{k}",
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
                result['scanNotes'].append(f"DocSummaryInfo error: {str(e)}")
            
            try:
                # Try SummaryInformation
                for prop in ole.get_properties(['\x05SummaryInformation']):
                    for k, v in prop.items():
                        kstr = str(k).lower()
                        if any(x in kstr for x in ['msip', 'sensitivity', 'label', 'mip']):
                            entry = {
                                "labelId": None,
                                "labelName": str(v) if v is not None else None,
                                "description": None,
                                "parentLabels": [],
                                "whereItCameFrom": f"ole:SummaryInformation:{k}",
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
                result['scanNotes'].append(f"SummaryInfo error: {str(e)}")
            
            ole.close()
        except Exception as e:
            result['status'] = 'scan_error'
            result['scanNotes'].append(f"Failed to parse OLE: {str(e)}")
            return result
        
        if result['labelEntries']:
            result['status'] = 'labelled'
        else:
            result['status'] = 'no_label_detected'
        
        return result
