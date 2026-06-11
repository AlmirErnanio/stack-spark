import glob
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_date

# Carrega .env quando rodando localmente (no-op dentro do Docker)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BUCKET   = os.environ["AWS_S3_BUCKET"]
PREFIX   = "bronze/dimensao/categorias"                          # ajuste o caminho dentro do bucket
S3_PATH  = f"s3a://{BUCKET}/{PREFIX}"

_master = os.environ.get("SPARK_MASTER", "local[*]")

builder = (
    SparkSession.builder
    .appName("import_data_s3")
    .master(_master)
)

# Fora do Docker: injeta os JARs do S3A e credenciais via config
# (no cluster, o spark-defaults.conf já cuida disso)
if _master == "local[*]":
    builder = (
        builder
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.4.2,"
            "software.amazon.awssdk:bundle:2.29.52",
        )
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.access.key",  os.environ["AWS_ACCESS_KEY_ID"])
        .config("spark.hadoop.fs.s3a.secret.key",  os.environ["AWS_SECRET_ACCESS_KEY"])
        .config("spark.hadoop.fs.s3a.endpoint.region",
                os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
    )

spark = builder.getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# ── Leitura ────────────────────────────────────────────────────────────────────
df = (
    spark.read
    .option("mergeSchema", "true")   # útil quando parquet tem partições com schemas evoluídos
    .parquet(S3_PATH)
)

print(f"\n>>> Schema do dataset ({S3_PATH}):")

# ── Escrita local ───────────────────────────────────────────────────────────────
_root      = Path(__file__).resolve().parent.parent / "data" / "raw"
_tmp_dir   = str(_root / "_tmp_categorias")
_dest_file = str(_root / "categorias.parquet")

_root.mkdir(parents=True, exist_ok=True)

df.coalesce(1).write.mode("overwrite").parquet(_tmp_dir)

_part = glob.glob(f"{_tmp_dir}/part-*.parquet")[0]
shutil.move(_part, _dest_file)
shutil.rmtree(_tmp_dir)

print(f">>> Arquivo salvo em: {_dest_file}")

spark.stop()
