# get_assert_corpus.py
# from assert_gpt

import re
from pathlib import Path

from source.shared import Parser03 as Parser

def get_assert_corpus(parser: Parser, corpus01_file_path: Path) -> list[list[str]]:
    all_utterances: set[str] = _generate_all_asserts(parser=parser, corpus01_file_path=corpus01_file_path)
    assert_corpus: list[list[str]] = []
    for i, utterance in enumerate(all_utterances):
        assert_utterance = []
        assert_utterance += utterance.split()
        assert_utterance.append('<|over|>')
        assert_corpus.append(assert_utterance)
    return assert_corpus

def _generate_all_asserts(parser: Parser, corpus01_file_path: Path) -> set[str]:
    all_utterances: set[str] = set()
    wffs = _get_wffs(corpus01_file_path)
    count = 0
    max_count = len(parser.result.items())
    proof_count = 0
    for statement_label, value in parser.result.items():
        if value[2].startswith('$a'):
            continue
        givens = value[1]
        if value[2].startswith('$p'):
            parts = re.split(r" \$= ", value[2].removesuffix(' $.'))
            proof = parts[1].split()
        else:
            proof = None
        if proof:
            proof_count += 1
            utterances = _get_assert_utterances(proof, givens, wffs, parser)
            all_utterances.update(utterances)
        count += 1
        if count % 10000 == 0:
            print(f'generate_all_asserts: count={count} of {max_count}; proof_count={proof_count}; #all_utterances={len(all_utterances)}')
    return all_utterances

def _get_wffs(corpus01_file_path: Path):
    wffs = dict()
    file = open(corpus01_file_path, 'r')
    while True:
        statement = file.readline().rstrip()
        if not statement:
            break
        tokens = list(statement.split(" "))
        if len(tokens) > 4 and tokens[0] == '$f' and tokens[2] == 'wff':
            label = tokens[1]
            expression = ' '.join(tokens[3:-1])
            wffs[label] = str(expression)
    file.close()
    return wffs

def _get_assert_utterances(proof, hypotheses, wffs, parser) -> set[str]:
    utterances: set[str] = set()
    givens = dict()
    stack = []
    for hyp in hypotheses:
        tau = hyp.split(' ', 1)
        givens[tau[0]] = tau[1]
    for item in proof:
        if item in givens:
            stack.append(givens[item])
            utterances.add(givens[item])
        elif item in wffs:
            stack.append(f'wff {wffs[item]}')
        elif item in parser.labels and parser.labels[item][0] == '$f':
            stack.append(' '.join(parser.labels[item][1]))
        else:
            alpha = parser.result[item]
            if alpha[2].startswith('$a') or alpha[2].startswith('$p'):
                f_hyps = alpha[0]
                e_hyps = alpha[1]
                hyps = f_hyps + e_hyps
                prop = alpha[2].removesuffix(' $.').split(' ', 2)[-1]
                if alpha[2].startswith('$p'):
                    prop = prop.split(' $= ', 1)[0]
                target_f_hyps = stack[-len(hyps): len(stack) - len(e_hyps)]
                subst = dict()
                for f_hyp, target_f_hyp in zip(f_hyps, target_f_hyps):
                    subst[f_hyp.split(' ', 1)[1]] = target_f_hyp.split(' ', 1)[1]
                conclusion = " ".join([subst.get(x, x) for x in prop.split()])
                stack = stack[:len(stack)-len(hyps)] + [conclusion]
                if prop.startswith('|-'):
                    utterances.add(conclusion)
    return utterances
