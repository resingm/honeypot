#[derive(Debug)]
pub enum Origin {
    Dataplane,
    Residential,
    Campus,
    Cloud,
    Darknet,
}

#[derive(Debug)]
pub enum Category {
    Ssh,
    Telnet,
    Vnc,
}

#[derive(Debug)]
pub struct LogEntry {
    pub origin: Origin,
    pub origin_id: i64,
    pub timestamp: i64,
    pub ip: i64,
    pub category: Category,
}

impl LogEntry {
    pub fn new(
        origin: Origin,
        origin_id: i64,
        timestamp: i64,
        ip: i64,
        category: Category,
    ) -> LogEntry {
        LogEntry {
            origin,
            origin_id,
            timestamp,
            ip,
            category,
        }
    }
}
