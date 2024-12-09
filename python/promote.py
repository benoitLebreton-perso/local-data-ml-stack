"""
Bug : for now we don't use it. We locate the model using its uri in minio
"""
import os

import mlflow.client
import mlflow.runs

import mlflow

os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:8999"

run_id = "5de9a928814e41bb86e2156fd4c65c31"
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("scoring-client")
mlflow.set_registry_uri("http://localhost:8999")


mc = mlflow.client.MlflowClient()
mc.create_registered_model("my_model")
mlflow.register_model(f"runs:/{run_id}/model", "my_model")
