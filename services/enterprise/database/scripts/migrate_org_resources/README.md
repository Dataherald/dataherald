### How to migrate an organization to a new database

## Prerequisite

Make sure to have [MongoDB Command Line Tools](https://www.mongodb.com/try/download/database-tools) installed before running the scripts

## Instructions
1. switch the organization to enterprise if not already.
2. run `dump_org_resources.sh <mongodb uri> <database name> <organization_id>`  get the dump file, be sure to include the credentials in the mongodb uri.
3. restore the dump file in the new database using `restore_org_resources.sh <mongodb uri> <database name> <old database name> (default value is k2-serverless, should match the folder name in org_dump)`
4. populate the vector db with enterprise's script `/enterprise/database/scripts/populate_pinecone_db/script.py` or in engine's script `/engine/dataherald/scripts/delete_and_populate_golden_records.py`
5. use the same encryption key in the environment variables from the old database