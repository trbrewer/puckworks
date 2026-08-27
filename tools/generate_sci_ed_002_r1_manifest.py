"""Generate the deterministic SCI-ED-002-R1 source manifest."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; R1=ROOT/'docs/analysis/sci_ed_002/r1'
files=[]
for p in sorted(R1.iterdir()):
    if p.is_file() and p.name!='SOURCE_MANIFEST.json':
        files.append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out={'schema_version':'sci-ed-002-r1-source-manifest/v1','files':files}
(R1/'SOURCE_MANIFEST.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
