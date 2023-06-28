from overrides import override

from dataherald.eval import Evaluator


class SimpleEvaluator(Evaluator):
    @override
    def evaluate(self, question: str, sql: str = None, tables_used=None) -> bool:
        pass
