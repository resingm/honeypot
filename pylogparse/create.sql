CREATE TABLE IF NOT EXISTS "dataplane" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sync_ts" TIMESTAMPTZ NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "asn" INT NOT NULL,
    "asname" VARCHAR(255) NOT NULL,
    "category" VARCHAR(16) NOT NULL,
    "ip" INET NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_dataplane_categor_a3f196" ON "dataplane" ("category");

CREATE TABLE IF NOT EXISTS "log" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "origin" VARCHAR(16) NOT NULL,
    "origin_id" INT NOT NULL,
    "sync_ts" TIMESTAMPTZ NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "category" VARCHAR(16) NOT NULL,
    "ip" INET NOT NULL,
    "username" VARCHAR(255) NOT NULL,
    "raw" VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS "idx_log_origin_802b2d" ON "log" ("origin");
CREATE INDEX IF NOT EXISTS "idx_log_categor_456a64" ON "log" ("category");

CREATE TABLE IF NOT EXISTS "ip" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "ip" INET NOT NULL,
    "city" VARCHAR(64) NOT NULL,
    "region" VARCHAR(64) NOT NULL,
    "longitude" DOUBLE PRECISION,
    "latitude" DOUBLE PRECISION,
    "org" VARCHAR(255) NOT NULL,
    "postal" VARCHAR(16) NOT NULL,
    "timezone" VARCHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS "idx_ip_ip" ON "ip" ("ip");
