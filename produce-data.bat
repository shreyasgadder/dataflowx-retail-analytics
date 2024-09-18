@echo off
set /p filename="Enter the CSV file name: "

echo Copying data from /csv_mount/%filename%.csv to the PostgreSQL table...

docker exec -i postgres psql -U admin -d retail -c "COPY transactions FROM '/csv_mount/%filename%.csv' DELIMITER ',' CSV HEADER;"

if %errorlevel% neq 0 (
    echo Failed to copy data from /csv_mount/%filename%.csv.
    exit /b %errorlevel)

echo Data copied successfully. Running producer.py...

docker exec -it python-base python producer.py

if %errorlevel neq 0 (
    echo Failed to run producer.py.
    exit /b %errorlevel%
)

echo Process completed successfully.