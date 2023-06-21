from dataherald.eval.base import EvaluatorBase



class SimpleEvaluator(EvaluatorBase):
    def __init__(self):
        pass

    def evaluate(self, question, sql, tables_used = None):
        return True