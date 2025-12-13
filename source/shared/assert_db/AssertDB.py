# from shared.assert_gpt
# AssertDB.py

import sqlite3
import pandas as pd

from pathlib import Path
from collections import namedtuple
from tabulate import tabulate

def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

Labels_By_Variable_Row = namedtuple('LabelsByVariableRow', ['var_name', 'label'])
Typecodes_By_Variable_Row = namedtuple('Typecodes_By_Variable_Row', ['var_name', 'typecode'])
Labels_by_syntax_expression_row = namedtuple('Labels_by_syntax_expression_row', ['syntax_expression', 'label'])
Math_statements_by_label_row = namedtuple('Math_statements_by_label_row',['statement_ID', 'statement_label', 'statement_type', 'type_code', 'statement', 'hyps'])

class AssertDB:

    def __init__(self, assert_db_file_path: Path):
        # print(f'assert_db_file_path={assert_db_file_path}')
        self.conn = sqlite3.connect(assert_db_file_path)

        self.conn.row_factory = namedtuple_factory

        self._create_labels_by_variable_table()
        self._create_typecodes_by_var_table()
        self._create_labels_by_syntax_expression_table()
        self._create_math_statements_by_label_table()

    def commit(self):
        self.conn.commit()
        print(f'AssertDB did commit')

    def close(self):
        self.conn.close()
        print(f'AssertB did close')

    def dump_table(self, table_name: str):
        print(f'\n=== Dump {table_name} table using pandas ===')
        table = pd.read_sql_query(f"SELECT * from {table_name} ORDER BY id", self.conn)
        print(tabulate(table, showindex=False, headers=table.columns, stralign="left", tablefmt='psql'))

    def _create_labels_by_variable_table(self):
        sql_statement = \
            """CREATE TABLE IF NOT EXISTS labels_by_variable_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    var_name TEXT NOT NULL, 
                    label TEXT);
            """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS labels_by_variable_index ON labels_by_variable_table(var_name)')
        except sqlite3.Error as e:
            print(e)

    def _create_typecodes_by_var_table(self):
        sql_statement = \
            """CREATE TABLE IF NOT EXISTS typecodes_by_var_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    var_name TEXT NOT NULL, 
                    typecode TEXT);
            """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
        except sqlite3.Error as e:
            print(e)

    def _create_labels_by_syntax_expression_table(self):
        sql_statement = \
            """CREATE TABLE IF NOT EXISTS labels_by_syntax_expression_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    syntax_expression TEXT NOT NULL, 
                    label TEXT);
            """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
        except sqlite3.Error as e:
            print(e)

    def _create_math_statements_by_label_table(self):
        sql_statement = \
            """CREATE TABLE IF NOT EXISTS math_statements_by_label_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    statement_ID INTEGER,
                    statement_label TEXT NOT NULL,
                    statement_type TEXT,
                    type_code TEXT,
                    statement TEXT,
                    hyps TEXT);
            """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_statement)
        except sqlite3.Error as e:
            print(e)
