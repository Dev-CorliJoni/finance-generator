import os.path

from dataclasses import dataclass, field
from finance_models import BitpandaModel as _BitpandaModel
from html_exporter import export_html as _export_html

@dataclass
class ModelConnection:
    name_part: str = field()
    file_extension: str = field()
    model: type = field(default_factory=lambda: None)

    def match(self, filename: str) -> bool:
        return self.name_part in filename and filename.endswith(self.file_extension)


class Controller:

    def __init__(self, *args: str) -> None:
        self.finance_models = []
        model_connector = (
            ModelConnection("bitpanda-trades", "csv", _BitpandaModel),
        )

        if len(args) == 0:
            pass # raise Error

        for arg in args:
            if os.path.isfile(arg):
                for model_connection in model_connector:
                    if model_connection.match(arg):
                        self.finance_models.append(model_connection.model(arg))
            else:
                pass  # raise Error

    def export(self, filename: str) -> None:
        _export_html(self.finance_models, filename)
