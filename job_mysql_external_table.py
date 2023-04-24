import math
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Start
datasource = glueContext.create_dynamic_frame_from_options(
    'mysql',
    connection_options={
        "url": "jdbc:mysql://<url servidor>:<porta>/<database>?ssl-mode=REQUIRED",
        "user": "usuario",
        "password": "senha",
        "dbtable": "schema.table"
    }
)

datasource = datasource.repartition(1)
glueContext.write_dynamic_frame.from_options(
    frame=datasource,
    connection_type='s3',
    connection_options={
        "path": "s3://xxxxxxx/xxxxxx/unloading"
    },
    format="csv"
)

#End

job.commit()

# Rename file and add file extension
# i.e. = file_0001_dataset rename to Xxxxxxx_Dataset.csv
# Delete file_0001_dataset

import boto3

client = boto3.client('s3')

BUCKET_NAME = 'nomedobucket'
PREFIX = 'prefixbucket/unloading'
NEW_FILE_NAME = '/Name_Dataset.csv'

response = client.list_objects(
    Bucket=BUCKET_NAME,
    Prefix=PREFIX
)

file_name_key = response["Contents"][0]["Key"]
copy_source = {
    "Bucket": BUCKET_NAME,
    "Key": file_name_key
}

client.copy_object(
    Bucket=BUCKET_NAME,
    CopySource=copy_source,
    Key=PREFIX + NEW_FILE_NAME
)

client.delete_object(
    Bucket=BUCKET_NAME,
    Key=file_name_key
)