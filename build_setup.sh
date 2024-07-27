source settings.sh

HERE=`pwd`
cd docker

# Build images and run containers - detached mode
if [ $KAFKA_MONITOR -eq 1 ]
then
	docker compose -f docker-compose.yml -f docker-compose_kafka-monitor.yml up --build --force-recreate -d
else
	docker compose up --build --force-recreate -d
fi

# Wait for the server to actually run
echo "=> Please wait for InfluxDB first setup..."
sleep 5s

# Perform first InfluxDB setup
docker exec -it $INFLUXDB_CONT_NAME influx setup \
	--host http://$HOST:$INFLUXDB_PORT \
	-o $INFLUXDB_ORG \
	-u $INFLUXDB_USER \
	-p $INFLUXDB_PASS \
	-b $INFLUXDB_BUCKET \
	-f

echo "=> Sending InfluxDB api token to Grafana and Spark master containers..."

# Write token on host
docker compose exec -i $INFLUXDB_CONT_NAME \
	influx auth ls > influxdb_token.txt

# Send token to grafana container
docker cp influxdb_token.txt $GRAFANA_CONT_NAME:/setup

# Send token to grafana container
docker cp influxdb_token.txt $SPARK_MASTER_CONT_NAME:/opt/bitnami/spark

# Grafana setup with python script
docker exec -i $GRAFANA_CONT_NAME \
	python3 /setup/grafana_setup.py

cd $HERE
