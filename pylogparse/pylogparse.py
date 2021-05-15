#!/usr/bin/env python3

import glob
import logging
import os
import re

from datetime import datetime

from tortoise.models import Model
from tortoise import Tortoise, fields
from yacf import Configuration

CONFIG = "/etc/pylogparse.toml"

log = logging.getLogger(__name__)


class LogRecord(Model):
    id = fields.IntField(pk=True)
    origin = fields.CharField(max_length=16)
    origin_id = fields.IntField()
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    category = fields.CharField(max_length=16)
    ip = fields.IntField()
    username = fields.CharField(max_length=32)


class DataplaneRecord(Model):
    id = fields.IntField(pk=True)
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    asn = fields.IntField()
    asname = fields.CharField(max_length=255)
    category = fields.CharField(max_length=16)
    ip = fields.IntField()


def get_file_lists(directory: str, import_log: str):
    imported = []

    log.info("Reading import log...")
    if not os.path.exists(import_log):
        log.debug(f"Import log {import_log} does not exist. Creating import log...")
        with open(import_log, "w"):
            pass
        log.debug(f"Created import log {import_log}")

    with open(import_log, "r") as f:
        imported = f.readlines()
        log.debug(f"Read {len(imported)} lines from {import_log}")

    imported = [x for x in imported if len(x)]
    imported = [x for x in imported if x[0] != "#"]
    log.info(f"Read import log. Registered {len(imported)} files as already imported.")

    log.info("Checking for new files...")

    if not directory.endswith("/*"):
        directory += "/*"

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

def parse_line():
    timestamp = None
    category = ""
    ip = ""
    username = ""

    # Parse category:
    if "sshd" in line:
        category = "ssh"
    elif "telnetd" in line or "login" in line:
        category = "telnet"
    elif "linuxvnc":
        category = "vnc"
    else:
        return None

    # Parse timestamp
    split = l.split(" ")
    day = split[1]
    month = 5 if split[0] == "May" else 6
    hour, minute, second = split[2].split(':')
    timestamp = datetime(2021, month, day, hour, minute, second)

    # parse IP
    pattern = re.compoile(r'(\d{1,3}\.\d{1.3}\.\d{1,3}\.\d{1,3})')
    ip = pattern.search(l)
    if len(ip):
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

        rec = LogRecord(
            origin=hp_cat,
            origin_id=hp_id,
            sync_ts=sync_ts,
            timestamp=timestamp,
            category=category,
            ip=ip,
            username=username,
        )
        recs.

    return recs


async def main():
    global log
    log = logging.getLogger(__name__)

    log.debug(f"Loading configuration {CONFIG}...")
    config = Configuration(CONFIG)
    log.debug(f"Loaded configuration {CONFIG}")

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

    for f in files:
        _f = f.split("/")
        hp_cat, hp_id, f_name = _f[-3], _f[-2], _f[-1]

        lines = []
        with open(f, "r") as _f:
            lines = _f.readlines()

        try:
            # TODO: Load sync_ts from timestamp
            year, month, day, hour, minute, second = f_name[:-4].split("_")
            sync_ts = datetime(year, month, day, hour, minute, second)
            records = parse_lines(hp_cat, hp_id, sync_ts, lines)
            created = await LogRecord.bulk_create(records, batch_size=500)

        except Exception as e:
            log.error(f"Unknown exception: {str(e)}")
            log.debug("Details: ", exc_info=e)


if __name__ == "__main__":
    await main()
