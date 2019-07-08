extern crate serde;
extern crate rmp_serde as rmps;
extern crate zmq;

#[macro_use]
extern crate clap;
use clap::App;

use std::thread;
use std::time::Duration;

mod stdout;



fn main() {

    // parse arguments from command line interface
    let yaml = load_yaml!("cli.yml");
    let matches = App::from_yaml(yaml).get_matches();
//
//    let config = matches.value_of("config").unwrap();
//    println!("Value for config: {}", config);

    let sample_period = value_t!(matches, "sample-period", f64).unwrap();
    println!("Value for sampling : {}", sample_period);

    let stdout = value_t!(matches, "enable-stdout-backend", bool).unwrap();
    println!("Value for stdout : {}", stdout);


    // receive data using zeromq
    let context = zmq::Context::new();
    let receiver = context.socket(zmq::PULL).unwrap();
    assert!(receiver.bind("tcp://0.0.0.0:5556").is_ok());

    loop {
        match receiver.recv_bytes(1) {
            Ok(x) => stdout::push(x), // push data to backend
            Err(e) => println!("error {}", e),
        };

         thread::sleep(Duration::from_millis(5000));
    }

}



