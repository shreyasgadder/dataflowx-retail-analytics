import logging
import time
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaPostgresProducer:
    def __init__(self, spark_session, kafka_bootstrap_servers, jdbc_url, jdbc_properties):
        """
        Initializes the KafkaPostgresProducer with Spark session, Kafka, and PostgreSQL configurations.
        """
        self.spark = spark_session
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.jdbc_url = jdbc_url
        self.jdbc_properties = jdbc_properties
            

    def get_last_tid_from_kafka(self):
        """
        Retrieves the last processed TID (Transaction ID) from the Kafka topic `last_tid_topic`.
        If no TID is found, it defaults to 0.
        """
        logger.info("Fetching the last processed transaction_id from Kafka...")
        kafka_config = {
            "kafka.bootstrap.servers": self.kafka_bootstrap_servers,
            "subscribe": "last_tid_topic"
        }

        try:
            df = self.spark.read.format("kafka").options(**kafka_config).load()

            if df.count() == 0:
                logger.info("No records found in Kafka-last_tid_topic. Starting from transaction_id 0.")
                return 0  # Default if there are no records in Kafka

            # Extract the last TID value from Kafka messages
            last_tid = int(df.selectExpr("CAST(value AS STRING)").rdd.max()[0])
            logger.info(f"Last processed transaction_id from Kafka: {last_tid}")
            return last_tid
        except Exception as e:
            logger.error(f"Error fetching last transaction_id from Kafka-last_tid_topic: {e}")
            return 0

    def publish_last_tid_to_kafka(self, last_tid):
        """
        Publishes the last processed TID back to Kafka to track progress.
        """
        logger.info(f"Publishing the last processed transaction_id {last_tid} to Kafka-last_tid_topic...")
        try:
            data = [(last_tid,)]
            tid_df = self.spark.createDataFrame(data, ["transaction_id"])

            tid_df.selectExpr("CAST(transaction_id AS STRING) AS value") \
                .write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
                .option("topic", "last_tid_topic") \
                .save()
            logger.info(f"Successfully published last transaction_id {last_tid} to Kafka-last_tid_topic.")
        except Exception as e:
            logger.error(f"Error publishing last transaction_id {last_tid} to Kafka: {e}")

    def get_new_transactions_from_postgres(self, last_tid):
        """
        Fetches new transactions from PostgreSQL where TID > last_tid.
        """
        logger.info(f"Fetching new transactions from PostgreSQL with transaction_id > {last_tid}...")
        query = f"(SELECT * FROM transactions WHERE transaction_id > {last_tid}) AS new_transactions"
        
        try:
            df = self.spark.read.jdbc(url=self.jdbc_url, table=query, properties=self.jdbc_properties)
            logger.info(f"Fetched {df.count()} new transactions from PostgreSQL.")
            return df
        except Exception as e:
            logger.error(f"Error fetching new transactions from PostgreSQL: {e}")
            return None

    def publish_transactions_to_kafka(self, df):
        """
        Publishes the new transactions to the Kafka `transactions` topic.
        """
        logger.info("Publishing new transactions to Kafka-transactions...")
        try:
            df.selectExpr("CAST(transaction_id AS STRING) AS key", "to_json(struct(*)) AS value") \
                .write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
                .option("topic", "transactions") \
                .save()
            logger.info("Successfully published new transactions to Kafka-transactions.")
        except Exception as e:
            logger.error(f"Error publishing transactions to Kafka: {e}")

    def process(self):
        """
        Orchestrates the fetching of new transactions from PostgreSQL and publishing them to Kafka.
        """
        try:            
            # Get the last processed TID from Kafka
            last_tid = self.get_last_tid_from_kafka()

            # Fetch new transactions from PostgreSQL
            new_transactions_df = self.get_new_transactions_from_postgres(last_tid)
            if new_transactions_df is None or new_transactions_df.count() == 0:
                logger.info("No new transactions to process.")
                return

            # Publish new transactions to Kafka
            self.publish_transactions_to_kafka(new_transactions_df)

            # Get the maximum TID from the processed transactions
            new_last_tid = new_transactions_df.agg({"transaction_id": "max"}).collect()[0][0]

            # Update the last processed TID to Kafka
            self.publish_last_tid_to_kafka(new_last_tid)
        except Exception as e:
            logger.error(f"Error in processing: {e}")

# Main logic
if __name__ == "__main__":
    try:
        logger.info("Starting PostgreSQL-Kafka producer...")
        
        """
        spark = SparkSession.builder \
        .appName("KafkaProducer") \
        .config("spark.sql.debug.maxToStringFields", 1000) \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,"
                "org.postgresql:postgresql:42.5.0") \
        .getOrCreate()
        """

        # Create Spark session
        spark = SparkSession.builder \
        .appName("KafkaProducer") \
        .config("spark.ui.port", "4045") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.sql.streaming.checkpointLocation", "/app/checkpoints/kafka-to-mongodb") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .config("spark.sql.debug.maxToStringFields", 1000) \
        .config("spark.jars",",".join([
        "/opt/spark/jars/postgresql-42.5.0.jar",
        "/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.2.jar",
        "/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.2.jar",
        "/opt/spark/jars/kafka-clients-3.4.1.jar",
        "/opt/spark/jars/jsr305-3.0.0.jar",
        "/opt/spark/jars/commons-pool2-2.11.1.jar",
        "/opt/spark/jars/hadoop-client-runtime-3.3.4.jar",
        "/opt/spark/jars/lz4-java-1.8.0.jar",
        "/opt/spark/jars/snappy-java-1.1.10.5.jar",
        "/opt/spark/jars/slf4j-api-2.0.7.jar",
        "/opt/spark/jars/hadoop-client-api-3.3.4.jar",
        "/opt/spark/jars/commons-logging-1.1.3.jar"
        ])) \
        .getOrCreate()
        
        kafka_bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
        psql_user = os.environ.get('POSTGRES_USER')
        psql_password = os.environ.get('POSTGRES_PASSWORD')
        psql_db = os.environ.get('POSTGRES_DB')
        psql_host = os.environ.get('POSTGRES_HOST')
        

        # PostgreSQL connection properties
        jdbc_url = f"jdbc:postgresql://{psql_host}:5432/{psql_db}"
        jdbc_properties = {
            "user": psql_user,
            "password": psql_password,
            "driver": "org.postgresql.Driver"
        }

        # Initialize PostgreSQL-Kafka producer
        producer = KafkaPostgresProducer(spark, kafka_bootstrap_servers, jdbc_url, jdbc_properties)

        # Start the process of fetching transactions and publishing to Kafka
        producer.process()

        logger.info("PostgreSQL-Kafka producer completed successfully.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if 'spark' in locals():
            spark.stop()