use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;
use std::sync::Arc;
use std::fs::File;
use std::io::Read;
use std::vec::IntoIter;


pub struct MemoryBackend {
    pub backend_name: String,
    cgroup_manager: Arc<CgroupManager>,
}

impl MemoryBackend {
    pub fn new(cgroup_manager: Arc<CgroupManager>) -> MemoryBackend {
        let backend_name = "Memory".to_string();
        MemoryBackend {backend_name, cgroup_manager}
    }
}

impl Backend for MemoryBackend {
    fn say_hello(&self) {
        println!("hello my name is memory backend");
    }

    fn open(&self) {
    }

    fn close(&self) {
    }

    fn get_metric_names(&self) -> IntoIter<String> {
        let mut file = File::open("/sys/fs/cgroup/memory/memory.stat").unwrap();
        let mut content = String::new();
        file.read_to_string(&mut content).unwrap();
        let mut lines: Vec<&str> = content.split("\n").collect();
        let mut res : Vec<String> = Vec::new();
         for mut i in 0..lines.len()-1 {
            let line = lines[i];
            let tmp1 = line.to_string();
            let tmp2 : Vec<&str> = tmp1.split(" ").collect();
            res.push(tmp2[0].to_string());
        }
        let metric_names = res[..res.len()].to_vec().into_iter();
        metric_names
    }

    fn get_metric_values(&self) -> IntoIter<String> {
        let mut file = File::open("/sys/fs/cgroup/memory/memory.stat").unwrap();
        let mut content = String::new();
        file.read_to_string(&mut content).unwrap();
        let mut lines: Vec<&str> = content.split("\n").collect();
        let mut res : Vec<String> = Vec::new();
        for mut i in 0..lines.len()-1 {
            let line = lines[i];
            let tmp1 = line.to_string();
            let tmp2 : Vec<&str> = tmp1.split(" ").collect();
            res.push(tmp2[1].to_string());
        }
        let metric_values = res[..res.len()].to_vec().into_iter();
        metric_values
    }
}