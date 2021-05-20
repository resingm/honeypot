#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
#   pyeval
#
# Simple script to evaluate the data in the honeypot database. It summarizes the
# data records and prettyprints it to the console.
#
# The script was written and published
#    by Max Resing <m.resing-1@student.utwente.nl>
#
# ------------------------------------------------------------------------------

from datetime import datetime

import psycopg2
import yacf

from pretty_tables import PrettyTables

CONFIG = "/etc/pylogparse.toml"

# Dates to consider (last date is excluded)
DATES = [
    "2021-05-17",
    "2021-05-18",
    "2021-05-19",
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

HONEYPOTS = [
    ("campus", "1"),
    ("campus", "3"),
    ("campus", "4"),
    ("cloud", "12"),
    ("cloud", "13"),
    ("cloud", "14"),
    ("cloud", "15"),
    ("residential", "6"),
    ("residential", "7"),
    ("residential", "8"),
    ("residential", "9"),
]

CATEGORIES = ["ssh", "telnet", "vnc"]


def _eval_dates(cur, dates):
    """Evaluates the database based on each single date."""
    rows = []

    for d in dates:
        row = [d[0]]

        cur.execute(
            "SELECT COUNT(*) FROM log WHERE timestamp >= %s AND timestamp < %s;",
            (d[1], d[2]),
        )
        count = cur.fetchone()[0]
        row.append(count)

        for c in CATEGORIES:
            cur.execute(
                "SELECT COUNT(*) FROM log WHERE timestamp >= %s AND timestamp < %s AND category=%s;",
                (d[1], d[2], c),
            )
            count = cur.fetchone()
            row += count

        rows.append(row)

        if row[1] == 0:
            # Break early, if no data was logged for some date.
            # This means we have no further data available
            break

    return rows


def _eval_honeypots(cur, honeypots):
    """Summarizes the logging data per honeypot over the entire log range"""
    rows = []

    for h in HONEYPOTS:
        row = [h[0], h[1]]

        cur.execute("SELECT COUNT(*) FROM log WHERE origin=%s AND origin_id=%s", h)
        count = cur.fetchone()[0]
        row.append(count)

        for c in CATEGORIES:
            cur.execute(
                "SELECT COUNT(*) FROM log WHERE origin=%s AND origin_id=%s and CATEGORY=%s",
                (h[0], h[1], c),
            )
            count = cur.fetchone()[0]
            row.append(count)

        rows.append(row)

        if row[1] == 0:
            # Break early, if no data was logged for some date.
            # This means we have no further data available
            break

    return rows


def print_table(title, headers, rows):
    print()
    print("-" * 64)
    print(f"  {title}")
    print()

    tmp = []

    for r in rows:
        tmp.append([f"{x:,}".rjust(13, " ") if isinstance(x, int) else x for x in r])

    print(
        PrettyTables.generate_table(
            headers=headers,
            rows=tmp,
            empty_cell_placeholder="-",
        )
    )
    print()
    print()


def main():
    conf = yacf.Configuration(CONFIG)
    conf.load()

    dbc = psycopg2.connect(conf.get("db.url"))

    with dbc.cursor() as cur:

        rows = []
        dates = [("All", DATES[0], DATES[-1])]
        for i in range(len(DATES) - 1):
            dates.append((DATES[i], DATES[i], DATES[i + 1]))

        ################################
        # Print summary over time
        ################################
        print_table(
            "Overview of login attempts per date",
            ["Date", "Total", "# SSH", "# Telnet", "# VNC"],
            _eval_dates(cur, dates),
        )

        ################################
        # Print summary of each honeypot
        ################################

        rows = []

        print_table(
            "Overview of login attempts per honeypot",
            ["Network", "Honeypot", "Total", "# SSH", "# Telnet", "# VNC"],
            _eval_honeypots(cur, HONEYPOTS),
        )


if __name__ == "__main__":
    main()
