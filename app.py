import os.path
import shutil
import sys
import traceback
import gradio as gr
import json
import random
import time
from conversation import Conversation
from prompt_engineering.prompts import *
import yaml
from front_end.js import js
from front_end.css import css
from utils.utils import *

class app():
    def __init__(self, config_path='config.yaml'):
        print("Load config: ", config_path)
        self.config = yaml.load(open(config_path, 'r'), Loader=yaml.FullLoader)
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
                print(self.conv.programmer.messages[0]["content"])


    def init_local_cache_path(self, project_cache_path):
        current_fold = time.strftime('%Y-%m-%d', time.localtime())
        hsid = str(hash(id(self))) #new_uuid = str(uuid.uuid4())
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
        local_cache_path = os.path.join(self.session_cache_path,filename)
        gen_info = self.conv.my_data_cache.get_description()
        self.conv.programmer.messages[0]["content"] += f"\nNow, user uploads the data in {local_cache_path}\n, and here is the general information of the dataset:\n {gen_info}. \nYou should care about the missing values and type of each column in your later processing."
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
            my_app.conv.programmer.messages.append({"role": "user", "content": message})
        else:
            message = code
        return "", chat_history + [[message, None]]

    def save_dialogue(self, chat_history):
        self.conv.save_conv()
        with open(os.path.join(self.session_cache_path, 'test_system_dialogue.json'), 'w') as f:
            json.dump(chat_history, f, indent=4)
            f.close()
        print(f"Dialogue saved in {os.path.join(self.session_cache_path, 'test_system_dialogue.json')}.")

    def load_dialogue(self, json_file):
        with open(json_file, 'r') as f:
            chat_history = json.load(f)
            f.close()
        self.conv.chat_history_display = chat_history
        return chat_history

    def clear_all(self, message, chat_history):
        self.conv.clear()
        return "", []

my_app = app()

with gr.Blocks(theme=gr.themes.Soft(), css=css, js=js) as demo:
    chatbot = gr.Chatbot(value=my_app.conv.chat_history_display, height=600, label="LAMBDA", show_copy_button=True)
    with gr.Group():
        with gr.Row():
            upload_btn = gr.UploadButton(label="Upload Data", file_types=["csv", "xlsx"], scale=1)
            msg = gr.Textbox(show_label=False, placeholder="Sent message to LLM", scale=6, elem_id="chatbot_input")
            submit = gr.Button("Submit", scale=1)
    with gr.Row():
        board = gr.Button(value="Show/Update DataFrame", elem_id="df_btn", elem_classes="df_btn")
        export_notebook = gr.Button(value="Notebook")
        down_notebook = gr.DownloadButton("Download Notebook", visible=False)
        generate_report = gr.Button(value="Generate Report")
        down_report = gr.DownloadButton("Download Report", visible=False)

        edit = gr.Button(value="Edit Code", elem_id="ed_btn", elem_classes="ed_btn")
        save = gr.Button(value="Save Dialogue")
        clear = gr.ClearButton(value="Clear All")

    with gr.Group():
        with gr.Row(visible=False, elem_id="ed", elem_classes="ed"):
            code = gr.Code(label="Code", scale=6)
            code_btn = gr.Button("Submit Code", scale=1)
    code_btn.click(fn=my_app.chat_streaming, inputs=[msg, chatbot, code], outputs=[msg, chatbot]).then(my_app.conv.stream_workflow, inputs=[chatbot, code], outputs=chatbot)

    df = gr.Dataframe(visible=False, elem_id="df", elem_classes="df")

    upload_btn.upload(fn=my_app.add_file, inputs=upload_btn)
    msg.submit(my_app.chat_streaming, [msg, chatbot], [msg, chatbot], queue=False).then(
        my_app.conv.stream_workflow, chatbot, chatbot
    )
    submit.click(my_app.chat_streaming, [msg, chatbot], [msg, chatbot], queue=False).then(
        my_app.conv.stream_workflow, chatbot, chatbot
    )
    board.click(my_app.open_board, inputs=[], outputs=df)
    edit.click(my_app.rendering_code, inputs=None, outputs=code)
    export_notebook.click(my_app.export_code, inputs=None, outputs=[export_notebook, down_notebook])
    down_notebook.click(my_app.down_notebook, inputs=None, outputs=[export_notebook, down_notebook])
    generate_report.click(my_app.generate_report, inputs=[chatbot], outputs=[generate_report, down_report])
    down_report.click(my_app.down_report, inputs=None, outputs=[generate_report, down_report])
    save.click(my_app.save_dialogue, inputs=chatbot)
    clear.click(fn=my_app.clear_all, inputs=[msg, chatbot], outputs=[msg, chatbot])


if __name__ == '__main__':
    config = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
    session_cache_path = config["project_cache_path"]
    demo.launch(server_name="0.0.0.0", server_port=8000, allowed_paths=[session_cache_path], share=True)
