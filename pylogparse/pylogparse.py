#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
#   pylogparse.py
#
# The script parses and imports those files which are not yet processed and
# entered in the database. One of the dependencies is tortoise-orm. Tortoise-ORM
# does not support the Postgres datatype INET. Thus, it is recommended to run
# the create.sql script manually before first starting this script.
#
# ------------------------------------------------------------------------------

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
LOGLVL = log.DEBUG


class Log(Model):
    id = fields.IntField(pk=True)
    origin = fields.CharField(max_length=16, index=True)
    origin_id = fields.IntField()
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    category = fields.CharField(max_length=16, index=True)
    ip = fields.CharField(max_length=64)
    username = fields.CharField(max_length=255)
    raw = fields.CharField(max_length=255)


class Dataplane(Model):
    id = fields.IntField(pk=True)
    sync_ts = fields.DatetimeField()
    timestamp = fields.DatetimeField()
    asn = fields.IntField()
    asname = fields.CharField(max_length=255)
    category = fields.CharField(max_length=16, index=True)
    ip = fields.CharField(max_length=64)


def get_file_lists(directory: str, import_log: str):
    imported = []

    log.info("Reading import log...")
    if not os.path.exists(import_log):
        log.debug(f"Import log {import_log} does not exist. Creating import log...")
        with open(import_log, "w+") as f:
            f.write(
                "# File includes log files which were already imported into the database\n"
            )

        log.debug(f"Created import log {import_log}")

    with open(import_log, "r") as f:
        imported = f.readlines()
        log.debug(f"Read {len(imported)} lines from {import_log}")

    imported = [x for x in imported if len(x)]
    imported = [x for x in imported if x[0] != "#"]
    imported = [x.replace("\n", "") for x in imported]
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

    search_terms = []

    skip = False

    # Parse category:
    if "sshd" in line:
        skip = "Failed password" not in line
        skip = skip or ("Did not receive ident" in line)
        category = "ssh"

        search_terms += ["Failed password for invalid user "]
        search_terms += ["Failed password for "]

    elif "login[" in line:
        skip = "FAILED LOGIN" not in line
        category = "telnet"

        search_terms += ["' FOR '"]
    elif "linuxvnc" in line:
        skip = "Got connection from" not in line
        category = "vnc"
    else:
        return None

    if skip:
        # If lines do not start with defined phrase, it can be skipped.
        return None

    parts = line.split("]: ")
    if len(parts) <= 1:
        return None

    s = parts[1]

    for term in search_terms:
        # if s.startswith(term):
        if term in s:
            i = s.find(term) + len(term)
            j = i

            # increase i as long as i is not a space or a "'"
            while s[j] not in "' ":
                j += 1

            username = s[i:j]
            break

    parts = line.split(" ")

    # Parse timestamp
    day = int(parts[1])
    month = 5 if parts[0] == "May" else 6
    hour, minute, second = parts[2].split(":")
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    timestamp = datetime(2021, month, day, hour, minute, second)

    # parse IP
    pattern = "(\d{1,3}(\.|-)\d{1,3}(\.|-)\d{1,3}(\.|-)\d{1,3})"
    ip = re.findall(pattern, line)
    # ip = pattern.search(line)
    if ip:
        ip = ip[0]

        if isinstance(ip, tuple):
            ip = ip[0]
    else:
        return None

    # Normalize IP input (alter '-' to '.' and remove leading zeros in octets)
    ip = ip.replace("-", ".")
    ip = ".".join([(x if x == "0" else x.lstrip("0")) for x in ip.split(".")])

    return (timestamp, category, ip, username)


def parse_dataplane_lines(sync_ts, lines):
    recs = []

    for l in lines:
        # Continue on empty line
        if not len(l):
            continue

        # Continue on commented line
        if l[0] == "#":
            continue

        arr = [x.strip(" ") for x in l.split("|")]
        if len(arr) < 5:
            continue

        asn = int(arr[0]) if arr[0].isnumeric() else -1
        asname = arr[1]
        ip = arr[2]
        # Normalize IP string
        ip = ".".join([(x if x == "0" else x.lstrip("0")) for x in ip.split(".")])
        timestamp = datetime.fromisoformat(arr[3])
        category = ""

        if ":" in ip:
            # Skip IPv6 addresses
            continue

        if "ssh" in arr[4]:
            category = "ssh"
        elif "telnet" in arr[4]:
            category = "telnet"
        elif "vnc" in arr[4]:
            category = "vnc"
        else:
            continue

        rec = Dataplane(
            sync_ts=sync_ts,
            timestamp=timestamp,
            asn=asn,
            asname=asname,
            category=category,
            ip=ip,
        )
        recs.append(rec)

    return recs


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
            raw=(l[:250] + "[...]" if len(l) > 255 else l),
        )
        recs.append(rec)

    return recs


async def main():
    # Configure logging
    root = log.getLogger()
    root.setLevel(LOGLVL)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(LOGLVL)
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
        log.error("Details: ", exc_info=e)
        return

    for f in files:
        _f = f.split("/")

        try:
            hp_cat, hp_id, f_name = _f[-3], _f[-2], _f[-1]
            if hp_id == "dataplane":
                hp_cat = hp_id
            else:
                hp_id = int(hp_id)

            lines = []
            with open(f, "r") as _f:
                lines = _f.readlines()

            year, month, day, hour, minute, second = f_name[:-4].split("_")
            year = int(year)
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
            second = int(second)

            sync_ts = datetime(year, month, day, hour, minute, second)

            if hp_cat == "dataplane":
                log.info(f"Processing new file: {f}")
                log.info("Extracting records from dataplane download...")
                records = parse_dataplane_lines(sync_ts, lines)
                log.info(
                    f"Found {len(records)} records in a total of {len(lines)} lines."
                )
                log.info("Inserting records into database...")
                await Dataplane.bulk_create(records, batch_size=500)
                log.info(f"Inserted {len(records)} new records in database.")
            else:
                log.info(f"Processing new file: {f}")
                records = parse_lines(hp_cat, hp_id, sync_ts, lines)
                log.info("Extracting records from log file...")
                log.info(
                    f"Found {len(records)} records in a total of {len(lines)} lines."
                )
                log.info("Inserting records into database...")
                await Log.bulk_create(records, batch_size=500)
                log.info(f"Inserted {len(records)} new records in database.")

            with open(import_log, "a") as _f:
                log.info(f"Save file {f} as processed")
                _f.write(f)
                _f.write("\n")

        except Exception as e:
            log.error(f"Unknown exception: {str(e)}")
            log.error("Details: ", exc_info=e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
