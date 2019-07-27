extern crate zmq;

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
}

