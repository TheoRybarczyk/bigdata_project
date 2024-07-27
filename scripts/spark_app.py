import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import FloatType, StructType, StructField, StringType, TimestampType
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pandas as pd
import os

KAFKA_BROKER_EXT = f"{os.getenv('KAFKA_BROKER_CONT_NAME')}:{os.getenv('KAFKA_BROKER_LISTEN_EXT_PORT')}"
KAFKA_BROKER_CL = f"{os.getenv('HOST')}:{os.getenv('KAFKA_BROKER_LISTEN_CLIENT_PORT')}"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

INFLUXDB_CONT_NAME = os.getenv("INFLUXDB_CONT_NAME")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

INFLUXDB_TOKEN_FILE = "/opt/bitnami/spark/influxdb_token.txt"

def create_spark_session():
    """Create the Spark session for this app."""
    logging.basicConfig(level=logging.INFO)
    spark = None
    try:
        spark = SparkSession.builder \
            .appName("SparkToInfluxDB") \
            .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
            .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        logging.info("Spark session created successfully!")
    except Exception as e:
        logging.exception(f"Failed to create Spark session: {e}")
    return spark

def read_from_kafka(spark):
    """Attempt to get a Spark dataframe from the Kafka source."""
    kafka_df = None
    try:
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", f"{KAFKA_BROKER_EXT},{KAFKA_BROKER_CL}") \
            .option("subscribe", KAFKA_TOPIC) \
            .option('startingOffsets', 'latest') \
            .option("failOnDataLoss","False") \
            .load()
        logging.info("Kafka DataFrame created successfully")
    except Exception as e:
        logging.warning(f"Failed to create Kafka DataFrame: {e}")
    return kafka_df

def process_kafka_data(kafka_df):
    """Format and parse the data from the reveived json input data."""
    schema = StructType([
        StructField("AAAAMMJJHH", TimestampType(), True),
        StructField("NOM_USUEL", StringType(), True),
        StructField("LAT", FloatType(), True),
        StructField("LON", FloatType(), True),
        StructField("TN", FloatType(), True),
        StructField("TX", FloatType(), True),
        StructField("RR1", FloatType(), True),
        StructField("DRR1", FloatType(), True),
        StructField("FF", FloatType(), True),
        StructField("DD", FloatType(), True),
        StructField("UN", FloatType(), True),
        StructField("UX", FloatType(), True),
        StructField("PSTAT", FloatType(), True),
        StructField("VV", FloatType(), True)
    ])
    processed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    return processed_df
    
class InfluxDBWriter:
    
    def __init__(self, client, write_api):
        self.client = client
        self.write_api = write_api

    def open(self, partition_id, epoch_id):
        # Open connection. This method is optional in Python.
        logging.info("Opened %d, %d" % (partition_id, epoch_id))
        return True

    def process(self, row):
        # Write row to connection. This method is NOT optional in Python.
        bucket = INFLUXDB_BUCKET
        measurement = INFLUXDB_BUCKET
        org = INFLUXDB_ORG
        
        point = (
            Point(measurement)
                .field("Timestamp", str(row["AAAAMMJJHH"]))
                .tag("Station", row["NOM_USUEL"])
                .field("LAT", row["LAT"])
                .field("LON", row["LON"])    
                .field("T_min (°C)", row["TN"])
                .field("T_max (°C)", row["TX"])
                .field("Precipitations (mm)", row["RR1"])
                .field("Precipitations_dur (mn)", row["RR1"])
                .field("Wind_speed (m/s)", row["FF"])
                .field("Wind_dir (°)", row["DD"])
                .field("Humidity_min (%)", row["UN"])
                .field("Humidity_max (%)", row["UX"])
                .field("Pressure (hPa)", row["PSTAT"])
                .field("Visibility (m)", row["VV"])
                .time(datetime.utcnow())
        )
        self.write_api.write(bucket=bucket, org=org, record=point)

    def close(self, error):
        # Close the connection. This method in optional in Python.
        self.write_api.__del__()
        self.client.__del__()
        logging.info("Closed with error: %s" % str(error))


if __name__ == "__main__":
    
    token= pd.read_table(INFLUXDB_TOKEN_FILE).iloc[0,2]
    url = f"http://{INFLUXDB_CONT_NAME}:{INFLUXDB_PORT}"    

    client = InfluxDBClient(url=url, token=token, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
        
    spark = create_spark_session()
    if spark:
        kafka_df = read_from_kafka(spark)
        if kafka_df:
            processed_df = process_kafka_data(kafka_df)
            
            query = processed_df.writeStream \
                .outputMode("append") \
                .foreach(InfluxDBWriter(client, write_api)) \
                .start()            
            
            query.awaitTermination()
