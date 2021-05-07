use crate::models;

use regex::Regex;
use syslog_loose;

// SSH log
// May  7 10:31:31 pi sshd[11610]: Failed password for invalid user test from 192.168.0.43 port 48996 ssh2

// month
// day
// hour:minute:second
// _user
// _sshd[11610]:
// _: Faile
//
// Telnet log
// May  7 10:34:03 pi telnetd[12341]: connect from 192.168.0.43 (192.168.0.43)

// VNC log
// May  7 10:35:15 pi linuxvnc[425]: 07/05/2021 10:35:15 Got connection from client 192.168.0.43
//
//

// Note: This is not a perfect IP regex, but it's faster than using the complete
//       IP regex. We can expect that the messages just include valid IPs

///
/// Determines the service protocol/category based on the string of the app name.
/// If it can not resolve to Category::{Ssh, Telnet, Vnc} then it returns None.
/// Otherwise Some(models::Category)
///
fn parse_appname(appname: String) -> Option<models::Category> {
    if appname.contains("sshd") {
        println!("Discovered SSH");
        Some(models::Category::Ssh)
    } else if appname.contains("telnetd") {
        println!("Discovered Telnet");
        Some(models::Category::Telnet)
    } else if appname.contains("linuxvnc") {
        println!("Discovered VNC");
        Some(models::Category::Vnc)
    } else {
        println!("Discovered None");
        None
    }
}

///
/// Takes the syslog message and tries to find the IP in the string. If it finds
/// an IP address, it calculates the IPs numeric value and returns it. If it can
/// not find an IP it returns None
///
fn parse_ip_from_msg(msg: String) -> Option<i64> {
    let re: Regex = Regex::new(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}").unwrap();
    let ip: &str = re.find(&msg)?.as_str();
    let mut v: Vec<&str> = ip.split('.').collect();

    if v.len() != 4 {
        return None;
    }

    let mut ip = 0;
    let mut exp = 0;
    let base: i64 = 255;

    while v.len() > 0 {
        let x = v.pop().unwrap();
        let x: i64 = x.parse().unwrap();
        ip = ip + x * base.pow(exp);
        exp += 1;
    }

    Some(ip)
}

pub fn parse(origin: models::Origin, origin_id: i64, log: &str) -> Option<models::LogEntry> {
    let msg = syslog_loose::parse_message(log);

    // TODO: Make check to check for string start, e.g. :
    //         - "Failed password for" (SSH)
    //         - "Got connection from" (VNC)
    //         - "connect from" (Telnet)

    let timestamp = msg.timestamp?.timestamp();

    // parse IP
    let ip = parse_ip_from_msg(String::from(msg.msg))?;

    // parse category
    let category = msg.appname?;
    let category = parse_appname(String::from(category))?;

    Some(models::LogEntry::new(
        origin, origin_id, timestamp, ip, category,
    ))
}
