import hashlib, json
from pathlib import Path

def canonical_bytes(obj): return (json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n").encode()
def write_json(path,obj): Path(path).write_bytes(canonical_bytes(obj))
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
