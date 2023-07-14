set -e

mongosh <<EOF
use $MONGO_INITDB_DATABASE

db.createUser({
  user: '$MONGO_INITDB_ROOT_USERNAME',
  pwd: '$MONGO_INITDB_ROOT_PASSWORD',
  roles: [{
    role: 'readWrite',
    db: '$MONGO_INITDB_DATABASE'
  }]
})

db.database_connection.insert({
    "alias": "postgres_ssh",
    "ssh_settings": {
      "host": '$SSH_HOST',
      "username": '$SSH_USERNAME',
      "password": '$SSH_PASSWORD',
      "remote_host": '$SSH_REMOTE_HOST',
      "remote_db_name": '$SSH_REMOTE_DB_NAME',
      "remote_db_password": '$SSH_REMOTE_DB_PASSWORD',
      "private_key_path": '$SSH_PRIVATE_KEY_PATH',
      "private_key_password": '$SSH_PRIVATE_KEY_PASSWORD',
      "db_driver": '$SSH_DB_DRIVER',
    },
    "uri": '$DATABASE_URI',
    "use_ssh": '$SSH_ENABLED'
  })

EOF
