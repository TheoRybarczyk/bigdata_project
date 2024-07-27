KAFKA_MONITOR=1 # 1: activate kafka schema-registry and control-center

export HOST=localhost

export DATASTREAM_CONT_NAME=datastream
export DATASTREAM_FLASK_PORT=5000 #default=5000
export STREAMING_TIME_DELTA=0.05
export KAFKA_TOPIC=meteo

export KAFKA_ZOOKPR_CONT_NAME=zookeeper
export KAFKA_ZOOKPR_PORT=2181 #default=2181

export KAFKA_BROKER_CONT_NAME=broker
export KAFKA_BROKER_LISTEN_EXT_PORT=29092 #default=29092
export KAFKA_BROKER_LISTEN_CLIENT_PORT=9092 #default=9092
export KAFKA_BROKER_JMX_PORT=9101 #default=9101

export KAFKA_SCHREG_CONT_NAME=schema-registry
export KAFKA_SCHREG_PORT=8081 #default=8081

export KAFKA_CC_CONT_NAME=control-center
export KAFKA_CC_PORT=9021 #default=9021

export SPARK_MASTER_CONT_NAME=spark-master
export SPARK_MASTER_SERV_PORT=7077 #default=7077
export SPARK_MASTER_WEBUI_PORT=8080 #default=8080

#export SPARK_WORKER_CONT_NAME=spark-worker
export SPARK_WORKER_NUMBER=2

export INFLUXDB_CONT_NAME=influxdb
export INFLUXDB_PORT=8086 #default=8086
export INFLUXDB_ORG=valdom
export INFLUXDB_USER=admin
export INFLUXDB_PASS=adminvaldom
export INFLUXDB_BUCKET=meteo

export GRAFANA_CONT_NAME=grafana
export GRAFANA_PORT=3000 #default=3000
export GRAFANA_USER=admin # do not change
export GRAFANA_PASS=admin # do not change

