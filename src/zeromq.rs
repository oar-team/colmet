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


pub struct ZmqSender {
    socket: zmq::Socket,
}

impl ZmqSender {

    pub fn init() -> ZmqSender {
        let context = zmq::Context::new();
        let socket = context.socket(zmq::PUSH).unwrap();
        ZmqSender{socket}
    }

    pub fn open(&self, uri:&str, linger:i32, high_watermark:i32){
        self.socket.connect(uri).unwrap();
        self.socket.set_linger(linger).unwrap();
        self.socket.set_sndhwm(high_watermark).unwrap();
    }

    pub fn send(&self, message:&str){
        self.socket.send(message, 0).unwrap();
        println!("sent message");
    }

    pub fn send_metrics(&self, metrics: HashMap<i32, (String, i32, Vec<(String, Vec<i32>, Vec<i64>)>)>) {


        println!("m to s {:#?}", metrics.clone());
        let mut buf = Vec::new();

        metrics.serialize(&mut Serializer::new(&mut buf)).unwrap();
        println!("buffer binaire {:#?}", buf);

        let mut de = Deserializer::new(&buf[..]);
        let res: HashMap<i32, (String, i32, Vec<(String, Vec<i32>, Vec<i64>)>)> = Deserialize::deserialize(&mut de).unwrap();
        println!("####################################### unserialized result {:#?}", res);

        self.socket.send(buf, 0).unwrap();
    }
}
