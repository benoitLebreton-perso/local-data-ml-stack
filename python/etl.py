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
import unitycatalog_client
import unitycatalog_client.api_client
import unitycatalog_client.api_response
from unitycatalog_client.models.column_info import ColumnInfo
from unitycatalog_client.rest import ApiException

df = pl.from_records(
    [
        {"x1": 1, "x2": 2, "y": 0},
        {"x1": 1, "x2": 2, "y": 0},
        {"x1": 1, "x2": 2, "y": 0},
        {"x1": 1, "x2": 2, "y": 0},
        {"x1": 8, "x2": 9, "y": 1},
        {"x1": 8, "x2": 9, "y": 1},
        {"x1": 8, "x2": 9, "y": 1},
        {"x1": 8, "x2": 9, "y": 1},
        {"x1": 8, "x2": 9, "y": 1},
    ]
)
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
s3_path = "s3://landing-bronze/df.parquet"
endpoint_url = "http://localhost:9000"
# df_schema = df.collect_schema()
# df_schema_pydantic = [
#     {"name": col_name, "type_name": col_type}
#     for col_name, col_type in zip(df.columns, df_schema.values())
# ]

df_schema_pydantic = [
    ColumnInfo(
        name="id",
        type_text="INT",
        type_json='{"type":"INT"}',
        type_name="INT",
        position=0,
        comment="a comment",
    ),
    ColumnInfo(
        name="score",
        type_text="FLOAT",
        type_json='{"type":"FLOAT"}',
        type_name="FLOAT",
        position=1,
        comment="a comment",
    ),
    ColumnInfo(
        name="score",
        type_text="FLOAT",
        type_json='{"type":"FLOAT"}',
        type_name="FLOAT",
        position=2,
        comment="a comment",
    ),
]
fs = s3fs.S3FileSystem()

with fs.open(s3_path, mode="wb") as f:
    df.write_parquet(f)

configuration = unitycatalog_client.Configuration(
    host="http://localhost:8080/api/2.1/unity-catalog"
)


with unitycatalog_client.ApiClient(configuration) as api_client:
    catalog_api = unitycatalog_client.CatalogsApi(api_client)
    create_catalog = unitycatalog_client.CreateCatalog(name="finance")
    create_schema = unitycatalog_client.CreateSchema(
        name="bronze", catalog_name="finance", comment="financial data landing zone"
    )
    schema_api = unitycatalog_client.SchemasApi(api_client)
    table_api = unitycatalog_client.TablesApi(api_client)
    create_table = unitycatalog_client.CreateTable(
        name="score_table",
        catalog_name="finance",
        schema_name="bronze",
        table_type="EXTERNAL",
        data_source_format="PARQUET",
        columns=df_schema_pydantic,
        storage_location=s3_path,
        comment="scoring of companies",
    )
    try:
        catalog_response = catalog_api.create_catalog(create_catalog=create_catalog)
        schema_response = schema_api.create_schema(create_schema)
        table_response = table_api.create_table(create_table=create_table)
    except ApiException as e:
        print(e)
