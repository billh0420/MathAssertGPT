# print_syntax_deriver_errors.py

from source.shared import SyntaxDeriverError
from source.shared import SyntaxDeriverMismatchTerminalError
from source.shared import SyntaxDeriverIncompleteError
from source.shared import SyntaxDeriverNoMarkLabelError, SyntaxDeriverNoVariableLabelError
from source.shared import SyntaxDeriverNoAssertionStatementError, SyntaxDeriverNoMathStatementError
from source.shared import SyntaxDeriverUnknownMarkTypeError
from source.shared import SyntaxDeriverWffRuleError, SyntaxDeriverNoResultError
from source.shared import SyntaxDeriverNotCompletedError
from source.shared import SyntaxDeriverFatalError

def print_syntax_deriver_error(syntaxDeriverError: SyntaxDeriverError):
    line = _get_error_line(syntaxDeriverError)
    if line is not None:
        print(line)

def _get_error_line(error: SyntaxDeriverError) -> str | None:
    if isinstance(error, SyntaxDeriverFatalError):
        return f'SyntaxDeriverFatalError'
    elif isinstance(error, SyntaxDeriverWffRuleError):
        return f'SyntaxDeriverWffRuleError'
    elif isinstance(error, SyntaxDeriverMismatchTerminalError):
        return f'SyntaxDeriverMismatchTerminalError'
    elif isinstance(error, SyntaxDeriverNoResultError):
        return f'SyntaxDeriverNoResultError'
    elif isinstance(error, SyntaxDeriverNotCompletedError):
        return f'SyntaxDeriverNotCompletedError'
    elif isinstance(error, SyntaxDeriverIncompleteError):
        return f'SyntaxDeriverIncompleteError'
    elif isinstance(error, SyntaxDeriverNoAssertionStatementError):
        return f'SyntaxDeriverNoAssertionStatementError'
    elif isinstance(error, SyntaxDeriverNoMarkLabelError):
        return f'SyntaxDeriverNoMarkLabelError'
    elif isinstance(error, SyntaxDeriverNoMathStatementError):
        return f'SyntaxDeriverNoMathStatementError'
    elif isinstance(error, SyntaxDeriverNoVariableLabelError):
        return f'SyntaxDeriverNoVariableLabelError'
    elif isinstance(error, SyntaxDeriverUnknownMarkTypeError):
        return f'SyntaxDeriverUnknownMarkTypeError'
    elif isinstance(error, SyntaxDeriverFatalError):
        return f'SyntaxDeriverFatalError'
    else:
        return None
