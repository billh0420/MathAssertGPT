#
# parser01.py
#

import re
from pathlib import Path

from source.shared.frame_stack.frame_stack import FrameStack
from source.shared.proof.proof import Proof

from typing import Self

class Parser01:

    def __init__(self, source: str):
        self.source = source
        self.frame_stack = FrameStack()
        self.labels = {}
        self.statements = []
        self.axiom_statements = []
        self.proved_statements = []
        self.label = None
        self.proved_statement_labels = set()
        self.used_proved_statement_labels = set()
        self.token_index = 0
        self.count = 0
        self.tokens: list[str] = self.remove_comments(self.collapse_whitespace(self.source))

    def setUp(self):
        self.frame_stack = FrameStack()
        self.labels = {}
        self.statements = []
        self.axiom_statements = []
        self.proved_statements = []
        self.label = None
        self.proved_statement_labels = set()
        self.used_proved_statement_labels = set()
        self.token_index = 0
        self.count = 0
        self.tokens: list[str] = self.remove_comments(self.collapse_whitespace(self.source))

    def save(self, corpus01_file_path: Path):
        with open(corpus01_file_path, 'w') as file:
            for line in self.statements:
                file.write(f'{line}\n')
        print(f"Done save corpus01: {corpus01_file_path}")

    def get_next_token(self) -> str | None:
        token = self.tokens[self.token_index] if self.token_index < len(self.tokens) else None
        self.token_index += 1
        return token

    def collapse_whitespace(self, source: str) -> list[str]:
        # Replace multiple contiguous whitespace characters with a single space.
        # Remove leading and trailing spaces.
        # Return split by space.
        return re.sub(r'\s+', ' ', source).strip().split(" ")

    def remove_comments(self, words: list[str]) -> list[str]:
        new_words = []
        from_words = iter(words)
        word = next(from_words, None)
        while word:
            if word == "$(":
                while word is not None and word != "$)":
                    word = next(from_words, None)
                if word == "$)":
                    word = next(from_words, None)
                else:
                    raise Exception(f'comment not terminated')
            else:
                new_words.append(word)
                word = next(from_words, None)
        return new_words

    def parse(self) -> Self:
        self.setUp()
        self.frame_stack.push()
        done = False
        while not done:
            token = self.get_next_token()
            if token:
                self.count += 1
                if self.count % (1000000 // 100) == 0:
                    print(f'{self.count}: {token}')
                if token == '$a':
                    self.handle_axiom_statement()
                elif token == '$c':
                    self.handle_constant_statement()
                elif token == '$d':
                    self.handle_disjoint_statement()
                elif token == '$e':
                    self.handle_essential_hypothesis()
                elif token == '$f':
                    self.handle_floating_hypothesis()
                elif token == '$p':
                    self.handle_proved_statement()
                elif token == '$v':
                    self.handle_variable_statement()
                elif token == '$[':
                    self.handle_include_statement()
                elif token == '${':
                    self.frame_stack.push()
                elif token == '$}':
                    self.frame_stack.pop()
                else:
                    if not self.label:
                        self.label = token
                    else:
                        raise Exception(f'label not used: {self.label}')
            else:
                done = True
        return self
        # print(self.tokens.token_buffer)

    def handle_axiom_statement(self):
        if not self.label:
            raise Exception(f'No label for $a')
        math_symbols = []
        type_code = self.get_next_token()
        if not type_code:
            raise Exception(f'No type code for axiom statement')
        math_symbols.append(type_code)
        token = self.get_next_token()
        while token != '$.':
            math_symbols.append(token)
            token = self.get_next_token()
        if token:
            assertion = self.frame_stack.make_assertion(math_symbols)
            self.labels[self.label] = ('$a', assertion)
            axiom_statement = f'$a {self.label} {" ".join(math_symbols)} $.'
            self.axiom_statements.append(axiom_statement)
            self.statements.append(axiom_statement)
            self.label = None
        else:
            raise Exception('$a not closed')

    def handle_constant_statement(self):
        if self.label:
            raise Exception(f'Label for $c')
        constants = []
        token = self.get_next_token()
        while token != '$.':
            constants.append(token)
            token = self.get_next_token()
        if token:
            for constant in constants:
                self.frame_stack.add_c(constant)
            constant_statement = f'$c {" ".join(constants)} $.'
            self.statements.append(constant_statement)
        else:
            raise Exception('$c not closed')

    def handle_disjoint_statement(self):
        if self.label:
            raise Exception(f'Label for $d')
        variables = []
        token = self.get_next_token()
        if token:
            variables.append(token)
            token = self.get_next_token()
        else:
            raise Exception('$d not closed')
        if token:
            variables.append(token)
            token = self.get_next_token()
        else:
            raise Exception('$d not closed')
        while token != '$.':
            variables.append(token)
            token = self.get_next_token()
        if token:
            self.frame_stack.add_d(variables)
            disjoint_statement = f'$d {" ".join(variables)} $.'
            self.statements.append(disjoint_statement)
        else:
            raise Exception('$d not closed')

    def handle_essential_hypothesis(self):
        if not self.label:
            raise Exception(f'No label for $e')
        math_symbols = []
        type_code = self.get_next_token()
        if not type_code:
            raise Exception(f'No type code for essential hypothesis')
        token = self.get_next_token()
        while token != '$.':
            math_symbols.append(token)
            token = self.get_next_token()
        if token:
            self.frame_stack.add_e(math_symbols, self.label)
            self.labels[self.label] = ('$e', f'{type_code} {" ".join(math_symbols)}')
            essential_hypothesis = f'$e {self.label} {type_code} {" ".join(math_symbols)} $.'
            self.statements.append(essential_hypothesis)
            self.label = None
        else:
            raise Exception('$e not closed')

    def handle_floating_hypothesis(self):
        if not self.label:
            raise Exception(f'No label for $f')
        type_code = self.get_next_token()
        if not type_code:
            raise Exception('No type code for floating hypothesis')
        variable = self.get_next_token()
        if not variable:
            raise Exception('No variable for floating hypothesis')
        token = self.get_next_token()
        if token == '$.':
            self.frame_stack.add_f(variable, type_code, self.label)
            self.labels[self.label] = ('$f', [type_code, variable])
            floating_hypothesis = f'$f {self.label} {type_code} {variable} $.'
            self.statements.append(floating_hypothesis)
            self.label = None
        else:
            raise Exception('$f not closed')

    def handle_proved_statement(self):
        if not self.label:
            raise Exception(f'No label for $p')
        math_symbols = []
        proof = []
        type_code = self.get_next_token()
        if not type_code:
            raise Exception(f'No type code for proved statement')
        math_symbols.append(type_code)
        token = self.get_next_token()
        while token != '$=':
            math_symbols.append(token)
            token = self.get_next_token()
        if token == '$=':
            token = self.get_next_token()
            while token != '$.':
                proof.append(token)
                token = self.get_next_token()
        if token:
            if proof[0] == '(':
                uncompressed_proof = Proof.decompress_proof_2(self.label, math_symbols, proof, self.frame_stack, self.labels)
            else:
                uncompressed_proof = proof
            proved_statement = f'$p {self.label} {" ".join(math_symbols)} $= {" ".join(uncompressed_proof)} $.'
            self.proved_statements.append(proved_statement)
            self.statements.append(proved_statement)
            self.labels[self.label] = ('$p', self.frame_stack.make_assertion(math_symbols))
            self.proved_statement_labels.add(self.label)
            for tau in uncompressed_proof:
                if tau in self.proved_statement_labels:
                    self.used_proved_statement_labels.add(tau)
            self.label = None
        else:
            raise Exception('$p not closed')

    def handle_variable_statement(self):
        if self.label:
            raise Exception(f'Label for $v')
        variables = []
        token = self.get_next_token()
        while token != '$.':
            variables.append(token)
            token = self.get_next_token()
        if token:
            for variable in variables:
                self.frame_stack.add_v(variable)
            variable_statement = f'$v {" ".join(variables)} $.'
            self.statements.append(variable_statement)
        else:
            raise Exception('$v not closed')

    def handle_include_statement(self):
        raise Exception(f'Cannot handle include statement')
