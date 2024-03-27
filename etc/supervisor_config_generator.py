
template = """[program:trader{0}]
directory=/home/trader{0}
command=/home/trader{0}/venv/bin/python -m app.trader
user=trader{0}
stopsignal=INT
autorestart=false
autostart=true
stderr_logfile=/var/log/trader/trader{0}-log.txt
stderr_logfile_maxbytes=5MB
stderr_logfile_backups=10
stdout_logfile=/var/log/trader/trader{0}-stats.txt
stdout_logfile_maxbytes=100KB
stdout_logfile_backups=1
"""

if __name__ == '__main__':
    for i in range(1, 41):
        print(template.format(i))
