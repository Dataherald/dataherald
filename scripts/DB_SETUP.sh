#!/bin/bash

# run all the setup python scripts in the current directory in the following order
# 1. setup_databases.py ./config/db_config.json
# 2. setup_table_descriptions.py ./config/table_descriptions.json
# 3. setup_golden_records.py

# add scripts directory to the python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/scripts

# 1. setup_database.py
python setup_database.py ./config/db_config.json

# 2. setup_scanner.py
python setup_scanner.py ./config/scanner_config.json

# 3. setup_golden_records.py
python setup_golden_records.py
