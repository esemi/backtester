```shell
apt-get update
apt-get install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt install supervisor python3.11 python3.11-venv redis mysql-server mytop net-tools

curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

python3.10 -m pip install --upgrade setuptools
python3.11 -m pip install --upgrade setuptools

groupadd supervisor
usermod -a -G supervisor root
vi /etc/supervisor/supervisord.conf  # change chown and chmod params
service supervisor restart

mkdir -p /var/log/trader
chown -R root:supervisor /var/log/trader
chmod -R 0775 /var/log/trader

adduser admin-agent
usermod -a -G supervisor admin-agent

adduser -q trader1
usermod -a -G supervisor trader1

cp etc/supervisor-example.conf /etc/supervisor/conf.d/traders.conf

# run deploy from github actions

mysql_secure_installation
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'your-password';
FLUSH PRIVILEGES;

service supervisor restart

# repeat deploy from github actions
```