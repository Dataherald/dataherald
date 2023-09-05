# run all the setup python scripts in the current directory in the following order
# 0. remove all the existing tables in the database
# 1. setup_database.py
# 2. setup_scanner.py
# 3. setup_golden_records.py

# delete all the data under the dbdata folder
del /Q dbdata\*

# 1. setup_database.py
python setup_database.py

# 2. setup_scanner.py
python setup_scanner.py

# 3. setup_golden_records.py
python setup_golden_records.py
