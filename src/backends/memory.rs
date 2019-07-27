use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;


pub struct MemoryBackend {
    pub backend_name: String,
    cgroup_manager: Rc<CgroupManager>,
}

impl MemoryBackend {
    pub fn new(cgroup_manager: Rc<CgroupManager>) -> MemoryBackend {
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

    fn get_metric_names(&self) -> String {
        "ok".to_string()
    }

    fn get_metric_values(&self) {
    }
}