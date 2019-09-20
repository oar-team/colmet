extern crate zmq;
extern crate serde;
extern crate rmp_serde as rmps;

use std::collections::HashMap;
extern crate rmp_serialize;
extern crate rustc_serialize;

use serde::{Deserialize, Serialize};
use rmps::{Deserializer, Serializer};
use self::zmq::Message;
use std::sync::{Arc, Mutex};
use crate::backends::{Backend};

pub struct ZmqSender<'a> {
    sender: zmq::Socket, // sends counters to colmet-collector
    receiver: zmq::Socket, // receives user configuration
    backends: &'a Vec<Box<dyn Backend>>,
}

impl ZmqSender<'_> {

    pub fn init(backends: &Vec<Box<dyn Backend>>) -> ZmqSender {
        let context = zmq::Context::new();
        let sender = context.socket(zmq::PUSH).unwrap();
        let receiver = context.socket(zmq::PULL).unwrap();
        ZmqSender{sender, receiver, backends}
    }

    pub fn open(&self, uri:&str, linger:i32, high_watermark:i32){
        self.sender.connect(uri).unwrap();
        self.sender.set_linger(linger).unwrap();
        self.sender.set_sndhwm(high_watermark).unwrap();
        self.receiver.bind("tcp://0.0.0.0:5557").unwrap();
        self.receiver.set_linger(linger).unwrap();
        self.receiver.set_rcvhwm(high_watermark).unwrap();

    }

    pub fn send_metrics(&self, metrics: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)>) {
        let mut buf = Vec::new();
        match metrics.serialize(&mut Serializer::new(&mut buf)){
            Err(e) => println!("{}", e),
            Ok(_t) => ()
        }
//        let mut de = Deserializer::new(&buf[..]);
//        let res: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)> = Deserialize::deserialize(&mut de).unwrap();
        self.sender.send(buf, 0).unwrap();
    }

    // receive message containing a new config for colmet, change sample period and metrics collected by backends (only perfhw at the moment)
    pub fn receive_config(&self, sample_period: Arc<Mutex<f64>>) {
        let mut message = Message::new();
        match self.receiver.recv(&mut message, 1) {
            Err(_e) => (),
            Ok(_t) => {
                let mut deserializer = Deserializer::new(&message[..]);
                let config:HashMap<String, String>  = Deserialize::deserialize(&mut deserializer).unwrap();
                println!("config {:#?}", config);
                *(&*sample_period).lock().unwrap() = config["sample_period"].parse().unwrap();

                for backend in self.backends{
                    if backend.get_backend_name() == "Perfhw"{
                        let m : Vec<&str> = config["perfhw_metrics"].split(",").collect();
                        let mut metrics = Vec::new();
                        for metric in m{
                            metrics.push(metric.to_string());
                        }
                        backend.set_metrics_to_get(metrics);
                    }
                }
            }
        }
    }
}
