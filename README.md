# Purpose

I try to do the same thing as https://github.com/VillePuuska/Local-Lakehouse/tree/main but with more ML tools (mlflow).
And I use the official unity-catalog python sdk https://pypi.org/project/unitycatalog-client/.


# Setup

## Up infra

````bash
docker compose -f "docker-compose.yml" up -d --build
````

### Minio

On minio http://localhost:9001 you need to :
- login (user: minioadmin pass: minioadmin)
- create two buckets
    - landing-bronze
    - mlflow-artifacts
- Optional : create two users in Identity/Users and use the access-keys instead of the admin-access
    - etl : with a corresponding access-key / secret-key and use those in `~/.aws/credentials`
    - mlflow : with a corresponding access-key / secret-key and use those in mlflow container

On you computer write `~/.aws/credentials` file
````conf
[default]
endpoint_url = http://localhost:8999
s3 =
    endpoint_url = http://localhost:8999
aws_access_key_id=minioadmin
aws_secret_access_key=minioadmin
````

### Postgres

Prerequisites : install libq with brew for macOs

````bash
psql postgres://postgres:postgres@localhost:5432/postgres
````

````postgres=# 
create database ucdata;
create database mlflowdata;
````

or directly
````bash
psql postgres://postgres:postgres@localhost:5432/postgres -c 'create database ucdb;'
psql postgres://postgres:postgres@localhost:5432/postgres -c 'create database mlflowdb;'
````

## Python scripts
Setup python env with the tool of your choice

with pyenv+virtualenv and python3.10
````
pyenv virtualenv 3.10.15 venv
pip install -r python/requirements.txt
````

Run ETL to create data into the lakehouse (with unity catalog metadata)
````
python python/etl.py
````

See 
 - on unity catalog the metadata : `http://localhost:3000/data/finance/bronze/score_table`
 - on minio the data : `http://localhost:9001/browser/landing-bronze`

![unity-catalog](docs/unity-ui.png "Unity Catalog")
![minio-data](docs/minio-landing-data.png "Minio Landing Data")

Run training of the model and log it to mlflow
````
python python/train.py
````

See 
 - on mlflow experiment tracking the run : `http://localhost:5000/#/experiments/1`
 - (optional) on minio under the hood : `http://localhost:9001/browser/mlflow-artifacts/`

![mlflow-run](docs/mlflow-run.png)
![mlflow-artifact](docs/mlflow-artifact.png)
![minio-mlflow-artifact-under-ther-hood](docs/minio-mlflow-artifact-under-the-hood.png)
## Inference

Find the uri in the registry on minio or mlflow.

````console
(venv) ➜  modern_data_stack git:(main) ✗ mlflow models serve -m s3://mlflow-artifacts/1/aa2110d499664590be2aef98ee7d5ac1/artifacts/model -p 5001 --no-conda
2024/12/05 21:49:11 INFO mlflow.models.flavor_backend_registry: Selected backend for flavor 'python_function'
2024/12/05 21:49:11 INFO mlflow.pyfunc.backend: === Running command 'exec gunicorn --timeout=60 -b 127.0.0.1:5001 -w 1 ${GUNICORN_CMD_ARGS} -- mlflow.pyfunc.scoring_server.wsgi:app'
[2024-12-05 21:49:11 +0100] [13864] [INFO] Starting gunicorn 23.0.0
[2024-12-05 21:49:11 +0100] [13864] [INFO] Listening at: http://127.0.0.1:5001 (13864)
[2024-12-05 21:49:11 +0100] [13864] [INFO] Using worker: sync
[2024-12-05 21:49:11 +0100] [13870] [INFO] Booting worker with pid: 13870
````

Call the inference service from where you want

````console
(venv) ➜  modern_data_stack git:(main) ✗ curl http://127.0.0.1:5001/invocations -H 'Content-Type: application/json' -d '{"inputs":[{"x1":"0","x2":"1"}]}'
{"predictions": [0]}%  
````

```console
(venv) ➜  modern_data_stack git:(main) ✗ curl http://127.0.0.1:5001/invocations -H 'Content-Type: application/json' -d '{"inputs":[{"x1":"0","x2":"1"},{"x1":"3","x2":"4"}]}'
{"predictions": [0, 0]}%  
```

TODO : Use UnityCatalog to follow this id ?
I think I will make a real FastAPI service for the inference and 
- use Unity Catalog in it to find the model
- log the inference in mlflow or log in in the lakehouse
