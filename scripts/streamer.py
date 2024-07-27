from flask import Flask, request
import pandas as pd
from kafka import KafkaProducer
import threading
import time
import os

KAFKA_BROKER = f"{os.getenv('KAFKA_BROKER_CONT_NAME')}:{os.getenv('KAFKA_BROKER_LISTEN_EXT_PORT')}"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
CSV_FILE_PATH = "/app/data/H_31_latest-2023-2024.csv"
COLUMNS = ["AAAAMMJJHH", "NOM_USUEL", "LAT", "LON", "TN", "TX", "RR1", "DRR1", "FF", "DD", "UN", "UX", "PSTAT", "VV"]
COLUMN_DATE = "AAAAMMJJHH"
STREAMING_TIME_DELTA = os.getenv("STREAMING_TIME_DELTA")

# KAFKA_BROKER = "localhost:9092"
# CSV_FILE_PATH = "../data/H_31_latest-2023-2024.csv"

try:
    t_delta = float(STREAMING_TIME_DELTA)
except:
    t_delta = 0.1

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask app is running.\n'

producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])

import json

def stream_json_to_kafka():
    global t_delta
    while True:
        df = pd.read_csv(CSV_FILE_PATH, delimiter=';')[COLUMNS]
        clean_names = dict(zip(df.columns, [col.strip() for col in df.columns]))
        df = df.rename(clean_names)
        df[COLUMN_DATE] = pd.to_datetime(df[COLUMN_DATE].astype("str"), format="%Y%m%d%H")
        df.sort_values(by=COLUMN_DATE, inplace=True)
        df[COLUMN_DATE] = df[COLUMN_DATE].astype("str") # timestamps are not json serializable
        
        for _, row in df.iterrows():
            row_dict = row.to_dict()

            # Convert row to JSON string
            json_message = json.dumps(row_dict)

            try:
                producer.send(KAFKA_TOPIC, value=json_message.encode('utf-8'))
            except Exception as e:
                print(f"Error in sending meteo message to cluster : {e}")

            time.sleep(t_delta)

@app.route('/start_streaming', methods=['POST'])
def start_streaming():
    global streaming_thread
    streaming_thread = threading.Thread(target=stream_json_to_kafka)
    streaming_thread.start()
    return f"CSV streaming started with streaming time delta = {t_delta}\n"

@app.route('/stop_streaming', methods=['POST'])
def stop_streaming():
    global streaming_thread
    streaming_thread.join()
    return "CSV streaming stopped\n"

@app.route('/time_delta', methods=['POST'])
def time_delta():
    global t_delta
    try:
        t_delta = float(request.form.get("t_delta"))
    except:
        return f"Invalid value received {request.data}: time delta unchanged\n"
    return f"Streaming time delta changed to {t_delta}\n"

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')