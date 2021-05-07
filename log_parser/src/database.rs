use crate::models;
//use postgres::Client;

#[derive(Debug)]
pub struct Record {
    _id: i64,
    sync_ts: i64,
    origin: String,
    origin_id: i64,
    timestamp: i64,
    ip: i64,
    category: String,
}

impl Record {
    pub fn from(sync_ts: i64, log: models::LogEntry) -> Record {
        // map origin to string
        let origin: String = match log.origin {
            models::Origin::Campus => String::from("campus"),
            models::Origin::Cloud => String::from("cloud"),
            models::Origin::Dataplane => String::from("dataplane"),
            models::Origin::Residential => String::from("residential"),
            _ => String::from(""),
        };

        // map category to string
        let category: String = match log.category {
            models::Category::Ssh => String::from("ssh"),
            models::Category::Telnet => String::from("telnet"),
            models::Category::Vnc => String::from("vnc"),
        };

        Record {
            _id: 0,
            sync_ts,
            origin,
            origin_id: log.origin_id,
            timestamp: log.timestamp,
            ip: log.ip,
            category,
        }
    }

    //pub fn insert(&self, pgc: &mut Client) {}
}
