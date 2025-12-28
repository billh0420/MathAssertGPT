# from assert_gpt.evaluate_model
# ModelEvaluator.py

from source.evaluate_model.get_syntax_deriver import get_syntax_deriver

from source.shared import generate_predicted_dictum

def get_prompt() -> str:
    # prompt is |-
    prompt = '|- '
    return prompt

def get_reply(dictum: str, terminal_token: str) -> str:
    stripped_statement = dictum.removesuffix(f' {terminal_token}')
    reply_parts = stripped_statement.split(' ', maxsplit=1)
    if len(reply_parts) == 1:
        reply_parts.append(terminal_token)
    reply = reply_parts[1]
    return reply

class ModelEvaluator:

    def __init__(self, corpus_folder_path: str, model):
        # here are all the unique tokens that occur in this text
        vocab_size = len(model.encoder.tokens)
        print(f'vocab_size={vocab_size}')
        print(f'epoch={model.epoch}; step={model.step}; n_head={model.n_head}; n_layer={model.n_layer}')

        self.terminal_token = '<|over|>'
        self.syntax_deriver = get_syntax_deriver(corpus_folder_path=corpus_folder_path)
        self.model = model

        # All the following need to be reset when start evaluate_model
        self.error_count = 0

    def _reset(self):
        self.error_count = 0

    def evaluate_model(self, max_examples: int):
        self.model.eval()  # set to eval mode
        print(f'=== start evaluate_model ===')
        print(f'max_val_examples={max_examples}')
        syntax_deriver = self.syntax_deriver
        self._reset()
        for example in range(max_examples):
            prompt = get_prompt()
            predicted_statement = generate_predicted_dictum(prompt=prompt, terminal_token=self.terminal_token, model=self.model)
            wff_statement = get_reply(dictum=predicted_statement, terminal_token=self.terminal_token)
            context = '\n'.join([prompt, predicted_statement])
            syntax_deriver.derive_syntax(statement=wff_statement, context=context)
            if syntax_deriver.syntaxDerivation is None:
                self.error_count += 1
            if (example + 1) % 10 == 0 and example + 1 <= max_examples:  # show progress
                print(f'{example + 1}. error_count={self.error_count}')
        self.model.train()  # set to train mode

def unit_test_evaluate_model(corpus_folder_path: str):
    terminal_token = '<|over|>'
    syntax_deriver = get_syntax_deriver(corpus_folder_path=corpus_folder_path)
    prompt = get_prompt()
    # wff = '( E. x A. y ( y e. x <-> E. x ( x e. w /\\ A e. y ) ) <-> E. y A. x ( x e. y <-> ( A F x <-> E. y ( y e. z /\\ E. x ( x e. w /\\ A F y ) ) ) ) )'
    # wff = '( ( ( ( ( ps -> ps ) -> ( -. -. ps -> -. ps ) ) -> -. ps ) -> ps ) -> ph ) -> ps ) -> ( ( ps /\ ps ) -> ( -. ps -> -. ps ) ) )'  # this has a wff followed by more tokens
    # wff = '( ( ( ( ( ps -> ps ) -> ( -. -. ps -> -. ps ) ) -> -. ps ) -> ps ) -> ph )'  # this is a wff
    wff = '( A e. V -> [_ A / x ]_ { C } = { [_ [_ A / x ]_ C } )'
    predicted_statement = f'|- {wff} {terminal_token}'
    wff_statement = get_reply(dictum=predicted_statement, terminal_token=terminal_token)
    context = '\n'.join([prompt, predicted_statement])
    syntax_deriver.derive_syntax(statement=wff_statement, context=context)
    is_ok = syntax_deriver.syntaxDerivation is not None
    print(f'is_ok={is_ok}')
