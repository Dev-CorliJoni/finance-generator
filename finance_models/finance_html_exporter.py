
class FinanceHTMLExporter(object):

    def __init__(self, template_path):
        with open(template_path) as f:
            self.html = f.read()

    def export_html(self, **kwargs):
        return self.html.format(**kwargs)
