from dataherald.eval import Evaluator
from overrides import override


class SimpleEvaluator(Evaluator):

    @override
    def evaluate(self, question: str, sql: str = None, tables_used = None) -> bool:
        print('Evaluating question: ', question)
        return True