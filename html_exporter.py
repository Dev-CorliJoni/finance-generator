
def export_html(finance_models: list, export_path: str) -> None:
    template_path = ".\\index_template.html"
    content = ""

    with open(template_path, 'r') as f:
        html = f.read()

    for finance_model in finance_models:
        content = content + finance_model.to_html()

    with open(export_path, 'w') as f:
        f.write(html.format(website_content=content))
