# Colmet-rust

Start of a rewrite of colmet-node in rust.

Test it on Grid5000:

- Start a job

`oarsub -I`

- Install Rust

`sudo-g5k`

`curl https://sh.rustup.rs -sSf | sh`

`source $HOME/.cargo/env`

- Clone Colmet repository and cd into it

`git clone --single-branch --branch colmet-rust https://github.com/oar-team/colmet.git`

`cd Colmet`

- Install ZeroMQ

`sudo apt-get install libzmq3-dev`

- Install MsgPack (for collector)

`pip3 install msgpack`

- Initialize perfevent cgroup

```
sudo ln -s /sys/fs/cgroup/perf_event /dev/oar_cgroups_links/

sudo mkdir -p /dev/oar_cgroups_links/perf_event$OAR_CPUSET

echo $$ | sudo tee -a /dev/oar_cgroups_links/perf_event$OAR_CPUSET/tasks
```

- Compile perfhw library

`sudo make -C ./src/backends/`

- Compile and start Colmet-node

`cargo build`

`sudo ./target/debug/colmet-node-rust`

- Start Colmet-collector (in another terminal in the same job)

`python3 ./collector/main.py`

- You can change Colmet sample period and metrics collected by perfhw without restarting Colmet-node by sending 0mq message with this python script:

`python3 configure_colmet.py 1.5 "cache_ll,emulation_faults"`


Code architecture :
![colmet rust architecture](https://raw.githubusercontent.com/oar-team/colmet/colmet-rust/colmet%20rust.png)
 
What remains to be done :

colmet-collector : hdf5 backend, make code error-resistant regardeless the data received from colmet-node

colmet-node : several backends, handle errors (especially when backends can't access underlying monitoring tools, librairies, etc), reset metrics collected by perfhwbakend at the end of the job, and also make more tests.
