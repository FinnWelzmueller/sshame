# sshame

This lightweight monitoring-tool detects failed ssh logins on your (Linux-)system and visualizes them in dashboard.

## Software architecture

The **backend** is written in Python. It reads the auth.log file and filters failed ssh logins. The IP, time and username are stored in a **database**, where influxDB is used.
The **dashboard** is done with Grafana. The **deployment** is done in Docker Compose.

## Requirements

- Docker Compose as it is used for the deployment
- Have an .env-file ready with an API Key for the geolocation. It has to be copied in the top folder after cloning. The keyword is GEO_APIKEY.

## Deployment

```bash

git clone https://github.com/FinnWelzmueller/sshame.git
cd sshame
mv <path-to-envfile> .
docker-compose up --build -d
```

## Features

- Detection of failed SSH login attempts
- Aggregated statistics by IP address and username
- Time series of failed logins
- Geolocation of IPs for world map visualization
- Prebuilt Grafana dashboards

## Security Notes

- sshame only monitors failed logins and has no alert system. You are responsible for your server security.
- the usage is only intended for local analysis or internal monitoring.

## Licence

This project is licensed under the MIT License. Contributions and forks are welcome.
