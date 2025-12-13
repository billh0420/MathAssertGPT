# from shared.syntax_deriver
# SyntaxDeriverErrorState.py

from dataclasses import dataclass

from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverError

@dataclass(eq=True, unsafe_hash=True)
class ErrorState:
    error: SyntaxDeriverError
    token_count: int
    tokens: str
    current_token_count: int
    current_tokens: str

@dataclass(eq=True, unsafe_hash=True)
class ErrorStateRule(ErrorState):
    ruleName: str
    rule: str
    mark_index: int

@dataclass(eq=True, unsafe_hash=True)
class ErrorStateNotCompleted(ErrorState):
    pass
