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

from tortoise.models import Model
from tortoise import Tortoise, fields
from yacf import Configuration


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

async def main():
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


