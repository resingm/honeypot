# Honeypot Research

The repository includes code snipptes & software which I wrote while working on
my Bachelor thesis.


## Log Data

The logging data of the honeypots will be stored in a central database. Also the
ground-truth data of dataplane.org will be stored. The data set just stores the
kind of information which is required to answer the research questions of the
proposal. There will be two tables in the database as described below:

**LogRecord:**

```
id        : serial
origin    : varchar ('residential' | 'campus' | 'cloud')
origin_id : integer
sync_ts   : datetime
timestamp : datetime
category  : varchar ('ssh' | 'telnet' | 'vnc')
ip        : integer
username  : varchar
```

**DataplaneRecord:**

```
id        : serial
sync_ts   : datetime
timestamp : datetime
asn       : integer
asname    : varchar
category  : varchar ('ssh' | 'telnet' | 'vnc')
ip        : integer
```

Most of the data fields should be clear by the name. The `sync_ts` is the
timestamp when the data was obtained, e.g. the moment when the `dataplane.org`
data feeds were accessed or the moment when the honeypot synchronized the data.

The `origin` is the category of the honeypot. The `origin_id` is a unique id
which identifies the honeypot which has logged the record. `timestamp` is the
moment the honeypot logged the record. In case of the dataplane data, it is the
`last_seen` field.


## Honeypots

Check `config/README.md` for details regarding the honeypots.

