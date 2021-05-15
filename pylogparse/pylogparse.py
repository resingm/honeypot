#!/usr/bin/env python3

import asyncio
import glob
import logging as log
import os
import re
import sys

from datetime import datetime

from tortoise.models import Model
from tortoise import Tortoise, fields
from yacf import Configuration

CONFIG = "/etc/pylogparse.toml"


class Log(Model):
    id = fields.IntField(pk=True)
    origin = fields.CharField(max_length=16)
    origin_id = fields.IntField()
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    category = fields.CharField(max_length=16)
    ip = fields.CharField(max_length=16)
    username = fields.CharField(max_length=32)


class Dataplane(Model):
    id = fields.IntField(pk=True)
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    asn = fields.IntField()
    asname = fields.CharField(max_length=255)
    category = fields.CharField(max_length=16)
    ip = fields.CharField(max_length=16)


def get_file_lists(directory: str, import_log: str):
    imported = []

    log.info("Reading import log...")
    if not os.path.exists(import_log):
        log.debug(f"Import log {import_log} does not exist. Creating import log...")
        with open(import_log, "w+") as f:
            f.write(
                "# File includes log files which were already imported into the database"
            )

        log.debug(f"Created import log {import_log}")

    with open(import_log, "r") as f:
        imported = f.readlines()
        log.debug(f"Read {len(imported)} lines from {import_log}")

    imported = [x for x in imported if len(x)]
    imported = [x for x in imported if x[0] != "#"]
    log.info(f"Read import log. Registered {len(imported)} files as already imported.")

    log.info("Checking for new files...")

    if not directory.endswith("/**"):
        directory += "/**"

    files = glob.glob(directory, recursive=True)
    log.debug(f"Found {len(files)} entries in {directory}.")
    files = [x for x in files if x.endswith(".log")]
    log.debug(f"Found {len(files)} log files.")
    files = [x for x in files if x not in imported]
    log.info(f"Found {len(files)} files to be imported.")

    return imported, files


async def connect_db(db_url):
    db = db_url.split("@")

    log.debug(f"Connecting to database {db[1]}...")
    await Tortoise.init(db_url=db_url, modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()
    log.debug(f"Connected to database {db[1]}.")


def parse_line(line):
    timestamp = None
    category = ""
    ip = ""
    username = ""

    # Parse category:
    if "sshd" in line:
        category = "ssh"
    elif "telnetd" in line or "login" in line:
        category = "telnet"
    elif "linuxvnc" in line:
        category = "vnc"
    else:
        return None

    # Parse timestamp
    split = line.split(" ")
    day = int(split[1])
    month = 5 if split[0] == "May" else 6
    hour, minute, second = split[2].split(":")
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    timestamp = datetime(2021, month, day, hour, minute, second)

    # parse IP
    # pattern = re.compile(r"\d{1,3}\.\d{1.3}\.\d{1,3}\.\d{1,3}")
    pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    ip = re.findall(pattern, line)
    # ip = pattern.search(line)
    if ip:
        ip = ip[0]
    else:
        return None

    # TODO: Try to parse the username
    username = ""
    return (timestamp, category, ip, username)


def parse_lines(hp_cat, hp_id, sync_ts, lines):
    recs = []

    for l in lines:

        values = parse_line(l)
        if values is None:
            continue

        (timestamp, category, ip, username) = values

        rec = Log(
            origin=hp_cat,
            origin_id=hp_id,
            sync_ts=sync_ts,
            timestamp=timestamp,
            category=category,
            ip=ip,
            username=username,
        )
        recs.append(rec)

    return recs


async def main():
    # Configure logging
    root = log.getLogger()
    root.setLevel(log.DEBUG)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.DEBUG)
    formatter = log.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    log.info(f"Loading configuration {CONFIG}...")
    config = Configuration(CONFIG)
    config.load()
    log.info(f"Loaded configuration {CONFIG}")

    # Configuration parameters
    directory = config.get("directory")
    import_log = config.get("import_log")
    db_url = config.get("db.url")

    imported, files = get_file_lists(directory, import_log)

    try:
        await connect_db(db_url)
    except Exception as e:
        log.error(f"Unknown exception occured: {str(e)}")
        log.debug("Details: ", exc_info=e)
        return

    for f in files:
        _f = f.split("/")

        try:
            hp_cat, hp_id, f_name = _f[-3], int(_f[-2]), _f[-1]

            lines = []
            with open(f, "r") as _f:
                lines = _f.readlines()

            # TODO: Load sync_ts from timestamp
            year, month, day, hour, minute, second = f_name[:-4].split("_")
            year = int(year)
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
            second = int(second)

            sync_ts = datetime(year, month, day, hour, minute, second)
            records = parse_lines(hp_cat, hp_id, sync_ts, lines)
            created = await Log.bulk_create(records, batch_size=500)

        except Exception as e:
            log.error(f"Unknown exception: {str(e)}")
            log.debug("Details: ", exc_info=e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
