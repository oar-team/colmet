use std::collections::HashMap;
use std::sync::{Arc};

use crate::backends::memory::MemoryBackend;
use crate::backends::cpu::CpuBackend;

use crate::backends::metric::Metric;
use crate::cgroup_manager::CgroupManager;
use crate::CliArgs;
use std::time::SystemTime;
use crate::backends::perfhw::PerfhwBackend;

pub(crate) mod metric;

mod memory;
mod cpu;
mod perfhw;

use std::cell::RefCell;
use std::rc::Rc;


// start backends and periodically fetch all of them to get the metrics

// used to send more little messages on the network, metric names are replaced by an id, this list must be the same in colmet-collector
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
        ("cpu_cycles", 37), // Perfhw Backend
        ("instructions", 38),
        ("cache_references", 39),
        ("cache_misses", 40),
        ("branch_instructions", 41),
        ("branch_misses", 42),
        ("bus_cycles", 43),
        ("ref_cpu_cycles", 44),
        ("cache_l1d", 45),
        ("cache_ll", 46),
        ("cache_dtlb", 47),
        ("cache_itlb", 48),
        ("cache_bpu", 49),
        ("cache_node", 50),
        ("cache_op_read", 51),
        ("cache_op_prefetch", 52),
        ("cache_result_access", 53),
        ("cpu_clock", 54),
        ("task_clock", 55),
        ("page_faults", 56),
        ("context_switches", 57),
        ("cpu_migrations", 58),
        ("page_faults_min", 59),
        ("page_faults_maj", 60),
        ("alignment_faults", 61),
        ("emulation_faults", 62),
        ("dummy", 63),
        ("bpf_output", 64),
        ].into_iter().collect();
}

// replace metric names by their id
pub fn compress_metric_names(metric_names: Vec<String>) -> Vec<i32> {
        let mut res: Vec<i32> = Vec::new();
        for metric_name in metric_names {
            res.push(*METRIC_NAMES_MAP.get(metric_name.as_str()).unwrap());
        }
        res
}

pub trait Backend {
    fn say_hello(&self); // for debug
    fn get_backend_name(&self) -> String;
    fn open(&self);
    fn close(&self);
    fn get_metrics(& self) -> HashMap<i32, Metric>;
    fn set_metrics_to_get(& self, metrics_to_get: Vec<String>);
}

pub struct BackendsManager {
    backends: Rc<RefCell<Vec<Box<dyn Backend>>>>,
}

impl BackendsManager {
    pub fn new() -> BackendsManager {
        let backends = Rc::new(RefCell::new(Vec::new()));
        BackendsManager { backends }
    }

    pub fn init_backends(& self, cli_args: CliArgs, cgroup_manager : Arc<CgroupManager>) ->  Rc<RefCell<Vec<Box<dyn Backend>>>> {
        let memory_backend = MemoryBackend::new(cgroup_manager.clone());
        let cpu_backend = CpuBackend::new(cgroup_manager.clone());

        let perfhw_backend = PerfhwBackend::new(cgroup_manager.clone());

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
        self.add_backend(Box::new(perfhw_backend));

        return self.backends.clone();
    }

    pub fn add_backend(& self, backend: Box<dyn Backend>) {
        (*self.backends).borrow_mut().push(backend);
    }


    pub fn get_all_metrics(& self) -> HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)> {
        let timestamp = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap().as_millis() as i64;
        let mut metrics: HashMap<i32, (String, i64, Vec<(String, Vec<i32>, Vec<i64>)>)>= HashMap::new();

        let b = (*self.backends).borrow();
        let bi = b.iter();
        for backend in bi {
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

