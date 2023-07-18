from overrides import overrides

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.types import NLQuery, NLQueryResponse


class TestEvaluator(Evaluator):
    def __init__(self, system: System):
        pass

    @overrides
    def is_acceptable_response(
        self, question: NLQuery, generated_answer: NLQueryResponse
    ) -> bool:
        return True

    @overrides
    def evaluate(
        self, question: NLQuery, generated_answer: NLQueryResponse
    ) -> Evaluation:
        return Evaluation(question_id="0", answer_id="0", score=0.8)
