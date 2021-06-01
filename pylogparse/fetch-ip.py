#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
#   fetch-ip.py
#
# Query and store IP addresses of the log data in the database. The data is
# queried from ipinfo.io.
#
# ------------------------------------------------------------------------------

import asyncio
import json
import logging as log
import requests
import sys

import psycopg2

from yacf import Configuration

CONFIG = "/etc/pylogparse.toml"
LOGLVL = log.DEBUG


"""
Tortoise Model:

class Ip(Model):
    id = fields.IntField(pk=True)
    ip = fields.CharField(max_length=64)
    city = fields.CharField(max_length=64)
    region = fields.CharField(max_length=64)
    longitude = fields.FloatField()
    latitude = fields.FloatField()
    org = fields.CharField(max_length=255)
    postal = fields.CharField(max_length=16)
    timezone = fields.CharField(max_length=64)
"""


async def main():
    root = log.getLogger()
    root.setLevel(LOGLVL)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(LOGLVL)
    formatter = log.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    log.info(f"Loading configuration {CONFIG}")
    config = Configuration(CONFIG)
    config.load()
    log.info(f"Loaded configuration {CONFIG}")

    db_url = config.get("db.url")
    token = config.get("token")

    try:
        # await Tortoise.init(db_url=db_url, modules={"models": ["__main__"]})
        # log.info("Connection to database established")
        # log.info("Creating database schema...")
        # await Tortoise.generate_schemas()
        # log.info("Created database schema.")

        log.info("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        log.info("Connection to database established.")

        log.info("Querying IP addresses of log...")
        cur.execute("SELECT ip FROM log GROUP BY ip ORDER BY ip;")
        ips = []
        for x in cur.fetchall():
            ips.append(x[0])
        log.info(f"Found {len(ips)} distinct IP addresses in database.")

        log.info("Querying covered IPs from database...")
        cur.execute("SELECT ip FROM ip GROUP BY ip")
        filtered = []
        for x in cur.fetchall():
            filtered.append(x[0])
        log.info(f"Found {len(filtered)} IPs which are already covered.")

        log.info("Filter on uncovered IPs...")
        ips = [x for x in ips if x not in filtered]
        log.info(f"Continue querying geoinformation of {len(ips)} IPs.")

        # r = requests.get(f"http://ipinfo.io/37.201.171.98?token={token}")
        # content = r.json()
        # log.info(type(content))
        # return

        for ip in ips:
            # TODO: Query data from ipinfo.io
            r = requests.get(f"http://ipinfo.io/{ip}?token={token}")
            v = r.json()

            # Parse long & lat
            longitude, latitude = None, None
            if "loc" in v.keys():
                longitude, latitude = v.get("loc").split(",")

            # Insert record into DB
            cur.execute(
                """
                INSERT INTO ip (ip, city, region, longitude, latitude, org, postal, timezone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    ip,
                    v.get("city", ""),
                    v.get("region", ""),
                    longitude,
                    latitude,
                    v.get("org", ""),
                    v.get("postal", ""),
                    v.get("timezone", ""),
                ),
            )
            conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        log.error(f"Unknown execption occured: {str(e)}")
        log.error("Details: ", exc_info=e)
        return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
