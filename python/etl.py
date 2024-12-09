"""
ETL with polars to create a data set in a landing zone on the datalake
In a fake finance catalog in bronze schema
And register it to unityCatalog
So the table path is fincance.bronze.score_table
It later would be accessible from a SQL Engine (DuckDB)
TODO ingest from postgres db to bronze
then ETL from bronze to silver to gold (SQL Engine ? DuckDB ?)
and have the train get data from gold
"""
import os

import polars as pl
import s3fs
from transform.transactions import clean_transactions
from transform.users import rfm_users
from unitycatalog_client import Configuration, TablesApi
from unitycatalog_client.api_client import ApiClient
from unitycatalog_client.rest import ApiException

os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
endpoint_url = "http://localhost:9000"

configuration = Configuration(
    host="http://localhost:8080/api/2.1/unity-catalog"
)

with ApiClient(configuration) as api_client:
    table_api = TablesApi(api_client)
    try:
        bronze_users = table_api.get_table("marketing.bronze.users")
        bronze_transactions = table_api.get_table("marketing.bronze.transactions")
        gold_users = table_api.get_table("marketing.gold.users")
        gold_transactions = table_api.get_table("marketing.gold.transactions")
    except ApiException as e:
        print(e)
fs = s3fs.S3FileSystem()

with fs.open(bronze_users.storage_location, mode='r') as f:
    users = pl.read_parquet(f)

with fs.open(bronze_transactions.storage_location, mode='r') as f:
    transactions = pl.read_parquet(f)

refined_transactions = clean_transactions(transactions)
with fs.open(gold_transactions.storage_location, mode="wb") as f:
    refined_transactions.write_parquet(f)


refined_users = rfm_users(users, refined_transactions)
with fs.open(gold_users.storage_location, mode="wb") as f:
    refined_users.write_parquet(f)
