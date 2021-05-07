use std::fs;

mod database;
mod models;
mod parser;

fn main() {
    /*
    let mut pgc = Client::connect(
        "postgresql://postgres:postgres@192.168.0.100/honeypot",
        NoTls,
    );
    */

    /*
    let rec = database::Record {
        _id: 0,
        sync_ts: 0,
        origin: String::from(""),
        origin_id: String::from(""),
        timestamp: 0,
        ip: 0,
        category: String::from(""),
    };
    */

    /*
    pgc.execute(
        "INSERT INTO log (sync_ts, origin, origin_id, timestamp, ip, category) VALUES ($1, $2, $3, $4, $5, $6)",
        &[&rec.sync_ts, &rec.origin, &rec.origin, &rec.origin_id, &rec.timestamp, &rec.ip, &rec.category]
    )?;
    */

    let filename = "test.log";

    let log = fs::read_to_string(filename).expect("Something went wrong reading the file");
    let log = log.split('\n');

    let mut v: Vec<models::LogEntry> = Vec::new();
    for l in log {
        let origin = models::Origin::Residential;
        let origin_id: i64 = 1;

        match parser::parse(origin, origin_id, l) {
            Some(e) => v.push(e),
            _ => (),
        }
    }

    println!("File content:\n{:#?}", v);
}
