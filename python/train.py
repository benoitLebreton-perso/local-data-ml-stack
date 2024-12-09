"""
Train a fake model
track the experiment with mlflow
and log the model in the mlflow registry
TODO : inference with mllfow a logging of inferences
"""

import os

import boto3
import numpy as np
import pandas as pd
import unitycatalog_client
from sklearn.ensemble import RandomForestClassifier
from unitycatalog_client.models import CreateRegisteredModel
from unitycatalog_client.rest import ApiException

import mlflow

s3 = boto3.client("s3")
s3.list_buckets()
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("scoring-client")
mlflow.set_registry_uri("http://localhost:8999")
# mlflow.set_registry_uri("uc:http://localhost:8080")  # uc
# os.environ["MLFLOW_UC_OSS_TOKEN"] = "<your OSS UC access token>"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:8999"
mlflow.sklearn.autolog()

configuration = unitycatalog_client.Configuration(
    host="http://localhost:8080/api/2.1/unity-catalog"
)

with (
    unitycatalog_client.ApiClient(configuration) as api_client,
    mlflow.start_run() as run
):
    table_api = unitycatalog_client.TablesApi(api_client)
    try:
        train_table = table_api.get_table("marketing.gold.users")
        # check_freshness = train_table.updated_at
        # print("freshness : ", check_freshness)
    except ApiException as e:
        print(e)
    data = pd.read_parquet(
        train_table.storage_location,
        storage_options={"client_kwargs": {"endpoint_url": "http://localhost:8999"}},
    )
    dummies_rfm = pd.get_dummies(data["rfm"])
    X = (
        data
        .assign(**{
            c:dummies_rfm[c] for c in dummies_rfm.columns
        })
        .drop(columns=["id","surname","rfm"])
    )
    y = np.random.choice([1.0, 0.0], size=len(X))
    clf = RandomForestClassifier()
    clf.fit(X=X, y=y)
    mlflow.log_metric("accuracy", 0.8)
    # mlflow.sklearn.log_model(clf, artifact_path="artifacts")
    models_api = unitycatalog_client.RegisteredModelsApi(api_client)
    create_registered_model = CreateRegisteredModel(
        name="score_users_random",
        catalog_name="marketing",
        schema_name="gold",
        comment="this model is too random to be used",
    )
    try:
        models_response = models_api.create_registered_model(create_registered_model)
    except ApiException as e:
        print(e)
