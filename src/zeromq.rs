extern crate zmq;
extern crate serde;
extern crate rmp_serde as rmps;

use crate::backends::metric::Metric;
use std::collections::HashMap;
use std::vec::IntoIter;
extern crate rmp_serialize;
extern crate rustc_serialize;

use serde::{Deserialize, Serialize};
use rmps::{Deserializer, Serializer};
use self::zmq::Message;
use std::sync::{Arc, Mutex};
use std::cell::RefCell;


pub struct ZmqSender {
    sender: zmq::Socket, // sends counters to colmet-collector
    receiver: zmq::Socket, // receives user configuration
}

impl ZmqSender {

    pub fn init() -> ZmqSender {
        let context = zmq::Context::new();
        let sender = context.socket(zmq::PUSH).unwrap();
        let receiver = context.socket(zmq::PULL).unwrap();
        ZmqSender{sender, receiver}
    }

    pub fn open(&self, uri:&str, linger:i32, high_watermark:i32){
        self.sender.connect(uri).unwrap();
        self.sender.set_linger(linger).unwrap();
        self.sender.set_sndhwm(high_watermark).unwrap();
        self.receiver.bind("tcp://0.0.0.0:5557").unwrap();
        self.receiver.set_linger(linger).unwrap();
        self.receiver.set_rcvhwm(high_watermark).unwrap();

    }

    pub fn send(&self, message:&str){
        self.sender.send(message, 0).unwrap();
    }

    pub fn send_metrics(&self, metrics: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)>) {
        let mut buf = Vec::new();
        metrics.serialize(&mut Serializer::new(&mut buf));
        let mut de = Deserializer::new(&buf[..]);
        let res: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)> = Deserialize::deserialize(&mut de).unwrap();
        self.sender.send(buf, 0).unwrap();
    }

    pub fn receive_config(&self, sample_period: Arc<Mutex<f64>>) {
        let mut message = Message::new();
        match self.receiver.recv(&mut message, 1) {
            Err(e) => (),
            Ok(t) => {
                let mut deserializer = Deserializer::new(&message[..]);
                *(&*sample_period).lock().unwrap() = Deserialize::deserialize(&mut deserializer).unwrap();
            }
        }
    }
}
