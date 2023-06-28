db.createUser(
    {
        user: '$MONGO_INITDB_ROOT_USERNAME',
        pwd: '$MONGO_INITDB_ROOT_PASSWORD',
        roles: [
            {
                role: "readWrite",
                db: '$MONGO_INITDB_DATABASE'
            }
        ]
    }
);
