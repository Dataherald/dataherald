#!/bin/bash

# run all the setup python scripts in the current directory in the following order
# 1. setup_databases.py ./config/db_config.json
# 2. setup_table_descriptions.py ./config/table_descriptions.json
# 3. setup_golden_records.py

# add scripts directory to the python path
# print the pwd and add it to the python path
echo $(pwd)
export PYTHONPATH=$PYTHONPATH:$(pwd)/scripts
# print the python path
echo $PYTHONPATH

# 1. setup_database.py
python setup_databases.py ./config_files/db_config.json

# 2. setup_scanner.py
python setup_scanner.py ./config_files/table_descriptions.json

# 3. setup_golden_records.py
python setup_golden_records.py
