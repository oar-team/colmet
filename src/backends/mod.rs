use std::collections::HashMap;
use std::sync::{Arc};

use crate::backends::memory::MemoryBackend;
use crate::backends::cpu::CpuBackend;

use crate::backends::metric::Metric;
use crate::cgroup_manager::CgroupManager;
use crate::CliArgs;
use std::time::SystemTime;

pub(crate) mod metric;

mod memory;
mod cpu;

lazy_static! {
static ref METRIC_NAMES_MAP: HashMap<&'static str, i32> = vec![
        ("cache", 1), // Memory Backend
        ("rss", 2),
        ("rss_huge", 3),
        ("shmem", 4),
        ("mapped_file", 5),
        ("dirty", 6),
        ("writeback", 7),
        ("pgpgin", 8),
        ("pgpgout", 9),
        ("pgfault", 10),
        ("pgmajfault", 11),
        ("inactive_anon", 12),
        ("active_anon", 13),
        ("inactive_file", 14),
        ("active_file", 15),
        ("unevictable", 16),
        ("hierarchical_memory_limit", 17),
        ("total_cache", 18),
        ("total_rss", 19),
        ("total_rss_huge", 20),
        ("total_shmem", 21),
        ("total_mapped_file", 22),
        ("total_dirty", 23),
        ("total_writeback", 24),
        ("total_pgpgin", 25),
        ("total_pgpgout", 26),
        ("total_pgfault", 27),
        ("total_pgmajfault", 28),
        ("total_inactive_anon", 29),
        ("total_active_anon", 30),
        ("total_inactive_file", 31),
        ("total_active_file", 32),
        ("total_unevictable", 33),
        ("nr_periods", 34), // Cpu Backend
        ("nr_throttled", 35),
        ("throttled_time", 36),
        ].into_iter().collect();
}

pub fn compress_metric_names(metric_names: Vec<String>) -> Vec<i32> {
        let mut res: Vec<i32> = Vec::new();
        for metric_name in metric_names {
            res.push(*METRIC_NAMES_MAP.get(metric_name.as_str()).unwrap());
        }
        res
}


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
    pub fn new() -> BackendsManager {
        let backends = Vec::new();
        BackendsManager { backends }
    }

    pub fn init_backends(&mut self, cli_args: CliArgs, cgroup_manager : Arc<CgroupManager>) {
        let memory_backend = MemoryBackend::new(cgroup_manager.clone());
        let cpu_backend = CpuBackend::new(cgroup_manager.clone());

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
        self.add_backend(Box::new(memory_backend));
        self.add_backend(Box::new(cpu_backend));

    }

    pub fn add_backend(&mut self, backend: Box<dyn Backend>) {
        self.backends.push(backend);
    }


    pub fn get_all_metrics(&mut self) -> HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)> {
        let timestamp = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis() as i64;
        let mut metrics: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)>= HashMap::new();
        for backend in &mut self.backends {
            for (job_id, metric) in backend.get_metrics() {
                match metrics.get_mut(&job_id) {
                    Some(tmp) => {
                        let (_hostname, _timestamp, m) = tmp;
                        m.push((metric.backend_name, compress_metric_names(metric.metric_names), metric.metric_values.unwrap()));

                    },
                    None => {
                        metrics.insert(job_id, (metric.hostname, timestamp, vec![(metric.backend_name, compress_metric_names(metric.metric_names), metric.metric_values.unwrap() )]));
                    },
                }
            }
        }
        metrics
    }
}

