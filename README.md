# Colmet-rust

Start of a rewrite of colmet-node in rust.

Test it on Grid5000:

- Start a job

`oarsub -I`

- Install Rust

`curl https://sh.rustup.rs -sSf | sh`

`source $HOME/.cargo/env`

- Clone Colmet repository and cd into it

`git clone --single-branch --branch colmet-rust https://github.com/oar-team/colmet.git`

`cd Colmet`

- Install ZeroMQ

`apt-get install libzmq3-dev`

- Install MsgPack (for collector)

`pip3 install msgpack`

- Compile and start Colmet-node

`cargo run -- -vvv`

- Start Colmet-collector (in another terminal in the same job)

`python3 ./collector/main.py`


Code architecture :
![colmet rust architecture](https://raw.githubusercontent.com/oar-team/colmet/colmet-rust/colmet%20rust.png)
 
