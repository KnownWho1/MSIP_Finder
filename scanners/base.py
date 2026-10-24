import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class BaseScanner:
    SUPPORTED_EXTENSIONS = set()
    
    def __init__(self):
        self.scanned_at = datetime.utcnow().isoformat() + "Z"
    
    def can_scan(self, file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def scan(self, file_path: Path) -> Dict[str, Any]:
        raise NotImplementedError
    
    def normalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return normalize_result(result)

def normalize_result(data: Dict[str, Any]) -> Dict[str, Any]:
    label_entries = data.get('labelEntries', []) or []
    
    # Deduplicate identical labels by (labelId + labelName)
    seen = set()
    deduped = []
    for entry in label_entries:
        key = (str(entry.get('labelId') or '').strip(), str(entry.get('labelName') or '').strip())
        if key in seen and (key[0] or key[1]):
            continue  # skip duplicate
        if key[0] or key[1]:
            seen.add(key)
        deduped.append(entry)
    
    label_count = len(deduped)
    has_multiple = label_count > 1
    
    # Check for potential change
    potential_change = False
    change_details = {
        "detected": False,
        "evidence": None,
        "from": None,
        "to": None
    }
    
    # Look for explicit previous label evidence
    for entry in deduped:
        prev_id = entry.get('previousLabelId')
        prev_name = entry.get('previousLabelName')
        curr_id = entry.get('labelId')
        curr_name = entry.get('labelName')
        if prev_id or prev_name:
            if curr_id != prev_id or curr_name != prev_name:
                potential_change = True
                change_details = {
                    "detected": True,
                    "evidence": f"Found previous label ({prev_id or prev_name}) and current label ({curr_id or curr_name}) in metadata",
                    "from": {"labelId": prev_id, "labelName": prev_name},
                    "to": {"labelId": curr_id, "labelName": curr_name}
                }
                break
    
    # If multiple different labels and no explicit previous/current pairing but different IDs, still check
    if not potential_change and has_multiple:
        # Only flag if there's clear indication - but be strict per requirements
        # Check if any entry has previous fields
        ids = set()
        for e in deduped:
            if e.get('labelId'):
                ids.add(e.get('labelId'))
        if len(ids) > 1:
            # Multiple different labels present - could indicate change, but need explicit evidence
            # Don't auto-flag without explicit previousLabel fields per requirements
            pass
    
    result = {
        "fileName": data.get('fileName'),
        "filePath": data.get('filePath'),
        "archiveSource": data.get('archiveSource'),
        "fileExtension": data.get('fileExtension'),
        "status": data.get('status', 'no_label_detected'),
        "labelEntries": deduped,
        "labelCount": label_count,
        "hasMultipleLabels": has_multiple,
        "potentialChange": potential_change,
        "changeDetails": change_details,
        "scanNotes": data.get('scanNotes', []) or [],
        "scannedAt": data.get('scannedAt') or datetime.utcnow().isoformat() + "Z"
    }
    return result
