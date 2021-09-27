# Wownero Funding System

![whoop](https://i.imgur.com/xVS3UGq.png)

A simple Flask application for managing donations.

Example
-------

[https://funding.wownero.com](https://funding.wownero.com)

## Installation

Good luck with trying to get this to run! Some pointers:


#### Install Wownero
https://github.com/wownero-project/wownero
```bash
git clone https://github.com/wownero-project/wownero.git
  sudo apt update && sudo apt install build-essential cmake pkg-config libboost-all-dev libssl-dev libzmq3-dev libunbound-dev libsodium-dev libunwind8-dev liblzma-dev libreadline6-dev libldns-dev libexpat1-dev libpgm-dev libhidapi-dev libusb-1.0-0-dev libprotobuf-dev protobuf-compiler libudev-dev git -y
  git clone https://git.wownero.com/wownero/wownero && cd wownero
  make -j$(nproc)
```
find the binaries and then run the wallet cli, and create a wallet.


#### Daemon

First make sure the daemon is up.

```bash
./wownerod --max-concurrency 4
```

#### Wallet RPC

Expose wallet via RPC.

```bash
./wownero-wallet-rpc --rpc-bind-port 45678 --disable-rpc-login --wallet-file yourwallet --password ""
```

#### Install postgres
https://tecadmin.net/how-to-install-postgresql-in-ubuntu-20-04/
step 1 through step 3


#### Web application

Download application and configure.

```

sudo apt install libjpeg-dev libpng-dev python3 redis-server postgresql-server-dev-*
sudo apt install python3-virtualenv
sudo apt install python3.8-venv
git clone https://git.wownero.com/wownero/wownero-funding-system.git
cd wownero-funding-system
python3 -m venv yourvirtualenviornment
source yourvirtualenviornment/bin/activate
pip uninstall pillow
pip install wheel
pip install -r requirements.txt
CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
cp settings.py_example settings.py
- change settings accordingly
```
eg change the psql_pass to your database password, psql_db to your database name

Run the application:

```bash
python run_dev.py
```

Beware `run_dev.py` is meant as a development server.

When running behind nginx/apache, inject `X-Forwarded-For`.

### Setting Up Admins
go into your postgres user then
```
// substitute postgres with whatever username you set up in the postgres step
sudo su - postgres
psql
```

select your database
```
\dt
\c yourdatabasename
```

find the user_id of the user you want to turn into an admin, then do:
```
SELECT * FROM users;
UPDATE users SET admin = TRUE WHERE user_id = your_number;
```
### Contributors

- [camthegeek](https://github.com/camthegeek)

### License

© 2018 WTFPL – Do What the Fuck You Want to Public License
