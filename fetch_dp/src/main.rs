use std::env;
use chrono::{DateTime, Utc};
use ureq;

struct Meta {
    ts: DateTime<Utc>,
    origin: String,
    origin_id: u64,
    category: String,
}

fn main() -> Result<(), ureq::Error> {
    let args: Vec<String> = env::args().collect();

    let ts: DateTime<Utc> = Utc::now();

    let meta = Meta {
        ts,
        origin: String::from("dataplane"),
        origin_id: 1,
        category: String::from("ssh"),
    };

    let body: String  = ureq::get("https://dataplane.org/sshpwauth.txt")
        .call()?
        .into_string()?;

    //println!("{}", body);

    //println!("{:?}", args);

    Ok(())
}
