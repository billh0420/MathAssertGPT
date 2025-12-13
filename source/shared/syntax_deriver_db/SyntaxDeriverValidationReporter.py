# from shared.syntax_deriver_db
# SyntaxDeriverValidationReporter.py

from collections.abc import Callable

from source.shared.syntax_deriver_db.SyntaxDeriverDB import SyntaxDeriverDB

class SyntaxDeriverValidationReporter:

    def __init__(self, syntax_deriver_db: SyntaxDeriverDB, block_size: int):
        self.syntax_deriver_db = syntax_deriver_db
        self.block_size = block_size
        # reset variables
        self.error_count = 0
        self.ok_count = 0
        self.error_counts = [0] * block_size  # error_count by number correct
        self.ok_counts = [0] * block_size  # ok_count by number correct
        self.max_error_index = 0
        self.max_ok_index = 0

    def print_validation_report(self, max_print_error: int, max_print_ok: int, print_context: Callable[[str], None] | None = None):
        self._reset()
        conn = self.syntax_deriver_db.conn
        cursor = conn.cursor()
        sql = 'SELECT id, statement, context, derivation, derivation_correct_count, syntax_deriver_error FROM math_statements ORDER BY id'
        cursor.execute(sql)
        math_statement_rows = cursor.fetchall()
        example_count = len(math_statement_rows)
        if example_count > 0:
            print(f'\n=== print_validation_report ===\n')
            for example, math_statement_row in enumerate(math_statement_rows):
                derivation = math_statement_row.derivation
                derivation_correct_count = math_statement_row.derivation_correct_count
                if derivation is None:
                    self.error_count += 1
                    self.error_counts[derivation_correct_count] += 1
                    self.max_error_index = max(self.max_error_index, derivation_correct_count)
                    statement_id = math_statement_row.id
                    sql = f'SELECT statement_id, rule_name, rule, mark_index, rule_tokens, current_rule_tokens FROM rule_errors WHERE statement_id = {statement_id} ORDER BY id'
                    cursor.execute(sql)
                    rule_error_rows = cursor.fetchall()
                    if self.error_count <= max_print_error:
                        self.print_math_statement_error(example=example, error_count=self.error_count, math_statement_row=math_statement_row, print_context=print_context)
                        self.print_rule_errors(math_statement_row=math_statement_row, rule_error_rows=rule_error_rows)
                else:
                    self.ok_count += 1
                    self.ok_counts[derivation_correct_count] += 1
                    self.max_ok_index = max(self.max_ok_index, derivation_correct_count)
                    if self.ok_count <= max_print_ok:
                        self._print_math_statement_ok(example=example, math_statement_row=math_statement_row, print_context=print_context)
            self._print_summary(example_count=example_count)

    def _reset(self):
        self.error_count = 0
        self.ok_count = 0
        self.error_counts = [0] * self.block_size  # error_count by number correct
        self.ok_counts = [0] * self.block_size  # ok_count by number correct
        self.max_error_index = 0
        self.max_ok_index = 0

    def _print_math_statement_ok(self, example: int, math_statement_row, print_context):
        derivation = math_statement_row.derivation
        print(f'===== Example {example + 1} =====')
        if print_context is not None:
            context = math_statement_row.context
            if context is not None:
                print_context(context)
        print(f'syntaxDerivation: {derivation}')

    def print_math_statement_error(self, example: int, error_count: int, math_statement_row, print_context):
        syntax_deriver_error = math_statement_row.syntax_deriver_error
        derivation_correct_count = math_statement_row.derivation_correct_count
        print(f'===== Example {example + 1} error:{error_count} =====')
        if print_context is not None:
            context = math_statement_row.context
            if context is not None:
                print_context(context)
        if syntax_deriver_error is not None:
            print(f'{syntax_deriver_error}')
        print(f'derivation_correct_count={derivation_correct_count}')

    def print_rule_errors(self, math_statement_row, rule_error_rows):
        syntax_deriver_error = math_statement_row.syntax_deriver_error
        if syntax_deriver_error == 'SyntaxDeriverNotCompletedError':
            self._print_not_completed_error(math_statement_row=math_statement_row)
        else:
            for rule_error_row in rule_error_rows:
                self._print_rule_error_row(math_statement_row=math_statement_row, rule_error_row=rule_error_row)

    def _print_not_completed_error(self, math_statement_row):
        wff_statement = math_statement_row.statement
        derivation_correct_count = math_statement_row.derivation_correct_count
        statement_tokens = wff_statement.split()
        statement_part = " ".join(statement_tokens[:derivation_correct_count])
        statement_rest = " ".join(statement_tokens[derivation_correct_count:])
        print(f'\tfull_statement: {wff_statement}')
        print(f'\tstatement_part: {statement_part}')
        print(f'\tstatement_rest: {statement_rest}')
        print(f'\texpected: statement_rest should be empty since statement_part is a wff.')
        print(f'\tderivation_correct_count={derivation_correct_count}')

    def _print_rule_error_row(self, math_statement_row, rule_error_row):
        wff_statement = math_statement_row.statement
        rule_name = rule_error_row.rule_name
        mark_index = rule_error_row.mark_index
        rule = rule_error_row.rule.split()
        rule_tokens = rule_error_row.rule_tokens.split()
        current_rule_tokens = rule_error_row.current_rule_tokens.split()
        rule_token_count = len(rule_tokens)
        current_rule_token_count = len(current_rule_tokens)
        statement_tokens = wff_statement.split()
        statement_part = " ".join(statement_tokens[:-rule_token_count])
        statement_rest = rule_error_row.rule_tokens
        if current_rule_token_count == 0:
            statement_peek = rule_tokens
            actual_token = 'end_of_statement'
        else:
            statement_peek = " ".join(rule_tokens[:-current_rule_token_count])
            actual_token = statement_tokens[-current_rule_token_count]
            print(f'{rule_name}: {rule_error_row.rule} mark_index={mark_index} token_count={rule_token_count} current_token_count={current_rule_token_count}')
        print(f'\tfull_statement: {wff_statement}')
        print(f'\tstatement_part: {statement_part}')
        print(f'\tstatement_rest: {statement_rest}')
        print(f'\tstatement_peek: {statement_peek}')
        print(f'\texpected: {rule[mark_index]} got: {actual_token}')

    def _print_summary(self, example_count: int):
        print()
        print(f'ok_count={self.ok_count}')
        print(f'error_count={self.error_count}')
        print(f'errors={self.error_counts[:self.max_error_index + 1]}')
        print(f'oks={self.ok_counts[:self.max_ok_index + 1]}')
        print(f'error_percentage={self.error_count * 100 / example_count: .2f}%')
