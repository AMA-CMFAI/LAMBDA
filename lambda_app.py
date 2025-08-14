import gradio as gr
from front_end.js import js
from front_end.css import css
from LAMBDA import LAMBDA


def launch_app():
    Lambda = LAMBDA(config_path='config.yaml')
    with gr.Blocks(theme=gr.themes.Soft(), css=css, js=js) as demo:
        chatbot = gr.Chatbot(value=Lambda.conv.chat_history_display, height=600, label="LAMBDA", show_copy_button=True)
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
        code_btn.click(fn=Lambda.chat_streaming, inputs=[msg, chatbot, code], outputs=[msg, chatbot]).then(
            Lambda.conv.stream_workflow, inputs=[chatbot, code], outputs=chatbot)

        df = gr.Dataframe(visible=False, elem_id="df", elem_classes="df")

        upload_btn.upload(fn=Lambda.add_file, inputs=upload_btn)
        msg.submit(Lambda.chat_streaming, [msg, chatbot], [msg, chatbot], queue=False).then(
            Lambda.conv.stream_workflow, chatbot, chatbot
        )
        submit.click(Lambda.chat_streaming, [msg, chatbot], [msg, chatbot], queue=False).then(
            Lambda.conv.stream_workflow, chatbot, chatbot
        )
        board.click(Lambda.open_board, inputs=[], outputs=df)
        edit.click(Lambda.rendering_code, inputs=None, outputs=code)
        export_notebook.click(Lambda.export_code, inputs=None, outputs=[export_notebook, down_notebook])
        down_notebook.click(Lambda.down_notebook, inputs=None, outputs=[export_notebook, down_notebook])
        generate_report.click(Lambda.generate_report, inputs=[chatbot], outputs=[generate_report, down_report])
        down_report.click(Lambda.down_report, inputs=None, outputs=[generate_report, down_report])
        save.click(Lambda.save_dialogue, inputs=chatbot)
        clear.click(fn=Lambda.clear_all, inputs=[msg, chatbot], outputs=[msg, chatbot])

        demo.launch(server_name="0.0.0.0", server_port=8000, allowed_paths=[Lambda.config["project_cache_path"]],
                    share=True, inbrowser=True)


if __name__ == '__main__':
    launch_app()
