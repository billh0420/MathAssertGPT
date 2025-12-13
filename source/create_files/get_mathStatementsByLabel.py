# get_mathStatementsByLabel.py
# from assert_gpt

from source.shared import Parser03 as Parser

def get_mathStatementsByLabel(parser: Parser, labelsBySyntaxExpression):
    mathStatementsByLabel = dict()
    for statement_label, value in parser.result.items():
        split_value = value[2].removesuffix(' $.').split(' ', 3)
        statementType = split_value[0]
        statement = value[2].removesuffix(' $.').split(' ', 2)[2]
        type_code = split_value[2]
        if statementType == '$f':
            statementID = 0
            mathStatement = {'statementType': statementType,
                             'statement': statement,
                             'statementID': statementID,
                             'statement_label': statement_label,
                             'type_code': type_code,
                             'hyps': []}
            mathStatementsByLabel[statement_label] = mathStatement
        if statementType != '$a':
            continue
        if type_code == '|-':
            continue
        hyps = value[0]
        subst = dict()
        for hyp in hyps:
            tokens = hyp.split()
            assert len(tokens) == 2
            subst[tokens[1]] = tokens[0]
        item = " ".join([subst.get(x, x) for x in split_value[3].split()])
        if item not in labelsBySyntaxExpression:
            raise Exception('should not happen')
        if type_code == 'wff' or type_code == 'class':
            statementID = 0
            mathStatement = {'statementType': statementType,
                             'statement': statement,
                             'statementID': statementID,
                             'statement_label': statement_label,
                             'type_code': type_code,
                             'hyps': hyps}
            mathStatementsByLabel[statement_label] = mathStatement
    return mathStatementsByLabel
