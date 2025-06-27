from influxdb_client import InfluxDBClient, Point, WritePrecision
from dateutil import parser as date_parser
import os

# Configuration via environment variables or fallback defaults
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "your-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sshame")

# Initialize the InfluxDB client
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
)

write_api = client.write_api(write_options=None)

def write_ssh_event(ip, user, timestamp_str, port=None):
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
        if port is not None:
            point.tag("port", str(port))

        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

    except Exception as e:
        print(f"Failed to write event to InfluxDB: {e}")
