#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
#   hosts2ip
#
# Since some of the telnet servers rather logged hostnames instead of IPs, we
# had to lookup those from another source (day by day). The results will be
# imported with this script.
#
# ------------------------------------------------------------------------------

import psycopg2
import yacf
import pprint


CONFIG = "/etc/pylogparse.toml"
import_pattern = "/home/max/workspace/ut/thesis/hosts/import/results-xxx.csv"

# Dates to consider (last date is excluded)
dates = [
    "2021-05-17",
    "2021-05-18",
    "2021-05-19",
    "2021-05-20",
    "2021-05-21",
    "2021-05-22",
    "2021-05-23",
    "2021-05-24",
    "2021-05-25",
    "2021-05-26",
    "2021-05-27",
    "2021-05-28",
    "2021-05-29",
    "2021-05-30",
    "2021-05-31",
]


def main():
    # Load configuration
    conf = yacf.Configuration(CONFIG)
    conf.load()

    ips = {}

    # Load input data
    for i in range(len(dates) - 1):
        d = dates[i]

        f = import_pattern.replace("xxx", d)
        with open(f, "r") as _f:
            lines = _f.readlines()

        lines = [l.replace("\n", "") for l in lines]

        if lines[0].startswith("ptr_record,"):
            del lines[0]

        lines = [l.split(",") for l in lines]
        lines = [(l[2], l[3]) for l in lines]

        ips[d] = lines

    pprint.pp(ips)

    dbc = psycopg2.connect(conf.get("db.url"))

    with dbc.cursor() as cur:
        for i in range(len(dates) - 1):
            d = dates[i]
            de = dates[i + 1]

            for (host, ip) in ips[d]:
                print(f"Updating {d} set IP={ip} where host={host}")
                q = f"""
                    UPDATE log
                    SET ip='{ip}'
                    WHERE raw like '%{host}%'
                    AND '{d}' <= timestamp AND timestamp < '{de}';
                """
                cur.execute(q)


if __name__ == "__main__":
    main()
