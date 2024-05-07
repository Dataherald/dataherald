.. _modules:

Modules
====================================================

Dataherald is built on a modular architecture and provides standaridized, extensible interfaces for anyone to replace any of these modules with their own implementation. This section outlines these modules. 

.. toctree::
   :hidden:

   context_store
   text_to_sql_engine
   api_server
   evaluator
   vector_store
   db
   finetuning

Introduction
------------

The system is built on the following modules, and you can implement your own and replace the default implementation from the ``.env`` file. In many instances the codebase already has multiple implementations which can be selected. We encourage the community to build their own modules and submit them for inclusion in the codebase.  

System Modules
--------------

The following are the core modules which make up the Dataherald engine.

- :doc:`Context Store <context_store>`: Which stores the relevant business and data context used in few-shot prompting.

- :doc:`Text-to-SQL Engine <text_to_sql_engine>`: The module that translates the Natural Language question to SQL

- :doc:`API Server <api_server>`: The server that exposes the API

- :doc:`Evaluator <evaluator>`: The module that assigns a confidence score to the generated SQL

- :doc:`Vector Store <vector_store>`: The vector store which stores application embeddings.

- :doc:`Database Integration <db>`: Used to store and persist application data.

- :doc:`Finetuning <finetuning>`: The module that responsible for finetuning LLMs on ground truth Question/SQL pairs.

System architecture
--------------------

The following diagram illustrates the overall system architecture.

.. image:: architecture.png
   :align: center
   :alt: Dataherald Architecture



