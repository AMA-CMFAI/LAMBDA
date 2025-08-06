import shutil
import gradio as gr
import json
import time
from conversation import Conversation
from prompt_engineering.prompts import *
import yaml
from utils.utils import *


class LAMBDA:
    def __init__(self, config_path='config.yaml'):
        print("Load config: ", config_path)
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.session_cache_path = to_absolute_path(self.init_local_cache_path(self.config["project_cache_path"]))
        print("Session cache path: ", self.session_cache_path)
        self.config["session_cache_path"] = self.session_cache_path
        self.conv = Conversation(self.config)

        self.conv.programmer.messages = [
            {
                "role": "system",
                "content": PROGRAMMER_PROMPT.format(working_path=self.session_cache_path)
            }
        ]

        if self.conv.retrieval:
            self.conv.programmer.messages[0]["content"] += KNOWLEDGE_INTEGRATION_SYSTEM

    def init_local_cache_path(self, project_cache_path):
        current_fold = time.strftime('%Y-%m-%d', time.localtime())
        hsid = str(hash(id(self)))  # new_uuid = str(uuid.uuid4())
        session_cache_path = os.path.join(project_cache_path, current_fold + '-' + hsid)
        if not os.path.exists(session_cache_path):
            os.makedirs(session_cache_path)
        return session_cache_path

    def open_board(self):
        return self.conv.show_data()

    def add_file(self, files):
        file_path = files.name
        shutil.copy(file_path, self.session_cache_path)
        filename = os.path.basename(file_path)
        self.conv.add_data(file_path)
        self.conv.file_list.append(filename)
        local_cache_path = os.path.join(self.session_cache_path, filename)
        gen_info = self.conv.my_data_cache.get_description()
        self.conv.programmer.messages[0][
            "content"] += f"\nNow, user uploads the data in {local_cache_path}\n, and here is the general information of the dataset:\n {gen_info}. \nYou should care about the missing values and type of each column in your later processing."
        print(f"Upload file in gradio path: {file_path}, local cache path: {local_cache_path}")

    def rendering_code(self):
        return self.conv.rendering_code()

    def generate_report(self, chat_history):
        down_path = self.conv.document_generation(chat_history)
        return [gr.Button(visible=False), gr.DownloadButton(label=f"Download Report", value=down_path, visible=True)]

    def export_code(self):
        down_path = self.conv.export_code()
        return [gr.Button(visible=False), gr.DownloadButton(label=f"Download Notebook", value=down_path, visible=True)]

    def down_report(self):
        return [gr.Button(visible=True), gr.DownloadButton(visible=False)]

    def down_notebook(self):
        return [gr.Button(visible=True), gr.DownloadButton(visible=False)]

    def chat_streaming(self, message, chat_history, code=None):
        if not code:
            self.conv.programmer.messages.append({"role": "user", "content": message})
        else:
            message = code
        return "", chat_history + [[message, None]]

    def save_dialogue(self, chat_history):
        self.conv.save_conv()
        with open(os.path.join(self.session_cache_path, 'system_dialogue.json'), 'w') as f:
            json.dump(chat_history, f, indent=4)
        print(f"Dialogue saved in {os.path.join(self.session_cache_path, 'system_dialogue.json')}.")

    def load_dialogue(self, dialogue):
        with open(dialogue, 'r') as f:
            chat_history = json.load(f)
        self.conv.chat_history_display = chat_history
        return chat_history

    def clear_all(self, message, chat_history):
        self.conv.clear()
        return "", []
