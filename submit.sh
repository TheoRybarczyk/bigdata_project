source settings.sh
docker exec -it $SPARK_MASTER_CONT_NAME spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master spark://$SPARK_MASTER_CONT_NAME:$SPARK_MASTER_SERV_PORT spark_app.py
