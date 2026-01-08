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
add-apt-repository ppa:ondrej/php
apt install php8.2 php8.2-fpm php8.2-curl php8.2-intl php8.2-mbstring php8.2-mysql php8.2-zip php8.2-gd php8.2-xml php8.2-soap php8.2-bcmath php8.2-bz2
apt install nginx composer
cp etc/supervisor-admin-agent.conf /etc/supervisor/conf.d/admin-agent.conf # нужно из папки etc файлы скопировать


adduser -q trader1
usermod -a -G supervisor trader1

cp etc/supervisor-example.conf /etc/supervisor/conf.d/traders.conf # нужно из папки etc файлы скопировать

# run deploy from github actions (нужно ещё ветку deploy-bots сделать rebase от master, а также добавить в файл deploy-pool.yml новый сервер )
# сохраняем локально проект и далее в терминале
# git checkout master — переключиться на ветку master.
# git pull — подтянуть изменения с удалённого репозитория в текущую ветку (master).
# git checkout deploy-bots — переключиться на ветку deploy-bots.
# git pull — подтянуть изменения в deploy-bots.
# git rebase master — перенести (перепроиграть) коммиты deploy-bots поверх актуального master.
# git push -f — принудительно отправить изменения в удалённую deploy-bots (переписывает историю на сервере).

mysql_secure_installation
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'your-password';
FLUSH PRIVILEGES;

service supervisor restart

# repeat deploy from github actions
```
