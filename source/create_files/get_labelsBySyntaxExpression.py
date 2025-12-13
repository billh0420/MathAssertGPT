# get_labelsBySyntaxExpression.py
# from assert_gpt.create_files

from source.shared import Parser03 as Parser

def get_labelsBySyntaxExpression(parser: Parser):
    labelsBySyntaxExpression = {}
    for statement_label, value in parser.result.items():
        split_value = value[2].removesuffix(' $.').split(' ', 3)
        statementType = split_value[0]
        type_code = split_value[2]
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
        labelsBySyntaxExpression[item] = statement_label
    return labelsBySyntaxExpression
