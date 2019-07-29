use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;
use std::sync::Arc;


pub struct BlkioBackend {
    pub backend_name: String,
    cgroup_manager: Arc<CgroupManager>,
}

impl BlkioBackend {
    pub fn new(cgroup_manager: Arc<CgroupManager>) -> BlkioBackend {
        let backend_name = "Blkio".to_string();
        BlkioBackend {backend_name, cgroup_manager}
    }
}

impl Backend for BlkioBackend {
    fn say_hello(&self) {
        println!("hello my name is blkio backend");
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