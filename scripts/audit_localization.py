import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.i18n import LANGS, TEXT

base=set(TEXT[LANGS[0]])
errors=False
for lang in LANGS[1:]:
    missing=sorted(base-set(TEXT[lang])); extra=sorted(set(TEXT[lang])-base)
    if missing or extra:
        errors=True
        print(f'{lang}: missing={missing} extra={extra}')
if errors:
    raise SystemExit(1)
print(f'LOCALIZATION_PARITY_OK keys={len(base)} langs={len(LANGS)}')
