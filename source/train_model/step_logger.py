# from assert_gpt
# step_logger.py

from pathlib import Path

from source.shared import Encoder
from source.shared import generate_predicted_dictum
from source.shared import StepLogger

from source.evaluate_model import get_syntax_deriver

class AssertStepLogger(StepLogger):

    def __init__(self, model, encoder: Encoder, terminal_token: str, model_folder_path: str, corpus_folder_path: str):
        self.model = model
        self.encoder = encoder
        self.terminal_token = terminal_token
        self.model_folder_path = Path(model_folder_path).resolve()
        self.errors_file = self.model_folder_path.joinpath('errors.txt')
        self.oks_file = self.model_folder_path.joinpath('oks.txt')
        self.syntax_deriver = get_syntax_deriver(corpus_folder_path=corpus_folder_path)

    def log_step(self, step: int, max_examples: int):
        block_size = self.model.block_size
        error_count = 0
        ok_count = 0
        error_counts = [0] * block_size  # error_count by number correct
        ok_counts = [0] * block_size  # ok_count by number correct
        self.model.eval()  # set to eval mode
        for example in range(max_examples):
            prompt = '|- '
            predicted_statement = generate_predicted_dictum(prompt=prompt, terminal_token=self.terminal_token, model=self.model)
            wff_statement = predicted_statement.removeprefix('|- ').removesuffix(' <|over|>')
            self.syntax_deriver.derive_syntax(statement=wff_statement, context=None)
            syntax_derivation = self.syntax_deriver.syntaxDerivation
            derivation_correct_count = self.syntax_deriver.derivation_correct_count
            if syntax_derivation is None:
                error_count += 1
                error_counts[derivation_correct_count] += 1
            else:
                ok_count += 1
                ok_counts[derivation_correct_count] += 1
        with open(self.errors_file, "a") as errors_file:
            str_error_counts = ', '.join(map(str, error_counts))
            line = f'{step}, {str_error_counts}\n'
            errors_file.write(line)
        with open(self.oks_file, "a") as oks_file:
            str_ok_counts = ', '.join(map(str, ok_counts))
            line = f'{step}, {str_ok_counts}\n'
            oks_file.write(line)
        self.model.train()  # set to train mode
