from overrides import override

from dataherald.eval import Evaluation, Evaluator


class SimpleEvaluator(Evaluator):
    @override
    def get_golden_sql(self, question: str) -> str:  # noqa: ARG002
        """Obtains the golden SQL for the given question"""
        return "golden sql"

    @override
    def evaluate(self, question: str, golden_sql: str) -> Evaluation:  # noqa: ARG002
        """Evaluates a question with an SQL pair."""
        return Evaluation(question_id="", score=0.5)
