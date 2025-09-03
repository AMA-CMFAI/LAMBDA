import queue
import re
import base64
from io import BytesIO
import re
import os
from typing import Tuple, Any
import jupyter_client
from PIL import Image
from subprocess import PIPE
from pprint import pprint
import nbformat
from nbformat import v4 as nbf
import time
import ansi2html
from utils.utils import check_install_kernel

IPYKERNEL = os.environ.get('IPYKERNEL', 'lambda')


class CodeKernel(object):
    def __init__(self,
                 kernel_name='kernel',
                 kernel_id=None,
                 kernel_config_path="",
                 python_path=None,
                 ipython_path=None,
                 init_file_path="./startup.py",
                 session_cache_path="",
                 max_exe_time=18000,
                 verbose=1):

        self.kernel_name = kernel_name
        self.kernel_id = kernel_id
        self.kernel_config_path = kernel_config_path
        self.python_path = python_path
        self.ipython_path = ipython_path
        self.init_file_path = init_file_path
        self.session_cache_path = session_cache_path
        # self.executed_cells = []
        self.max_exe_time = max_exe_time
        self.nb = nbf.new_notebook()
        self.nb_path = os.path.join(session_cache_path, 'notebook.ipynb')
        self.verbose = verbose
        self.interrupt_signal = False

        if python_path is None and ipython_path is None:
            env = None
        else:
            env = {"PATH": self.python_path + ":$PATH", "PYTHONPATH": self.python_path}

        check_install_kernel('lambda')

        self.kernel_manager = jupyter_client.KernelManager(
            kernel_name=IPYKERNEL,
            connection_file=self.kernel_config_path,
            exec_files=[self.init_file_path],
            env=env)

        # if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        #     self.kernel_manager = jupyter_client.KernelManager(
        #         connection_file=self.kernel_config_path,
        #         exec_files=[self.init_file_path],
        #         env=env)
        # else:
        #     self.kernel_manager = jupyter_client.KernelManager(
        #         kernel_name=IPYKERNEL,
        #         connection_file=self.kernel_config_path,
        #         exec_files=[self.init_file_path],
        #         env=env)

        if self.kernel_config_path:
            self.kernel_manager.load_connection_file()
            self.kernel_manager.start_kernel(stdout=PIPE, stderr=PIPE)
            print("Backend kernel started with the configuration: {}".format(
                self.kernel_config_path))
        else:
            self.kernel_manager.start_kernel(stdout=PIPE, stderr=PIPE)
            print("Backend kernel started with the configuration: {}".format(
                self.kernel_manager.connection_file))

        if verbose:
            pprint(self.kernel_manager.get_connection_info())

        self.kernel = self.kernel_manager.blocking_client()
        self.kernel.start_channels()
        print("Code kernel started.")

    def execute_code_(self, code):
        msg_id = self.kernel.execute(code)
        # Get the output of the code
        msg_list = []
        while True:
            try:
                iopub_msg = self.kernel.get_iopub_msg(timeout=self.max_exe_time)
                msg_list.append(iopub_msg)
                if iopub_msg['msg_type'] == 'status' and iopub_msg['content'].get('execution_state') == 'idle':
                    break
            except:
                if self.interrupt_signal:
                    self.kernel_manager.interrupt_kernel()
                    self.interrupt_signal = False
                continue

        all_output = []
        # sign = None
        for iopub_msg in msg_list:
            if iopub_msg['msg_type'] == 'stream':
                if iopub_msg['content'].get('name') == 'stdout':
                    output = iopub_msg['content']['text']
                    all_output.append(('stdout', output))
            elif iopub_msg['msg_type'] == 'execute_result':
                if 'data' in iopub_msg['content']:
                    if 'text/plain' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['text/plain']
                        all_output.append(('execute_result_text', output))

                    if 'text/html' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['text/html']
                        all_output.append(('execute_result_html', output))

                    if 'image/png' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['image/png']
                        all_output.append(('execute_result_png', output))
                        save_b64_2_img(output, self.session_cache_path)

                    if 'image/jpeg' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['image/jpeg']
                        all_output.append(('execute_result_jpeg', output))
                        save_b64_2_img(output, self.session_cache_path)
            elif iopub_msg['msg_type'] == 'display_data':
                if 'data' in iopub_msg['content']:
                    if 'text/plain' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['text/plain']
                        all_output.append(('display_text', output))

                    if 'text/html' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['text/html']
                        all_output.append(('display_html', output))

                    if 'image/png' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['image/png']
                        all_output.append(('display_png', output))
                        save_b64_2_img(output, self.session_cache_path)

                    if 'image/jpeg' in iopub_msg['content']['data']:
                        output = iopub_msg['content']['data']['image/jpeg']
                        all_output.append(('display_jpeg', output))
                        save_b64_2_img(output, self.session_cache_path)
            elif iopub_msg['msg_type'] == 'error':
                if 'traceback' in iopub_msg['content']:
                    output = '\n'.join(iopub_msg['content']['traceback'])
                    all_output.append(('error', output))
        # print("len of console messages: " + str(len(all_output)))

        return all_output

    def execute_code(self, code) -> Tuple[
        list, str, str]:  # list[list, list, list]: #  Return: 1. sginal of resut, eg: text, error. 2. test to LLM. 3. The content to display.
        text_to_llm = ["Summary of console output:\n"]
        sign = list()
        content_to_display = []
        images = []
        result = self.execute_code_(code)
        self.add_code_cell_to_notebook(code)
        # print("Console output: " ,content_to_display)
        for mark, out_str in result:
            if mark in ('stdout', 'execute_result_text', 'display_text'):
                sign.append('text')  # sign.append(mark)
                text_to_llm.append(out_str)
                content_to_display.append(out_str)
                self.add_code_cell_output_to_notebook(out_str)

            elif mark in ('execute_result_png', 'execute_result_jpeg', 'display_png', 'display_jpeg'):
                sign.append("image")
                text_to_llm.append(f'Generated an image file in {self.session_cache_path}.')
                # content_to_display.append(out_str)
                if 'png' in mark:
                    images.append(('png', out_str))
                    self.add_image_to_notebook(out_str, 'image/png')
                else:
                    images.append(('jpg', out_str))
                    self.add_image_to_notebook(out_str, 'image/jpeg')

            elif mark == 'error':
                text_to_llm.append(delete_color_control_char(out_str))  # the error msg gave to LLM should be clean
                sign.append('error')
                self.add_code_cell_error_to_notebook(out_str)

        return sign, '\n'.join(text_to_llm), '\n'.join(content_to_display)  # '\n'.join(text_to_gpt), content_to_display
        # return sign, '\n'.join(text_to_llm), '\n'.join(content_to_display)

    # def export(self, file_path):
    #     # nb = nbf.v4.new_notebook()
    #     # nb.cells = self.executed_cells
    #     # print("cell: ", nb.cells)
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         nbf.write(nb, f)
    #     print(f"Notebook exported to {file_path}")

    # def export(self, file_path):
    #     # nb = nbf.v4.new_notebook()
    #     # nb.cells = self.executed_cells
    #     # print("cell: ", nb.cells)
    #     with open(file_path, 'w', encoding='utf-8') as f:
    #         nbf.write(nb, f)
    #     print(f"Notebook exported to {file_path}")

    def execute_interactive(self, code, verbose=False):
        shell_msg = self.kernel.execute_interactive(code)
        if shell_msg is queue.Empty:
            if verbose:
                print("Timeout waiting for shell message.")
        self.check_msg(shell_msg, verbose=verbose)

        return shell_msg

    def inspect(self, code, verbose=False):
        msg_id = self.kernel.inspect(code)
        shell_msg = self.kernel.get_shell_msg(timeout=30)
        if shell_msg is queue.Empty:
            if verbose:
                print("Timeout waiting for shell message.")
        self.check_msg(shell_msg, verbose=verbose)

        return shell_msg

    def get_error_msg(self, msg, verbose=False) -> str | None:
        if msg['content']['status'] == 'error':
            try:
                error_msg = msg['content']['traceback']
            except:
                try:
                    error_msg = msg['content']['traceback'][-1].strip()
                except:
                    error_msg = "Traceback Error"
            if verbose:
                print("Error: ", error_msg)
            return error_msg
        return None

    def check_msg(self, msg, verbose=False):
        status = msg['content']['status']
        if status == 'ok':
            if verbose:
                print("Execution succeeded.")
        elif status == 'error':
            for line in msg['content']['traceback']:
                if verbose:
                    print(line)

    def shutdown(self):
        # Shutdown the backend kernel
        self.kernel_manager.shutdown_kernel(now=True)
        print("Backend kernel shutdown.")
        # Shutdown the code kernel
        self.kernel.shutdown()
        print("Code kernel shutdown.")

    def restart(self):
        # Restart the backend kernel
        self.kernel_manager.restart_kernel()
        print("Backend kernel restarted.")

    def start(self):
        # Initialize the code kernel
        self.kernel = self.kernel_manager.blocking_client()
        # self.kernel.load_connection_file()
        self.kernel.start_channels()
        print("Code kernel started.")

    def interrupt(self):
        # Interrupt the backend kernel
        self.kernel_manager.interrupt_kernel()
        print("Backend kernel interrupted.")

    def is_alive(self):
        return self.kernel.is_alive()

    def add_code_cell_to_notebook(self, code):
        code_cell = nbf.new_code_cell(source=code)
        self.nb['cells'].append(code_cell)

    def add_code_cell_output_to_notebook(self, output):
        html_content = ansi_to_html(output)
        cell_output = nbf.new_output(output_type='display_data', data={'text/html': html_content})
        self.nb['cells'][-1]['outputs'].append(cell_output)

    def add_code_cell_error_to_notebook(self, error):
        nbf_error_output = nbf.new_output(
            output_type='error',
            ename='Error',
            evalue='Error message',
            traceback=[error]
        )
        self.nb['cells'][-1]['outputs'].append(nbf_error_output)

    def add_image_to_notebook(self, image, mime_type):
        image_output = nbf.new_output(output_type='display_data', data={mime_type: image})
        self.nb['cells'][-1]['outputs'].append(image_output)

    def add_markdown_to_notebook(self, content, title=None):
        if title:
            content = "##### " + title + ":\n" + content
        markdown_cell = nbf.new_markdown_cell(content)
        self.nb['cells'].append(markdown_cell)

    def write_to_notebook(self, notebook_path):
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(self.nb, f)
        print(f"Notebook exported to {notebook_path}")


