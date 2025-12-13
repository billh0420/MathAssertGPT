# from assert_gpt
# get_syntax_deriver.py

from pathlib import Path

from source.shared import SyntaxDeriver
from source.shared import AssertDB

def get_syntax_deriver(corpus_folder_path: Path) -> SyntaxDeriver:
    assert_db = AssertDB(assert_db_file_path=corpus_folder_path.joinpath('assert.db'))
    syntax_deriver = SyntaxDeriver(assert_db=assert_db)
    return syntax_deriver
