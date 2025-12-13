# get_typecodesByVar.py
# from assert_gpt

from source.shared import Parser03 as Parser

def get_typecodesByVar(parser: Parser):
    typecodesByVar = dict()
    for x in parser.statements:
        if not x.startswith('$f'):
            continue
        split_x = x.split()
        var = split_x[3]
        typecode = split_x[2]
        old_typecode = typecodesByVar.get(var, None)
        if old_typecode is None:
            typecodesByVar[var] = typecode
        else:
            assert typecode == old_typecode
    return typecodesByVar
