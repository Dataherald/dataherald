import os

from flask import Blueprint, jsonify
from flask import Flask


from dataherald.smart_cache.in_memory import InMemoryCache
from dataherald.eval.simple_evaluator import SimpleEvaluator
from dataherald.sql_database.base import SQLDatabase
from dataherald.executor import single_question

def create_app(test_config=None):
    swagger_destination_path = '/static/swagger.yaml'

    # Create the bluepints
    blueprint = Blueprint('objects', __name__)
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
        return single_question(user_question)

        

    return app