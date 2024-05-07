How to connect your DB to an NL interface: A Step by Step Guide
================================================================

Introduction
------------

Lots of business data is stored in relational databases. To query this data for insights, users need to know SQL. New LLMs such as GPT-4 can produce valid SQL but they are missing business and data context. As a result, they often produce SQL that is syntactically correct but does not accurately answer natural language questions from the relational data.

In this article, we will explore how we can set up a natural language interface to any SQL database. We will be using Streamlit for the front-end and Dataherald for the semantic layer on our database. We will be using a database of US real estate data (home sale prices, rents, number of active listings) as our sample database. However, the same approach can be applied to any database.

All the code in this article is open source and can be accessed here: `Dataherald GitHub <https://github.com/Dataherald/dataherald>`_. You can fork the repo and modify the database to connect the end-to-end solution to your own data.

Prerequisites
--------------

Before starting, you need to set up and run the Dataherald engine. You can use this guide for detailed instructions on deploying the Dataherald engine with Docker locally.

Dataherald is a natural language to SQL engine for question answering over relational databases. It allows users to add context about the data through a few mechanisms:

- **Database Scans**: Automatically detecting tables, columns, and identifying the categorical columns along with their categories.

- **Golden records**: Adding sample questions and the SQL that answers them from the database. They are automatically grabbed for few-shot prompting based on similarity.

- **Database-level instructions**: Adding explicit rules on SQL that are passed to the LLM.

- **Table and column-level descriptions**: Can be used to help the agent identify the appropriate columns and tables to answer a question. This can be especially useful if the column and table names are not descriptive.

Once you have set up the Dataherald engine, you can verify its status by making the following API call:

.. code-block:: bash

    curl -X 'GET' \
      'http://localhost/api/v1/heartbeat' \
      -H 'accept: application/json'

If everything is functioning correctly, you should receive a response like this:

.. code-block:: json

    {
      "nanosecond heartbeat": 1696274893083888600
    }

Setting up the Streamlit app
------------------------------

Once Dataherald is set up, we will deploy the Streamlit app and connect it to the Dataherald engine.

To get started, begin by cloning the repository that contains the Streamlit app files and navigate to the directory using the following commands:

.. code-block:: bash

    git clone https://github.com/Dataherald/streamlit-app.git
    cd streamlit-app

Next, create a virtual environment and install the necessary python packages:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt  # use pip3, if you have both python2 and python3

Now, let's set your Dataherald-AI engine URI to establish a connection between the Streamlit app and your deployed engine:

You'll need to update the default host value in 🏠_Home.py to point to your own deployed Dataherald engine URI, which is your localhost. Additionally, you also have to change the default database alias and choose one of your connected databases. Here's how to do it:

.. code-block:: python

    # changing the host
    HOST = st.sidebar.text_input("Engine URI", value="http://streamlit_engine.dataherald.ai")
    # change the above line to:
    HOST = st.sidebar.text_input("Engine URI", value="http://localhost")

    # changing the default database
    DEFAULT_DATABASE = "RealState"
    # change the above line to whatever db alias you have connected with your engine
    DEFAULT_DATABASE = "Your db alias"

Now we are ready to launch the app! Simply use the following command:

.. code-block:: bash

        streamlit run 🏠_Home.py

The application should now be running and accessible through your browser at http://localhost:8501.


