use std::collections::HashMap;
use std::cell::RefCell;
extern crate inotify;
use std::thread::sleep;
use std::thread;

use std::env;

use inotify::{
    EventMask,
    WatchMask,
    Inotify,
};


pub struct CgroupManager {
    cgroups: RefCell<HashMap<i32, String>>,
}

impl CgroupManager {
    pub fn new() -> CgroupManager {
        let cgroups = RefCell::new(HashMap::new());
        CgroupManager {cgroups}
    }

     pub fn add_cgroup(& self, id: i32, name: String) {
         self.cgroups.borrow_mut().insert(id, name);
    }

     pub fn remove_cgroup(& self, id: i32){
         self.cgroups.borrow_mut().remove(&id);
    }

     pub fn print_cgroups(& self){
        println!("{:#?}", self.cgroups);
    }

    pub fn say_hello() {
        println!("hello my name is cgroup manager");
    }
}

pub fn not() {
    let mut inotify = Inotify::init()
        .expect("Failed to initialize inotify");

    let current_dir = env::current_dir()
        .expect("Failed to determine current directory");

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
            print_ok();
            let events = inotify
                .read_events_blocking(&mut buffer)
                .expect("Failed to read inotify events");

            for event in events {
                if event.mask.contains(EventMask::CREATE) {
                    if event.mask.contains(EventMask::ISDIR) {
                        println!("Directory created: {:?}", event.name);
                    } else {
                        println!("File created: {:?}", event.name);
                    }
                } else if event.mask.contains(EventMask::DELETE) {
                    if event.mask.contains(EventMask::ISDIR) {
                        println!("Directory deleted: {:?}", event.name);
                    } else {
                        println!("File deleted: {:?}", event.name);
                    }
                } else if event.mask.contains(EventMask::MODIFY) {
                    if event.mask.contains(EventMask::ISDIR) {
                        println!("Directory modified: {:?}", event.name);
                    } else {
                        println!("File modified: {:?}", event.name);
                    }
                }
            }
        }
    });
}


fn print_ok(){
    println!("ok");
}