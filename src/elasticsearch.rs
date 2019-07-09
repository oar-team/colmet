extern crate reqwest;
// on linux, require openssl-sys >= 0.9.47 => apt install libssl-dev
extern crate serde_json;

use core::borrow::Borrow;
use rmps::Deserializer;
use serde::Deserialize;
use serde_json::{Map, Number, Value};
use std::collections::HashMap;
//use reqwest::{IntoUrl};

pub fn push(x: Vec<u8>) {
    let mut de = Deserializer::new(&x[..]);
    let received_data: Vec<(String, String, i64, HashMap<String, HashMap<String, u64>>)> =
        Deserialize::deserialize(&mut de).unwrap();
    let job_id: i64 = received_data[0].0.parse().unwrap();
    let hostname: &str = &received_data[0].1;
    let timestamp: i64 = received_data[0].2;

    for backend in received_data[0].3.iter() {
        let backend_name = backend.0;
        let mut elastic_document = Map::new();
        elastic_document.insert("job_id".to_string(), serde_json::json!(job_id));
        elastic_document.insert("hostname".to_string(), serde_json::json!(hostname));
        elastic_document.insert("timestamp".to_string(), serde_json::json!(timestamp));

        for metric in backend.1.iter() {
            elastic_document.insert(metric.0.to_string(), serde_json::json!(metric.1));
        }
        create_index_if_necessary(backend_name);
        index_document(elastic_document, backend_name);
    }

    fn index_document(elastic_document: Map<String, Value>, index: &String) {
        let url = format!(
            "{elastic_host}/{index}/_doc/",
            elastic_host = "http://fgrenoble.grenoble.grid5000.fr:9200",
            index = index
        );

        let client = reqwest::Client::new();
        let res = match client.post(&url).json(&elastic_document).send() {
            Ok(r) => (),
            Err(e) => println!("{}", e),
        };
    }

    fn create_index_if_necessary(index: &String) {
        let url = format!(
            "{elastic_host}/{index}",
            elastic_host = "http://fgrenoble.grenoble.grid5000.fr:9200",
            index = index
        );

        let client = reqwest::Client::new();
        let res = match client.head(&url).send() {
            Ok(r) => {
                if r.status() == 404 {
                    // # index does not exist
                    let mapping = r#"
                    {
                        "mappings": {
                            "properties": {
                                "timestamp": {
                                    "type": "date",
                                    "format": "epoch_second"
                                }
                            }
                        }
                    }"#;
                    let json_mapping: Result<Value, serde_json::Error> = serde_json::from_str(mapping);
                    let res = match client.put(&url).json(&json_mapping.unwrap()).send() {
                        Ok(r) => (),
                        Err(e) => println!("{}", e),
                    };
                }
            },
            Err(e) => println!("{}", e),
        };

    }
}
