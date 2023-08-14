API
=======================

.. _api:

Create a db connection
-----------------------

To use Lumache, first install it using pip:

.. code-block:: console

   (.venv) $ pip install lumache

Scan a db
----------------

To retrieve a list of random ingredients,
you can use the ``lumache.get_random_ingredients()`` function:

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

For example:

>>> import lumache
>>> lumache.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']

Ask a question
----------------
foo
