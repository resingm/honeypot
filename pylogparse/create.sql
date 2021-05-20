CREATE TABLE IF NOT EXISTS "dataplane" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sync_ts" TIMESTAMPTZ NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "asn" INT NOT NULL,
    "asname" VARCHAR(255) NOT NULL,
    "category" VARCHAR(16) NOT NULL,
    "ip" INET NOT NULL
);
CREATE TABLE IF NOT EXISTS "log" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "origin" VARCHAR(16) NOT NULL,
    "origin_id" INT NOT NULL,
    "sync_ts" TIMESTAMPTZ NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "category" VARCHAR(16) NOT NULL,
    "ip" INET NOT NULL,
    "username" VARCHAR(32) NOT NULL,
    "raw" VARCHAR(255) NOT NULL
);
