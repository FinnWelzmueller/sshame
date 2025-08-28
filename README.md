# sshame

This lightweight monitoring-tool detects failed ssh logins on your (Linux-)system and visualizes them in dashboard.

## Software architecture

The **backend** is written in Python. It reads the auth.log file and filters failed ssh logins based on the common keywords ("failed password").
The user, IPv4, port and timestamp is extracted from the line and the IP is searched in the geolocation **database**. As a database, a MySQL database is used. The country, latitude and longitude are extracted if the IP is found in the database. All entries are then written into another table of the database.  
The **dashboard** is done with Grafana. It just reads the written entries from the MySQL database. The **deployment** is done in Docker Compose.

## Requirements

- Docker Compose as it is used for the deployment
- Have a completed .env-file ready, similar to the example.  
- Have a csv-file for the geolocation table ready. The project is tailored to the csv-files from [IP2Location](https://lite.ip2location.com/database/db5-ip-country-region-city-latitude-longitude). You can use other files too but it has to have the following columns (in this order, enclosed in ""):  
  - Startingpoint of the IPv4 interval. The IPv4-format has to be encoded in int-format
  - Endpoint of the IPv4 interval. The IPv4-format has to be encoded in int-format
  - The country code
  - The country name
  - The region name
  - The city name
  - The latitude
  - The longitude

## Deployment

```bash

git clone https://github.com/FinnWelzmueller/sshame.git
cd sshame
mv <path-to-.env-example> ./.env
mv <path-to-csvfile> ./backend/mysql/init/
docker-compose up --build -d
```

The Grafana admin console is available port 3001, the MySQL database at port 3306. Please note that it might take some time until the geolocation table is set up. An available Grafana admin console shows that the setup has finished. Log into the console with the credentials from the .env file, navigate to your dashboard and publish it externally (if wanted). The created link can be handed to your proxy of choice for forwarding.

## Features

- Detection of failed SSH login attempts
- Aggregated statistics by IP address and username, country and port
- Geolocation of the IP address
- Time series of failed logins
- Prebuilt Grafana dashboards

## Security Notes

- sshame only monitors failed logins and has no alert system. You are responsible for your server security.
- the usage is only intended for local analysis or internal monitoring.
- the geolocation is rather a fun feature then a proper positioning. IPs are subject to changes and the use of virtual private networks (common standard in this domain) disguises the proper location of the attacker.

## Licence

This project is licensed under the MIT License. Contributions and forks are welcome.
