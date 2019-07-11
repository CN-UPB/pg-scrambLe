import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import csv
import pandas as pd
import os
from glob import glob
from pathlib import Path
import time

_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/OSM Results/OSM Results_set1/Final/"
cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*0-CPU-Final-Results.csv'))]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*0-MEM-Final-Results.csv'))]
sys_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-CPU-Final-Results.csv'))]
sys_load_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-Load-Final-Results.csv'))]
sys_ram_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-RAM-Final-Results.csv'))]


start_time = time.time()


# for _cpu_files in cpu_files:
#     _title = (Path(_cpu_files).name).split("-CPU")[0]
#     print(_title)
#     print(_cpu_files)

#     df = pd.read_csv(_cpu_files)
#     docker_col = df['Docker Container']
#     value_col = df['CPU Mean']
#     plt.figure(figsize=(14, 5))
#     plt.title(_title)
#     plt.pie(value_col,startangleplt.show()=45)
#     plt.axis('equal')
#     plt.legend(docker_col, loc="lower right", fontsize=10,labels=['%s - %1.1f %%' % (l, s) for l, s in zip(docker_col, value_col)])
#     plt.savefig('{}.png'.format(_title))

# for _mem_files in mem_files:
#     _title = (Path(_mem_files).name).split("-MEM")[0]
#     print(_title)
#     print(_mem_files)

#     df = pd.read_csv(_mem_files)
#     docker_col = df['Docker Container']
#     value_col = df['MEM Mean']
#     plt.figure(figsize=(14, 5))
#     plt.title(_title)
#     plt.pie(value_col,startangle=45)
#     plt.axis('equal')
#     plt.legend(docker_col, loc="lower right", fontsize=10,labels=['%s - %1.1f %%' % (l, s) for l, s in zip(docker_col, value_col)])
#     plt.savefig('{}.png'.format(_title))


# for _sys_files in sys_files:
#     _title = (Path(_sys_files).name).split("-System")[0]
#     print(_title)
#     print(_sys_files)
#     df = pd.read_csv(_sys_files)

#     divisions = [_title]
#     ylabel = df['CPU Mean']
#     index = np.arange(9)
#     width = 0.30

#     plt.bar(index, ylabel, width=0.2, color='b', align='center', label = _title)
#     plt.bar(index, ylabel, width=0.2, color='b', align='center', label = _title)
#     plt.title(_title)

#     plt.savefig('{}.png'.format(_title))


#system CPU

data_dict = {}

for _sys_cpu_files in sys_cpu_files:
    _title = (Path(_sys_cpu_files).name).split("-System-CPU")[0]
    _case = _title.split("s_")[1]
    _image = _title.split("_")[0]
    df = pd.read_csv(_sys_cpu_files)

    if not _case in data_dict:
        data_dict[_case] = {}
    
    if _image == "stress":
        data_dict[_case]["stress"] = df['CPU Mean'].mean()
    elif _image == "cirros":
        data_dict[_case]["cirros"] = df['CPU Mean'].mean()
        

    print(_title)
    print(_case)
    print(_image)
    print(_sys_cpu_files)

data = []


for _case, _data in sorted(data_dict.items()):
    data.append({
        'case': _case, 'CPU cirros': _data['cirros'], 'CPU stress': _data['stress']
    })

# data = [{'case': _case, 'CPU cirros': 1.00001, 'CPU stress':1.00010}, {'case': "case2", 'CPU cirros': 2, 'CPU stress':2}] 
  
# Creates DataFrame. 
df = pd.DataFrame(data) 
  
# Print the data 
df 

divisions = df['case']
cpu_cirros = df['CPU cirros']
cpu_stress = df['CPU stress']
index = np.arange(len(data))
width = 0.30

_title = "cpu"

plt.figure(figsize=(10,6))

plt.bar(index, cpu_cirros, width, color='b', label = 'Cirros')
plt.bar(index+width, cpu_stress, width, color='r', label = 'Stress')

