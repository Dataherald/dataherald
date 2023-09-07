<<<<<<< HEAD
@REM # run all the setup python scripts in the current directory in the following order
@REM # 0. remove all the existing tables in the database
@REM # 1. setup_database.py
@REM # 2. setup_scanner.py
@REM # 3. setup_golden_records.py

@REM # delete all the data under the dbdata folder
python inialize_db_folder.py

@REM # 0. remove all the existing tables in the database
echo "Removing all the existing tables in the database"
python remove_tables.py

@REM # 1. setup_database.py
echo "Setting up the database"
python setup_database.py

@REM # 2. setup_scanner.py
echo "Setting up the scanner. Tables and meta data"
python setup_scanner.py

@REM # 3. setup_golden_records.py
echo "Setting up the golden records"
=======
# run all the setup python scripts in the current directory in the following order
# 1. setup_database.py
# 2. setup_scanner.py
# 3. setup_golden_records.py

# 1. setup_database.py
python setup_database.py

# 2. setup_scanner.py
python setup_scanner.py

# 3. setup_golden_records.py
>>>>>>> 5937308 (added set up scripts)
python setup_golden_records.py
