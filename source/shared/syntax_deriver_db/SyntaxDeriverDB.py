# from shared.syntax_deriver_db
# SyntaxDeriverDB.py

import sqlite3
import pandas as pd

from collections import namedtuple

MathStatement_Row = namedtuple('MathStatement_Row',
                               ['statement', 'context', 'derivation', 'derivation_correct_count', 'syntax_deriver_error'])
RuleError_Row = namedtuple('RuleError_Row',
                           ['statement_id', 'rule_name', 'rule', 'mark_index', 'rule_tokens', 'current_rule_tokens'])

def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

def index_for(minor, major):
    result = len(major.split()) - len(minor.split())
    return result

class SyntaxDeriverDB:

    def __init__(self):
        self.conn = sqlite3.connect(':memory:')  # database in memory only

        self.conn.row_factory = namedtuple_factory
        self.conn.create_function("index_for", 2, index_for)

        self.create_math_statemnts_table()
        self.create_rule_errors_table()
        self.create_main_view()

    def reset(self):
        self.conn.execute('DELETE FROM rule_errors;')
        self.conn.execute('DELETE FROM math_statements;')

    def add_math_statement(self, math_statement_row: MathStatement_Row):
        field_names = ', '.join(math_statement_row._fields)
        question_marks = ",".join("?" * len(math_statement_row))
        sql = f'INSERT INTO math_statements({field_names}) VALUES({question_marks})'
        cursor = self.conn.cursor()
        cursor.execute(sql, math_statement_row)
        return cursor.lastrowid

    def add_rule_error(self, rule_error_row: RuleError_Row):  # prefer this one
        field_names = ', '.join(rule_error_row._fields)
        question_marks = ",".join("?" * len(rule_error_row))
        sql = f'INSERT INTO rule_errors({field_names}) VALUES({question_marks})'
        cursor = self.conn.cursor()
        cursor.execute(sql, rule_error_row)
        return cursor.lastrowid

    def update_math_statement_derivation(self, math_statement_id: int, derivation: str | None):  # FIXME: how to avoid multiple methods to update
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE math_statements SET derivation = ? WHERE id = ?', [derivation, math_statement_id])
        except sqlite3.Error as e:
            print(e)

    def update_math_statement_derivation_correct_count(self, math_statement_id: int, derivation_correct_count: int):  # FIXME: how to avoid multiple methods to update
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE math_statements SET derivation_correct_count = ? WHERE id = ?', [derivation_correct_count, math_statement_id])
        except sqlite3.Error as e:
            print(e)

    def delete_rule_errors(self, statement_id: int):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM rule_errors WHERE statement_id = ?', [statement_id])
        except sqlite3.Error as e:
            print(e)

    def delete_duplicate_rule_error_rows(self):
        field_names = ', '.join(RuleError_Row._fields)
        group_by = f'GROUP BY {field_names}'
        sql = \
    f"""
    DELETE FROM rule_errors WHERE ROWID NOT IN
    (
        SELECT MIN(ROWID) FROM rule_errors
        {group_by}
    );
    """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except sqlite3.Error as e:
            print(e)

    def create_main_view(self):
        sql = \
    """CREATE VIEW IF NOT EXISTS main_view AS
        SELECT rule_name, rule, mark_index, derivation_correct_count, statement,
                index_for(rule_tokens, statement) AS token_index,
                index_for(current_rule_tokens, statement) AS current_token_index
        FROM rule_errors
        JOIN math_statements ON math_statements.id = rule_errors.statement_id
    """
        self.conn.execute(sql)

    def print_main_view(self):
        cursor = self.conn.cursor()
        cursor.execute('select rule_name, rule, mark_index, statement, derivation_correct_count, token_index, current_token_index from main_view')
        rows = cursor.fetchall()
        for row in rows:
            rule_name, rule, mark_index, statement, derivation_correct_count, token_index, current_token_index = row
            split_statement = statement.split()
            print(f'statement: {statement}')
            print(f'rule_name: {rule_name} rule: {rule} mark_index: {mark_index}')
            print(f'\ttoken_index={token_index} token={split_statement[token_index]}')
            print(f'\tcurrent_token_index={current_token_index} current_token={split_statement[current_token_index]}')

    def dump_math_statements_table(self):
        print(f'\n=== Dump math_statements table using pandas ===')
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        table = pd.read_sql_query("SELECT * from math_statements ORDER BY id", self.conn)
        print(table)

    def dump_rule_errors_table(self):
        print(f'\n=== Dump rule_errors table using pandas ===')
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        table = pd.read_sql_query("SELECT * from rule_errors ORDER BY id", self.conn)
        print(table)

    def create_math_statemnts_table(self):
        sql_statement = \
    """CREATE TABLE IF NOT EXISTS math_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            statement TEXT NOT NULL, 
            context TEXT,
            derivation TEXT,
            derivation_correct_count INT,
            syntax_deriver_error TEXT);
    """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
        except sqlite3.Error as e:
            print(e)

    def create_rule_errors_table(self):
        sql_statement = \
    """CREATE TABLE IF NOT EXISTS rule_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            rule_name TEXT NOT NULL,
            rule TEXT NOT NULL,
            mark_index INT,
            rule_tokens TEXT,
            current_rule_tokens TEXT,
            statement_id INT NOT NULL,
            FOREIGN KEY (statement_id) REFERENCES math_statements (id));
    """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
        except sqlite3.Error as e:
            print(e)

    def drop_table(self, table_name: str):
        # Drop table if it already exists.
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        except sqlite3.Error as e:
            print(f'\nError drop_table table_name={table_name}: {e}\n')

    def show_math_statements_table(self):
        try:
            print(f'--- math_statements ---')
            cursor = self.conn.cursor()
            cursor.execute('select id, statement, derivation, derivation_correct_count from math_statements ORDER BY id')
            rows = cursor.fetchall()
            for row in rows:
                statement_id, statement, derivation, derivation_correct_count = row
                print(f'{statement_id}. statement: {statement} derivation: {derivation} derivation_correct_count: {derivation_correct_count}')
        except sqlite3.Error as e:
            print(e)

    def show_rule_errors_table(self):
        try:
            print(f'--- rule_errors ---')
            cursor = self.conn.cursor()
            cursor.execute('select id, statement_id, rule_name, rule, mark_index, rule_tokens, current_rule_tokens from rule_errors ORDER BY id')
            rows = cursor.fetchall()
            for row in rows:
                rule_error_id, statement_id, rule_name, rule, mark_index, rule_tokens, current_rule_tokens = row
                print(f'{rule_error_id}. statement_id: {statement_id} rule_name: {rule_name} rule: {rule} mark_index: {mark_index}')
                print(f'\trule_tokens: {rule_tokens}')
                print(f'\tcurrent_rule_tokens: {current_rule_tokens}')
        except sqlite3.Error as e:
            print(e)
