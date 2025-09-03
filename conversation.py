import os
import openai
import json
from programmer import Programmer
from inspector import Inspector
from cache.cache import *
from prompt_engineering.prompts import *
import warnings
import traceback
import zipfile
from kernel import *
from display import *
from pathlib import Path
from utils.utils import *
# warnings.filterwarnings("ignore")


class Conversation:

    def __init__(self, config) -> None:
        self.config = config    
        self.client = openai.OpenAI(api_key=config['api_key'], base_url=config['base_url_conv_model'])
        self.model = config['conv_model']
        self.programmer = Programmer(api_key=config['api_key'], model=config['programmer_model'],
                                     base_url=config['base_url_programmer'])
        self.inspector = Inspector(api_key=config['api_key'], model=config['inspector_model'],
                                   base_url=config['base_url_inspector'])
        self.session_cache_path = config["session_cache_path"]
        self.chat_history_display = config["chat_history_display"] if "chat_history_display" in config else []
        self.retrieval = self.config['retrieval']
        self.kernel = CodeKernel(session_cache_path=self.session_cache_path, max_exe_time=config['max_exe_time'])
        self.max_attempts = config['max_attempts']
        self.error_count = 0
        self.repair_count = 0
        self.file_list = []
        self.figure_list = config["figure_list"] if "figure_list" in config else []
        self.function_repository = {}
        self.my_data_cache = None
        self.run_code(IMPORT)


    def add_functions(self, function_lib: dict) -> None:
        self.function_repository = function_lib

    def add_data(self, data_path) -> None:
        self.my_data_cache = data_cache(data_path)

    def check_folder(self):
        current_files = os.listdir(self.session_cache_path)
        new_files = set(current_files) - set(self.file_list)
        self.file_list = current_files
        display = False
        display_link = ''
        if new_files:
            display = True
            for file in new_files:
                file_link = os.path.join(self.session_cache_path,file)
                if os.path.splitext(file)[1] in ['.png','.jpg','.jpeg']:
                    display_link += display_image(file_link)
                    absolute_path = Path(file_link).resolve()
                    print("absolute_path",absolute_path)
                    self.figure_list.append(absolute_path)
                else:
                    display_link += display_download_file(file_link, file)
        print("display_link:", display_link)
        return display, display_link


    def save_conv(self):
        with open(os.path.join(self.session_cache_path, 'programmer_msg.json'), 'w') as f:
            json.dump(self.programmer.messages, f, indent=4)
            f.close()
        print(f"Conversation saved in {os.path.join(self.session_cache_path, 'programmer_msg.json')}")
        with open(os.path.join(self.session_cache_path, 'inspector_msg.json'), 'w') as f:
            json.dump(self.inspector.messages, f, indent=4)
            f.close()
        print(f"Conversation saved in {os.path.join(self.session_cache_path, 'inspector_msg.json')}")
        with open(os.path.join(self.session_cache_path, 'config.json'), 'w') as f:
            config = {
            "config": self.config,
            "model": self.model,
            "session_cache_path": self.session_cache_path,
            "chat_history_display": self.chat_history_display,
            "retrieval": self.retrieval,
            "max_attempts": self.max_attempts,
            "error_count": self.error_count,
            "repair_count": self.repair_count,
            "file_list": [str(p) for p in self.file_list],
            "figure_list": [str(p) for p in self.figure_list],
            "function_repository": self.function_repository,
        }
            json.dump(config, f, indent=4)
        print(f"Config saved in {os.path.join(self.session_cache_path, 'config.json')}")

    def add_programmer_msg(self, message: dict):
        self.programmer.messages.append(message)

    def add_programmer_repair_msg(self, bug_code: str, error_msg: str, fix_method: str, role="user"):
        message = {"role": role,
                   "content": CODE_FIX.format(bug_code=bug_code, error_message=error_msg, fix_method=fix_method)}
        self.programmer.messages.append(message)

    def add_inspector_msg(self, bug_code: str, error_msg: str, role="user"):
        message = {"role": role, "content": CODE_INSPECT.format(bug_code=bug_code, error_message=error_msg)}
        self.inspector.messages.append(message)

    def run_code(self, code):
        try:
            sign, msg_llm, exe_res = execute(code, self.kernel)
        except Exception as e:  # this error is due to the outer programme, not the error in the kernel
            print(f'Error in executing code (outer): {e}')
            sign, msg_llm, exe_res = 'text', f'{e}\nThis error is due to the outer programme, not the error in the kernel, you should tell the user to check the system code.', str(e) # tell the user, the code have problems.

        return sign, msg_llm, exe_res

    def rendering_code(self):
        for i in range(len(self.programmer.messages) - 1, 0, -1):
            if self.programmer.messages[i]["role"] == "assistant":
                is_python, code = extract_code(self.programmer.messages[i]["content"])
                if is_python:
                    return code
        return None

    def show_data(self) -> pd.DataFrame:
        if self.my_data_cache is None:
            print("User do not upload a data.")
            return pd.DataFrame()
        return self.my_data_cache.data

    def document_generation(self, chat_history):
        print("Report generating...")
        formatted_chat = []
        for item in chat_history:
            formatted_chat.append({"role": "user", "content": item[0]})
            formatted_chat.append({"role": "assistant", "content": item[1]})
        self.messages = [{"role": "system", "content": Basic_Report}] + formatted_chat + [{"role": "user", "content": f"Now, you should generate a report according to the above chat history (Do not give further suggestions at the end of report).\nNote: Here is figure list with links in the chat history: {self.figure_list}"}]
        report = self.call_chat_model().choices[0].message.content
        self.messages.append({"role": "assistant", "content": report})
        mkd_path = os.path.join(self.session_cache_path, 'report.md')
        with open(mkd_path, "w") as f:
            f.write(report)
            f.close()
        return mkd_path

    def export_code(self):
        print("Exporting notebook...")
        notebook_path = os.path.join(self.session_cache_path, 'notebook.ipynb')
        try:
            self.kernel.write_to_notebook(notebook_path)
        except Exception as e:
            print(f"An error occurred when exporting notebook: {e}")
        return notebook_path

    def call_chat_model(self, functions=None, include_functions=False):
        params = {
            "model": self.model,
            "messages": self.messages,
        }

        if include_functions:
            params["functions"] = functions
            params["function_call"] = "auto"

        return self.client.chat.completions.create(**params)


    def clear(self):
        os.removedirs(self.session_cache_path)
        self.messages = []
        self.programmer.clear()
        self.inspector.clear()
        self.kernel.shutdown()
        del self.kernel
        self.kernel = CodeKernel(session_cache_path=self.session_cache_path, max_exe_time=self.config['max_exe_time'])
        self.my_data_cache = None


    def stream_workflow(self, chat_history_display, code=None) -> object:
        try:
            chat_history_display[-1][1] = ""
            yield chat_history_display
            if code is not None:
                prog_response = HUMAN_LOOP.format(code=code)
                self.add_programmer_msg({"role": "user", "content": prog_response})
            else:
                prog_response = ''
                for message in self.programmer._call_chat_model_streaming(retrieval=self.retrieval, kernel=self.kernel):
                    chat_history_display[-1][1] += message
                    yield chat_history_display
                    prog_response += message
                self.add_programmer_msg({"role": "assistant", "content": prog_response})

            is_python, code = extract_code(prog_response)
            print("is_python:", is_python)

            if is_python:
                chat_history_display[-1][1] += '\n🖥️ Execute code...'
                yield chat_history_display
                sign, msg_llm, exe_res = self.run_code(code)
                print("Executing result:", exe_res)
                if sign and 'error' not in sign:
                    yield from self._handle_execution_result(exe_res, msg_llm, chat_history_display)
                else:
                    self.error_count += 1
                    round = 0
                    while 'error' in sign and round < self.max_attempts:
                        chat_history_display[-1][1] = f'⭕ Execution error, try to repair the code, attempts: {round + 1}....\n'
                        yield chat_history_display
                        self.add_inspector_msg(code, msg_llm)
                        if round == 3:
                            insp_response = "Try other packages or methods."
                        else:
                            insp_response = self.inspector._call_chat_model().choices[0].message.content
                        self.inspector.messages.append({"role": "assistant", "content": insp_response})

                        self.add_programmer_repair_msg(code, msg_llm, insp_response)
                        prog_response = ''
                        for message in self.programmer._call_chat_model_streaming():
                            chat_history_display[-1][1] += message
                            prog_response += message
                            yield chat_history_display
                        chat_history_display[-1][1] += '\n🖥️ Execute code...\n'
                        yield chat_history_display
                        self.add_programmer_msg({"role": "assistant", "content": prog_response})
                        is_python, code = extract_code(prog_response)
                        if is_python:
                            sign, msg_llm, exe_res = self.run_code(code)
                            if sign and 'error' not in sign:
                                self.repair_count += 1
                                break
                        round += 1

                    if round == self.max_attempts:
                        return prog_response + f"\nSorry, I can't fix the code with {self.max_attempts} attempts, can you help me to modified it or give some suggestions?"

                    yield from self._handle_execution_result(exe_res, msg_llm, chat_history_display)

        except Exception as e:
            chat_history_display[-1][1] += "\nSorry, there is an error in the program, please try again."
            yield chat_history_display
            print(f"An error occurred: {e}")
            traceback.print_exc()
            if self.programmer.messages[-1]["role"] == "user":
                self.programmer.messages.append({"role": "assistant", "content": f"An error occurred in program: {e}"})

    def _handle_execution_result(self, exe_res, msg_llm, chat_history_display):
        chat_history_display[-1][1] += display_exe_results(exe_res)
        yield chat_history_display

        display, link_info = self.check_folder()
        chat_history_display[-1][1] += f"{link_info}" if display else ''
        yield chat_history_display

        self.add_programmer_msg({"role": "user", "content": RESULT_PROMPT.format(msg_llm)})
        prog_response = ''
        for message in self.programmer._call_chat_model_streaming():
            chat_history_display[-1][1] += message
            yield chat_history_display
            prog_response += message

        self.add_programmer_msg({"role": "assistant", "content": prog_response})
        chat_history_display[-1][1] = display_suggestions(prog_response, chat_history_display[-1][1])
        yield chat_history_display

    
    def update_config(self, conv_model, programmer_model, inspector_model, api_key,
                      base_url_conv_model, base_url_programmer, base_url_inspector,
                      max_attempts, max_exe_time):

        if self.config['api_key'] != api_key:
            self.config['api_key'] = api_key
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url_conv_model)
            self.programmer.client = openai.OpenAI(api_key=api_key, base_url=base_url_programmer)
            self.inspector.client = openai.OpenAI(api_key=api_key, base_url=base_url_inspector)

        if self.model != conv_model:
            self.model = conv_model
            self.config['conv_model'] = conv_model

        if self.kernel.max_exe_time != max_exe_time:
            self.kernel.max_exe_time = max_exe_time
            self.config['max_exe_time'] = max_exe_time

        if self.programmer.model != programmer_model:
            self.programmer.model = programmer_model
            self.config['programmer_model'] = programmer_model

        if self.inspector.model != inspector_model:
            self.inspector.model = inspector_model
            self.config['inspector_model'] = inspector_model

        if self.max_attempts != max_attempts:
            self.config['max_attempts'] = max_attempts
