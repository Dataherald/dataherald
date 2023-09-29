"""
1. Delete recursively the dbdata folder in the current working directory.
2. Create the a new dbdata folder in the current working directory.
"""

import os
import shutil

from MongoDB import MongoDB

if __name__ == "__main__":
    print("################################################################################")
    print("                      Initialize Database Folder")
    print("################################################################################")
    # print the current working directory
    print(f"Current working directory: {os.getcwd()}")

    # delete the dbdata folder if it exists
    if os.path.isdir("dbdata"):
        print("Deleting existing dbdata folder")
        shutil.rmtree("dbdata")

    # create the dbdata folder
    os.mkdir("dbdata")
    print("Created new dbdata folder in current working directory")
    print()

    print("################################################################################")
    print("                      Initialize Database collections")
    print("################################################################################")
    # create a MongoDB object and drop the following collections
    # database_connections
    # golden_records
    # table_descriptions
    mongo = MongoDB()
    mongo.drop_collection("database_connections")
    mongo.drop_collection("golden_records")
    mongo.drop_collection("table_descriptions")
    mongo.drop_collection("instructions")
    mongo.close()

    print("################################################################################")
