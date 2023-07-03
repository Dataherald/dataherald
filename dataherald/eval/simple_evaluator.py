from overrides import override

from dataherald.eval.types import Evaluation, Evaluator


class SimpleEvaluator(Evaluator):
    def get_golden_sql(self, question: str) -> bool:
        """Obtains the golden SQL for the given question"""
        pass

    @override
    def evaluate(self, question: str, golden_sql: str) -> Evaluation:
        """Evaluates a question with an SQL pair."""
        pass
