from datetime import datetime

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="import_dimensoes",
    description="Importa dimensões do S3 bronze → data/raw (categorias e clientes)",
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

    importar_clientes = SparkSubmitOperator(
        task_id="importar_clientes",
        application="/opt/airflow/jobs/import_clientes.py",
        conn_id="spark_default",
        name="import_clientes",
        deploy_mode="client",
        verbose=False,
    )

    importar_fornecedores = SparkSubmitOperator(
        task_id="importar_fornecedores",
        application="/opt/airflow/jobs/import_fornecedores.py",
        conn_id="spark_default",
        name="import_fornecedores",
        deploy_mode="client",
        verbose=False,
    )

    # tasks independentes — executam em paralelo
    [importar_categorias, importar_clientes, importar_fornecedores]
