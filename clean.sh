HERE=`pwd`
cd docker

docker compose -f docker-compose.yml -f docker-compose_kafka-monitor.yml down
docker volume rm influxVolume
docker image rm \
	influxdb \
	docker-grafana \
	docker-spark-master \
	docker-spark-worker \
	docker-datastream \
	confluentinc/cp-schema-registry:7.4.0 \
	confluentinc/cp-server:7.4.0 \
	confluentinc/cp-zookeeper:7.4.0 \
	confluentinc/cp-enterprise-control-center:7.4.0

cd $HERE
