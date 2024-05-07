if [ "$#" -le 1 ]; then
    echo "Usage: $0 <mongo_uri> (mongo_uri must include credentials) <database name> optional: <old database name> (default k2-serverless)"
    exit 1
fi

MONGO_URL=$1
DATABASE_NAME=$2
OLD_DATABASE_NAME=${3:-k2-serverless}

mongorestore ./org_dump --uri="$MONGO_URL" --nsFrom "$OLD_DATABASE_NAME.*" --nsTo "$DATABASE_NAME.*"