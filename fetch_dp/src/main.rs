use std::io::prelude::*;
use std::fs::File;
use std::path;

use chrono::{DateTime, Utc};
use clap::App;
use ureq;

const DEFAULT_DIR: &str = "/mnt/data";
const BASE_URL: &str = "https://dataplane.org";
const ENDPOINTS: (&str, &str, &str) = (
    "/sshpwauth.txt",
    "/telnetlogin.txt",
    "/vncrfb.txt",
);

#[derive(Debug, Clone)]
enum Category {
    Ssh,
    Telnet,
    Vnc,
}

impl ToString for Category {
    fn to_string(&self) -> String {
        let s = match self {
            Category::Ssh => "ssh",
            Category::Telnet => "telnet",
            Category::Vnc => "vnc",
        };
        String::from(s)
    }
}

#[derive(Debug)]
struct Meta {
    ts: DateTime<Utc>,
    origin: String,
    origin_id: u64,
    category: Category,
}

impl Meta {
    fn new(category: Category) -> Meta {
        Meta {
            ts: Utc::now(),
            origin: String::from("dataplane"),
            origin_id: 1,
            category,
        }
    }
}

#[derive(Debug)]
struct Data {
    body: String,
    meta: Meta,
}

impl Data {
    fn new(body: String, meta: Meta) -> Data {
        Data {
            body,
            meta,
        }
    }
}


fn get_url(c: &Category) -> String {
    match c {
        Category::Ssh => String::from(BASE_URL) + ENDPOINTS.0,
        Category::Telnet => String::from(BASE_URL) + ENDPOINTS.1,
        Category::Vnc => String::from(BASE_URL) + ENDPOINTS.2,
    }
}

fn get_filename(dir: &String, c: &Category, ts: &DateTime<Utc>) -> String {
    let mut path = String::from(dir);
    
    if path.chars().last().unwrap() != '/' {
        path += "/";
    }

    let path = path
        + &c.to_string()
        + "/dataplane_01_"
        + &ts.timestamp().to_string()
        + ".log";

    path
}


fn fetch(c: Category) -> Result<Data, ureq::Error> {
    let meta = Meta::new(c);
    let url = get_url(&meta.category);
    let body: String = ureq::get(&url)
        .call()?
        .into_string()?;

    Ok(Data::new(body, meta))
}

fn write_f(dir: &String, data: Data) -> std::io::Result<String> {
    let path = get_filename(dir, &data.meta.category, &data.meta.ts);

    // Create dir
    let prefix = path::Path::new(&path).parent().unwrap();
    std::fs::create_dir_all(prefix)?;

    let mut f = File::create(path.clone())?;
    f.write(data.body.as_bytes())?;

    Ok(path)
}

fn main() {
    let args = App::new("fetch_dp")
        .version("0.1.0")
        .about("Fetch data feeds of dataplane.org")
        .author("Max Resing")
        .arg("-o, --output=[DIR] 'Define an output directory'")
        .arg("-v, --verbose       'Set the output to verbose'")
        .get_matches();

    let verbose = args.is_present("verbose");

    let dir = args.value_of("output").unwrap_or(DEFAULT_DIR);
    let dir = String::from(dir);

    if verbose {
        println!("Check if output directory exists...")
    }

    if !path::Path::new(&dir).is_dir() {
        println!("Given output directory '{}' is not a directory. Exiting", dir);
        return;
    }

    let cats = vec![Category::Ssh, Category::Telnet, Category::Vnc];

    for cat in &cats {
        let c = cat.clone();

        if verbose {
            println!("Fetching data for {:?}", cat);
        }

        let res = fetch(c);
        let res = match res {
            Ok(data) => data,
            Err(error) => {
                panic!("Problem fetching the file: {:?}", error)
            },
        };

        if verbose {
            println!("Writing data of feed to file: {:?}", cat);
        }

        match write_f(&dir, res) {
            Ok(f) => {
                if verbose {
                    println!("Successfully wrote data to {}", f);
                }
            },
            Err(error) => {
                println!("Problem writing the file: {:?}", error)
            },
        }
    }

    if verbose {
        println!("Done")
    }
}
