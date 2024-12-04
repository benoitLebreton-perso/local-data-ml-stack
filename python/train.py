"""
Train a fake model
track the experiment with mlflow
and log the model in the mlflow registry
TODO : inference with mllfow a logging of inferences
"""

import os

import boto3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import mlflow
import unitycatalog_client
from unitycatalog_client.rest import ApiException


s3 = boto3.client("s3")
s3.list_buckets()
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")
mlflow.set_registry_uri("http://localhost:8999")
# mlflow.set_registry_uri("uc:http://localhost:8080")  # uc
# os.environ["MLFLOW_UC_OSS_TOKEN"] = "<your OSS UC access token>"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:8999"
mlflow.sklearn.autolog()
# pd.read_sql_table()  # it would be perfect to read form the unity catalog uri

configuration = unitycatalog_client.Configuration(
    host="http://localhost:8080/api/2.1/unity-catalog"
)

with unitycatalog_client.ApiClient(configuration) as api_client:
    table_api = unitycatalog_client.TablesApi(api_client)
    try:
        train_table = table_api.get_table("finance.bronze.score_table")
        check_freshness = train_table.updated_at
        location = train_table.storage_location
        print("freshness : ", check_freshness)
    except ApiException as e:
        print(e)

data = pd.read_parquet(
    location,
    storage_options={"client_kwargs": {"endpoint_url": "http://localhost:8999"}},
)
X = data.drop(columns=["y"])
y = data.filter(["y"])
with mlflow.start_run() as run:
    clf = RandomForestClassifier()
    clf.fit(X=X, y=y)
    mlflow.log_metric("accuracy", 0.8)
    # mlflow.sklearn.log_model(clf, artifact_path="artifacts")
