import requests
import os
import time

HOST_URL = "osmmano.cs.upb.de"

experiment_timestamps = {}

experiment_timestamps["start_time"] = int(time.time())
time.sleep(2)
experiment_timestamps["end_time"] = int(time.time())                                 

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

nit = experiment_timestamps["start_time"]
createFolder("./{nit}/".format(nit=nit))

system_charts = {
    "system.cpu" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.cpu&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL,after=experiment_timestamps["start_time"],before=experiment_timestamps["end_time"])
    },
    "system.load" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.load&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
    },
    "system.ram" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.ram&format=datasource&after={after}&before={before}&format=csv&options=nonzero".format(host=HOST_URL, after=experiment_timestamps['start_time'], before=experiment_timestamps["end_time"])
    },
    "system.net" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.net&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
    },
    "system.io" : { 
        "url": "http://{host}:19999/api/v1/data?chart=system.io&format=datasource&after={after}&before={before}&format=csv&group=average&gtime=0&datasource&options=nonzeroseconds".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"])
    }
    }

for _sc, value  in system_charts.items():
    print(_sc)
    try:
        # TODO: make verify=false as a fallback
        r = requests.get(value["url"], verify=False)
    except Exception as e:
        print(str(e))

    if r.status_code == requests.codes.ok:
        print("success")

    with open('./{nit}/{sc}.csv'.format(nit=nit,sc=_sc), 'w') as csv_file:
        csv_file.write(r.text)
                

print("http://{host}:9000/?host={host}&after={after}&before={before}".format(host=HOST_URL, after=experiment_timestamps["start_time"], before=experiment_timestamps["end_time"]))