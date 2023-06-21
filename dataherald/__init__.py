import os

from flask import Flask
from dataherald.smart_cache.in_memory import InMemoryCache
from dataherald.eval.simple_evaluator import SimpleEvaluator
from dataherald.sql_database.base import SQLDatabase

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    @app.route('/question', methods = ['POST'])
    def question(user_question):
        cache = InMemoryCache()
        evaluator = SimpleEvaluator()
        database = SQLDatabaseBase().from_uri("sqlite://")
        if cache.lookup(user_question) != None:
            return cache(user_question)
        else:
            generated_sql = database.run_sql(user_question)
            if evaluator.evaluate(user_question, generated_sql) == True:
                cache.add(user_question, generated_sql)
                return generated_sql

        

    return app