use std::collections::HashMap;
use crate::backends::memory::MemoryBackend;
use crate::backends::blkio::BlkioBackend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;


mod blkio;
mod memory;


pub trait Backend {
    fn say_hello(& self);
    fn open(& self);
    fn close(& self);
    fn get_metric_names(& self) -> String;
    fn get_metric_values(& self);
}

pub struct BackendsManager {
    backends: Vec<Box<dyn Backend>>,
}

impl BackendsManager {
    pub fn new() -> BackendsManager {
        let backends = Vec::new();
        BackendsManager{backends}
    }

    pub fn add_backend(& mut self, backend: Box<dyn Backend>){
        self.backends.push(backend);
    }

    pub fn get_all_metric_names(& self) -> Vec<String>{
        let mut metric_names: Vec<String> = Vec::new();
        for backend in &self.backends {
            metric_names.push(backend.get_metric_names());
        }
        metric_names
    }

    pub fn get_all_metric_values(){}

}


pub fn test() {

    let mut backends_manager = BackendsManager::new();

    let cgroup_manager = Rc::new(CgroupManager::new());

    let memory_backend = MemoryBackend::new(Rc::clone(&cgroup_manager));
    let memory_backend2 = MemoryBackend::new(Rc::clone(&cgroup_manager));

    memory_backend.say_hello();
    memory_backend2.say_hello();

    let blkio_backend = BlkioBackend::new(Rc::clone(&cgroup_manager));

    backends_manager.add_backend(Box::new(memory_backend));
    backends_manager.add_backend(Box::new(blkio_backend));

    cgroup_manager.add_cgroup(1, "lr_1".to_string());
    cgroup_manager.print_cgroups();


    println!("{:#?}",backends_manager.get_all_metric_names());

}

