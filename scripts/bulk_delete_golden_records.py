

import json
import os
import sys
import requests

# constants. TODO: move to a config file
DATAHERALD_REST_API_URL = "http://localhost"


def run(config_file) -> None:
  """parse the config file and delete the golden records in the list

  The format of the records is a list like this
  
  [
  {
    "_id": {"$oid": "650bd2b5ad23f9d1069a13a7"}
  },
  {
    "_id": {"$oid": "650bd394ad23f9d1069a13a8"}
  },
  ...
  ]
  
  the API endpoint: /api/v1/golden-records/{golden_record_id}


  Args:
      config_file (str): config file to use which is a json file.
  """
  
  # 1. read in the config file and parse as json
  with open(config_file, "r") as f:
    golden_records_to_delete = json.load(f)
    
    # 2. loop through the list and delete each record calling the REST API
    for record in golden_records_to_delete:
      # get the golden record id
      golden_record_id = record["_id"]["$oid"]
     
      delete_golden_record(golden_record_id)
     
      # print a blank line
      print()
    

def delete_golden_record(golden_record_id:str):
  """Deletes a golden record with the given ID."""
  print(f"Deleting golden record with id: {golden_record_id}")
  url = f"{DATAHERALD_REST_API_URL}/api/v1/golden-records/{golden_record_id}"
  response = requests.delete(url)
  print(f"    Response status code: {response.status_code}")
    

if __name__ == "__main__":
  print("################################################################################")
  print("                    Running bulk_delete_golden_records.py")
  print("################################################################################")
  # read in the database configuration file but use the default if not provided
  print(f"Current working directory: {os.getcwd()}")

  # default database configuration file
  default_config_file = str(os.path.join(os.path.dirname(
    __file__), "config_files", "golden_records_to_delete.json"))

  config_file_to_use = default_config_file
  if len(sys.argv) < 2:
    print("No database configuration file provided. Using default.")
  else:
    config_file_to_use = sys.argv[1]

  run(config_file_to_use)
