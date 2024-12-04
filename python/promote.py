"""
Bug : for now we don't use it. We locate the model using its uri in minio
"""
import mlflow
import os

import mlflow.client
import mlflow.runs

os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:8999"

run_id = "80d45aadbbf44f93ac6004f9d35c8deb"
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")
mlflow.set_registry_uri("http://localhost:8999")


mc = mlflow.client.MlflowClient()
mc.create_registered_model("my_model")
mlflow.register_model(f"runs:/{run_id}/model", "my_model")