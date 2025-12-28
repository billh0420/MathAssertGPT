# check_statement.py
# from source.shared.syntax_deriver_db

from pathlib import Path

from source.shared import AssertDB
from source.shared import SyntaxDeriver

def check_statement(statement: str, corpus_folder_path: str):
    assert_db = AssertDB(assert_db_file_path=Path(corpus_folder_path).joinpath('assert.db'))
    syntax_deriver = SyntaxDeriver(assert_db=assert_db)
    syntax_deriver.derive_syntax(statement=statement, context=None)
    sql = 'SELECT id, statement, context, derivation, derivation_correct_count, syntax_deriver_error FROM math_statements ORDER BY id'
    math_statement_rows = syntax_deriver.syntax_deriver_db.conn.execute(sql).fetchall()
    math_statement_row = math_statement_rows[0]
    sql = f'SELECT statement_id, rule_name, rule, mark_index, rule_tokens, current_rule_tokens FROM rule_errors WHERE statement_id = {math_statement_row.id} ORDER BY id'
    rule_error_rows = syntax_deriver.syntax_deriver_db.conn.execute(sql).fetchall()
    # print(math_statement_row)
    statement = math_statement_row.statement
    derivation = math_statement_row.derivation
    derivation_correct_count = math_statement_row.derivation_correct_count
    syntax_deriver_error = math_statement_row.syntax_deriver_error
    print(f'----- Check -----')
    if derivation:
        print('Statement has no error.')
    else:
        print('Statement has an error.')
    print(f'statement: {statement}')
    if derivation:
        print(f'derivation: {derivation}')
    else:
        correct_portion = " ".join(statement.split()[0: derivation_correct_count])
        invalid_token = statement.split()[derivation_correct_count]
        print(f'syntax_deriver_error: {syntax_deriver_error}')
        print(f'correct portion: {correct_portion}')
        print(f'invalid_token: {invalid_token}')
    print(f'derivation_correct_count: {derivation_correct_count}')
