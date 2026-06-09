import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_date


BUCKET   = os.environ["AWS_S3_BUCKET"]
PREFIX   = "raw/vendas"                          # ajuste o caminho dentro do bucket
S3_PATH  = f"s3a://{BUCKET}/{PREFIX}/"

spark = (
    SparkSession.builder
    .appName("import_data_s3")
    .master(os.environ.get("SPARK_MASTER", "spark://spark-master:7077"))
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# ── Leitura ────────────────────────────────────────────────────────────────────
df = (
    spark.read
    .option("mergeSchema", "true")   # útil quando parquet tem partições com schemas evoluídos
    .parquet(S3_PATH)
)

print(f"\n>>> Schema do dataset ({S3_PATH}):")
df.printSchema()

print(f">>> Total de linhas: {df.count():,}\n")

# ── Transformação mínima de exemplo ───────────────────────────────────────────
if "data_venda" in df.columns:
    df = df.withColumn("data_venda", to_date(col("data_venda")))

resumo = (
    df.groupBy("data_venda")
    .agg(count("*").alias("qtd_registros"))
    .orderBy("data_venda")
)

resumo.show(20, truncate=False)

# ── Escrita na camada silver (também no S3) ────────────────────────────────────
SILVER_PATH = f"s3a://{BUCKET}/silver/vendas/"

(
    df.write
    .mode("overwrite")
    .partitionBy("data_venda")
    .parquet(SILVER_PATH)
)

print(f">>> Dados gravados em: {SILVER_PATH}")

spark.stop()
