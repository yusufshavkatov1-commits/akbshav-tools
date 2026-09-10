from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
patterns=[r'BOT_TOKEN\s*=\s*["\'](?!\$)', r'ADMIN_BOT_TOKEN\s*=\s*["\'](?!\$)', r'password\s*=\s*["\'][^"\']+["\']', r'shell\s*=\s*True']
violations=[]
for path in root.rglob('*.py'):
    if any(part in {'.venv','__pycache__','.pytest_cache'} for part in path.parts): continue
    text=path.read_text(encoding='utf-8')
    for pat in patterns:
        if re.search(pat,text,re.I): violations.append(f'{path}: {pat}')
if violations:
    print('\n'.join(violations)); raise SystemExit(1)
print('SECURITY_STATIC_CHECK_OK')
