extern crate gethostname;

use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::sync::Arc;
use std::time::SystemTime;

use crate::backends::Backend;
use crate::cgroup_manager::CgroupManager;
use crate::backends::metric::Metric;

use std::slice;
use std::cell::RefCell;
use std::rc::Rc;

extern crate libc;


pub struct PerfhwBackend {
    pub backend_name: String,
    cgroup_manager: Arc<CgroupManager>,
    metrics: Rc<RefCell<HashMap<i32, Metric>>>,
    metrics_to_get: Rc<RefCell<Vec<String>>>,
}

impl PerfhwBackend {
    pub fn new(cgroup_manager: Arc<CgroupManager>) -> PerfhwBackend {
        let backend_name = "Perfhw".to_string();

        let metrics = Rc::new(RefCell::new(HashMap::new()));

        let metrics_to_get = Rc::new(RefCell::new(vec!("instructions".to_string(), "cache_misses".to_string(), "page_faults".to_string())));

        for (cgroup_id, cgroup_name) in cgroup_manager.get_cgroups() {
            let metric_names = (*metrics_to_get).borrow().clone();
            let hostname: String = gethostname::gethostname().to_str().unwrap().to_string();
            let now = SystemTime::now();
            let timestamp = now.duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis() as i32;
            let metric = Metric { job_id: cgroup_id, hostname, timestamp, backend_name: backend_name.clone(), metric_names, metric_values: None };
            (*metrics).borrow_mut().insert(cgroup_id, metric);
        }
        PerfhwBackend { backend_name, cgroup_manager, metrics, metrics_to_get }
    }
}

impl Backend for PerfhwBackend {
    fn say_hello(&self) {
        println!("hello my name is perfhw backend");
    }

    fn get_backend_name(&self) -> String{
        return self.backend_name.clone();
    }

    fn open(&self) {}

    fn close(&self) {}

    fn get_metrics(& self) ->HashMap<i32, Metric> {
        for (cgroup_id, cgroup_name) in self.cgroup_manager.get_cgroups() {
            let cgroup_name_string = format!("/oar/{}{}", cgroup_name, "\0").to_string();
            let cgroup_name = cgroup_name_string.as_ptr();

            let metric_values = get_metric_values(cgroup_name, format!("{}{}", (*self.metrics_to_get).borrow().join(","), "\0").as_ptr(), (*self.metrics_to_get).borrow().len());
            (*self.metrics).borrow_mut().get_mut(&cgroup_id).unwrap().metric_values = Some(metric_values);
        }
        println!("new metric {:#?}", self.metrics.clone());
        (*self.metrics).borrow_mut().clone()
    }

    fn set_metrics_to_get(& self, metrics_to_get: Vec<String>){
        *(*self.metrics_to_get).borrow_mut() = metrics_to_get.clone();
        let mut metrics = HashMap::new();
         for (cgroup_id, cgroup_name) in self.cgroup_manager.get_cgroups() {
             let metric_names = metrics_to_get.clone();
             let hostname: String = gethostname::gethostname().to_str().unwrap().to_string();
             let now = SystemTime::now();
             let timestamp = now.duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis() as i32;
             let metric = Metric { job_id: cgroup_id, hostname, timestamp, backend_name: self.backend_name.clone(), metric_names, metric_values: None };
             metrics.insert(cgroup_id, metric);
         }
        *(*self.metrics).borrow_mut() = metrics;
    }
}

fn get_metric_values(cgroup_name: *const u8, metrics_to_get: *const u8, nb_metrics_to_get: usize) -> Vec<i64> {

    #[link(name = "_perf_hw")]
    extern {
        fn init_cgroup(cgroup_name: *const u8, metrics: *const u8) -> i32;
    }

    extern {
        fn get_counters(values: *mut i64, cgroup_name: *const u8) -> i32;
    }

    let res = unsafe {init_cgroup(cgroup_name, metrics_to_get)};
    let mut buffer = Vec::with_capacity(3*64 as usize);
    let buffer_ptr = buffer.as_mut_ptr();
    let res2 = unsafe {get_counters(buffer_ptr, cgroup_name)};
    let metric_values = unsafe { slice::from_raw_parts(buffer_ptr, nb_metrics_to_get).to_vec()};
    metric_values
}