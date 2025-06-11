import os
import shutil
import gradio as gr

from assets.i18n.i18n import I18nAuto

i18n = I18nAuto()

now_dir = os.getcwd()


def create_log_folder(folder_name, files):
    if not folder_name:
        return "Folder name must not be empty."

    folder_name = os.path.basename(folder_name)
    target_folder = os.path.join(now_dir, "logs", folder_name)

    os.makedirs(target_folder, exist_ok=True)

    if files:
        for f in files:
            shutil.move(f, os.path.join(target_folder, os.path.basename(f)))

    return f"Files moved to folder {target_folder}"


def log_manager_tab():
    gr.Markdown(i18n("## Model Folder Creator"))
    gr.Markdown(
        i18n(
            "Create or open a folder for a model inside logs and move uploaded files into it."
        )
    )
    with gr.Column():
        folder_name = gr.Textbox(
            label=i18n("Model Name"),
            placeholder=i18n("Enter model name"),
            value="",
            interactive=True,
            max_lines=1,
        )
        files = gr.File(
            label=i18n("Files"), type="filepath", file_count="multiple"
        )
        create_button = gr.Button(i18n("Create Log Folder"))
        output_info = gr.Textbox(
            label=i18n("Output Information"),
            info=i18n("The output information will be displayed here."),
        )

    create_button.click(
        fn=create_log_folder,
        inputs=[folder_name, files],
        outputs=[output_info],
    )
