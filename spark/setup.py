
import findspark
findspark.init('/opt/spark');

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as fn

import pandas as pd

spark = SparkSession.builder \
    .master(configuration['spark_uri']) \
    .appName(APP_NAME) \
    .config('spark.driver.host', configuration['spark_host']) \
    .config('spark.jars', 'postgresql-42.2.20.jar') \
    .getOrCreate()


options = {
    "url": configuration['pg_url'],
    "user": configuration['pg_user'],
    "password": configuration["pg_password"],
    "driver": "org.postgresql.Driver",
}

df_log = spark.read.format("jdbc").options(
    dbtable="log",
    **options,
).load()

df_dp = spark.read.format("jdbc").options(
    dbtable="dataplane",
    **options,
).load()

df_ip = spark.read.format("jdbc").options(
    dbtable="ip",
    **options,
).load()