plt.ylabel('System CPU Mean', fontsize=20)
plt.xlabel('Cases', fontsize=20)

plt.xticks(rotation=-30)
plt.xticks(index+width/2, divisions)


plt.legend(loc='best')


plt.savefig('{}.png'.format(_title) ,bbox_inches='tight',dpi=100)

# System Load

data_dict = {}

for _sys_load_files in sys_load_files:
    _title = (Path(_sys_load_files).name).split("-System-Load")[0]
    _case = _title.split("s_")[1]
    _image = _title.split("_")[0]
    df = pd.read_csv(_sys_load_files)

    if not _case in data_dict:
        data_dict[_case] = {}
    
    if _image == "stress":
        data_dict[_case]["stress"] = df['Load1 Mean'].mean()
    elif _image == "cirros":
        data_dict[_case]["cirros"] = df['Load1 Mean'].mean()
        

    print(_title)
    print(_case)
    print(_image)
    print(_sys_load_files)

data = []


for _case, _data in sorted(data_dict.items()):
    data.append({
        'case': _case, 'Load cirros': _data['cirros'], 'Load stress': _data['stress']
    })

# data = [{'case': _case, 'CPU cirros': 1.00001, 'CPU stress':1.00010}, {'case': "case2", 'CPU cirros': 2, 'CPU stress':2}] 
  
# Creates DataFrame. 
df = pd.DataFrame(data) 
 
# Print the data 
df 
divisions = df['case']
cpu_cirros = df['Load cirros']
cpu_stress = df['Load stress']
index = np.arange(len(data))
width = 0.30
_title = "load"
plt.figure(figsize=(10,6))
plt.bar(index, cpu_cirros, width, color='y', label = 'Cirros')
plt.bar(index+width, cpu_stress, width, color='r', label = 'Stress')
plt.ylabel('System Load Mean', fontsize=20)
plt.xlabel('Cases', fontsize=20)
plt.xticks(rotation=-30)
plt.xticks(index+width/2, divisions)
plt.legend(loc='best')
plt.savefig('{}.png'.format(_title) ,bbox_inches='tight',dpi=100)
print("Total time: {}".format(time.time() - start_time))

#System RAM

data_dict = {}

for _sys_ram_files in sys_ram_files:
    _title = (Path(_sys_ram_files).name).split("-System-RAM")[0]
    _case = _title.split("s_")[1]
    _image = _title.split("_")[0]
    df = pd.read_csv(_sys_ram_files)

    if not _case in data_dict:
        data_dict[_case] = {}
    
    if _image == "stress":
        data_dict[_case]["stress"] = df['RAM Mean'].mean()
    elif _image == "cirros":
        data_dict[_case]["cirros"] = df['RAM Mean'].mean()
        

    print(_title)
    print(_case)
    print(_image)
    print(_sys_ram_files)

data = []


for _case, _data in sorted(data_dict.items()):
    data.append({
        'case': _case, 'RAM cirros': _data['cirros'], 'RAM stress': _data['stress']
    })

# data = [{'case': _case, 'CPU cirros': 1.00001, 'CPU stress':1.00010}, {'case': "case2", 'CPU cirros': 2, 'CPU stress':2}] 
  
# Creates DataFrame. 
df = pd.DataFrame(data) 
 
# Print the data 
df 
divisions = df['case']
cpu_cirros = df['RAM cirros']
cpu_stress = df['RAM stress']
index = np.arange(len(data))
width = 0.30
_title = "ram"
plt.figure(figsize=(10,6))
plt.bar(index, cpu_cirros, width, color='y', label = 'Cirros')
plt.bar(index+width, cpu_stress, width, color='r', label = 'Stress')
plt.ylabel('System RAM Mean', fontsize=20)
plt.xlabel('Cases', fontsize=20)
plt.xticks(rotation=-30)
plt.xticks(index+width/2, divisions)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.savefig('{}.png'.format(_title) ,bbox_inches='tight',dpi=100)
print("Total time: {}".format(time.time() - start_time))





