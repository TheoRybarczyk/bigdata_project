source settings.sh
docker exec -it $DATASTREAM_CONT_NAME curl -X POST http://$DATASTREAM_CONT_NAME:$DATASTREAM_FLASK_PORT/start_streaming

