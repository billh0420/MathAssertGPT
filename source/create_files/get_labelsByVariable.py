# get_labelsByVariable.py
# from assert_gpt

from source.shared import Parser03 as Parser

def get_labelsByVariable(parser: Parser):
    labelsByVariable = dict()
    variables = set()
    for statement in parser.statements:
        if statement.startswith('$f'):
            split = statement.split(' ')
            label = split[1]
            variable = split[3]
            if variable in variables:
                labelsByVariable[variable] = label
        elif statement.startswith('$v'):
            split = statement.split(' ', 2)
            variables.add(split[1])
    return labelsByVariable
