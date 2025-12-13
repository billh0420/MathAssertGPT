# SyntaxDeriverError.py

from dataclasses import dataclass

@dataclass(eq=True, unsafe_hash=True)
class SyntaxDeriverError(Exception):

    def __init__(self):
        super().__init__()

    @property
    def short_name(self) -> str:
        return 'SyntaxDeriverError'

class SyntaxDeriverIncompleteError(SyntaxDeriverError):

    def __init__(self, where: str):
        super().__init__()
        self.where = where

    def __str__(self):
        return f'IncompleteError: where={self.where}'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverIncompleteError({self.where})'

class SyntaxDeriverMismatchTerminalError(SyntaxDeriverError):

    def __init__(self, terminal: str):
        super().__init__()
        self.terminal = terminal

    def __str__(self):
        return f'MismatchTerminalError: terminal={self.terminal}'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverMismatchTerminalError'


class SyntaxDeriverNoAssertionStatementError(SyntaxDeriverError):

    def __init__(self, ruleName: str):
        super().__init__()
        self.where = ruleName

    def __str__(self):
        return f'NoAssertionStatementError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNoAssertionStatementError({self.where})'


class SyntaxDeriverNoMarkLabelError(SyntaxDeriverError):

    def __init__(self, where: str):
        super().__init__()
        self.where = where

    def __str__(self):
        return f'NoMarkLabelError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNoMarkLabelError({self.where})'


class SyntaxDeriverNoMathStatementError(SyntaxDeriverError):

    def __init__(self, ruleName: str):
        super().__init__()
        self.where = ruleName

    def __str__(self):
        return f'NoMathStatementError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNoMathStatementError({self.where})'


class SyntaxDeriverNotCompletedError(SyntaxDeriverError):

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f'NotCompletedError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNotCompletedError'


class SyntaxDeriverNoResultError(SyntaxDeriverError):

    def __init__(self, expected_type: str, result_type: str):
        super().__init__()
        self.expected_type = expected_type
        self.result_type = result_type

    def __str__(self):
        return f'NoResultError(result_type={self.result_type} expected_type={self.expected_type})'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNoResultError'


class SyntaxDeriverNoVariableLabelError(SyntaxDeriverError):

    def __init__(self, where: str):
        super().__init__()
        self.where = where

    def __str__(self):
        return f'NoVariableLabelError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverNoVariableLabelError'


class SyntaxDeriverUnknownMarkTypeError(SyntaxDeriverError):

    def __init__(self, mark: str, mark_type: str):
        super().__init__()
        self.mark = mark
        self.mark_type = mark_type

    def __str__(self):
        return f'UnknownMarkTypeError({self.mark}: {self.mark_type}'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverUnknownMarkTypeError'


class SyntaxDeriverWffRuleError(SyntaxDeriverError):

    def __init__(self, rulesByName: dict[str, list[str]]):
        super().__init__()
        self.rulesByName = rulesByName  # FIXME: drop this; useless

    def __str__(self):
        return f'WffRuleError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverWffRuleError'


class SyntaxDeriverFatalError(SyntaxDeriverError):

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def __str__(self):
        return f'FatalError'

    @property
    def short_name(self) -> str:
        return f'SyntaxDeriverFatalError'
