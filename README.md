# DataFlowX: Real-Time Retail Analytics Pipeline

**Repository Name:** [dataflowx-retail-analytics](https://github.com/shreyasgadder/dataflowx-retail-analytics/)

**Description:**  
DataFlowX is a comprehensive real-time retail analytics pipeline that processes and transforms transaction data from a PostgreSQL database using PySpark. The data is streamed to Kafka for message brokering and then consumed via batch processing and stored in MongoDB. All components are orchestrated using Docker containers, ensuring scalable and efficient data handling for enhanced retail insights.

---

## Project Overview

DataFlowX aims to provide a robust solution for real-time retail analytics. It processes transaction data sourced from a PostgreSQL database, transforms it with PySpark, and streams it through Kafka. The data is then consumed via Spark Streaming and stored in MongoDB. This setup allows for efficient and scalable data processing, enabling businesses to gain timely insights into their retail operations.

### Key Features:
- **Data Ingestion**: Reads transaction data from a PostgreSQL database.
- **Data Transformation**: Utilizes PySpark for data transformation and processing.
- **Real-time Streaming**: Streams data to Kafka for real-time data processing.
- **Batch Processing**: Consumes and processes data from Kafka in batch mode using PySpark.
- **Data Storage**: Stores the final transformed data in MongoDB.
- **Dockerized**: All services are containerized using Docker for ease of deployment and scalability.

---

## Installation Instructions

### Prerequisites

- **Docker**: Install Docker to manage containerized services.
- **Docker Compose**: Install Docker Compose


### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dataflowx-retail-analytics.git
   cd dataflowx-retail-analytics
   ```

2. Build and start Docker containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
   Or directly:
   ```bash
   docker-compose up -d --build
   ```

---

## Command Flow

1. **Prepare Data and Run Producers:**
   - Execute `produce_data.bat`:
     - It will prompt you for the filename that needs to be processed.
     - The data from the file is copied to the PostgreSQL table.
     - `producer.py` is then executed to handle the data transformation and streaming.

2. **Run the Consumer:**
   - In a new terminal tab, run:
     ```bash
     docker exec -it python-base python consumer.py
     ```

---

## Usage

### Verify Data

#### PostgreSQL

1. Connect to the PostgreSQL database inside the container:
   ```bash
   docker exec -it postgres psql -U admin -d retail
   ```

2. Import data from a CSV file into the `transactions` table:
   ```sql
   COPY transactions FROM '/csv_mount/data.csv' DELIMITER ',' CSV HEADER;
   ```

3. Retrieve the first 10 rows from the `transactions` table:
   ```sql
   SELECT * FROM transactions LIMIT 10;
   ```

#### MongoDB

1. Connect to the MongoDB shell inside the container:
   ```bash
   docker exec -it mongo mongosh
   ```

2. Switch to the `retail_db` database:
   ```js
   use retail_db
   ```

3. Display all collections in the current database:
   ```js
   show collections
   ```

4. Retrieve all documents in the `transactions` collection with formatted output:
   ```js
   db.transactions.find().pretty()
   ```

5. Find documents with `transaction_id` 1 in the `transactions` collection:
   ```js
   db.transactions.find({transaction_id: 1}).pretty()
   ```

6. Count the number of documents in the `transactions` collection:
   ```js
   db.transactions.count()
   ```

---

## Data Flow Diagram

![Data Flow Diagram](path_to_your_diagram_image)

The diagram visualizes how data moves from PostgreSQL through Spark to Kafka and then consumed via batch processing and stored in MongoDB.

---

## Contributing Guidelines

We welcome contributions to the DataFlowX project! Please follow these guidelines:

- **Fork** the repository and create a new branch for your feature or bug fix.
- **Write** clear, concise commit messages and update documentation as necessary.
- **Submit** a pull request with a detailed description of your changes.

For coding standards, please refer to our [coding guidelines](path_to_your_coding_guidelines).

---

## License Information

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

---

Feel free to adjust the paths, filenames, or commands based on your specific setup and requirements.
