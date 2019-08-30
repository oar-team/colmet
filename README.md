# Colmet-rust

Start of a rewrite of colmet-node in rust.

Test it on Grid5000:

- Start a job

`oarsub -I`

- Install Rust

`curl https://sh.rustup.rs -sSf | sh`

`source $HOME/.cargo/env`

- Start Colmet-node

`cargo run`

...


Code architecture :
![colmet rust architecture](https://raw.githubusercontent.com/oar-team/colmet/colmet-rust/colmet%20rust.png)
 
