import csv
import psycopg2
import subprocess
import argparse
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def copy_from_file(conn, file_path):
    """Use COPY FROM to load data from the temp CSV file into PostgreSQL."""
    try:
        cursor = conn.cursor()
        logging.info(f"Loading data from {file_path} into PostgreSQL.")
        with open(file_path, 'r') as f:
            cursor.copy_expert("""
            COPY transactions
            FROM STDIN WITH CSV
            """, f)
        conn.commit()
        logging.info("Data successfully loaded into PostgreSQL.")

        # Trigger producer.py after inserting each batch
        logging.info("Triggering producer.py.")
        subprocess.run(['python', 'producer.py'], check=True)
        logging.info("producer.py executed successfully.")
        
    except Exception as e:
        logging.error(f"Error during COPY FROM operation: {e}")
        exit(0)
    finally:
        cursor.close()

def process_csv(file_name, batch_size):
    """Process CSV file and insert data in batches."""
    file_path = os.path.join('/csv_mount', file_name)
    logging.info(f"Starting CSV processing for file: {file_name}")

    psql_user = os.environ.get('POSTGRES_USER')
    psql_password = os.environ.get('POSTGRES_PASSWORD')
    psql_db = os.environ.get('POSTGRES_DB')
    psql_host = os.environ.get('POSTGRES_HOST')

    # Connect to PostgreSQL
    conn = psycopg2.connect(dbname=psql_db, user=psql_user, host=psql_host, password=psql_password)
    
    total_orders_processed = 0
    batch = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            for row in reader:
                batch.append(row)
                total_orders_processed += 1

                if len(batch) == batch_size:
                    # Write batch to temporary file and use COPY FROM
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
                        writer = csv.writer(temp_file)
                        writer.writerows(batch)
                        temp_file_path = temp_file.name

                    logging.info(f"Batch of {batch_size} rows ready. Processing batch.")
                    # Perform bulk insert using COPY FROM
                    copy_from_file(conn, temp_file_path)
                    batch = []
                    os.remove(temp_file_path)

            # Insert remaining rows if any
            if batch:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
                    writer = csv.writer(temp_file)
                    writer.writerows(batch)
                    temp_file_path = temp_file.name

                logging.info(f"Final batch of {len(batch)} rows ready. Processing final batch.")
                # Perform bulk insert using COPY FROM
                copy_from_file(conn, temp_file_path)
                os.remove(temp_file_path)
                
    finally:
        conn.close()
        logging.info(f"Processing complete. Total orders processed: {total_orders_processed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV and insert data into PostgreSQL in batches.')
    parser.add_argument('file_name', type=str, nargs='?', default='data.csv', help='Name of the CSV file (default: data.csv)')
    parser.add_argument('--batch-size', type=int, default=200, help='Number of rows per batch (default: 200)')
    
    args = parser.parse_args()
    process_csv(args.file_name, args.batch_size)
