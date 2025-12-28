# Settings

import os
import param
import panel as pn

from pathlib import Path

class Settings(param.Parameterized):
    limit_count = param.Integer(1000 * 40, allow_None=True) # default 1000 * 40

    n_embd = param.Integer(1000, label="n_embd") # default 1000
    dropout = param.Number(0.2, label="dropout") # default 0.2
    n_head = param.Integer(10, label='n_head') # default 10
    block_size = param.Integer(150, label='block_size')  # the maximum context length for predictions
    n_layer = param.Integer(10, label='n_layer') # default 10

    learning_rate = param.Number(1e-4,label='learning_rate') # default 1e-4

    mmx_file_path = param.Path(default=os.fspath(Path('../../set.new2023.mmx').resolve()), label='mmx_file_path')
    corpus01_file_path = param.Path(default=os.fspath(Path('../../corpus01.txt').resolve()), check_exists=False, label='corpus01_file_path')
    corpus_folder_path = param.Path(default=os.fspath(Path('../corpus').resolve()), label='corpus_folder_path')
    model_folder_path = param.Path(default=os.fspath(Path("../model").resolve()), label='model_folder_path')

    def view(self):
        return pn.WidgetBox(
            pn.Column(pn.pane.Markdown("# Settings")),
            pn.Column(
                "## Parser03",
                self.param.limit_count,
            ),
            pn.Column(
                "## model",
                self.param.n_embd,
                self.param.n_head,
                self.param.block_size,
                self.param.dropout,
                self.param.n_layer,
            ),
            pn.Column(
                "## optimizer",
                self.param.learning_rate,
            ),
            pn.Column(
                "## paths",
                self.param.mmx_file_path,
                self.param.corpus01_file_path,
                self.param.corpus_folder_path,
                self.param.model_folder_path,
            ),
            pn.Column(pn.pane.Markdown("# End")),
            max_width=600,
        )