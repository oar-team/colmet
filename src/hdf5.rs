extern crate hdf5; // require hdf5 >= 1.8.4 -> apt install libhdf5-serial-dev

use std::collections::HashMap;
use serde::{Deserialize};
use rmps::{Deserializer};
use core::borrow::Borrow;

pub fn push(x: Vec<u8>){
//    let mut de = Deserializer::new(&x[..]);
//    let res : Vec<(String, String, u64, HashMap<String, HashMap<String, u64>>)> = Deserialize::deserialize(&mut de).unwrap();

//    let ex_data = res[0].3["memory"].borrow();
//
//    let ex_data = Metric{data:(1,2)};
//
//    println!("{:#?}", ex_data);
//
//    let file = hdf5::File::open("test_hdf5.hdf5", "w").unwrap();
//
//    let group = file.create_group("dir").unwrap();
//    let memory = group.new_dataset::<Metric>().create("memory", (2,2)).unwrap();
//
//    memory.write(ex_data);



//    println!("{:#?}", ex_data);
}