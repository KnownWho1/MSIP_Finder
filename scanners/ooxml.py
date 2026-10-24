import zipfile
from pathlib import Path
from typing import Dict, Any, List
from lxml import etree
from .base import BaseScanner

class OOXMLScanner(BaseScanner):
    SUPPORTED_EXTENSIONS = {'.docx', '.docm', '.xlsx', '.xlsm', '.pptx', '.pptm'}
    
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
            with zipfile.ZipFile(file_path, 'r') as z:
                # Look in custom properties
                try:
                    custom = z.read('docProps/custom.xml')
                    result = self._parse_custom_props(custom, result, 'docx:customProps/custom.xml')
                except KeyError:
                    pass
                # Also check extended/app props sometimes have hints
                try:
                    app = z.read('docProps/app.xml')
                except:
                    pass
        except Exception as e:
            result['status'] = 'scan_error'
            result['scanNotes'].append(f"Failed to parse OOXML: {str(e)}")
            return result
        
        if result['labelEntries']:
            result['status'] = 'labelled'
        else:
            result['status'] = 'no_label_detected'
        
        return result
    
    def _parse_custom_props(self, xml_bytes, result, where_from):
        try:
            tree = etree.fromstring(xml_bytes)
            # OOXML custom properties namespace
            ns = {'ct': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
                  'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'}
            
            for prop in tree.xpath('.//ct:property', namespaces=ns):
                name = prop.get('name', '')
                lname = name.lower()
                if any(k in lname for k in ['msip', 'sensitivity', 'label', 'mip', 'classification']):
                    # Extract value
                    val_elem = prop.find('.//vt:lpwstr', namespaces=ns) or prop.find('.//vt:lpstr', namespaces=ns) or prop.find('.//vt:bstr', namespaces=ns)
                    if val_elem is None:
                        # try any text
                        val = prop.text
                    else:
                        val = val_elem.text
                    
                    entry = {
                        "labelId": None,
                        "labelName": None,
                        "description": None,
                        "parentLabels": [],
                        "whereItCameFrom": f"{where_from}:{name}",
                        "rawFieldValue": {name: val},
                        "appliedAt": None,
                        "previousLabelId": None,
                        "previousLabelName": None
                    }
                    # Try to extract structured info if it's JSON-like or has known patterns
                    if val:
                        val_str = str(val)
                        # Common patterns
                        if 'labelid' in val_str.lower() or '{' in val_str:
                            # Try to parse as best effort
                            pass
                        # Heuristic extraction
                        entry['labelName'] = val_str if len(val_str) < 200 else val_str[:200]
                        # Look for GUIDs
                        import re
                        guids = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', val_str)
                        if guids:
                            entry['labelId'] = guids[0]
                    
                    result['labelEntries'].append(entry)
        except Exception as e:
            result['scanNotes'].append(f"Error parsing custom props: {str(e)}")
        return result
