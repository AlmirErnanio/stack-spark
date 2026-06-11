from datetime import datetime

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="import_categorias",
    description="Importa dimensão categorias do S3 staging → ram",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["spark", "dimensao", "s3"],
) as dag:

    importar_categorias = SparkSubmitOperator(
        task_id="importar_categorias",
        application="/opt/airflow/jobs/import_categorias.py",
        conn_id="spark_default",
        name="import_categorias",
        deploy_mode="client",
        verbose=False,
    )
