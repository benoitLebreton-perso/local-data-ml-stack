# Purpose

I try to do the same thing as https://github.com/VillePuuska/Local-Lakehouse/tree/main but with more ML tools (mlflow).
And I use the official unity-catalog python sdk https://pypi.org/project/unitycatalog-client/.


# Setup

## Up infra

````bash
docker compose -f "docker-compose.yml" up -d --build
````

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

Run training of the model and log it to mlflow
````
python python/train.py
````

See 
 - on mlflow experiment tracking the run : `http://localhost:5000/#/experiments/1`
 - (optional) on minio under the hood : `http://localhost:9001/browser/mlflow-artifacts/`

## Inference

find the run id to fill the uri. 
TODO : Use UnityCatalog to follow this id ?
I think I will make a real FastAPI service for the inference and 
- use Unity Catalog in it to find the model
- log the inference in mlflow or log in in the lakehouse
````bash
mlflow models serve -m s3://mlflow-artifacts/1/80d45aadbbf44f93ac6004f9d35c8deb/artifacts/model -p 5001
````

Call the inference service from where you want
````bash
curl http://127.0.0.1:5001/invocations -H 'Content-Type: application/json' -d '{"inputs":[{"x1":"0","x2":"1"}]}'
curl http://127.0.0.1:5001/invocations -H 'Content-Type: application/json' -d '{"inputs":[{"x1":"0","x2":"1"},{"x1":"3","x2":"4"}]}'

````