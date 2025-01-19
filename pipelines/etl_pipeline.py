from dagster import job, op, Definitions, resource
import duckdb
import boto3
import os
import json

# Paths and configuration
CSV_PATH = "data/data.csv"
DUCKDB_PATH = "data/processed.db"
S3_BUCKET = "dagster-project-bucket"
CHUNK_SIZE = 10000

@resource
def duckdb_resource(context):
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("SET memory_limit='1GB'")
    return conn

@resource
def aws_resource(context):
    return {
        's3': boto3.client('s3'),
        'lambda': boto3.client('lambda')
    }

@op(required_resource_keys={'duckdb'})
def load_csv_to_duckdb(context):
    context.resources.duckdb.execute(f"""
        CREATE TABLE IF NOT EXISTS test_table AS
        SELECT * FROM read_csv_auto('{CSV_PATH}',
            SAMPLE_SIZE={CHUNK_SIZE},
            ALL_VARCHAR=1)
    """)
    row_count = context.resources.duckdb.execute("SELECT COUNT(*) FROM test_table").fetchone()[0]
    context.log.info(f"Loaded {row_count} rows into DuckDB")
    return DUCKDB_PATH

@op(required_resource_keys={'aws'})
def upload_for_processing(context, db_path):
    context.resources.aws['s3'].upload_file(
        db_path,
        S3_BUCKET,
        os.path.basename(db_path)
    )
    context.log.info("Uploaded dB to S3")
    return {'bucket': S3_BUCKET, 'key': os.path.basename(db_path)}

@op(required_resource_keys={'aws'})
def trigger_remote_compute(context, s3_location):
    response = context.resources.aws['lambda'].invoke(
        FunctionName='process-duckdb-data',
        InvocationType='RequestResponse',
        Payload=json.dumps(s3_location)
    )
    return json.loads(response['Payload'].read())

@job(resource_defs={
    'duckdb': duckdb_resource,
    'aws': aws_resource
})
def etl_pipeline():
    db_path = load_csv_to_duckdb()
    s3_location = upload_for_processing(db_path)
    trigger_remote_compute(s3_location)

defs = Definitions(jobs=[etl_pipeline])