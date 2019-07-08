use std::collections::HashMap;
use serde::{Deserialize};
use rmps::{Deserializer};

pub fn display_metrics(x: Vec<u8>){
    let mut de = Deserializer::new(&x[..]);
    let res : Vec<(String, String, u64, HashMap<String, HashMap<String, u64>>)> = Deserialize::deserialize(&mut de).unwrap();

    println!("{:#?}", res);
}