# Honeypot Research

The repository includes code snipptes & software which I wrote while working on
my Bachelor thesis.

## Note

The scripts & data of this repository are not aimed to be production ready. They
are the result of a quick solution for a given problem statement. The code is
supposed to do one thing and to do it well: Run. It is far from perfect, not
optimized on performance and neither well documented. The code is the result of
quick and dirty solutions to get results quickly.


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
ip        : inet
username  : varchar
raw       : varchar(255)
```

**DataplaneRecord:**

```
id        : serial
sync_ts   : datetime
timestamp : datetime
asn       : integer
asname    : varchar
category  : varchar ('ssh' | 'telnet' | 'vnc')
ip        : inet
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


## TODOs

* ~~Fetch dataplane.org data~~
* ~~Extract username from Telnet & SSH logs~~
* ~~Import log data into database~~
* ~~Setup cron job to change log data ownership~~
* ~~Setup cron job to fetch data and store in home lab~~


