from influxdb_client import InfluxDBClient, Point, WritePrecision
from dateutil import parser as date_parser
import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# Configuration via environment variables or fallback defaults
INFLUXDB_URL = os.getenv("INFLUXDB_URL", None)
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", None)

# Initialize the InfluxDB client
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org="sshame",
)

write_api = client.write_api()

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
            point.field("lat", float(lat))
        if lon is not None:
            point.field("lon", float(lon))

        # Write to InfluxDB
        write_api.write(bucket="sshame", org="sshame", record=point)
        print(f"Wrote to influxDB: ip: {ip}, user: {user}, timestamp: {timestamp_str}, port: {port}, country: {country_long}, lat: {lat}, lon: {lon}.")

    except Exception as e:
        print(f"Failed to write event to InfluxDB: {e}")

#def write_ssh_event(ip, user, timestamp_str, port=None):
#    print(f"Writing to influx... ip: {ip}, user: {user}, timestamp: {timestamp_str}, port: {port}.")