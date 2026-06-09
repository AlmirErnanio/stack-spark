# Stage 1: extrai os binários Spark da imagem oficial (mesma versão do cluster)
FROM apache/spark:3.5.3 AS spark-dist

# Stage 2: imagem Airflow com Java + cliente Spark embutido
FROM python:3.11-slim

# Copia a instalação completa do Spark (spark-submit + jars)
COPY --from=spark-dist /opt/spark /opt/spark

# Java runtime + utilitários mínimos
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jre-headless \
        procps \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    # Cria symlink estável para JAVA_HOME (funciona em arm64 e amd64)
    && ln -sf "$(dirname "$(dirname "$(readlink -f /usr/bin/java)")")" /usr/local/active-jvm

ENV JAVA_HOME=/usr/local/active-jvm
ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"
ENV AIRFLOW_HOME=/opt/airflow

ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11

RUN pip install --no-cache-dir \
    "apache-airflow[postgres]==${AIRFLOW_VERSION}" \
    apache-airflow-providers-apache-spark \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

RUN pip install --no-cache-dir dbt-core dbt-spark

RUN pip install --no-cache-dir \
    apache-airflow-providers-amazon \
    boto3 \
    s3fs

RUN mkdir -p "${AIRFLOW_HOME}/dags" "${AIRFLOW_HOME}/logs" "${AIRFLOW_HOME}/plugins"

WORKDIR ${AIRFLOW_HOME}
