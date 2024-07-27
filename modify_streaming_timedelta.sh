source settings.sh
docker exec -it $DATASTREAM_CONT_NAME curl -X POST -d "t_delta=$1" http://$DATASTREAM_CONT_NAME:$DATASTREAM_FLASK_PORT/time_delta

