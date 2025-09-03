import re
from pathlib import Path
import os
import jupyter_client.kernelspec
from ipykernel.kernelspec import install
import sys
import os
from pathlib import Path

def get_project_root():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(os.path.dirname(sys.executable))
    else:
        # 如果是正常的 .py 腳本運行，使用原始的向上尋找邏輯
        current_dir = Path(__file__).resolve().parent
        while current_dir != current_dir.parent:
            if (current_dir / '.git').exists() or (current_dir / 'setup.py').exists():
                return current_dir
            current_dir = current_dir.parent
        # 如果找不到標記，可以返回當前工作目錄或腳本目錄作為備用
        return Path(os.getcwd())


def to_absolute_path(relative_path):
    project_root = get_project_root()
    if os.path.isabs(relative_path):
        return relative_path

    return str(project_root / relative_path)

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


def check_install_kernel(kernel_name: str):
    """
    Checks if a Jupyter kernel exists and installs it if it doesn't.

    The new kernel will be based on the Python environment
    that is currently running this script.
    """
    print("Checking for Jupyter kernel...")

    # Get a list of all installed kernel specs
    kernel_specs = jupyter_client.kernelspec.find_kernel_specs()

    if kernel_name in kernel_specs:
        print(f"✅ Kernel '{kernel_name}' already exists at: {kernel_specs[kernel_name]}")
    else:
        print(f"❌ Kernel '{kernel_name}' not found. Installing now...")
        # Install the new kernel for the current user
        install(user=True, kernel_name=kernel_name)
        print(f"✅ Successfully installed kernel '{kernel_name}'.")


if __name__ == '__main__':
    # check_install_kernel(kernel_name="lambda")
    print(to_absolute_path("cache/conv_cache/"))