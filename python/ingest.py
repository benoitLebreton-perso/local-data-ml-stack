"""From web_app database (postgres)
we ingest to the analytics Lakehouse
on the landing zone (bronze)"""

import os

import polars as pl
import s3fs
from sqlalchemy import create_engine
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
        lake_users = table_api.get_table("marketing.bronze.users")
        lake_transactions = table_api.get_table("marketing.bronze.transactions")

    except ApiException as e:
        print(e)

fs = s3fs.S3FileSystem()

web_app_conn = create_engine("postgresql://postgres:postgres@localhost:5432/web_app")
users_query = "SELECT * FROM users"
users = pl.read_database(query=users_query, connection=web_app_conn.connect())

with fs.open(lake_users.storage_location, mode="wb") as f:
    users.write_parquet(f)

shop_conn = create_engine("postgresql://postgres:postgres@localhost:5432/shop")
transactions_query = "SELECT * FROM transactions"
transactions = pl.read_database(query=transactions_query, connection=shop_conn.connect())

with fs.open(lake_transactions.storage_location, mode="wb") as f:
    transactions.write_parquet(f)
