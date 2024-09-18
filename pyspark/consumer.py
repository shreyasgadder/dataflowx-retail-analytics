from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
import datetime
import json
import os
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType
from pyspark.sql.functions import first, last, count



def console_output(df, epoch_id):
    # Get the first and last values of transaction_id
    first_transid = df.select(first("transaction_id")).collect()[0][0]
    last_transid = df.select(last("transaction_id")).collect()[0][0]

    # Get the total number of records
    total_records = df.count()

    # Print the results in a tabular format with batch number
    print("-" * 40)
    print(f"** BATCH {epoch_id + 1} **")
    print("-" * 40)
    print(f"transaction_id's processed: {first_transid} to {last_transid}")
    print(f"Total records processed: {total_records}")
    print("-" * 40)
    

# Custom upsert function using PyMongo
def upsert_to_mongo(df, epoch_id):
    mongo_uri = os.environ.get('MONGO_URI')
    mongo_db = os.environ.get('MONGO_DB')
    
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db["transactions"]
    
    records = df.collect()

    for record in records:
        record_dict = record.asDict()

        # Convert any datetime.date objects to datetime.datetime
        for key, value in record_dict.items():
            if isinstance(value, datetime.date):
                record_dict[key] = datetime.datetime.combine(value, datetime.datetime.min.time())

        transaction_id = record_dict["transaction_id"]
        
        record_dict["ins_upd_ts"] = datetime.datetime.now()

        # Perform the upsert operation
        collection.replace_one({"transaction_id": transaction_id}, record_dict, upsert=True)

    # print(f"Batch {epoch_id} processed: {len(records)} records upserted to MongoDB")


def consume_data_spark():

    schema = StructType([
        StructField("transaction_id", IntegerType(), True),
        StructField("order_id", StringType(), True),
        StructField("order_date", DateType(), True),
        StructField("ship_date", DateType(), True),
        StructField("ship_mode", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("customer_name", StringType(), True),
        StructField("segment", StringType(), True),
        StructField("country", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("postal_code", StringType(), True),
        StructField("region", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("category", StringType(), True),
        StructField("sub_category", StringType(), True),
        StructField("product_name", StringType(), True),
        StructField("sales", DoubleType(), True)
    ])
    
    
    
    # Initialize SparkSession with Kafka and MongoDB connectors
    # checkpointLocation - Specifies the checkpoint directory for the streaming query for fault tolerance.
    # output.uri - Specifies the MongoDB connection URI including the database and collection name.
    
    """
    spark = SparkSession.builder \
        .appName("KafkaToMongoDB") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,"
                "org.mongodb.spark:mongo-spark-connector_2.12:10.4.0") \
        .getOrCreate()
    """
    spark = SparkSession.builder \
        .appName("KafkaToMongoDB") \
        .config("spark.ui.port", "4045") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.sql.streaming.checkpointLocation", "/app/checkpoints/kafka-to-mongodb") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .config("spark.jars", ",".join([
        "/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.2.jar",
        "/opt/spark/jars/mongo-spark-connector_2.12-10.4.0.jar",
        "/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.2.jar",
        "/opt/spark/jars/kafka-clients-3.4.1.jar",
        "/opt/spark/jars/jsr305-3.0.0.jar",
        "/opt/spark/jars/commons-pool2-2.11.1.jar",
        "/opt/spark/jars/hadoop-client-runtime-3.3.4.jar",
        "/opt/spark/jars/lz4-java-1.8.0.jar",
        "/opt/spark/jars/snappy-java-1.1.10.5.jar",
        "/opt/spark/jars/slf4j-api-2.0.7.jar",
        "/opt/spark/jars/hadoop-client-api-3.3.4.jar",
        "/opt/spark/jars/commons-logging-1.1.3.jar",
        "/opt/spark/jars/mongodb-driver-sync-5.1.4.jar",
        "/opt/spark/jars/bson-5.1.4.jar",
        "/opt/spark/jars/mongodb-driver-core-5.1.4.jar",
        "/opt/spark/jars/bson-record-codec-5.1.4.jar"
        ])) \
        .getOrCreate()

    kafka_bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
    
    # Read from Kafka topic 'transactions'
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "earliest") \
        .load()
        

    # Deserialize Kafka messages from JSON with proper schema
    messages_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
        .select(from_json("json_value", schema).alias("data")) \
        .filter(col("data.transaction_id").isNotNull()) \
        .select("data.*")
    

    # Print messages to the console for debugging
    console_query = messages_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .foreachBatch(lambda df, epoch_id: console_output(df, epoch_id)) \
    .start()
    
    
    mongo_query = messages_df.writeStream \
        .foreachBatch(upsert_to_mongo) \
        .start()
    
    """
    # Write the streaming DataFrame to MongoDB
    mongo_query = messages_df.writeStream \
    .format("mongodb") \
    .option("checkpointLocation", "/app/checkpoints/kafka-to-mongodb") \
    .option("forceDeleteTempCheckpointLocation", "true") \
    .option("spark.mongodb.connection.uri", mongo_uri) \
    .option("spark.mongodb.database", "retail_db") \
    .option("spark.mongodb.collection", "transactions") \
    .outputMode("append") \
    .start()
    """

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    consume_data_spark()
