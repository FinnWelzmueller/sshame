CREATE TABLE IF NOT EXISTS ip_locations (
    ip_from BIGINT,
    ip_to BIGINT,
    country_short VARCHAR(10),
    country_long VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    lat DOUBLE,
    lon DOUBLE
);

LOAD DATA INFILE '/var/lib/mysql-files/geoloc.csv'
INTO TABLE ip_locations
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(ip_from, ip_to, country_short, country_long, region, city, lat, lon);
