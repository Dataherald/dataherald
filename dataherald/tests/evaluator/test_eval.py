from overrides import overrides

from dataherald.eval import Evaluation, Evaluator
from dataherald.types import NLQuery, NLQueryResponse


class TestEvaluator(Evaluator):
    @overrides
    def evaluate(self, question: NLQuery, generated_answer: NLQueryResponse) -> Evaluation:
        return super().evaluate(question, generated_answer)
