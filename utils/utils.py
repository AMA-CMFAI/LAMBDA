import re
from pathlib import Path
import os
import jupyter_client.kernelspec
from ipykernel.kernelspec import install
import sys
import os
from pathlib import Path
import json
import shutil

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

def clear_working_path(session_cache_path):
    for filename in os.listdir(session_cache_path):
        file_path = os.path.join(session_cache_path, filename)

        # 如果是文件，删除文件
        if os.path.isfile(file_path):
            os.remove(file_path)
        # 如果是目录，递归删除目录及其内容
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    print(f"Directory {session_cache_path} has been cleared.")

def ensure_config_file(path="config.yaml"):
    """Make sure the config.yaml exist，otherwise create it."""
    DEFAULT_CONFIG = """#================================================================================================
    #                                       Config of the LLMs
    #================================================================================================
    conv_model : "gpt-5-mini"       # the conversation model
    programmer_model : "gpt-4.1-mini" # the programming model
    inspector_model : "gpt-4.1-mini"  # the inspector model
    api_key : ""                    # Set your API Key here.
    base_url_conv_model : 'https://api.openai.com/v1'
    base_url_programmer : 'https://api.openai.com/v1'
    base_url_inspector : 'https://api.openai.com/v1'

    #================================================================================================
    #                                       Config of the system
    #================================================================================================
    project_cache_path : "cache/conv_cache/"  # local cache path
    max_attempts : 5                          # The max attempts of self-correcting
    max_exe_time: 18000                       # max time for the execution
    load_chat: False                          # whether to load the dialogue from the local cache
    chat_history_path: ""                     # The path of the chat history, effective if load_chat is True.

    # knowledge integration
    retrieval : False                         # whether to start a knowledge retrieval.
    """
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG)
        print(f"[INFO] Created default config file at {os.path.abspath(path)}")
    else:
        print(f"[INFO] Using existing config file at {os.path.abspath(path)}")


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


def check_install_kernel_by_hand(kernel_name: str, display_name: str = None):
    print("Checking for Jupyter kernel...")

    if display_name is None:
        display_name = f"Python 3 ({kernel_name})"

    try:
        kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
        if kernel_name in kernel_specs:
            print(f"✅ Kernel '{kernel_name}' already exists at: {kernel_specs[kernel_name]}")
            return

        print(f"❌ Kernel '{kernel_name}' not found. Installing now...")

        spec_manager = jupyter_client.kernelspec.KernelSpecManager()
        user_kernel_dir = Path(spec_manager.user_kernel_dir)
        kernel_path = user_kernel_dir / kernel_name

        print(f"Target kernel path: {kernel_path}")

        print("Ensuring kernel directory exists...")
        os.makedirs(kernel_path, exist_ok=True)

        # 4. define kernel.json
        # todo: problem: sys.executable will point to python.exe in the app version
        kernel_spec = {
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}"
            ],
            "display_name": display_name,
            "language": "python",
            "metadata": {
                "debugger": True
            }
        }

        kernel_json_path = kernel_path / 'kernel.json'
        print(f"Writing kernel spec to: {kernel_json_path}")

        with open(kernel_json_path, 'w', encoding='utf-8') as f:
            json.dump(kernel_spec, f, indent=4)

        print(f"✅ Successfully installed kernel '{kernel_name}'.")

    except Exception as e:
        print(f"An error occurred during kernel installation: {e}")

if __name__ == '__main__':
    # check_install_kernel(kernel_name="lambda")
    print(to_absolute_path("cache/conv_cache/"))