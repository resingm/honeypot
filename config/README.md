# README

When you read this, you probably agreed to participate in my research, which
requires me to operate a bunch of honeypots in different environments, e.g.
residential areas, cloud environments or campus networks. First of all, thank
you for your participation!

This document aims to explain what happens on your device/VM and elaborates on
the software which is used. All honeypots are so-called low-interaction
honeypots. A low-interaction honeypot gives the attacker very little attacking
surface, which makes them a secure choice to operate. Low-interaction means, the
honeypot will provide an endpoint but does not allow the attacker to gain access
to the system. This kind of honeypot is suitable for this research, since I
just need to log the requesting IP addresses. I am not interested in any other
kind of information.


## Requirements

Operating a honeypot requires a few things. Firstly, the device or VM should run
on a Debian-based system. Debian, Ubuntu or Raspberry OS are great candidates.
Debian was chosen, since it is one of the most widespread operating system which
means it can run on embedded devices/Raspberry Pis as well as in a cloud VPS.
This makes it a suitable choice.

Next, your Internet service provider should provide you a public IPv4. There is
no need to have a static IPv4 but it should be at least publicly routable to
ensure scanning activity can reach your internet-exposed router endpoint.

Furthermore, it is crucial to configure port forwarding in your router. Make
sure the device on which the honeypot is operating has a static IP assigned by
your routers DHCP server. Afterwards you can setup the port forwarding. Your
router need to port-forward the given ports to the honeypot:

```
  Router Port   22 - Default SSH port
  Router Port   23 - Default Telnet port
  Router Port 5900 - Default VNC port
```

If you need help in setting up the port forwarding or if you are not sure if you
match all requirements, do not hesitate to contact me.


## Setup

To setup the honeypot, just download the setup script:

```
curl -o $HOME/setup-debian-hp.sh https://static.maxresing.de/pub/setup-debian-hp.sh
```

After downloading the script, execute it with super-user permission:

```
sudo bash $HOME/setup-debian-hp.sh
```

The script will ask for some input in which you have to enter the information
which I provide to you. Each honeypot will be identified by a unique ID and a
category in which the honeypot operates. In your case it will be either `campus`
or `residential`.

The setup script will download and replace existing configuration files. Before
doing so, the configuration files are backed up and will be restored with the
help of the `remove-debian-hp.sh` script.


## Security Essentials

The details of the security essentials are explained in the software section.
This is just an overview of the steps you definitely need to follow:

 * Do NOT use default credentials for your system ; Chose a secure password!
 * SSH will operate on the default port 22
 * Do NOT use Telnet to login ; Telnet transmits passwords in plain text
 * Optionally: Increase security of your SSH server to just allow specific users


## Software

The script sets up honeypots based on well-established software which you are
probably already familiar with.


### SSH

A regular OpenSSH server is used as the SSH honeypot. It prohibits root access
but allows password authentication. Therefore, it is important to use a strong
username/password combination. The SSH is configured such that it allows
password authentication. SSH promotes different login options to the connecting
SSH client. Thus, this option should be enabled to propose being a potential
target for a the scanners. The package includes a systemd unit file, which is
enabled during the setup.

SSH is one of the most common services to login to a machine remotely. It was
designed with the intent to replace the insecure telnet protocol.

Scanners/attackers will try to login to the SSH server by trying combinations of
common usernames and passwords. Therefore, it is essential to have a strong
password.

The default SSH port is 22. The installed Debian package is `openssh-server`.
The SSH server logs to `/var/log/auth.log`


### Telnet


The regular `telnetd` implementation of the `inetutils` is used. The service is
still maintained and well tested. `telnetd` runs on top of the `inetd` daemon.
The package includes a systemd unit file, which is enabled during the setup.

Telnet transmits the username and password in plaintext over the network. This
makes it an insecure option per se. I recommend it to not use it, even if it is
just in your home network.

Scanners/Attackers will try to login to the Telnet server by trying combinations
of common usernames and passwords. Therefore, it is essential to have a strong
password.

The default telnet port is 23. The installed Debian package is
`inetutils-telnetd`. The inetd server logs to `/var/log/syslog`.


### VNC

