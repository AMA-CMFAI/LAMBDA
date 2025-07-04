import gradio
import html

def display_text(text):
    return f"""<div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;"><p>{text}</p></div>"""

def display_image(path):
    return f"""<img src=\"file={path}\" style="max-width: 80%;">"""


def display_exe_results(text):
    escaped_text = html.escape(text)
    return f"""<details style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;"><summary style="font-weight: bold; cursor: pointer;">✅Click to view execution results</summary><pre>{escaped_text}</pre></details>"""


def display_download_file(path, filename):
    return f"""<div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;"><a href=\"file={path}\" download style="font-weight: bold; color: #007bff;">Download {filename}</a></div>"""

def suggestion_html(suggestions: list) -> str:
    buttons_html = ""
    for suggestion in suggestions:
        buttons_html += f"""<button class='suggestion-btn'>{suggestion}</button>"""
    return f"<div>{buttons_html}</div>"