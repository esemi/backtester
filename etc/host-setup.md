```shell
apt-get update
apt-get install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt install supervisor python3.11 python3.11-venv nginx

curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

python3.10 -m pip install --upgrade setuptools
python3.11 -m pip install --upgrade setuptools

groupadd supervisor
usermod -a -G supervisor root
vi /etc/supervisor/supervisor.conf  # change chown and chmod params

mkdir -p /var/log/trader

adduser trader1
usermod -a -G supervisor trader1
service supervisor restart

cp etc/supervisor-example.conf /etc/supervisor/conf.d/traders.conf

# run deploy from github actions

service supervisor restart
```