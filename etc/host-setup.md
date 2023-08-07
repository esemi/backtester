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
vi /etc/supervisor/supervisor.conf  # change chown and chmod params

adduser trader1
usermod -a -G supervisor trader1
usermod -a -G supervisor root
service supervisor restart

vi /etc/supervisor/conf.d/trader1.conf

# run deploy from github actions

service supervisor restart

vi /etc/nginx/sites-enabled/trader.conf
mkdir /var/www/trader
chown root:supervisor /var/www/trader 
chmod 0771 /var/www/trader
usermod -a -G supervisor www-data
```