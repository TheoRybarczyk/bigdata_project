import requests
import pandas as pd
import json
import os

GRAFANA_USER = os.getenv("GRAFANA_USER")
GRAFANA_PASS = os.getenv("GRAFANA_PASS")
GRAFANA_PORT = os.getenv("GRAFANA_PORT")

print(GRAFANA_USER, GRAFANA_PASS, GRAFANA_PORT)

INFLUXDB_CONT_NAME = os.getenv("INFLUXDB_CONT_NAME")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

INFLUXDB_TOKEN_FILE = "/setup/influxdb_token.txt"
DASHBOARD_FILE = "/setup/dashboard.json"

url = f"http://{GRAFANA_USER}:{GRAFANA_PASS}@localhost:{GRAFANA_PORT}/api/"

headers={"Accept": "application/json",
         "Content-Type": "application/json"}

print("=> => Setting up InfluxDB datasource for Grafana")

token = pd.read_table(INFLUXDB_TOKEN_FILE).iloc[0,2]

response = requests.post(
    url+"datasources",
    headers=headers,
    json={
        "name": "influxdb",
        "type": "influxdb",
        "url": f"http://{INFLUXDB_CONT_NAME}:{INFLUXDB_PORT}",
        "uid": "a58c11ab-8723-4a5d-86c5-112a732a2ba4",
        "access": "proxy",
        "basicAuth": False,
        "jsonData": {
            'defaultBucket': f"{INFLUXDB_BUCKET}",
            'httpMode': 'POST',
            'organization': f"{INFLUXDB_ORG}",
            'version': 'Flux'},
        "secureJsonData": {
            "token": token
        }
    }
)

if response.status_code == 200:
    print(f"data source created")
else:
    print(f"issue during data source creation, returned code {response.status_code}")
    
print("=> => Importing Grafana dashboard")

with open(DASHBOARD_FILE, "r") as f:
    dashboard = json.load(f)

response = requests.post(
    url+"dashboards/db",
    headers=headers,
    json={
        "dashboard": dashboard,
        "folderId": 0,
        "message": "Automatically created.",
        "overwrite": False,
    }
)

if response.status_code == 200:
    print(f"dashboard created")
else:
    print(f"issue during dashboard creation, returned code {response.status_code}")
    
pass