def ansi_to_html(ansi_text):
    converter = ansi2html.Ansi2HTMLConverter()
    html_text = converter.convert(ansi_text)
    return html_text


def delete_color_control_char(string):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', string)


def save_b64_2_img(data, path):
    bs64_img = base64.b64decode(data)
    img_path = os.path.join(path, f"{hash(time.time())}.png")
    with open(img_path, 'wb') as f:
        f.write(bs64_img)
    print(f"Executing: Image saved in {img_path}")
    return f"Image saved in {img_path}"  # Image.open(buff)


def clean_ansi_codes(input_string):
    ansi_escape = re.compile(r'(\x9B|\x1B\[|\u001b\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', input_string)


def execute(code, kernel: CodeKernel):
    msg = kernel.execute_code(code)
    return msg


# @st.cache_resource
def get_kernel():
    kernel = CodeKernel()
    return kernel


if __name__ == '__main__':
    kernel = CodeKernel(session_cache_path="./cache/cache_test/")
    text_code = "print('Hello world!')"
    print(text_code, kernel)
    table_code = """
    import pandas as pd
    data = pd.read_csv('data/wine.csv')
    data.head()
    """
    img_code = """
    import matplotlib.pyplot as plt
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 6]

    plt.plot(x, y)

    plt.title('Simple Line Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.show()
    """

    file_code = """
    text_content = "This is file test."
    with open('example.txt', 'w', encoding='utf-8') as file:
        file.write(text_content)

    print("saved example.txt")
    """

    error_code = "print(ss)"

    none_code = "a = None"
    # res_type, res = execute(img_code, kernel)
    # print(res_type,res)
    all_test_code = [text_code, table_code, img_code, file_code, error_code, none_code]
    for i in all_test_code:
        msg = execute(i, kernel)
        print(msg)
    kernel.write_to_notebook("./cache/cache_test/my_notebook2.ipynb")
