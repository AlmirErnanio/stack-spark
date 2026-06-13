import glob
import os
import shutil

from pyspark.sql import SparkSession

BUCKET   = os.environ["AWS_S3_BUCKET"]
S3_INPUT = f"s3a://{BUCKET}/bronze/dimensao/clientes"

# workers e scheduler montam ./data em /opt/spark/work-dir/data
DATA_DIR  = "/opt/spark/work-dir/data/raw"
TMP_DIR   = f"{DATA_DIR}/_tmp_clientes"
DEST_FILE = f"{DATA_DIR}/clientes.parquet"

spark = (
    SparkSession.builder
    .appName("import_clientes")
    .master(os.environ.get("SPARK_MASTER", "spark://spark-master:7077"))
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# ── Leitura (bronze/S3) ──────────────────────────────────────────────────────────
df = (
    spark.read
    .option("mergeSchema", "true")
    .parquet(S3_INPUT)
)

print(f"\n>>> Schema do dataset ({S3_INPUT}):")
df.printSchema()
print(f">>> Total de linhas: {df.count():,}\n")

# ── Escrita local (data/raw) ─────────────────────────────────────────────────────
os.makedirs(DATA_DIR, exist_ok=True)

df.coalesce(1).write.mode("overwrite").parquet(TMP_DIR)

part = glob.glob(f"{TMP_DIR}/part-*.parquet")[0]
shutil.move(part, DEST_FILE)
shutil.rmtree(TMP_DIR)

print(f">>> Arquivo salvo em: {DEST_FILE}")

spark.stop()
