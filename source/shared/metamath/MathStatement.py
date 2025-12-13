# MathStatement.py

class MathStatement:

    def __init__(self, statementType: str, statement: str, statementID: int):
        self.statementType = statementType
        self.statement = statement
        self.statementID = statementID


class CommentStatement(MathStatement):

    def __init__(self, statementType: str, statement: str, statementID: int, label: str | None):
        super().__init__(statementType, statement, statementID)
        self.label = label


class LabeledStatement(MathStatement):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str):
        super().__init__(statementType, statement, statementID)
        self.statementLabel = statementLabel
        self.constant = constant


class Hypothesis(LabeledStatement):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str):
        super().__init__(statementType, statement, statementID, statementLabel, constant)


class EssentialHypothesis(Hypothesis):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str):
        super().__init__(statementType, statement, statementID, statementLabel, constant)


class FloatingHypothesis(Hypothesis):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str, variable: str):
        super().__init__(statementType, statement, statementID, statementLabel, constant)
        self.variable = variable


class AssertionStatement(LabeledStatement):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str, fHypLabels: list[str]):
        super().__init__(statementType, statement, statementID, statementLabel, constant)
        self.fHypLabels = fHypLabels
        self.eHypLabels: list[str] = []
        self.assertionID: int = 0
        self.compressedProof: str | None = None
        self.normalProof: str | None = None


class AxiomStatement(AssertionStatement):
    pass


class ProvedStatement(AssertionStatement):

    def __init__(self, statementType: str, statement: str, statementID: int, statementLabel: str, constant: str, fHypLabels: list[str]):
        super().__init__(statementType, statement, statementID, statementLabel, constant, fHypLabels)
        self.oHypLabels: list[str] | None = None
