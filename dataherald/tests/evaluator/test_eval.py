from typing import override

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.types import NLQuery, NLQueryResponse


class TestEvaluator(Evaluator):
    def __init__(self, system: System):
        pass

    def start(self):
        pass

    def is_acceptable_response(
        self, question: NLQuery, generated_answer: NLQueryResponse
    ) -> bool:
        pass

    @override
    def evaluate(self, question: NLQuery, generated_answer: NLQueryResponse) -> Evaluation:
        pass
