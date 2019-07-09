extern crate rmp_serde as rmps;
extern crate serde;
extern crate zmq;

#[macro_use]
extern crate clap;
use clap::App;

use std::thread;
use std::time::Duration;

mod elasticsearch;
mod hdf5;
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
            Ok(x) => elasticsearch::push(x), // push data to backend
            Err(e) => println!("error {}", e),
        };

        thread::sleep(Duration::from_millis(5000));
    }
}

//extern crate hdf5; // require hdf5 >= 1.8.4 -> apt install libhdf5-serial-dev
//extern crate ndarray;
//
//#[derive(hdf5::H5Type, Clone, PartialEq, Debug)]
//#[repr(u8)]
//pub enum Color {
//    RED = 1,
//    GREEN = 2,
//    BLUE = 3,
//}
//
//#[derive(hdf5::H5Type, Clone, PartialEq, Debug)]
//#[repr(C)]
//pub struct Pixel {
//    xy: (i64, i64),
//    color: Color,
//}
//
//#[derive(hdf5::H5Type, Clone, PartialEq, Debug)]
//#[repr(C)]
//pub struct Metric {
//    data: (i64, i64, i64, i64)
//}
//
//
//fn main() {
//    use self::Color::*;
//    use ndarray::{arr1, arr2};
//
//    // so that libhdf5 doesn't print errors to stdout
//    let _ = hdf5::silence_errors();
//    // write
//    let file = hdf5::File::open("pixels.hdf5", "w").unwrap();
//
//    let metric = file.new_dataset::<Metric>().create("metric", (2,1)).unwrap();
//
//    let res = metric.write(&arr2(&[
//        [Metric{data:(1,2,3,4)}],
//        [Metric{data:(5,6,7,8)}],
//    ])).unwrap();

//    let data = Metric{data:(3,14)};
//    let res = metric.write(data);

//    let colors = file.new_dataset::<Color>().create("colors", 2)?;
//    colors.write(&[RED, BLUE])?;
//    let group = file.create_group("dir")?;
//    let pixels = group.new_dataset::<Pixel>().create("pixels", (2, 2))?;
//    let res = pixels.write(&arr2(&[
//        [Pixel { xy: (1, 2), color: RED }, Pixel { xy: (3, 4), color: BLUE }],
//        [Pixel { xy: (5, 6), color: GREEN }, Pixel { xy: (7, 8), color: RED }],
//    ]))?;

//}
