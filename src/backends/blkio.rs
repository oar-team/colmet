use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use std::rc::Rc;
use std::sync::Arc;
use std::fs::File;
use std::io::Read;
use std::vec::IntoIter;


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

    fn get_metric_names(&self) -> IntoIter<String> {
        let mut file = File::open("/sys/fs/cgroup/blkio/blkio.throttle.io_service_bytes").unwrap();
        let mut content = String::new();
        file.read_to_string(&mut content).unwrap();
        let mut lines: Vec<&str> = content.split("\n").collect();
        let mut res : Vec<String> = Vec::new();
        for mut i in 0..lines.len()-2 {
            let line = lines[i];
            let tmp1 = line.to_string();
            let tmp2 : Vec<&str> = tmp1.split(" ").collect();
            let tmp3 = format!("{} {}", tmp2[0], tmp2[1]);
            res.push(tmp3);
        }
        let metric_names = res[..].to_vec().into_iter();
        metric_names
    }

    fn get_metric_values(&self) -> IntoIter<String> {
        let mut file = File::open("/sys/fs/cgroup/blkio/blkio.throttle.io_service_bytes").unwrap();
        let mut content = String::new();
        file.read_to_string(&mut content).unwrap();
        let mut lines: Vec<&str> = content.split("\n").collect();
        let mut res : Vec<String> = Vec::new();
         for mut i in 0..lines.len()-2 {
            let line = lines[i];
            let tmp1 = line.to_string();
            let tmp2 : Vec<&str> = tmp1.split(" ").collect();
            res.push(tmp2[2].to_string());
        }
        let metric_values = res[..res.len()-1].to_vec().into_iter();
        metric_values
    }
}