# DataFlowX: Real-Time Retail Analytics Pipeline

---
https://github.com/shreyasgadder/dataflowx-retail-analytics/blob/main/README.md#testing-and-debugging-commands
## Table of Contents

1. [Project Overview](#project-overview)
2. [Data Flow Diagram](#data-flow-diagram)
3. [Folder Structure](#folder-structure)
4. [Installation Instructions](#installation-instructions)
5. [Command Flow](#command-flow)
6. [Usage](#usage)
7. [Testing And Debugging Commands](#testing-and-debugging-commands)
8. [Contributing Guidelines](#contributing-guidelines)
9. [License Information](#license-information)

## Project Overview

**DataFlowX** offers a powerful solution for real-time retail analytics. This application efficiently manages and transforms transaction data from PostgreSQL to MongoDB, leveraging Apache Kafka and PySpark. It showcases a comprehensive data pipeline, encompassing data ingestion, transformation, and storage—all within Docker containers. Transaction data flows from PostgreSQL to Kafka for message brokering, then is processed and transformed by Spark Streaming, and finally stored in MongoDB. This architecture ensures scalable and efficient data processing, empowering businesses to swiftly derive actionable insights into their retail operations.

### Key Features:
- **Data Ingestion**: Reads transaction data from a PostgreSQL database.
- **Data Transformation**: Utilizes PySpark for data transformation and processing.
- **Real-time Streaming**: Streams data to Kafka for real-time data processing.
- **Batch Processing**: Consumes and processes data from Kafka in batch mode using PySpark.
- **Data Storage**: Stores the final transformed data in MongoDB.
- **Dockerized**: All services are containerized using Docker for ease of deployment and scalability.
- **Schema Registry**: The schema registry is set up for managing and evolving Kafka message schemas.
- **Control Center UI**: Kafka Topics and Consumer Groups, Kafka metrics - including topic throughput, consumer lag, and schema compatibility, can be monitored via the Control Center.

---

## Data Flow Diagram

![Data Flow Diagram](path_to_your_diagram_image)

The diagram visualizes how data moves from PostgreSQL through Spark to Kafka and then consumed via batch processing and stored in MongoDB.

---

## Folder Structure

```plaintext
.
├── docker-compose.yaml             # Docker Compose configuration file for the entire application
├── Dockerfile.pyspark              # Dockerfile for generaing python-base image
├── init-mongo.js                   # MongoDB initialization script
├── init.sql                        # SQL script for initializing PostgreSQL database
├── produce-data.bat                # Batch script for data production
├── requirements.txt                # Python dependencies required for the project
├── wait-for-kafka.sh               # Script to ensure Kafka is up and running before starting other services
├── pyspark/                        # Directory containing PySpark scripts
│   ├── consumer.py                 # PySpark consumer script
│   ├── place_order.py              # Script to simulate real-time order placement
│   ├── producer.py                 # PySpark producer script
│   ├── test_mongo_connection.py    # Script to test MongoDB connection
└── superstore_sales/               # Directory containing CSV data files
    ├── data.csv                    # Full CSV dataset
    ├── batch1.csv                  # Batch 1 of CSV data
    ├── batch2.csv                  # Batch 2 of CSV data
    ├               
    ├── batch9.csv                  # Batch 9 of CSV data
    └── batch10.csv                 # Batch 10 of CSV data
```

---

## Installation Instructions

### Prerequisites

- **Docker**: Install Docker to manage containerized services.
- **Docker Compose**: Install Docker Compose


### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/shreyasgadder/dataflowx-retail-analytics.git
   cd dataflowx-retail-analytics
   ```

2. Build and start Docker containers:
   ```bash
   docker-compose pull
   docker-compose build
   docker-compose up -d
   ```
   Or directly:
   ```bash
   docker-compose up -d --build
   ```

3. **Access Confluent Control Center UI:**

   Navigate to [http://localhost:9021](http://localhost:9021) to monitor Kafka metrics and operations.

---

## Command Flow

### Initial Setup

1. **Check if Kafka is up and running and topics are created:**
   ```bash
   docker logs -f init-kafka
   ```

2. **Data Production:**

   You can either process data in batches or process the entire file at once.

   > The `superstore_sales` folder contains `data.csv` with the full dataset or `batch1.csv`, `batch2.csv`, ..., `batch10.csv`, which are subsets of `data.csv`.
   > In **Option 1**, these batch files can be processed individually, while in **Option 2**, they can be used for quicker execution.

   **Option 1: Process data using `produce_data.bat`:**
   - Execute `produce_data.bat`:
     - It will prompt you for the filename that needs to be processed.
     - The data from the file is copied to the PostgreSQL table.
     - `producer.py` is then executed to handle the data production to Kafka.
   
   **Option 2 (Recommended): Process data in batches using `place_order.py`:**
   - Run the following command to process the data file in batches:
     ```bash
     docker exec -it python-base python place_order.py file.csv --batch-size 500
     ```
     - `file.csv` and `batch-size` are optional. The default values are `data.csv` and `200` respectively.
     - Keeps on placing orders and calling `producer.py` mimicking real-time order placement scenario
    
3. **Data Consumption:**
   1.  **[Optional] Verify the connection to MongoDB before consuming data:**
       - Run a quick test to ensure MongoDB is connected properly:
        ```bash
        docker exec -it python-base python test_mongo_connection.py
        ```
   2. **Run the Consumer:**
       - In a new terminal tab, run the consumer to process and transform the data and insert in MongoDB:
        ```bash
        docker exec -it python-base python consumer.py
        ```

### Verifying Data

After running the consumer, verify that the data has been transferred and transformed correctly.

#### PostgreSQL

1. Connect to PostgreSQL:
   ```bash
   docker exec -it postgres psql -U admin -d retail
   ```

2. View the first 10 rows of the `transactions` table:
   ```sql
   SELECT * FROM transactions LIMIT 10;
   ```

#### MongoDB

1. Connect to the MongoDB shell:
   ```bash
   docker exec -it mongo mongosh
   ```

2. Switch to the `retail_db` database:
   ```js
   use retail_db
   ```

3. Display all collections in the database:
   ```js
   show collections
   ```

4. View transformed data in the `transactions` collection:
   ```js
   db.transactions.find().pretty()
   ```

5. Count documents in the `transactions` collection:
   ```js
   db.transactions.countDocuments()
   ```

6. Find documents with specific `transaction_id` in the `transactions` collection:
   ```js
   db.transactions.find({transaction_id: 1}).pretty()
   ```
---

## Testing and Debugging Commands

- **Stop and Remove Containers:**

  ```bash
  docker-compose down -v
  ```

- **Prune Docker System:**

  ```bash
  docker system prune -a --volumes
  ```

- **List Docker Containers:**

  ```bash
  docker ps -a
  ```

- **List Kafka Topics:**

  ```bash
  docker exec -it myBroker kafka-topics --list --bootstrap-server myBroker:9092
  ```

- **Describe Kafka Topics:**

  ```bash
  docker exec -it myBroker kafka-topics --describe --topic transactions --bootstrap-server myBroker:9092
  docker exec -it myBroker kafka-topics --describe --topic last_tid_topic --bootstrap-server myBroker:9092
  ```

- **Consume Kafka Messages:**

  ```bash
  docker exec -it myBroker kafka-console-consumer --bootstrap-server myBroker:9092 --topic transactions --from-beginning
  ```

- **Inspect Docker Network:**

  ```bash
  docker network inspect super_store_nw
  ```

---

## Contributing Guidelines

We welcome contributions to the DataFlowX project! Please follow these guidelines:

1. **Fork the Repository:**
   - Create a personal copy of the repository on GitHub.

2. **Clone Your Fork:**
   - `git clone <your-fork-url>`

3. **Create a Branch:**
   - `git checkout -b <your-branch-name>`

4. **Make Changes:**
   - Implement your changes and test them.

5. **Push Changes:**
   - `git add .`
   - `git commit -m "Describe your changes"`
   - `git push origin <your-branch-name>`

6. **Submit a Pull Request:**
   - Go to the repository on GitHub and create a new pull request from your branch with a detailed description of your changes.

For coding standards, please refer to our [coding guidelines](path_to_your_coding_guidelines).

---

## License Information

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

---

