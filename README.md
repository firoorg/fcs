# Firo Funding System

A simple Flask application for managing donations.

Example
-------

[https://fcs.firo.org](https://fcs.firo.org)

## Installation

Good luck with trying to get this to run! Some pointers:

Make sure you have a machine with about 200GB of space.


### How to install Firo Wallet/Node on Ubuntu

#### Download and unzip last release 

<code>wget https://github.com/firoorg/firo/releases/download/v0.14.8.0/firo-0.14.8.0-linux64.tar.gz | tar -xvf</code>

#### Send files to binary folder

<code>cd firo-0.14.8; cp bin/* /usr/local/bin</code>
```
firo-cli help
```

#### Create config file
nano /root/.firo/firo.config

<pre>
#----
rpcuser=user
rpcpassword=password
rpcallowip=127.0.0.1
rpcport=8332
#----
listen=1
server=1
daemon=1
logtimestamps=1
txindex=1
</pre>

#### Run node as daemon with systemctl
https://github.com/firoorg/firo/wiki/Configuring-masternode-with-systemd


### Install postgres
```
sudo apt install aptitude
sudo aptitude install postgresql postgresql-contrib
```
https://tecadmin.net/how-to-install-postgresql-in-ubuntu-20-04/


### Web application

Download application and configure.

```

sudo apt install libjpeg-dev libpng-dev python3 redis-server postgresql-server-dev-*
sudo apt install python3-virtualenv
sudo apt install python3-venv
git clone https://github.com/firoorg/fcs.git
cd fcs
python3 -m venv yourvirtualenviornment
source yourvirtualenviornment/bin/activate
pip uninstall pillow
pip install wheel
pip install -r requirements.txt
CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
cp settings.py_example settings.py
- change settings.py accordingly
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

© 2022 WTFPL – Do What the Fuck You Want to Public License
