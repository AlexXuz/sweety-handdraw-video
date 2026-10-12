#!/usr/bin/env python3
"""Validate and package the single skill without host files or build artifacts."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
package = root / 'skills/sweety-handdraw-video'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
subprocess.run([sys.executable, '-B', str(package/'scripts/validate_package.py')], check=True)
version = (package/'VERSION').read_text().strip()
args.output.mkdir(parents=True, exist_ok=True)
archive = args.output / f'sweety-handdraw-video-v{version}.zip'
checks = {}
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
    for path in sorted(package.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name == '.DS_Store' or path.suffix == '.pyc':
            continue
        relative = path.relative_to(package).as_posix()
        content = path.read_bytes()
        checks[relative] = hashlib.sha256(content).hexdigest()
        metadata = zipfile.ZipInfo('sweety-handdraw-video/'+relative, date_time=(2026,10,12,0,0,0))
        metadata.compress_type = zipfile.ZIP_DEFLATED
        metadata.external_attr = 0o644 << 16
        bundle.writestr(metadata,content)
(args.output/'package-sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
(args.output/'SHA256SUMS.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
print(json.dumps({'archive':str(archive),'files':len(checks),'bytes':archive.stat().st_size}))
