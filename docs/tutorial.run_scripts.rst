Run scripts
==================================

Within the `scripts` folder located inside the `dataherald` directory, you have the ability to upgrade your versions. For instance, if you are currently using version 0.0.3 and wish to switch to version 0.0.4, simply execute the following command:

.. code-block:: rst

    docker-compose exec app python3 -m dataherald.scripts.migrate_v003_to_v004

Script to populate golden records
------------------------------

Additionally, we provide a script for managing the Vector Store data. You can delete the existing data and upload all the Golden Records to the `golden_records` collection in MongoDB. If you are utilizing `Chroma` in-memory storage, it's important to note that data is lost upon container restart. To repopulate the data, execute the following command:

.. code-block:: rst

    docker-compose exec app python3 -m dataherald.scripts.delete_and_populate_golden_records
