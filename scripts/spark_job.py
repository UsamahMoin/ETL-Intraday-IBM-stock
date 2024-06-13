from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, LongType

# Define the schema for the JSON data
schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("open", FloatType(), True),
    StructField("high", FloatType(), True),
    StructField("low", FloatType(), True),
    StructField("close", FloatType(), True),
    StructField("volume", LongType(), True)
])

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Stock Data Processing") \
    .master("spark://etl-spark-1:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.cores.max", "1") \
    .getOrCreate()

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "etl-kafka-1:9092") \
    .option("subscribe", "intraday_stock_data") \
    .option("startingOffsets", "earliest") \
    .load()

# Convert the value column from Kafka (which is in binary format) to a string
df = df.selectExpr("CAST(value AS STRING)")

# Parse the JSON data and create a DataFrame with the defined schema
json_df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Process the data as needed
# For example, add a new column with the parsed timestamp
processed_df = json_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

# Write the processed data to PostgreSQL
def write_to_postgres(df, epoch_id):
    df.write \
        .format("jdbc") \
        .mode("append") \
        .option("url", "jdbc:postgresql://etl-postgres-1:5432/airflow") \
        .option("dbtable", "processed_stock_data") \
        .option("user", "airflow") \
        .option("password", "airflow") \
        .save()

query = processed_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

query.awaitTermination()