The chosen VNC server for this research is `vncterm`. Since most honeypots will
operate on systems without an X server, the options were limited. `vncterm` is
a VNC server build on top of the [libvncserver](http://libvnc.github.io/) lib.
The server will serve one TTY session via VNC on port 5900. The package does not
include a systemd unit file, thus I provide a
[unit file](https://static.maxresing.de/pub/vncservice) myself.

VNC provides an authentication mechanism by design. This means, it does not rely
on the regular authentication which Linux has implemented. By default `vncterm`
does not require a password. Since this is more than insecure, when exposing it
to the internet, the systemd file is setup such that it generates a strong and
random password on the startup of the service.

The password has a length of 256 bytes (base64 encoded). A password of this
length should be complex enough. According to
[howsecureismypassword.net](https://howsecureismypassword.net/), a brute-force
attack would require "51 duovigintillion ducentillion years" to crack it.
If you are still paranoid, change the password just as you want in the unit
file:

```
/etc/systemd/system/vncservice.service
```

The random password is chosen, because there is no need for me to access the VNC
service.

Scanners/Attackers will try to login to the VNC server by trying common
passwords. Therefore, the random password with a complexity of 256 bytes is a
secure choice. According to [howsecureismypassword.net](https://howsecureismypassword.net/),
would a brute-force attack require "51 duovigintillion ducentillion years to
crack your password". I am pretty sure my research will have finished by then.

The default VNC port is 5900. The installed debian package is `linuxvnc`. The
VNC server logs to `/var/log/syslog`.


### Logrotate

The honeypot setup will alter your logrotation configuration. Logroate is
configured to rotate the log files each midnight. This means, at midnight the
log files will be moved by one rotation. Log rotations are those files which end
on a digit. For example, `auth.log` will be rotated to `auth.log.1` (previous
day). A possibly existing file will be rotated further to `auth.log.2` (two days
ago).

The following log files will be rotated daily:

```
/var/log/auth.log
/var/log/syslog
```

Logs will be stored for 21 days. 21 days were chosen to have the files locally
available on the honeypots. Just see it as a backup in case all other logs are
somehow lost.


### Cron Jobs

The setup script configures one cron job, which will run each night at 2am. The
cron job executes the script [upload-logs.sh](https://static.maxresing.de/pub/ut/upload-logs.sh).
The log rotation should be done by that moment. The script of the cron job
essentially greps all log entries from `/var/log/auth.log.1` and
`/var/log/syslog.1` which belong to one of the applications `sshd`, `telnetd` or
`linuxvnc`.

This research does not require any other log data and thus, does not transmit
it. The script of the cron job is stored in `/usr/local/bin`.
The `remove-debian-hp.sh` cleanup the cron job file `/etc/cron.d/honeypot` as
well as the `upload-logs.sh` script.


### Summary

The following software packages will be installed:

```
curl
inetutils-telnetd
linuxvnc
openssh-server
openssl
```

The system will serve the following services on the corresponding default ports

```
  22 - sshd.service (sshd)
  23 - inetd.service (telnet)
5900 - vncservice.service (linuxvnc)
```

Furthermore, the following script is configured as a cron job to transmit the
logging data:

```
/usr/bin/
```

Those are the scripts you need to download:

 * [setup-debian-hp.sh](https://static.maxresing.de/pub/setup-debian-hp.sh)
 * [remove-debian-hp.sh](https://static.maxresing.de/pub/remove-debian-hp.sh)

To setup the honeypot execute the setup script:

```
sudo bash $HOME/setup-debian-hp.sh
```

At the end of the research, you can revert the changesL

```
sudo bash $HOME/remove-debian-hp.sh
```

The configuration files can be found here:

 * [/etc/inetd.conf](https://static.maxresing.de/pub/inetd.conf)
 * [/etc/logrotate.conf](https://static.maxresing.de/pub/logrotate.conf)
 * [/etc/ssh/sshd_config](https://static.maxresing.de/pub/sshd_config)
 * [/etc/systemd/system/vncservice.service](https://static.maxresing.de/pub/vncservice)


If there are any questions left, please contact me:
  Max Resing <m.resing-1@student.utwente.nl>

Thank you!
