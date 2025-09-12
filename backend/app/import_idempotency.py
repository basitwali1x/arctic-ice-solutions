import hashlib
import json
from typing import Dict, Any

def hash_file_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def stable_row_hash(row: Dict[str, Any]) -> str:
    normalized = {}
    for k in row:
        if row.get(k) is not None:
            val = row[k]
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            normalized[k.replace(' ', '_').lower()] = val
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def make_idempotency_key(file_hash: str, sheet: str, row_index: int, row_hash: str) -> str:
    return f"{file_hash}:{sheet}:{row_index}:{row_hash}"
