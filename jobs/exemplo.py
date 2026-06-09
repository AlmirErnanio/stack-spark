from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Exemplo").getOrCreate()

dados = [("Alice", 30), ("Bob", 25), ("Carlos", 35)]
df = spark.createDataFrame(dados, ["nome", "idade"])

df.show()
df.groupBy().avg("idade").show()

spark.stop()
