```shell

#--------------root доступ-------------------------
sudo passwd root
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sudo systemctl restart ssh
su
#-------------установка время UTC-------------------
sudo timedatectl set-timezone UTC
sudo timedatectl set-ntp true
timedatectl

#------------------------------------SEMEN SETUP--------------------------------------------
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
vi /etc/supervisor/supervisord.conf  # установить chown=root:supervisor и chmod=0770
service supervisor restart

mkdir -p /var/log/trader
chown -R root:supervisor /var/log/trader
chmod -R 0775 /var/log/trader

adduser admin-agent
usermod -a -G supervisor admin-agent
add-apt-repository ppa:ondrej/php
apt install php8.2 php8.2-fpm php8.2-curl php8.2-intl php8.2-mbstring php8.2-mysql php8.2-zip php8.2-gd php8.2-xml php8.2-soap php8.2-bcmath php8.2-bz2
apt install nginx composer
scp C:\Users\serjl\backtester\etc\supervisor-admin-agent.conf root@62.171.151.136:/tmp/ #Сделай так на локальной машине (PowerShell):
#cp etc/supervisor-admin-agent.conf /etc/supervisor/conf.d/admin-agent.conf # нужно из папки etc файлы скопировать
sudo cp /tmp/supervisor-admin-agent.conf /etc/supervisor/conf.d/admin-agent.conf
sudo service supervisor restart


# adduser -q trader1
# usermod -a -G supervisor trader1
# чтоб массов это сделать и PASS123 меняем на свой пароль
PASS='yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6'
for i in $(seq 1 50); do
  adduser -q --disabled-password --gecos "" trader$i
  usermod -a -G supervisor trader$i
  echo "trader$i:$PASS" | chpasswd
done

scp C:\Users\serjl\backtester\etc\supervisor-example.conf root@62.171.151.136:/tmp/ #Сделай так на локальной машине (PowerShell):
#cp etc/supervisor-example.conf /etc/supervisor/conf.d/traders.conf # нужно из папки etc файлы скопировать
sudo cp /tmp/supervisor-example.conf /etc/supervisor/conf.d/traders.conf
sudo service supervisor restart

# run deploy from github actions 
# (нужно ещё ветку deploy-bots сделать rebase от master, а также добавить в файл deploy-pool.yml новый сервер )
# run deploy from github actions 
# (нужно ещё ветку deploy-bots сделать rebase от master, а также добавить в файл deploy-pool.yml новый сервер )
# сохраняем локально проект и далее в терминале
git checkout master      # переключиться на ветку master.
git pull                 # подтянуть изменения с удалённого репозитория в текущую ветку (master).
git checkout deploy-bots # переключиться на ветку deploy-bots.
git pull                 # подтянуть изменения в deploy-bots.
git rebase master        # перенести (перепроиграть) коммиты deploy-bots поверх актуального master.
git push -f              # принудительно отправить изменения в удалённую deploy-bots (переписывает историю на сервере).

mysql_secure_installation
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!';
FLUSH PRIVILEGES;
exit

service supervisor restart

# repeat deploy from github actions

#как пушить изменения в файле с локально на гит
git status -sb                                                #Проверить статус:
git add etc/host-setup.md .github/workflows/deploy-pool.yml   #Добавить нужные файлы:
git commit -m "Update deploy pool and host setup docs"        #Сделать коммит:
git push origin master

#------------------------------------SASHA SETUP--------------------------------------------

# скопировать файлы sim-agent-create-state-empty-files.sh и db-for-agent.sql в /home/admin-agent
# добавить admin-agent в sudoers, зайди под пользователем с правами sudo
# заходим под root
sudo usermod -aG sudo admin-agent
su - admin-agent #перелогиниться
sudo chown admin-agent:admin-agent /home/admin-agent/sim-agent-create-state-empty-files.sh
sudo chmod 0760 /home/admin-agent/sim-agent-create-state-empty-files.sh
sudo ./sim-agent-create-state-empty-files.sh
  #	(должны сообщения выйти "Файл создан и права установлены для Х") 50 раз
mkdir -p ~/.ssh && chmod 700 ~/.ssh
sudo apt-get update
sudo apt-get install nano
nano ~/.ssh/id_rsa
# скопировать ключ (файл в папке) id_rsa
# вставить - клик правой кнопкой мыши
# Ctrl+O → Enter → Ctrl+X
echo -e "Host github.com\n    HostName github.com\n    IdentityFile ~/.ssh/id_rsa\n    User git" > ~/.ssh/config
chmod 0600 ~/.ssh/config && chmod 0600 ~/.ssh/id_rsa
su
# ввести рут пароль, ентер
mkdir -p /home/admin-agent/www #создать папку если нет
#rm -rf ./www/* #если папка была удаляет всё содержимое внутри папки www в текущей директории
sudo chown -R admin-agent:admin-agent ./www
bash -c 'echo "# Файл конфига
	server {
		listen 80 default_server;
		listen [::]:80 default_server;

		root /home/admin-agent/www/public;

		index index.php;

		server_name _;

		location / {
			try_files \$uri \$uri/ /index.php?\$args;
		}

		location ~ \.php$ {
			include snippets/fastcgi-php.conf;
			fastcgi_pass unix:/run/php/php8.2-fpm.sock;
		}

		location ~ /\.ht {
			deny all;
		}
	}" > /etc/nginx/sites-available/default'
chown admin-agent:admin-agent /run/php/php8.2-fpm.sock
sudo sed -i 's/^user .*;/user admin-agent;/g' /etc/nginx/nginx.conf
# заменить пользователя /etc/php/8.2/fpm/pool.d : user = admin-agent и listen.owner = admin-agent
	sudo sed -i 's/^\(user\s*=\s*\).*/\1admin-agent/g' /etc/php/8.2/fpm/pool.d/*.conf
	sudo sed -i 's/^\(listen\.owner\s*=\s*\).*/\1admin-agent/g' /etc/php/8.2/fpm/pool.d/*.conf
systemctl restart php8.2-fpm
systemctl reload nginx
exit
#заходим под admin-agent
git clone git@github.com:lxdianov/sim_agent.git ./www
# отвечаем yes
cd www
nano .env
# открываем .env из папки - заменяем IP адрес сервера и копируем в буфер (APP_URL=http://IP) допусти (APP_URL=http://55.55.55.55)
# вставляем правой кнопкой мыши
Ctrl+O → Enter → Ctrl+X
composer install

mysql -uroot -p
# вводим пароль mysql из буфера правым кликом, enter
create database thesim;
USE thesim;
\. /home/admin-agent/db-for-agent.sql
exit

php artisan app:clear
# на вопросы: очистить БД? -> yes (если первый запуск), пароль MySQL ввести

#-------------------если потребуется-----------------
php artisan migrate
# yes
php artisan app:clear
# очистить БД? -> no
#---------------------------------------------------

php artisan up

# проверка в браузере http://<IP>/
supervisorctl start sim_agent_worker:*
php artisan queue:restart

php artisan app:setup-token
# yes
php artisan optimize:clear && php artisan queue:restart

crontab -l # должно написать no crontab for admin-agent
(crontab -l 2>/dev/null; echo "* * * * * cd /home/admin-agent/www && php artisan schedule:run >> /dev/null 2>&1") | crontab -
crontab -l # * * * * * cd /home/admin-agent/www && php artisan schedule:run >> /dev/null 2>&1


# команды для supervisor
# Статус всех программ
sudo supervisorctl status

# Перезапустить supervisor (сервис)
sudo systemctl restart supervisor

# Подтянуть изменения в конфиге
sudo supervisorctl reread
sudo supervisorctl update

# Запуск / остановка / рестарт одной программы
sudo supervisorctl start <name>
sudo supervisorctl stop <name>
sudo supervisorctl restart <name>

# Запустить/остановить все программы
sudo supervisorctl start all
sudo supervisorctl stop all
sudo supervisorctl restart all

# Перезапустить все программы из конфигов
sudo supervisorctl restart all

# Запустить серию трейдеров 1..50
for i in $(seq 1 50); do sudo supervisorctl start trader$i; done

# Статус только трейдеров
sudo supervisorctl status | grep trader

# Автозапуск ботов после обновления/ребута
# (включить autostart/autorestart для всех trader*)
sudo sed -i 's/^autostart=false/autostart=true/g; s/^autorestart=false/autorestart=true/g' /etc/supervisor/conf.d/traders.conf
sudo supervisorctl reread
sudo supervisorctl update


```
tail -n 200 /var/log/trader/trader1-log.txt | egrep "tick |skip buy|invest body|debug:|state saved|ERROR|Traceback"
