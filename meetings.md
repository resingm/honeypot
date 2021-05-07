
# Meeting 2021-04-30

Campus: 1 Person
Residential homes: 2 People


## Transfer logs

Two options:

1) Logrotate might have a feature to automatically execute a command on log
   roation. That can then execute a script which publishes the data.

2) Setup a CRON job executing a script each night at 2 AM sending the newly
   created log file.


## Data Analysis

Data should be stored in a Postgres database.

In terms of software, either go for plain Python, or alternatively go for
Apache Spark. Pretty sure, Roland would prefer Apache Spark.


## What I need to do

Think about the requirements for the Digital Ocean services. He will create the
VMs for me as well as a server in the DACS group. This server will be used as a
central data storage which operates a Postgres database.

Also send Roland my public SSH key via mail to gain access to the service.


# Meeting 2021-05-07

Campus: 4 People (Neil, Tjeerd, Baris, Dre)
Residential: 5 People, 7 Honeypots (Pim, Jorrit, Stan, Roland, 3x Raffaele)
Cloud: 1 Person (Max)

## Honeypots

The honeypots will operate a regular OpenSSH and Telnetd service which works as
a honeypot. Login attempts will be logged to /var/log/auth.log (SSH) and
/var/log/syslog (Telnet & VNC). The setup scripts are implemented, however, the
scripts to extract the relevant lines from the log files and to transfer them
nightly aren't yet implemented.

## Database

Table structure was presented. Roland suggested two changes:

 * For the IP address, use the Postgres type for IP addresses
 * Store the dataplane data in another table to make joins more efficient

 ## Feedback

 Roland has the feeling I am quite on track and has no worries, that I am aiming
 in the wrong direction. Positive overall feedback so far.

## Data evaluation

It makes sense to start with the data evaluation already on the first or second
day. We are both pretty sure, we will have a decent amount of data already after
a couple of hours.

## Darknet Data

Roland suggested to use the darknet to store a TCP dump of some hours to a day.
We agreed it makes sense to run the TCP dump at the end of the honeypot logging.
It depends a bit on my progress, whether this darknet data will be used or not.


