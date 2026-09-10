import ast
from pathlib import Path
root=Path(__file__).resolve().parents[1]
errors=[]
for path in root.glob('**/*.py'):
    if any(part in {'.venv','__pycache__','.pytest_cache'} for part in path.parts): continue
    try: tree=ast.parse(path.read_text(encoding='utf-8'))
    except SyntaxError as exc: errors.append(f'{path}: syntax {exc}'); continue
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            meaningful=[n for n in node.body if not (isinstance(n,ast.Expr) and isinstance(getattr(n,'value',None),ast.Constant) and isinstance(n.value.value,str))]
            if meaningful and all(isinstance(n,ast.Pass) for n in meaningful): errors.append(f'{path}:{node.lineno} {node.name}: stub')
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print(f'FUNCTION_AUDIT_OK python_files={len(list(root.glob("**/*.py")))}')
