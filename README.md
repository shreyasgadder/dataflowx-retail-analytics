# DataFlowX: Real-Time Retail Analytics Pipeline

## Project Overview

The Retail Sales Application is a robust data processing system designed to handle transaction data from a PostgreSQL database. This application leverages PySpark to process and transform the data, which is then streamed to Kafka for real-time data streaming. The processed data is consumed via PySpark batch processing and stored in MongoDB. All components are orchestrated using Docker containers to ensure seamless integration and deployment.

### Key Features
- **Data Ingestion**: Reads transaction data from a PostgreSQL database.
- **Data Transformation**: Utilizes PySpark for data transformation and processing.
- **Real-time Streaming**: Streams data to Kafka for real-time data processing.
- **Batch Processing**: Consumes and processes data from Kafka in batch mode using PySpark.
- **Data Storage**: Stores the final transformed data in MongoDB.
- **Dockerized**: All services are containerized using Docker for ease of deployment and scalability.

## Installation Instructions

To set up the project locally, follow these steps:

### Prerequisites

1. **PostgreSQL**: Ensure PostgreSQL is installed and running. You will need access to a PostgreSQL database with transaction data.

2. **Apache Kafka**: Install Kafka and start the Kafka server. Ensure the Kafka broker is running and accessible.

3. **Apache Spark**: Install Apache Spark. Ensure Spark is configured to use Kafka and MongoDB connectors.

4. **Docker**: Install Docker to manage containerized services.

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/retail-sales-application.git
   cd retail-sales-application
   ```

2. **Build Docker Images**
   ```bash
   docker-compose build
   ```

3. **Start Services**
   ```bash
   docker-compose up
   ```

4. **Set Environment Variables**
   Create a `.env` file in the root directory with the following content:
   ```env
   POSTGRES_URI=jdbc:postgresql://localhost:5432/your_database
   KAFKA_BROKER=myBroker:9092
   MONGO_URI=mongodb://mongo:27017/retail_db
   ```

## Command Flow

### Data Processing Commands

1. **Ingest Data from PostgreSQL to Kafka**
   ```python
   spark.read \
       .format("jdbc") \
       .option("url", os.environ.get("POSTGRES_URI")) \
       .option("dbtable", "transactions") \
       .load() \
       .write \
       .format("kafka") \
       .option("kafka.bootstrap.servers", os.environ.get("KAFKA_BROKER")) \
       .option("topic", "transactions") \
       .save()
   ```

2. **Transform and Write Data from Kafka to MongoDB**
   ```python
   kafka_df = spark.readStream \
       .format("kafka") \
       .option("kafka.bootstrap.servers", os.environ.get("KAFKA_BROKER")) \
       .option("subscribe", "transactions") \
       .load()

   messages_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
       .select(from_json("json_value", schema).alias("data")) \
       .filter(col("data.transaction_id").isNotNull()) \
       .select("data.*")

   messages_df.writeStream \
       .format("mongodb") \
       .option("spark.mongodb.connection.uri", os.environ.get("MONGO_URI")) \
       .option("spark.mongodb.database", "retail_db") \
       .option("spark.mongodb.collection", "transactions") \
       .outputMode("update") \
       .start()
   ```

## Usage

1. **Run the Application**

   To start the application and process data, execute:
   ```bash
   docker-compose up
   ```

   This will start all necessary services, including PostgreSQL, Kafka, Spark, and MongoDB.

2. **Stop the Application**

   To stop all services, run:
   ```bash
   docker-compose down
   ```

## Data Flow Diagram

![Data Flow Diagram](path/to/data-flow-diagram.png)

## Contributing Guidelines

We welcome contributions to enhance the Retail Sales Application. To contribute, please follow these guidelines:

1. **Fork the Repository**: Create a fork of the repository on GitHub.
2. **Create a Branch**: Create a new branch for your changes.
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make Changes**: Implement your changes and test them.
4. **Submit a Pull Request**: Push your changes and create a pull request on GitHub. Ensure that your changes include appropriate documentation and test cases.

### Coding Standards
- Follow Python's PEP8 style guide.
- Use descriptive commit messages.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

