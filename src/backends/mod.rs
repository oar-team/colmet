use std::collections::HashMap;
use crate::backends::memory::MemoryBackend;
use crate::backends::blkio::BlkioBackend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;
use std::sync::Arc;
use crate::CliArgs;
use regex::Regex;
use std::vec::IntoIter;



mod blkio;
mod memory;


pub trait Backend {
    fn say_hello(& self);
    fn open(& self);
    fn close(& self);
    fn get_metric_names(& self) -> IntoIter<String>;
    fn get_metric_values(& self) -> IntoIter<String>;
}

pub struct BackendsManager {
    backends: Vec<Box<dyn Backend>>,
}

impl BackendsManager {
    pub fn new(regex_job_id: String) -> BackendsManager {
        let backends = Vec::new();
        BackendsManager{backends}
    }

    pub fn add_backend(& mut self, backend: Box<dyn Backend>){
        self.backends.push(backend);
    }

    pub fn get_all_metric_names(& self) -> Vec<IntoIter<String>>{
        let mut metric_names: Vec<IntoIter<String>> = Vec::new();
        for backend in &self.backends {
            metric_names.push(backend.get_metric_names());
        }
        metric_names
    }

    pub fn get_all_metric_values(& self) -> Vec<IntoIter<String>>{
        let mut metric_values: Vec<IntoIter<String>> = Vec::new();
        for backend in &self.backends {
            metric_values.push(backend.get_metric_values());
        }
        metric_values
    }

}


pub fn test(regex_job_id: String, cgroup_rootpath: String) {

    let mut backends_manager = BackendsManager::new(regex_job_id.clone());
    let cgroup_manager = CgroupManager::new(regex_job_id.clone(), cgroup_rootpath.clone());

    let memory_backend = MemoryBackend::new(Arc::clone(&cgroup_manager));
    let memory_backend2 = MemoryBackend::new(Arc::clone(&cgroup_manager));

    memory_backend.say_hello();
    memory_backend2.say_hello();

    let blkio_backend = BlkioBackend::new(Arc::clone(&cgroup_manager));

    backends_manager.add_backend(Box::new(memory_backend));
    backends_manager.add_backend(Box::new(blkio_backend));


    println!("all metric names {:#?}",backends_manager.get_all_metric_names());
    println!("all metric values {:#?}",backends_manager.get_all_metric_values());


}

