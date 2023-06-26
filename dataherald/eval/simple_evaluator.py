from dataherald.eval.base import EvaluatorBase
from overrides import override


class SimpleEvaluator(EvaluatorBase):

    @override
    def evaluate(self, question: str, sql: str = None, tables_used = None) -> bool:
        print('Evaluating question: ', question)
        return True