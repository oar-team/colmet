use std::collections::HashMap;

#[macro_use]
extern crate log;
extern crate simple_logger;

extern crate regex;
use regex::Regex;

use log::Level;

#[macro_use]
extern crate clap;

// command line argument parser
use clap::App;

use std::time::{Duration, SystemTime};
use std::thread::sleep;
use std::thread;

mod backends;

mod cgroup_manager;
mod zeromq;

extern crate inotify;

use std::env;

use inotify::{
    EventMask,
    WatchMask,
    Inotify,
};



fn main(){



    let cli_args = parse_cli_args();
    backends::test(cli_args.regex_job_id, cli_args.cgroup_rootpath);

    init_logger(cli_args.verbose);

    let zmq_sender = zeromq::ZmqSender::init();
    zmq_sender.open(&cli_args.zeromq_uri, cli_args.zeromq_linger, cli_args.zeromq_hwm);
    zmq_sender.send("hello world!!!");

    // main loop that pull backends measurements periodically ans send them with zeromq
    loop {
        let now = SystemTime::now();
        println!("{:#?}", now.duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis());
        // on appelle les backends et on envoie avec zmq
        debug!("time to take measures {} nanoseconds", now.elapsed().unwrap().as_nanos());
        sleep_to_round_timestamp((cli_args.sample_period * 1000000000.0) as u128);
    }
}

/// sleep until the next timestamp that is a multiple of given duration_nanoseconds
/// as a consequence, the function sleeps a duration that is almost duration_nanoseconds and ends on a round timestamp
fn sleep_to_round_timestamp(duration_nanoseconds: u128) {
    let now = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap().as_nanos();
    let duration_to_sleep = ((now / duration_nanoseconds) + 1) * duration_nanoseconds - now;
    sleep(Duration::new(0, duration_to_sleep as u32));
}


struct CliArgs {
    verbose: i32,
    sample_period: f64,
    enable_infiniband: bool,
    enable_lustre: bool,
    enable_perfhw: bool,
    enable_rapl: bool,
    zeromq_uri: String,
    zeromq_hwm: i32,
    zeromq_linger: i32,
    cgroup_rootpath: String,
    regex_job_id: String,
}

fn parse_cli_args() -> CliArgs {
    let yaml = load_yaml!("cli.yml");
    let matches = App::from_yaml(yaml).get_matches();
    let verbose = matches.occurrences_of("verbose") as i32;
    let sample_period = value_t!(matches, "sample-period", f64).unwrap();
    println!("sample perdiod {}", sample_period);
    let enable_infiniband = value_t!(matches, "enable-infiniband", bool).unwrap();
    let enable_lustre = value_t!(matches, "enable-lustre", bool).unwrap();
    let enable_perfhw = value_t!(matches, "enable-perfhw", bool).unwrap();
    let enable_rapl = value_t!(matches, "enable-RAPL", bool).unwrap();
    let zeromq_uri = value_t!(matches, "zeromq-uri", String).unwrap();
    let zeromq_hwm = value_t!(matches, "zeromq-hwm", i32).unwrap();
    let zeromq_linger = value_t!(matches, "zeromq-linger", i32).unwrap();
    let cgroup_rootpath = value_t!(matches, "cgroup-rootpath", String).unwrap();
    let regex_job_id = value_t!(matches, "regex-job-id", String).unwrap();


    let cli_args = CliArgs {
        verbose,
        sample_period,
        enable_infiniband,
        enable_lustre,
        enable_perfhw,
        enable_rapl,
        zeromq_uri,
        zeromq_hwm,
        zeromq_linger,
        cgroup_rootpath,
        regex_job_id
    };
    cli_args
}

fn init_logger(verbosity_lvl: i32) {
    match verbosity_lvl {
        0 => simple_logger::init_with_level(Level::Error).unwrap(),
        1 => simple_logger::init_with_level(Level::Warn).unwrap(),
        2 => simple_logger::init_with_level(Level::Info).unwrap(),
        3 => simple_logger::init_with_level(Level::Debug).unwrap(),
        _ => simple_logger::init_with_level(Level::Trace).unwrap(),
    }
}