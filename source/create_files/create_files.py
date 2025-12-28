# create_files.py
# from assert_gpt

import os
from pathlib import Path

from source.create_files.get_assert_corpus import get_assert_corpus
from source.create_files.get_labelsBySyntaxExpression import get_labelsBySyntaxExpression
from source.create_files.get_labelsByVariable import get_labelsByVariable
from source.create_files.get_mathStatementsByLabel import get_mathStatementsByLabel
from source.create_files.get_typecodesByVar import get_typecodesByVar

from source.shared import AssertDB
from source.shared import Encoder
from source.shared import get_tokens

from source.shared import Labels_By_Variable_Row, Typecodes_By_Variable_Row, Labels_by_syntax_expression_row, Math_statements_by_label_row

from source.shared import Parser03 as Parser

def create_files(corpus_folder_path: str, limit_count: int | None, mmx_file_path: Path, corpus01_file_path: Path):
    corpus_file_path = Path(corpus_folder_path).joinpath('corpus.txt').resolve()
    if not corpus_file_path.exists():
        assert_db_file_path = Path(corpus_folder_path).joinpath('assert.db').resolve()
        if os.path.exists(assert_db_file_path):
            raise Exception(f'assert.db already exists at {assert_db_file_path}')
        assert_db = AssertDB(assert_db_file_path=assert_db_file_path)

        print(f'mmx_file_path={mmx_file_path}')
        parser = Parser(mmx_file_path=mmx_file_path, limit_count=limit_count)
        assert_corpus = get_assert_corpus(parser=parser, corpus01_file_path=corpus01_file_path)

        print(f'#assert_corpus={len(assert_corpus)}')

        # labels_by_variable_table
        labelsByVariable = get_labelsByVariable(parser=parser)
        for var_name, label in labelsByVariable.items():
            row = Labels_By_Variable_Row(var_name=var_name, label=label)
            field_names = ', '.join(Labels_By_Variable_Row._fields)
            question_marks = ",".join("?" * len(row))
            sql = f'INSERT INTO labels_by_variable_table({field_names}) VALUES({question_marks})'
            cursor = assert_db.conn.cursor()
            cursor.execute(sql, row)

        # typecodes_by_var_table
        typecodesByVar = get_typecodesByVar(parser=parser)
        for var_name, typecode in typecodesByVar.items():
            row = Typecodes_By_Variable_Row(var_name=var_name, typecode=typecode)
            field_names = ', '.join(Typecodes_By_Variable_Row._fields)
            question_marks = ",".join("?" * len(row))
            sql = f'INSERT INTO typecodes_by_var_table({field_names}) VALUES({question_marks})'
            cursor = assert_db.conn.cursor()
            cursor.execute(sql, row)

        # labels_by_syntax_expression_table
        labelsBySyntaxExpression = get_labelsBySyntaxExpression(parser=parser)
        for syntax_expression, label in labelsBySyntaxExpression.items():
            row = Labels_by_syntax_expression_row(syntax_expression=syntax_expression, label=label)
            field_names = ', '.join(Labels_by_syntax_expression_row._fields)
            question_marks = ",".join("?" * len(row))
            sql = f'INSERT INTO labels_by_syntax_expression_table({field_names}) VALUES({question_marks})'
            cursor = assert_db.conn.cursor()
            cursor.execute(sql, row)

        # math_statements_by_label_table
        mathStatementsByLabel = get_mathStatementsByLabel(parser=parser, labelsBySyntaxExpression=labelsBySyntaxExpression)
        for label, math_statement in mathStatementsByLabel.items():  # FIXME: 240929 redo and simplify
            statementID = math_statement['statementID']
            statement_label = math_statement['statement_label']
            statement_type = math_statement['statementType']
            type_code = math_statement['type_code']
            statement = math_statement['statement']
            hyps = '\n'.join(math_statement['hyps'])  # FIXME: 240929 can this be done better ?
            row = Math_statements_by_label_row(statementID, statement_label, statement_type, type_code, statement, hyps)
            field_names = ', '.join(Math_statements_by_label_row._fields)
            question_marks = ",".join("?" * len(row))
            sql = f'INSERT INTO math_statements_by_label_table({field_names}) VALUES({question_marks})'
            cursor = assert_db.conn.cursor()
            cursor.execute(sql, row)

        assert_db.commit()

        # corpus_statements
        corpus_statements: list[str] = []
        for assert_utterance in assert_corpus:
            corpus_statement = ' '.join(assert_utterance)
            corpus_statements.append(corpus_statement)
        print(f'assert_corpus_size={len(assert_corpus)}')

        # encoder
        tokens = get_tokens(corpus_statements)
        encoder = Encoder(tokens=tokens)
        print(f'vocab_size={len(encoder.tokens)}')

        # save corpus_statements
        corpus_file_name = corpus_file_path.name
        print(f'create {corpus_file_name}: size={len(assert_corpus)}; corpus_file_path={corpus_file_path}')
        with open(corpus_file_path, 'w') as file:
            for statement in corpus_statements:
                file.write(f'{statement}\n')

        # save Encoder as json file (at least itos portion)
        print(f'create encoder.txt: corpus_folder_path={corpus_folder_path}')
        encoder.save_to_json(corpus_folder_path=corpus_folder_path)

        # close database
        assert_db.commit()
        assert_db.close()

        print("Done create_files")
