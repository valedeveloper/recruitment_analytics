DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "port": 5432,
    "password": "1234",
    "database": "candidates",
}

DB_SERVER_CONFIG = {
    key: value
    for key, value in DB_CONFIG.items()
    if key != "database"
}
