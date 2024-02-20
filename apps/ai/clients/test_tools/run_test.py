from langsmith import Client
from langsmith.evaluation import EvaluationResult, run_evaluator
from langsmith.schemas import Example, Run
from langchain.smith import RunEvalConfig, run_on_dataset
import pandas as pd
from apps.ai.clients.test_tools.dh_evaluator import DHEvaluator
from dataherald import Dataherald
from dataherald.types.sql_generation_create_params import Prompt
import sys
from langsmith.utils import LangSmithNotFoundError
from requests.exceptions import HTTPError

LANGSMITH_API_KEY = 'ls__13bbda71b62e46469dde2ef0646b647a'
dh_client = None
db_connection_id = None
dh_eval = None
validation_file_name = None
question_col = None
sql_col = None
testing_data = None

@run_evaluator
def dh_evaluator_score(run: Run, example: Example | None = None):
    sql_query = run.outputs['output']
    golden_queries = run.inputs['golden_sqls']
    score = dh_eval.get_confidence_score(run.inputs['question'], sql_query, golden_queries)
    return EvaluationResult(key="evaluator_score", score=score)

# @run_evaluator
# def num_tokens_score(run: Run, example: Example | None = None):
#     return EvaluationResult(key="num_tokens", score=run.total_tokens)

# @run_evaluator
# def runtime_score(run: Run, example: Example | None = None):
#     return EvaluationResult(key="runtime_in_seconds", score=(run.end_time - run.start_time).total_seconds())

evaluation_config = RunEvalConfig(
    custom_evaluators = [dh_evaluator_score]
)

def dhai_model(inputs):
    prompt = Prompt(text=inputs["question"], db_connection_id=db_connection_id)
    result = dh_client.sql_generations.create(prompt=prompt, finetuning_id='65b42fd11e6ef38522f4e6eb')
    return result.sql

def dhai_model_sheet(inputs):
    current_sql = testing_data[testing_data[question_col] == inputs["question"]].reset_index()[sql_col][0]
    current_sql = current_sql.replace('\\n', ' ')\
                             .replace('\n', ' ')
    return current_sql

if __name__ == "__main__":
    api_key = sys.argv[1]
    dataset_name = sys.argv[2]
    run_name = sys.argv[3]

    testing_data = None
    try:
        validation_file_name = sys.argv[4]
        try:
            question_col = sys.argv[5]
            sql_col = sys.argv[6]
            testing_data = pd.read_csv(validation_file_name)[[question_col, sql_col]]
        except:
            raise RuntimeError(f"Failed to read testing data from {validation_file_name}")
    except:
        pass

    if not api_key.startswith('dh'):
        raise ValueError('Invalid API key provided.')

    dh_client = Dataherald(api_key=api_key, timeout=360)
    db_connection_id = dh_client.database_connections.list()[-1].id
    dh_eval = DHEvaluator(dh_client)

    try:
        if testing_data == None:
            run_on_dataset(
                dataset_name=dataset_name,
                llm_or_chain_factory=dhai_model,
                client=Client(api_key=LANGSMITH_API_KEY),
                evaluation=evaluation_config,
                project_name=run_name
            )
        else:
            run_on_dataset(
                dataset_name=dataset_name,
                llm_or_chain_factory=dhai_model_sheet,
                client=Client(api_key=LANGSMITH_API_KEY),
                evaluation=evaluation_config,
                project_name=run_name
            )
    except LangSmithNotFoundError:
        raise ValueError('No such dataset exists in LangSmith.')
    except HTTPError: 
        raise ValueError('This run name already exists. Please try another one or delete the run in LangSmith.')