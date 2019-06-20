
# flame graph for docker 

sudo apt-get install software-properties-common
sudo apt-get update
sudo apt-get install python3.4


CONTAINER ID        IMAGE                            COMMAND                  CREATED             STATUS                 PORTS                                  NAMES
668936ca784f        opensourcemano/mon:latest        "/bin/sh -c '/bin/ba…"   10 days ago         Up 10 days (healthy)   8000/tcp                               osm_mon.1.08pgn230e3ftzmhhdgkijm4ri
f5e45fb8c07c        opensourcemano/lcm:latest        "python3 /usr/lib/py…"   10 days ago         Up 10 days (healthy)   9999/tcp                               osm_lcm.1.9zm9wv6ct04nl8b9kguvdloma
2443fea04f04        opensourcemano/pol:latest        "/bin/sh -c osm-poli…"   10 days ago         Up 10 days                                                    osm_pol.1.dz3k25uhzcfydced7fv1oi3dv
009a0a522bd1        opensourcemano/light-ui:latest   "supervisord -n"         10 days ago         Up 10 days             80/tcp                                 osm_light-ui.1.o6ih3pzs5c8ejtc7nkroupdj5
ef606cafec38        opensourcemano/nbi:latest        "python3 /usr/lib/py…"   10 days ago         Up 10 days (healthy)   9999/tcp                               osm_nbi.1.6bwh3sz921lywxvc9734zlkv1
5c0d9ae8889b        opensourcemano/keystone:latest   "/bin/sh -c ./start.…"   10 days ago         Up 10 days             5000/tcp                               osm_keystone.1.2jnj521qrx82qskkv7ji83jca
489b8f161e20        opensourcemano/ro:latest         "/bin/sh -c /bin/RO/…"   10 days ago         Up 10 days (healthy)   9090/tcp                               osm_ro.1.jcng00t4b45ep7yt2om7qyon4

mon
pyflame34 -s 10 -r 0.00001 -p 11998 -x --threads  | flamegraph.pl > child_process_profiling_2.svg

lcm
pol
lightui
nbi
keystone
ro


osmmano@osmmano:~$ docker top 668936ca784f
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                11859               11842               0                   Jun09               ?                   00:00:00            /bin/sh -c /bin/bash scripts/runInstall.sh
root                11994               11859               0                   Jun09               ?                   00:00:00            /bin/bash scripts/runInstall.sh
root                11996               11994               0                   Jun09               ?                   01:04:08            /usr/bin/python3 /usr/bin/osm-mon-server
root                11997               11994               0                   Jun09               ?                   00:04:06            /usr/bin/python3 /usr/bin/osm-mon-evaluator
root                11998               11994               0                   Jun09               ?                   00:29:39            /usr/bin/python3 /usr/bin/osm-mon-collector

osmmano@osmmano:~$ docker top f5e45fb8c07c
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                11386               11367               0                   Jun09               ?                   01:42:19            python3 /usr/lib/python3/dist-packages/osm_lcm/lcm.py

osmmano@osmmano:~$ docker top 2443fea04f04
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                9142                9124                0                   Jun09               ?                   00:00:00            /bin/sh -c osm-policy-agent
root                9209                9142                0                   Jun09               ?                   01:07:18            /usr/bin/python3 /usr/bin/osm-policy-agent

osmmano@osmmano:~$ docker top 009a0a522bd1
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3923                3825                0                   Jun09               ?                   00:02:08            /usr/bin/python /usr/bin/supervisord -n
root                6124                3923                0                   Jun09               ?                   00:00:00            nginx: master process /usr/sbin/nginx
root                6134                3923                0                   Jun09               ?                   00:00:36            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
www-data            6243                6124                0                   Jun09               ?                   00:00:42            nginx: worker process
www-data            6244                6124                0                   Jun09               ?                   00:00:09            nginx: worker process
www-data            6245                6124                0                   Jun09               ?                   00:00:41            nginx: worker process
www-data            6246                6124                0                   Jun09               ?                   00:00:41            nginx: worker process
www-data            6247                6124                0                   Jun09               ?                   00:00:41            nginx: worker process
www-data            6248                6124                0                   Jun09               ?                   00:00:33            nginx: worker process
www-data            6249                6124                0                   Jun09               ?                   00:00:41            nginx: worker process
www-data            6250                6124                0                   Jun09               ?                   00:00:41            nginx: worker process
root                7067                6134                0                   Jun09               ?                   00:00:01            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
root                7068                6134                0                   Jun09               ?                   00:00:01            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
root                7069                6134                0                   Jun09               ?                   00:00:02            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
root                7070                6134                0                   Jun09               ?                   00:00:05            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
root                7071                6134                0                   Jun09               ?                   00:00:08            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini
root                7074                6134                0                   Jun09               ?                   00:00:00            /usr/local/bin/uwsgi --ini /usr/share/osm-lightui/django.ini

osmmano@osmmano:~$ docker top ef606cafec38
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3733                3661                1                   Jun09               ?                   04:16:35            python3 /usr/lib/python3/dist-packages/osm_nbi/nbi.py

osmmano@osmmano:~$ docker top 489b8f161e20
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                3919                3789                0                   Jun09               ?                   00:00:00            /bin/sh -c /bin/RO/start.sh
root                5647                3919                0                   Jun09               ?                   00:00:00            /bin/bash /bin/RO/start.sh
root                7298                5647                0                   Jun09               ?                   00:38:49            /usr/bin/python /usr/bin/openmanod -c /etc/osm/openmanod.cfg --log-file=/var/log/osm/openmano.log --create-tenant=osm