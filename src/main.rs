extern crate serde;
extern crate rmp_serde as rmps;
extern crate zmq;

mod stdout;

use std::collections::HashMap;
use serde::{Deserialize};
use rmps::{Deserializer};

fn main() {

    use std::thread;
    use std::time::Duration;

    let context = zmq::Context::new();
    let receiver = context.socket(zmq::PULL).unwrap();
    assert!(receiver.bind("tcp://0.0.0.0:5556").is_ok());

    loop {
        match receiver.recv_bytes(1) {
            Ok(x) => stdout::display_metrics(x),
            Err(e) => println!("error {}", e),
        };

         thread::sleep(Duration::from_millis(5000));
    }

}



