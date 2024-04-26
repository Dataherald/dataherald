from sql_metadata import Parser


def extract_the_schemas_from_sql(sql):
    table_names = Parser(sql).tables
    schemas = []
    for table_name in table_names:
        if "." in table_name:
            schema = table_name.split(".")[0]
            schemas.append(schema.strip())
    return schemas
