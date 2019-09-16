extern crate gethostname;

use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::sync::Arc;
use std::time::SystemTime;

use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use crate::backends::metric::Metric;

pub struct MemoryBackend {
    pub backend_name: String,
    cgroup_manager: Arc<CgroupManager>,
    metrics: HashMap<i32, Metric>,
}

impl MemoryBackend {
    pub fn new(cgroup_manager: Arc<CgroupManager>) -> MemoryBackend {
        let backend_name = "Memory".to_string();
        let mut metrics = HashMap::new();
        for (cgroup_id, cgroup_name) in cgroup_manager.get_cgroups() {
            let filename = format!("/sys/fs/cgroup/memory/oar/{}/memory.stat", cgroup_name);
            let metric_names = get_metric_names(filename);
            let hostname: String = gethostname::gethostname().to_str().unwrap().to_string();
            let now = SystemTime::now();
            let timestamp = now.duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis() as i32;
            let metric = Metric { job_id: cgroup_id, hostname, timestamp, backend_name: backend_name.clone(), metric_names, metric_values: None };
            metrics.insert(cgroup_id, metric);
        }
        MemoryBackend { backend_name, cgroup_manager, metrics }
    }
}

impl Backend for MemoryBackend {
    fn say_hello(&self) {
        println!("hello my name is memory backend");
    }

    fn open(&self) {}

    fn close(&self) {}

    fn get_metrics(&mut self) -> HashMap<i32, Metric> {
        for (cgroup_id, cgroup_name) in self.cgroup_manager.get_cgroups() {
            let filename = format!("/sys/fs/cgroup/memory/oar/{}/memory.stat", cgroup_name);
            let metric_values = get_metric_values(filename);
            self.metrics.get_mut(&cgroup_id).unwrap().metric_values = Some(metric_values);
        }
//        println!("new metric {:#?}", self.metrics.clone());
        self.metrics.clone()
    }
}

fn get_metric_names(filename: String) -> Vec<String> {
    let mut file = File::open(filename).unwrap();
    let mut content = String::new();
    file.read_to_string(&mut content).unwrap();
    let lines: Vec<&str> = content.split("\n").collect();
    let mut res: Vec<String> = Vec::new();
    for i in 0..lines.len() - 1 {
        let line = lines[i];
        let tmp1 = line.to_string();
        let tmp2: Vec<&str> = tmp1.split(" ").collect();
        res.push(tmp2[0].to_string());
    }
    let metric_names = res[..res.len()].to_vec();

    metric_names
}

fn get_metric_values(filename: String) -> Vec<i64> {
    let mut file = File::open(filename).unwrap();
    let mut content = String::new();
    file.read_to_string(&mut content).unwrap();
    let lines: Vec<&str> = content.split("\n").collect();
    let mut res: Vec<i64> = Vec::new();
    for i in 0..lines.len() - 1 {
        let line = lines[i];
        let tmp1 = line.to_string();
        let tmp2: Vec<&str> = tmp1.split(" ").collect();
        res.push(tmp2[1].parse::<i64>().unwrap());
    }
    let metric_values = res[..res.len()].to_vec();
    metric_values
}