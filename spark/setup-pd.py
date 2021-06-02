import pandas as pd
import numpy as np
import psycopg2

dbc = psycopg2.connect(
    database=configuration['pg_database'],
    host=configuration['pg_host'],
    port=configuration['pg_port'],
    user=configuration['pg_user'], 
    password=configuration['pg_password'],
)

df_log = pd.read_sql_query(
    f"SELECT * FROM log where '{dates[0]}' <= timestamp AND timestamp < '{dates[-1]}'",
    con=dbc,
    index_col=['id'],
)

df.head()