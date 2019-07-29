use std::collections::HashMap;
use std::cell::RefCell;
use std::fs;

extern crate inotify;

extern crate regex;

use regex::Regex;

use std::thread::sleep;
use std::thread;

use std::env;
use std::path::PathBuf;

use inotify::{
    EventMask,
    WatchMask,
    Inotify,
};

use std::rc::Rc;
use std::sync::{Arc, Mutex};
use std::borrow::{BorrowMut, Borrow};


pub struct CgroupManager {
    cgroups: Mutex<HashMap<i32, String>>,
    regex_job_id: String,
    cgroup_rootpath: String,

}

impl CgroupManager {
    pub fn new(regex_job_id: String, cgroup_rootpath: String) -> Arc<CgroupManager> {
        let cgroups = Mutex::new(HashMap::new());
        let regex_job_id = regex_job_id;
        let cgroup_rootpath = cgroup_rootpath;
        let res = Arc::new(CgroupManager { cgroups, regex_job_id, cgroup_rootpath:cgroup_rootpath.clone()});
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
    }

    pub fn get_cgroups(& self) -> HashMap<i32, String>{
        self.cgroups.lock().unwrap().clone()
    }

    pub fn print_cgroups(&self) {
        println!("{:#?}", self.cgroups);
    }

    pub fn say_hello() {
        println!("hello my name is cgroup manager");
    }
}

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

    let child = thread::spawn(move || {
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
