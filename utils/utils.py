import re
from pathlib import Path
import os


def find_project_root():
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.parent:
        if (current_dir / '.git').exists() or (current_dir / 'setup.py').exists():
            return current_dir
        current_dir = current_dir.parent
    return current_dir


def to_absolute_path(relative_path):
    project_root = find_project_root()
    if os.path.isabs(relative_path):
        return relative_path

    return str((project_root / relative_path).resolve())

def extract_code(text: str) -> tuple[bool, str]:
    pattern = r'```python([^\n]*)(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches)>1:
        code_blocks = ''
        for match in matches:
            code_block = match[1]
            code_blocks += code_block
        return True, code_blocks
    elif len(matches):
        code_block = matches[-1]
        #if 'python' in code_block[0]:
        return True, code_block[1]
    else:
        return False, ''

if __name__ == '__main__':
    print(to_absolute_path("cache/conv_cache/"))