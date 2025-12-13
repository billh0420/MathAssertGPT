# from shared.syntax_deriver
# SyntaxDeriverExtraction.py

from typing import NamedTuple

class SyntaxDeriverExtraction(NamedTuple):
    peekedTokens: list[str]
    accumulator: list[str]
