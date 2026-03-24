"""
Databricks PySpark ETL Notebook — SwasthyaSetu AI
Ingests raw patient health records from a source into Delta Lake.

Run this notebook in a Databricks cluster environment.
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # SwasthyaSetu AI — ETL Pipeline
# MAGIC Ingests patient data into Delta Lake tables.

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import datetime

spark = SparkSession.builder.appName("SwasthyaSetuETL").getOrCreate()

# ── Schema ─────────────────────────────────────────────────────────────────
patient_schema = StructType([
    StructField("patient_id",  StringType(),    False),
    StructField("name",        StringType(),    False),
    StructField("age",         IntegerType(),   True),
    StructField("gender",      StringType(),    True),
    StructField("blood_group", StringType(),    True),
    StructField("phone",       StringType(),    True),
    StructField("occupation",  StringType(),    True),
    StructField("region",      StringType(),    True),
    StructField("created_at",  TimestampType(), True),
])

# ── Read from source (e.g. CSV / Kafka / REST API dump) ────────────────────
# Replace this path with your actual source
SOURCE_PATH = "dbfs:/mnt/swasthya/raw/patients/"

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", False)
    .schema(patient_schema)
    .csv(SOURCE_PATH)
)

print(f"Loaded {raw_df.count()} records from source.")
raw_df.printSchema()

# ── Transform ──────────────────────────────────────────────────────────────
transformed_df = (
    raw_df
    .withColumn("patient_id", F.upper(F.trim(F.col("patient_id"))))
    .withColumn("name",        F.initcap(F.trim(F.col("name"))))
    .withColumn("gender",      F.upper(F.trim(F.col("gender"))))
    .withColumn("blood_group", F.upper(F.trim(F.col("blood_group"))))
    .withColumn("updated_at",  F.lit(datetime.datetime.utcnow()).cast(TimestampType()))
    .dropDuplicates(["patient_id"])
    .filter(F.col("name").isNotNull())
)

print(f"After transform: {transformed_df.count()} clean records.")

# ── Write to Delta Lake ────────────────────────────────────────────────────
DELTA_TABLE = "swasthya.patients"

(
    transformed_df.write
    .format("delta")
    .mode("merge")
    .option("mergeSchema", "true")
    .saveAsTable(DELTA_TABLE)
)

print(f"✅ Written to Delta table: {DELTA_TABLE}")
spark.sql(f"OPTIMIZE {DELTA_TABLE}")
print("✅ OPTIMIZE complete.")
