#!/bin/bash
# wait-for-kafka.sh

host="$1"
shift
cmd="$@"

# Wait until Kafka is available
while ! echo exit | nc -z "$host" 9092; do
    echo "Waiting for Kafka to be ready on myBroker:9092..."
    sleep 5
done

echo "Kafka is up and running!"
exec "$@"
