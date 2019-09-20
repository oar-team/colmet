extern crate inotify;
extern crate regex;

use std::borrow::BorrowMut;
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::thread;

use inotify::{
    EventMask,
    Inotify,
    WatchMask,
};
use regex::Regex;


pub struct CgroupManager {
    cgroups: Mutex<HashMap<i32, String>>, // cgroup corresponding to user jobs, keys : cgroup id, values : cgroup name
    regex_job_id: String, // regex to find the cpuset directory
    initial_sample_period: f64, // sample period as defined by command line argument at the start of colmet
    current_sample_period: Arc<Mutex<f64>>, // current sample period, it can be changed by user by sending a new config with 0mq
}

impl CgroupManager {
    pub fn new(regex_job_id: String, cgroup_rootpath: String, current_sample_period: Arc<Mutex<f64>>, initial_sample_period: f64) -> Arc<CgroupManager> {
        let cgroups = Mutex::new(HashMap::new());
        let regex_job_id = regex_job_id;
        let cgroup_rootpath = cgroup_rootpath;
        let res = Arc::new(CgroupManager { cgroups, regex_job_id, initial_sample_period, current_sample_period });
        notify_jobs(Arc::clone(&res), cgroup_rootpath.clone());
        res
    }

    pub fn add_cgroup(&self, id: i32, name: String) {
        let mut map = self.cgroups.lock().unwrap();
        map.borrow_mut().insert(id, name);
    }

    pub fn remove_cgroup(&self, id: i32) {
        let mut map = self.cgroups.lock().unwrap();
        map.borrow_mut().remove(&id);
        *(&*self.current_sample_period).lock().unwrap() = self.initial_sample_period;
    }

    pub fn get_cgroups(&self) -> HashMap<i32, String> {
        self.cgroups.lock().unwrap().clone()
    }

    pub fn print_cgroups(&self) {
        println!("{:#?}", self.cgroups);
    }
}

// scan cpuset directory for changes and update cgroups list
pub fn notify_jobs(cgroup_manager: Arc<CgroupManager>, cgroup_rootpath: String) {
    let regex_job_id = Regex::new(&cgroup_manager.regex_job_id).unwrap();
    println!("{:#?}", cgroup_rootpath);
    let cgroups = fs::read_dir(cgroup_rootpath.clone()).unwrap();
    for cgroup in cgroups {
        let path = cgroup.unwrap().path();
        let cgroup_name = path.file_name().unwrap().to_str().unwrap();
        if let Some(v) = regex_job_id.find(cgroup_name) {
            cgroup_manager.add_cgroup(*(&cgroup_name[v.start() + 1..v.end()].parse::<i32>().unwrap()), cgroup_name.to_string())
        }
    }

    let mut inotify = Inotify::init()
        .expect("Failed to initialize inotify");

    let current_dir = PathBuf::from(cgroup_rootpath);

    inotify
        .add_watch(
            current_dir,
            WatchMask::MODIFY | WatchMask::CREATE | WatchMask::DELETE,
        )
        .expect("Failed to add inotify watch");

    println!("Watching current directory for activity...");

    let mut buffer = [0u8; 4096];

    let _child = thread::spawn(move || {
        loop {
            let events = inotify
                .read_events_blocking(&mut buffer)
                .expect("Failed to read inotify events");

            for event in events {
                cgroup_manager.print_cgroups();

                if event.mask.contains(EventMask::ISDIR) {
                    let cgroup_name = event.name.unwrap().to_str().unwrap();

                    if event.mask.contains(EventMask::CREATE) {
                        if let Some(v) = regex_job_id.find(cgroup_name) {
                            cgroup_manager.add_cgroup(*(&cgroup_name[v.start() + 1..v.end()].parse::<i32>().unwrap()), cgroup_name.to_string())
                        }
                    } else if event.mask.contains(EventMask::DELETE) && regex_job_id.is_match(cgroup_name) {
                        if let Some(v) = regex_job_id.find(cgroup_name) {
                            cgroup_manager.remove_cgroup(*(&cgroup_name[v.start() + 1..v.end()].parse::<i32>().unwrap()));
                        }
                    }
                }
            }
        }
    });
}
