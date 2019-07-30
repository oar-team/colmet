use std::collections::HashMap;
use crate::backends::memory::MemoryBackend;
use crate::cgroup_manager::CgroupManager;
use crate::backends::metric::Metric;
use std::sync::Arc;
use crate::CliArgs;

mod metric;
mod memory;


pub trait Backend {
    fn say_hello(&self);
    fn open(&self);
    fn close(&self);
    fn get_metrics(&mut self) -> HashMap<i32, Metric>;
}

pub struct BackendsManager {
    backends: Vec<Box<dyn Backend>>,
}

impl BackendsManager {
    pub fn new(cli_args: CliArgs) -> BackendsManager {
        let backends = Vec::new();
        if cli_args.enable_infiniband {
            ()
        }
        if cli_args.enable_lustre {
            ()
        }
        if cli_args.enable_rapl {
            ()
        }
        if cli_args.enable_perfhw {
            ()
        }

        BackendsManager { backends }
    }

    pub fn add_backend(&mut self, backend: Box<dyn Backend>) {
        self.backends.push(backend);
    }

    pub fn get_all_metrics(&mut self) -> () {
        for backend in &mut self.backends {
            backend.get_metrics();
        }
    }
}


pub fn test(cli_args: CliArgs) {
    let mut backends_manager = BackendsManager::new(cli_args.clone());
    let cgroup_manager = CgroupManager::new(cli_args.regex_job_id.clone(), cli_args.cgroup_rootpath.clone());

    let memory_backend = MemoryBackend::new(Arc::clone(&cgroup_manager));
    let memory_backend2 = MemoryBackend::new(Arc::clone(&cgroup_manager));

    memory_backend.say_hello();
    memory_backend2.say_hello();

//    let blkio_backend = BlkioBackend::new(Arc::clone(&cgroup_manager));

    backends_manager.add_backend(Box::new(memory_backend));
//    backends_manager.add_backend(Box::new(blkio_backend));

    backends_manager.get_all_metrics();
}

