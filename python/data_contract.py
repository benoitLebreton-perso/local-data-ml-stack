"""
Data contracts : documentation + automatic check definitions (expectations)
TODO great expectations creation"""
from unitycatalog_client import (CatalogsApi, Configuration, CreateCatalog,
                                 CreateSchema, CreateTable, SchemasApi,
                                 TablesApi)
from unitycatalog_client.api_client import ApiClient
from unitycatalog_client.models.column_info import ColumnInfo
from unitycatalog_client.rest import ApiException


bronze_s3_path_mask = "s3://landing-bronze/{}.parquet"
gold_s3_path_mask = "s3://lake-gold/{}.parquet"


users_table_schema = [
    ColumnInfo(
        name="id",
        type_text="INT",
        type_json='{"type":"INT"}',
        type_name="INT",
        position=0,
        comment="unique id of the user",
    ),
    ColumnInfo(
        name="surname",
        type_text="CHAR",
        type_json='{"type":"CHAR"}',
        type_name="CHAR",
        position=1,
        comment="surname of the client",
    ),
]

transactions_table_schema = [
    ColumnInfo(
        name="id",
        type_text="INT",
        type_json='{"type":"INT"}',
        type_name="INT",
        position=0,
        comment="unique id of the user",
    ),
    ColumnInfo(
        name="user_id",
        type_text="INT",
        type_json='{"type":"INT"}',
        type_name="INT",
        position=1,
        comment="User id (foreign key to users table)",
    ),
    ColumnInfo(
        name="time_stamp",
        type_text="TIMESTAMP",
        type_json='{"type":"TIMESTAMP"}',
        type_name="TIMESTAMP",
        position=2,
        comment="Timestamp of the transaction in local time",
    ),
    ColumnInfo(
        name="amount",
        type_text="DECIMAL",
        type_json='{"type":"DECIMAL"}',
        type_name="DECIMAL",
        position=3,
        comment="Amount of the transaction in $",
    ),
]

configuration = Configuration(
    host="http://localhost:8080/api/2.1/unity-catalog"
)

with ApiClient(configuration) as api_client:
    catalog_api = CatalogsApi(api_client)
    create_catalog = CreateCatalog(name="marketing")
    bronze_schema = CreateSchema(
        name="bronze", catalog_name="marketing", comment="marketing data landing zone"
    )
    gold_schema = CreateSchema(
        name="gold", catalog_name="marketing", comment="marketing data landing zone"
    )
    schema_api = SchemasApi(api_client)
    table_api = TablesApi(api_client)
    bronze_user_table_def = CreateTable(
        name="users",
        catalog_name="marketing",
        schema_name="bronze",
        table_type="EXTERNAL",
        data_source_format="PARQUET",
        columns=users_table_schema,
        storage_location=bronze_s3_path_mask.format("users"),
        comment="clients of the companies",
    )
    gold_users_table_schema = users_table_schema.copy()
    rfm_field = ColumnInfo(
        name="rfm",
        type_text="CHAR",
        type_json='{"type":"CHAR"}',
        type_name="CHAR",
        position=2,
        comment="RFM segment of the user R: Recency, F: Frequency, M: Amount",
    )
    gold_users_table_schema.append(rfm_field)
    gold_user_table_def = bronze_user_table_def.copy(update={
        "schema_name": "gold",
        "storage_location": gold_s3_path_mask.format("users"),
        "columns": gold_users_table_schema,
    })
    bronze_transaction_table_def = CreateTable(
        name="transactions",
        catalog_name="marketing",
        schema_name="bronze",
        table_type="EXTERNAL",
        data_source_format="PARQUET",
        columns=transactions_table_schema,
        storage_location=bronze_s3_path_mask.format("transactions"),
        comment="transactions of the clients (users table)",
    )
    gold_transactions_table_schema = transactions_table_schema.copy()
    gold_transactions_table_schema[-1].type_text="FLOAT"
    gold_transactions_table_schema[-1].type_json='{"type":"FLOAT"}'
    gold_transactions_table_schema[-1].type_name="FLOAT"
    gold_transaction_table_def = bronze_transaction_table_def.copy(update={
        "schema_name": "gold",
        "storage_location": gold_s3_path_mask.format("transactions"),
        "columns": gold_transactions_table_schema,
    })
    try:
        catalog_api.create_catalog(create_catalog=create_catalog)
        schema_api.create_schema(bronze_schema)
        schema_api.create_schema(gold_schema)
        table_api.create_table(create_table=bronze_user_table_def)
        table_api.create_table(create_table=gold_user_table_def)
        table_api.create_table(create_table=bronze_transaction_table_def)
        table_api.create_table(create_table=gold_transaction_table_def)
    except ApiException as e:
        print(e)
