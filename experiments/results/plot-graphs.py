import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import csv
import pandas as pd
import os
from glob import glob
from pathlib import Path
import time
import seaborn as sns

DOCKER_CPU_PIE = True
DOCKER_MEM_PIE = True
SYSTEM_CPU_BAR = True
SYSTEM_LOAD_BAR = True
SYSTEM_RAM_BAR = True

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/OSM Results/2_16/Final"
_OUT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/OSM Results/2_16/Graphs"

cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-CPU-Final-Results.csv')) if "System" not in y]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-MEM-Final-Results.csv'))]
sys_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-CPU-Final-Results.csv'))]
sys_load_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-Load-Final-Results.csv'))]
sys_ram_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-RAM-Final-Results.csv'))]

start_time = time.time()

##############################################
# Docker CPU Bar Chart 
##############################################

if DOCKER_CPU_PIE:
    for _cpu_files in cpu_files:
        cpu_title = (Path(_cpu_files).name).split("-CPU")[0]
        print(cpu_title)
        print(_cpu_files)

        df = pd.read_csv(_cpu_files)
        df = df.sort_values('CPU Mean')
        docker_col = df['Docker Container']
        value_col = df['CPU Mean']
        # df = df.sort_values('CPU Run1')
        # df = df.sort_values('CPU Run2')
        # df = df.sort_values('CPU SD')
        # cpu_run1 = df['CPU Run1']
        # cpu_run2 = df['CPU Run2']
        # e = df['CPU SD']
        width = 0.30
        _title = "CPU"
        plt.style.use('seaborn')
        plt.figure(figsize=(10,6))
        a=sns.barplot(docker_col,value_col,color='blue')
        #df = df.round({'CPU Mean': 2})
        for p in a.patches:
             a.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', fontsize=11, color='blue',fontweight='bold', xytext=(0, 20),
                 textcoords='offset points')
        #plt.errorbar(cpu_run1,cpu_run2, yerr=e, fmt='o')
        plt.xticks(rotation=-90)
        plt.title(cpu_title,fontsize=25)
        plt.xlabel("Dockers",fontsize=20)
        plt.ylabel("CPU Mean",fontsize=20)
        #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # plt.axis('equal')
        # plt.legend(docker_col, loc='best', fontsize=10,labels=['%s - %f' % (l, s) for l, s in zip(docker_col, value_col)], bbox_to_anchor=(1, 1))
        plt.savefig('{}/{}-CPU.png'.format(_OUT_PATH, cpu_title),bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# Docker MEM Bar Chart 
##############################################

if DOCKER_MEM_PIE:
    for _mem_files in mem_files:
        mem_title = (Path(_mem_files).name).split("-MEM")[0]
        print(mem_title)
        print(_mem_files)

        df = pd.read_csv(_mem_files)
        df = df.sort_values('MEM Mean')
        docker_col = df['Docker Container']
        value_col = df['MEM Mean']
        plt.style.use('seaborn')
        plt.figure(figsize=(10,6))
        a=sns.barplot(docker_col,value_col,color='blue')
        #df = df.round({'CPU Mean': 2})
        for p in a.patches:
             a.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', fontsize=11, color='blue',fontweight='bold', xytext=(0, 15),
                 textcoords='offset points')
        plt.xticks(rotation=-90)
        plt.title(mem_title,fontsize=25)
        plt.xlabel("Dockers",fontsize=20)
        plt.ylabel("MEM Mean",fontsize=20)

        plt.savefig('{}/{}-MEM.png'.format(_OUT_PATH, mem_title),bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# System CPU Bar Chart 
##############################################

if SYSTEM_CPU_BAR:
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


    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()


##############################################
# System LOAD Bar Chart 
##############################################

if SYSTEM_LOAD_BAR:

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
    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

##############################################
# System RAM Bar Chart 
##############################################

if SYSTEM_RAM_BAR:

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
    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()


#########################################
# END
#########################################

print("Total time: {}".format(time.time() - start_time))

