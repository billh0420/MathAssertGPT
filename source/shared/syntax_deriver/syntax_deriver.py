# from shared.syntax_deriver
# syntax_deriver.py

import itertools
import random

from source.shared.assert_db.AssertDB import AssertDB
from source.shared.syntax_deriver_db.SyntaxDeriverDB import SyntaxDeriverDB, MathStatement_Row, RuleError_Row

from source.shared.metamath.MathStatement import MathStatement, AssertionStatement
from source.shared.metamath.MathStatement import LabeledStatement, AxiomStatement, FloatingHypothesis
from source.shared.syntax_deriver.SyntaxDeriverErrorState import ErrorState, ErrorStateNotCompleted, ErrorStateRule
from source.shared.syntax_deriver.SyntaxDeriverExtraction import SyntaxDeriverExtraction

from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverMismatchTerminalError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverIncompleteError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverNoMarkLabelError, SyntaxDeriverNoVariableLabelError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverNoAssertionStatementError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverUnknownMarkTypeError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverWffRuleError, SyntaxDeriverNoResultError
from source.shared.syntax_deriver.SyntaxDeriverError import SyntaxDeriverNotCompletedError

class SyntaxDeriver:

    def __init__(self, assert_db: AssertDB):
        self.assert_db = assert_db
        self.syntax_deriver_db = SyntaxDeriverDB()
        cursor = self.assert_db.conn.cursor()

        cursor.execute('select * from labels_by_variable_table')
        labels_by_variable_rows = cursor.fetchall()
        cursor.execute('select * from typecodes_by_var_table')
        typecodes_by_var_rows = cursor.fetchall()
        cursor.execute('select * from math_statements_by_label_table')
        math_statements_rows = cursor.fetchall()
        cursor.execute('select * from labels_by_syntax_expression_table')
        labels_by_syntax_expression_rows = cursor.fetchall()

        mathVariables: set[str] = {x.var_name for x in labels_by_variable_rows}
        labelsByVariable = {x.var_name: x.label for x in labels_by_variable_rows}
        type_codes_by_var = {x.var_name: x.typecode for x in typecodes_by_var_rows}
        syntax_expressions_by_label = {x.label: x.syntax_expression for x in labels_by_syntax_expression_rows}  # (key: ruleName, value: productionRule)

        self.mathVariables: set[str] = mathVariables
        self.labelsByVariable = labelsByVariable
        self.type_codes_by_var = type_codes_by_var
        self.syntax_expressions_by_label = syntax_expressions_by_label

        math_statements_by_label = self._get_mathStatementsByLabel(labelsByVariable, type_codes_by_var, math_statements_rows)
        self.mathStatementsByLabel = math_statements_by_label

        # FIXME: 201010 added, testing
        self.all_wffRulesByName = dict()
        self.all_classRulesByName = dict()
        self._setupAllRules()
        self.all_wffRuleContentConstantsByName = {ruleName: set([x for x in rule if x not in self.mathVariables]) for ruleName, rule in self.all_wffRulesByName.items()}
        self.all_classRuleContentConstantsByName = {ruleName: set([x for x in rule if x not in self.mathVariables]) for ruleName, rule in self.all_classRulesByName.items()}

        # Need to be reset when derive_syntax called
        self.math_statement_id = None
        self.min_token_count = 0  # corresponging to min_current_token_count FIXME: 240920 does this do anything? Give an example where it matters.
        self.min_current_token_count = 0
        self.error_states: set[ErrorState] = set()
        self.statement: str | None = None
        self.syntaxDerivation: str | None = None
        self.derivation_correct_count = 0
        self.syntaxDeriverError: SyntaxDeriverError | None = None
        self.classRulesByName: dict[str, list[str]] = dict()
        # self.setRulesByName: dict[str, list[str]] = dict()
        # self.setvarRulesByName: dict[str, list[str]] = dict()
        self.wffRulesByName: dict[str, list[str]] = dict()

    def derive_syntax(self, statement: str, context: str | None):
        self.math_statement_id = None
        self.min_token_count = len(statement.split()) + 1
        self.min_current_token_count = len(statement.split()) + 1
        self.error_states = set()
        self.statement = statement
        self.syntaxDerivation = None
        self.derivation_correct_count = 0
        self.syntaxDeriverError = None
        self.classRulesByName: dict[str, list[str]] = dict()
        # self.setRulesByName: dict[str, list[str]] = dict()
        # self.setvarRulesByName: dict[str, list[str]] = dict()
        self.wffRulesByName: dict[str, list[str]] = dict()
        self._setupRulesFrom(statement)
        tokens = list(reversed(statement.split()))  # reversed because easier to pop from tail
        try:
            if self.syntax_deriver_db:
                math_statement_row = MathStatement_Row(statement=statement,
                                                       context=context,
                                                       derivation=None,
                                                       derivation_correct_count=0,
                                                       syntax_deriver_error=None)
                self.math_statement_id = self.syntax_deriver_db.add_math_statement(math_statement_row)
            (peekedTokens, accumulator) = self._extractWff(tokens=tokens)
            syntaxDerivation = ' '.join(accumulator)
            if len(peekedTokens) == len(tokens):
                assert self.syntaxDeriverError is None
                self.syntaxDerivation = syntaxDerivation
            else:
                e = SyntaxDeriverNotCompletedError()
                error_state = ErrorStateNotCompleted(error=e,
                                                     tokens=" ".join(reversed(tokens)),
                                                     token_count=len(tokens),
                                                     current_token_count=len(peekedTokens),
                                                     current_tokens=" ".join(reversed(peekedTokens)))
                self.error_states = {error_state}
                self.min_token_count = len(tokens)  # FIXME: does this make sense
                self.min_current_token_count = len(peekedTokens)  # FIXME: does this make sense
                if self.syntax_deriver_db:
                    self.syntax_deriver_db.delete_rule_errors(statement_id=self.math_statement_id)
                raise e
        except SyntaxDeriverError as e:
            self.syntaxDerivation = None
            self.syntaxDeriverError = e
        self.derivation_correct_count = _get_derivation_correct_count(statement=statement, derivation=self.syntaxDerivation, error_states=self.error_states)
        if self.syntax_deriver_db:
            if self.syntaxDeriverError is None:
                syntax_deriver_error = None
            else:
                syntax_deriver_error = self.syntaxDeriverError.short_name
                self.syntax_deriver_db.delete_duplicate_rule_error_rows()  # Note this
            self.syntax_deriver_db.conn.cursor().execute('UPDATE math_statements SET derivation = ? WHERE id = ?', [self.syntaxDerivation, self.math_statement_id])
            self.syntax_deriver_db.update_math_statement_derivation_correct_count(math_statement_id=self.math_statement_id, derivation_correct_count=self.derivation_correct_count)
            self.syntax_deriver_db.conn.cursor().execute('UPDATE math_statements SET syntax_deriver_error = ? WHERE id = ?', [syntax_deriver_error, self.math_statement_id])

    def _applyRule(self, rule: list[str], ruleName: str, tokens: list[str]) -> SyntaxDeriverExtraction:
        currentTokens = tokens.copy()
        collectedAccumulators: list[list[str]] = []
        mark_index = None
        max_peeked_tokens_size = 0
        try:
            for mark_index, mark in enumerate(rule):
                mark_type = self._mark_type_of(mark)
                if mark_type == "terminal":
                    peekedTokens = self._extractTerminal(tokens=currentTokens, terminal=mark)
                    if peekedTokens is not None:
                        max_peeked_tokens_size = max(max_peeked_tokens_size, len(peekedTokens))
                    del currentTokens[len(currentTokens) - len(peekedTokens):]
                elif mark_type == "wff":
                    (peekedTokens, accumulator) = self._extractWff(tokens=currentTokens)
                    markLabel = self.labelsByVariable.get(mark, None)
                    if markLabel is None:
                        SyntaxDeriverNoMarkLabelError(where='wff')
                    collectedAccumulators.append(accumulator)
                    if peekedTokens is not None:
                        max_peeked_tokens_size = max(max_peeked_tokens_size, len(peekedTokens))
                    del currentTokens[len(currentTokens) - len(peekedTokens):]
                elif mark_type == "class":
                    (peekedTokens, accumulator) = self._extractClass(tokens=currentTokens)
                    markLabel = self.labelsByVariable.get(mark, None)
                    if markLabel is None:
                        SyntaxDeriverNoMarkLabelError(where='class')
                    collectedAccumulators.append(accumulator)
                    if peekedTokens is not None:
                        max_peeked_tokens_size = max(max_peeked_tokens_size, len(peekedTokens))
                    del currentTokens[len(currentTokens) - len(peekedTokens):]
                elif mark_type == "setvar":
                    (peekedTokens, accumulator) = self._extractSetVar(tokens=currentTokens)
                    markLabel = self.labelsByVariable.get(mark, None)
                    if markLabel is None:
                        SyntaxDeriverNoMarkLabelError(where='setvar')
                    collectedAccumulators.append(accumulator)
                    if peekedTokens is not None:
                        max_peeked_tokens_size = max(max_peeked_tokens_size, len(peekedTokens))
                    del currentTokens[len(currentTokens) - len(peekedTokens):]
                # elif mark_type == "set":
                #     (peekedTokens, accumulator) = self._extractSet(tokens=currentTokens)
                #     markLabel = self.labelsByVariable.get(mark, None)
                #     if markLabel is None:
                #         SyntaxDeriverNoMarkLabelError(where='set')
                #     collectedAccumulators.append(accumulator)
                #     if peekedTokens is not None:
                #         max_peeked_tokens_size = max(max_peeked_tokens_size, len(peekedTokens))
                #     del currentTokens[len(currentTokens) - len(peekedTokens):]
                else:
                    raise SyntaxDeriverUnknownMarkTypeError(mark=mark, mark_type=mark_type)
            assertionStatement = self.mathStatementsByLabel.get(ruleName, None)
            if assertionStatement is None:
                raise SyntaxDeriverNoAssertionStatementError(ruleName=ruleName)
            # Note: sometimes need to reorder
            # Example: the rule "wex: E. x ph" has its hypotheses in the order ph follwed by x
            assert isinstance(assertionStatement, AssertionStatement)
            fHypLabels = assertionStatement.fHypLabels
            peekedTokens = [] if len(currentTokens) == len(tokens) else tokens[len(currentTokens):]
            reorderedAccumulators: list[list[str]] = []
            ruleOrdering = [x for x in rule if x in self.mathVariables]
            for fHypLabel in fHypLabels:
                fStatement = self.mathStatementsByLabel.get(fHypLabel, None)
                if fStatement is not None:
                    assert isinstance(fStatement, FloatingHypothesis)
                    fVariable = fStatement.variable
                    index = ruleOrdering.index(fVariable)
                    if index is not None:
                        collectedAccumulator = collectedAccumulators[index]
                        reorderedAccumulators.append(collectedAccumulator)
            currentAccumulator = list(itertools.chain.from_iterable(reorderedAccumulators))
            return SyntaxDeriverExtraction(peekedTokens=peekedTokens, accumulator=currentAccumulator)
        except SyntaxDeriverError as e:
            rule_text = " ".join(rule)
            error_state = ErrorStateRule(ruleName=ruleName,
                                     rule=rule_text,
                                     mark_index=mark_index,
                                     token_count=len(tokens),
                                     current_token_count=len(currentTokens),
                                     error=e,
                                     tokens=" ".join(reversed(tokens)),
                                     current_tokens=" ".join(reversed(currentTokens)))
            if len(currentTokens) < self.min_current_token_count: # reset error_states
                self.error_states = {error_state}
                self.min_token_count = len(tokens)
                self.min_current_token_count = len(currentTokens)
                if self.syntax_deriver_db:
                    self.syntax_deriver_db.delete_rule_errors(statement_id=self.math_statement_id)
                    self._add_rule_error(ruleName=ruleName, rule=rule, mark_index=mark_index, tokens=tokens, currentTokens=currentTokens)
            elif len(currentTokens) == self.min_current_token_count:
                if len(tokens) == self.min_token_count: # expand error_states
                    self.error_states.add(error_state)
                    self._add_rule_error(ruleName=ruleName, rule=rule, mark_index=mark_index, tokens=tokens, currentTokens=currentTokens)
                elif len(tokens) < self.min_token_count: # reset error_states
                    self.error_states = {error_state}
                    self.min_token_count = len(tokens)
                    if self.syntax_deriver_db:
                        self.syntax_deriver_db.delete_rule_errors(statement_id=self.math_statement_id)
                        self._add_rule_error(ruleName=ruleName, rule=rule, mark_index=mark_index, tokens=tokens, currentTokens=currentTokens)
            raise e

    def _extractWff(self, tokens: list[str]) -> SyntaxDeriverExtraction:
        try:
            if len(tokens) == 0:
                raise SyntaxDeriverIncompleteError(where='extractWff')
            else:
                currentToken = tokens[-1]
                result_type = self._mark_type_of(currentToken)
                if result_type == "wff":
                    variableLabel = self.labelsByVariable.get(currentToken, None)
                    if isinstance(variableLabel, str):
                        return SyntaxDeriverExtraction(peekedTokens=[currentToken], accumulator=[variableLabel])
                    else:
                        raise SyntaxDeriverNoVariableLabelError(where='extractWff')
                for ruleName, rule in self.wffRulesByName.items():
                    try:
                        (peekedTokens, accumulator) = self._applyRule(rule=rule, ruleName=ruleName, tokens=tokens)
                        return SyntaxDeriverExtraction(peekedTokens=peekedTokens, accumulator=accumulator + [ruleName])
                    except SyntaxDeriverError as e:
                        continue
                rulesByName = self._generalize(self.wffRulesByName)
                wffRuleError = SyntaxDeriverWffRuleError(rulesByName=rulesByName)
                raise wffRuleError
        except SyntaxDeriverError as e:
            raise e

    def _extractClass(self, tokens: list[str]) -> SyntaxDeriverExtraction:
        try:
            if len(tokens) == 0:
                raise SyntaxDeriverIncompleteError(where='extractClass')
            currentToken = tokens[-1]
            result_type = self._mark_type_of(currentToken)
            if result_type == "class" or result_type == "setvar":
                variableLabel = self.labelsByVariable.get(currentToken, None)
                if isinstance(variableLabel, str):
                    return SyntaxDeriverExtraction(peekedTokens=[currentToken], accumulator=[variableLabel])
                else:
                    raise SyntaxDeriverNoVariableLabelError(where='extractClass')
            else:
                for (ruleName, rule) in self.classRulesByName.items():
                    try:
                        (peekedTokens, accumulator) = self._applyRule(rule=rule, ruleName=ruleName, tokens=tokens)
                        return SyntaxDeriverExtraction(peekedTokens=peekedTokens, accumulator=accumulator + [ruleName])
                    except SyntaxDeriverError as e:
                        continue
                raise SyntaxDeriverNoResultError(expected_type='class', result_type=result_type)
        except SyntaxDeriverError as e:
            raise e

    def _extractSetVar(self, tokens: list[str]) -> SyntaxDeriverExtraction:
        try:
            if len(tokens) == 0:
                raise SyntaxDeriverIncompleteError(where='extractSetVar')
            currentToken = tokens[-1]
            result_type = self._mark_type_of(currentToken)
            if result_type == "setvar":
                variableLabel = self.labelsByVariable.get(currentToken, None)
                if isinstance(variableLabel, str):
                    return SyntaxDeriverExtraction(peekedTokens=[currentToken], accumulator=[variableLabel])
                else:
                    raise SyntaxDeriverNoVariableLabelError(where='extractSetVar')
            else:
                # for (ruleName, rule) in self.setRulesByName.items():
                #     try:
                #         (peekedTokens, accumulator) = self._applyRule(rule, ruleName, tokens=tokens)
                #         return SyntaxDeriverExtraction(peekedTokens=peekedTokens, accumulator=accumulator + [ruleName])
                #     except SyntaxDeriverError as e:
                #         continue
                raise SyntaxDeriverNoResultError(expected_type='setvar', result_type=result_type)
        except SyntaxDeriverError as e:
            raise e

    @staticmethod
    def _extractTerminal(tokens: list[str], terminal: str) -> list[str]:
        try:
            # currentToken must match expected terminal token
            if len(tokens) == 0:
                raise SyntaxDeriverIncompleteError(where='extractTerminal')
            currentToken = tokens[-1]
            if currentToken != terminal:
                raise SyntaxDeriverMismatchTerminalError(terminal=terminal)
            return [terminal]
        except SyntaxDeriverError as e:
            raise e

    def _mark_type_of(self, mark: str) -> str:
        markType = self.type_codes_by_var.get(mark, "terminal")
        return markType

    def _generalize(self, wffRulesByName) -> dict[str, list[str]]:
        return {ruleName: [self._generalize_mark(mark) for mark in wffRule] for ruleName, wffRule in wffRulesByName.items()}

    def _generalize_mark(self, mark) -> str:
        mark_type = self._mark_type_of(mark)
        return mark if mark_type == 'terminal' else mark_type

    def _add_rule_error(self, ruleName, rule, mark_index, tokens, currentTokens):
        if self.syntax_deriver_db:
            str_rule = ' '.join(rule)
            str_rule_tokens = ' '.join(reversed(tokens))
            str_current_rule_tokens = ' '.join(reversed(currentTokens))
            rule_error_row = RuleError_Row(statement_id=self.math_statement_id,
                                           rule_name=ruleName,
                                           rule=str_rule,
                                           mark_index=mark_index,
                                           rule_tokens=str_rule_tokens,
                                           current_rule_tokens=str_current_rule_tokens)
            self.syntax_deriver_db.add_rule_error(rule_error_row)

    def _setupRulesFrom(self, statement: str):  # FIXME: 241005 remove redundant code; check new code is ok
        assertionStatementConstants = set([x for x in statement.split() if x not in self.mathVariables])
        # for ruleName in self.syntax_expressions_by_label.keys():
        #     mathStatement = self.mathStatementsByLabel.get(ruleName, None)
        #     if mathStatement is None:
        #         raise SyntaxDeriverNoMathStatementError(ruleName=ruleName)
        #     # FIXME: need to insure that mathStatement is an AssertionStatement
        #     content = self._contentFor(statement=mathStatement.statement)
        #     rule = content.split(' ')
        #     statement_type = mathStatement.constant
        #     if statement_type == "wff":
        #         contentConstants = set([x for x in content.split() if x not in self.mathVariables])
        #         if contentConstants.issubset(assertionStatementConstants):
        #             self.wffRulesByName[ruleName] = rule
        #     elif statement_type == "class":
        #         contentConstants = set([x for x in content.split() if x not in self.mathVariables])
        #         if contentConstants.issubset(assertionStatementConstants):
        #             self.classRulesByName[ruleName] = rule
        #     # elif statement_type == "set":
        #     #     self.setRulesByName[ruleName] = rule
        #     else:
        #         raise SyntaxDeriverFatalError(message=f'Unknown statement_type={statement_type} for mathStatement={mathStatement}')
        wffRulesByName = dict()
        classRulesByName = dict()
        # setRulesByName = dict()
        for label, mathStatement in self.mathStatementsByLabel.items():
            if isinstance(mathStatement, AxiomStatement):
                constant = mathStatement.constant
                if constant == 'wff':
                    content = self._contentFor(statement=mathStatement.statement)
                    contentConstants = set([x for x in content.split() if x not in self.mathVariables])
                    if contentConstants.issubset(assertionStatementConstants):
                        rule = content.split(' ')
                        ruleName = mathStatement.statementLabel
                        wffRulesByName[ruleName] = rule
                elif constant == "class":
                    content = self._contentFor(statement=mathStatement.statement)
                    contentConstants = set([x for x in content.split() if x not in self.mathVariables])
                    if contentConstants.issubset(assertionStatementConstants):
                        rule = content.split(' ')
                        ruleName = mathStatement.statementLabel
                        classRulesByName[ruleName] = rule
                # elif constant == "set":
                #     content = self._contentFor(statement=mathStatement.statement)
                #     rule = content.split(' ')
                #     ruleName = mathStatement.statementLabel
                #     setRulesByName[ruleName] = rule
            # elif isinstance(mathStatement, FloatingHypothesis):
            #     constant = mathStatement.constant
            #     if constant == 'setvar':
            #         content = self._contentFor(statement=mathStatement.statement)
            #         rule = [content.split(' ')[2]]
            #         ruleName = mathStatement.statementLabel
            #         self.setvarRulesByName[ruleName] = rule  # FIXME: added 240912
        self.wffRulesByName = wffRulesByName
        self.classRulesByName = classRulesByName

    @staticmethod
    def _contentFor(statement: str) -> str:
        statementParts = statement.split(' ', maxsplit=1)
        content = '' if len(statementParts) < 2 else statementParts[1]
        return content

    @staticmethod
    def _get_mathStatementsByLabel(labelsByVariable, type_codes_by_var, math_statements_rows):
        mathStatementsByLabel: dict[str, MathStatement] = dict()
        for item in type_codes_by_var.items():
            # FIXME: 240908 the following does not seem to handle shadowing
            variable = item[0]
            type_code = item[1]
            statementType = '$f'
            statement_label = labelsByVariable[variable]
            statement = f'{statement_label} $f {type_code} {variable} $.'
            statementID = 0
            fHypStatement = FloatingHypothesis(statementType, statement, statementID, statement_label, type_code, variable)
            mathStatementsByLabel[statement_label] = fHypStatement
        for row in math_statements_rows:
            hyps = [x for x in row.hyps.split('\n') if x != '']
            statement = row.statement
            statementID = row.statement_ID
            statementType = row.statement_type
            statement_label = row.statement_label
            type_code = row.type_code
            if statementType == '$f':
                labeledStatement = LabeledStatement(statementType, statement, statementID, statement_label, type_code)
                mathStatementsByLabel[statement_label] = labeledStatement
            elif statementType == '$a' and (type_code == 'wff' or type_code == 'class'):
                statementID = 0
                fHypLabels = [labelsByVariable[x.split()[1]] for x in hyps]
                labeledStatement = AxiomStatement(statementType, statement, statementID, statement_label, type_code, fHypLabels)
                mathStatementsByLabel[statement_label] = labeledStatement
        return mathStatementsByLabel

    def _setupAllRules(self):  # FIXME: 241010 testing: is this useful
        wffRulesByName = dict()
        classRulesByName = dict()
        for label, mathStatement in self.mathStatementsByLabel.items():
            if isinstance(mathStatement, AxiomStatement):
                constant = mathStatement.constant
                if constant == 'wff':
                    content = self._contentFor(statement=mathStatement.statement)
                    rule = content.split(' ')
                    ruleName = mathStatement.statementLabel
                    wffRulesByName[ruleName] = rule
                elif constant == "class":
                    content = self._contentFor(statement=mathStatement.statement)
                    rule = content.split(' ')
                    ruleName = mathStatement.statementLabel
                    classRulesByName[ruleName] = rule
        self.all_wffRulesByName = wffRulesByName
        self.all_classRulesByName = classRulesByName

def _get_derivation_correct_count(statement, derivation, error_states) -> int:  # FIXME: where to place and drop duplicate methods
    derivation_correct_count = 0
    if derivation is not None:
        derivation_correct_count = len(statement.split())
    elif len(error_states) > 0:
        some_error = random.sample(list(error_states), 1)[0]  # FIXME: 240922 do this better ?
        if isinstance(some_error.error, SyntaxDeriverNotCompletedError):
            derivation_correct_count = some_error.current_token_count
        else:
            derivation_correct_count = len(statement.split()) - some_error.current_token_count  # FIXME: is this correct ?
            # derivation_correct_count = some_error.token_count + some_error.current_token_count # FIXME: is this correct ?
    return derivation_correct_count
