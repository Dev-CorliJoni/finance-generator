import shutil
from os import listdir, makedirs
from os.path import join, isfile, isdir


def export_html(finance_models: list, export_path: str) -> None:
    template_folder = ".//html_export"
    static_exports_folder = join(template_folder, "static_exports")
    template_path = join(template_folder, "index_template.html")
    content = ""

    with open(template_path, 'r') as f:
        html = f.read()

    for finance_model in finance_models:
        content = content + finance_model.to_html()

    if not isdir(export_path):
        makedirs(export_path)

    with open(join(export_path, "index.html"), 'w') as f:
        f.write(html.format(website_content=content))

    files = [(join(static_exports_folder, f), f".{join(static_exports_folder.replace(template_folder, ""), f)}")
             for f in listdir(static_exports_folder)]

    for file_path, name in files:
        if isfile(file_path):
            makedirs(join(export_path, *(name.split("/")[:-1])), exist_ok=True)
            shutil.copyfile(file_path, join(export_path, name))
