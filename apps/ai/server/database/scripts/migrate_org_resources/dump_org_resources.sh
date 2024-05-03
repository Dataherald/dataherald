#!/bin/bash

# Set database name
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <mongo_uri> (mongo_uri must include the database credentials) <database name> <organization_id> "
    exit 1
fi

MONGO_URL=$1
DATABASE_NAME=$2
ORG_ID=$3

engine_query='{"metadata.dh_internal.organization_id": "'$ORG_ID'"}'

enterprise_query='{"organization_id":"'$ORG_ID'"}'

organization_query='{"_id":{"$oid":"'$ORG_ID'"}}'

mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="database_connections" --query="$engine_query" --out="org_dump"
mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="golden_sqls" --query="$engine_query" --out="org_dump"
mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="instructions" --query="$engine_query" --out="org_dump"
mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="table_descriptions" --query="$engine_query" --out="org_dump"
mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="users" --query="$enterprise_query" --out="org_dump"
mongodump --uri="$MONGO_URL" --db="$DATABASE_NAME" --collection="organizations" --query="$organization_query" --out="org_dump"
