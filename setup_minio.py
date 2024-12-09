import boto3


s3 = boto3.client("s3")
s3.create_bucket(Bucket="landing-bronze")
s3.create_bucket(Bucket="lake-gold")
s3.create_bucket(Bucket="mlflow-artifacts")
s3.create_bucket(Bucket="unitycatalog-artifacts")
