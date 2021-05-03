# Honeypot Research

The repository includes code snipptes & software which I wrote while working on
my Bachelor thesis.


## Log Data

The logging data of the honeypots will be stored in a central database. Also the
ground-truth data of dataplane.org will be stored. The data set just stores the
kind of information which is required to answer the research questions of the
proposal. The only table in the database will have the following data fields:

```
id        : serial,
sync_ts   : datetime,
origin    : varchar ('dataplane' | 'residential' | 'campus' | 'cloud'),
origin_id : varchar
timestamp : datetime
ip        : integer
category  : varchar ('ssh' | 'telnet' | 'vnc')
```

Most of the data fields should be clear by the name. The `sync_ts` is the
timestamp when the data was obtained, e.g. the moment when the `dataplane.org`
data feeds were accessed or the moment when the honeypot synchronized the data.

The `origin` is the category of the honeypot. The `origin_id` is a unique id
which identifies the honeypot which has logged the record. `timestamp` is the
moment the honeypot logged the record. In case of the dataplane data, it is the
`last_seen` field.

