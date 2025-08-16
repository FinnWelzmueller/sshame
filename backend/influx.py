from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dateutil import parser as date_parser
import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
env_path = os.path.abspath(env_path)
load_dotenv(dotenv_path=env_path)


# Configuration via env-file
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_ADMIN_TOKEN", None)

if not INFLUXDB_URL:
    print("[WARNING] INFLUXDB_URL not set. Defaulting to http://localhost:8086")
else:
    print(f"[DEBUG] Using InfluxDB URL: {INFLUXDB_URL}")
if not INFLUXDB_TOKEN:
    print("[WARNING] INFLUXDB_ADMIN_TOKEN not set. No data will be written to InfluxDB.")
else:
    print("[DEBUG] Found InfluxDB token.")
# Initialize the InfluxDB client
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org="sshame",
)

write_api = client.write_api(write_options=SYNCHRONOUS)

def write_ssh_event(ip, user, timestamp_str, port=None, country_long=None, lat=None, lon=None):
    """
    Writes a single SSH failure event to InfluxDB.

    Parameters:
        ip (str):     Source IP address
        user (str):   Target username
        timestamp_str (str): Timestamp string in ISO 8601 format (incl. timezone)
        port (str|int, optional): SSH port, if available
    """
    try:
        # Parse and convert timestamp to UTC nanosecond-precision format
        timestamp = date_parser.isoparse(timestamp_str).astimezone().astimezone(tz=None)

        # Create the data point
        point = (
            Point("ssh_fail")
            .tag("ip", ip)
            .tag("user", user)
            .field("event", 1)  # Just a marker field; count happens in Grafana
            .time(timestamp, WritePrecision.NS)
        )

        # Optionally include port tag
        if port:
            point.tag("port", str(port))
        if country_long:
            point.tag("country", country_long)
        if lat is not None:
            point.field("latitude", float(lat))
        if lon is not None:
            point.field("longitude", float(lon))

        # Write to InfluxDB
        write_api.write(bucket="sshame", org="sshame", record=point)
        print(f"[DEBUG] Wrote to influxDB: ip: {ip}, user: {user}, timestamp: {timestamp_str}, port: {port}, country: {country_long}, lat: {lat}, lon: {lon}.")

    except Exception as e:
        print(f"[ERROR] Failed to write event to InfluxDB: {e}")

#def write_ssh_event(ip, user, timestamp_str, port=None):
#    print(f"Writing to influx... ip: {ip}, user: {user}, timestamp: {timestamp_str}, port: {port}.")