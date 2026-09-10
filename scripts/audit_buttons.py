from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
text='\n'.join(p.read_text(encoding='utf-8') for p in root.rglob('*.py') if '__pycache__' not in p.parts and '.pytest_cache' not in p.parts)
callbacks=set()
for m in re.finditer(r'callback_data\s*=\s*["\']([^"\']+)', text):
    callbacks.add(m.group(1).split(':',1)[0])
# Dynamic f-strings are intentionally audited by their static prefix.
handled=set()
for m in re.finditer(r'(?:data|q\.data)\s*(?:\.startswith\(\s*["\']|==\s*["\'])([^"\']+)', text):
    handled.add(m.group(1).split(':',1)[0])
unhandled=sorted(x for x in callbacks if x not in handled and x not in {'home','back'})
if unhandled:
    print('UNHANDLED_CALLBACK_PREFIXES', unhandled)
    raise SystemExit(1)
print(f'BUTTON_AUDIT_OK callbacks={len(callbacks)} handled_prefixes={len(handled)}')
