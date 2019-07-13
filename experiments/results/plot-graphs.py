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

DOCKER_CPU_BAR = True
DOCKER_MEM_BAR = True
DOCKER_CASE_CPU_BAR = True
DOCKER_CASE_MEM_BAR = True
SYSTEM_CPU_BAR = True
SYSTEM_LOAD_BAR = True
SYSTEM_RAM_BAR = True

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/OSM Results/2_16/Final"
_OUT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/OSM Results/2_16/Graphs"

RUNS = 3 # Not fully supported
CASES = 3 # Not fully supported

cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-CPU-Final-Results.csv')) if "System" not in y]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-MEM-Final-Results.csv'))]
docker_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-CPU-Docker-Final-Results.csv')) if "System" not in y]
docker_mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-MEM-Docker-Final-Results.csv'))]
sys_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-CPU-Final-Results.csv'))]
sys_load_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-Load-Final-Results.csv'))]
sys_ram_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-RAM-Final-Results.csv'))]

start_time = time.time()

##############################################
# Docker Case CPU Bar Chart 
##############################################

if DOCKER_CASE_CPU_BAR:
    data_dict = {}

    for _docker_cpu_files in docker_cpu_files:
        _title = (Path(_docker_cpu_files).name).split("-CPU")[0]
        # _case = _title.split("s_")[1]
        # _image = _title.split("_")[0]
        df = pd.read_csv(_docker_cpu_files)
        
        for index, row in df.iterrows():
            _case, _instances = row['Case'].split("s_")[1].split("_")
            _image = row['Case'].split("_")[0]

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["stress"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "stress":
                data_dict[_case][_instances]["stress"]["mean"] = row['CPU Mean']
                data_dict[_case][_instances]["stress"]["sd"] = row['CPU SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["mean"] = row['CPU Mean']
                data_dict[_case][_instances]["cirros"]["sd"] = row['CPU SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{}'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'CPU cirros mean': _instances_data['cirros']["mean"],
                        'CPU cirros sd': _instances_data['cirros']["sd"],
                        'CPU stress mean': _instances_data['stress']["mean"],
                        'CPU stress sd': _instances_data['stress']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                cpu_cirros = df['CPU cirros mean']
                cpu_cirros_sd = df['CPU cirros sd']
                cpu_stress = df['CPU stress mean']
                cpu_stress_sd = df['CPU stress sd']
        
                index = np.arange(len(data))
                width = 0.30

                axs[_count].bar(index, cpu_cirros, width, yerr=cpu_cirros_sd, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, cpu_stress, width,yerr=cpu_stress_sd, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Stress')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('CPU Mean', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-CPU-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# Docker Case MEM Bar Chart 
##############################################

if DOCKER_CASE_MEM_BAR:
    data_dict = {}

    for _docker_mem_files in docker_mem_files:
        _title = (Path(_docker_mem_files).name).split("-MEM")[0]
        df = pd.read_csv(_docker_mem_files)
        
        for index, row in df.iterrows():
            _case, _instances = row['Case'].split("s_")[1].split("_")
            _image = row['Case'].split("_")[0]

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["stress"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "stress":
                data_dict[_case][_instances]["stress"]["mean"] = row['MEM Mean']
                data_dict[_case][_instances]["stress"]["sd"] = row['MEM SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["mean"] = row['MEM Mean']
                data_dict[_case][_instances]["cirros"]["sd"] = row['MEM SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{}'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'MEM cirros mean': _instances_data['cirros']["mean"],
                        'MEM cirros sd': _instances_data['cirros']["sd"],
                        'MEM stress mean': _instances_data['stress']["mean"],
                        'MEM stress sd': _instances_data['stress']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                mem_cirros = df['MEM cirros mean']
                mem_cirros_sd = df['MEM cirros sd']
                mem_stress = df['MEM stress mean']
                mem_stress_sd = df['MEM stress sd']
        
                index = np.arange(len(data))
                width = 0.30

                axs[_count].bar(index, mem_cirros, width, yerr=mem_cirros_sd, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, mem_stress, width,yerr=mem_stress_sd, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Stress')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('MEM Mean', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-MEM-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# Docker CPU Bar Chart 
##############################################

if DOCKER_CPU_BAR:
    for _cpu_files in cpu_files:
        cpu_title = (Path(_cpu_files).name).split("-CPU")[0]
        print(cpu_title)
        print(_cpu_files)

        df = pd.read_csv(_cpu_files)
        df = df.sort_values('CPU Mean')
        docker_col = df['Docker Container']
        value_col = df['CPU Mean']
        value_sd_col = df['CPU SD']

        width = 0.30
        plt.figure(figsize=(10,6))
        a=plt.bar(docker_col, value_col, yerr=value_sd_col, alpha=0.6, ecolor='black', capsize=5, color='blue')
 
        for p in a.patches:
             plt.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', fontsize=9, color='blue',fontweight='bold', xytext=(0, 15),
                 textcoords='offset points')

        plt.xticks(rotation=-90)
        plt.title("CPU -- {}".format(cpu_title), fontsize=25)
        plt.xlabel("Dockers", fontsize=20)
        plt.ylabel("CPU Mean", fontsize=20)

        plt.savefig('{}/{}-CPU.png'.format(_OUT_PATH, cpu_title),bbox_inches='tight', dpi=100)
        plt.close()

##############################################
# Docker MEM Bar Chart 
##############################################

if DOCKER_MEM_BAR:
    for _mem_files in mem_files:
        mem_title = (Path(_mem_files).name).split("-MEM")[0]
        print(mem_title)
        print(_mem_files)

        df = pd.read_csv(_mem_files)
        df = df.sort_values('MEM Mean')
        docker_col = df['Docker Container']
        value_col = df['MEM Mean']
        value_sd_col = df['MEM SD']

        width = 0.30
        plt.figure(figsize=(10,6))
        a=plt.bar(docker_col, value_col, yerr=value_sd_col, alpha=0.6, ecolor='black', capsize=5, color='blue')
 
        for p in a.patches:
             plt.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', fontsize=9, color='blue',fontweight='bold', xytext=(0, 15),
                 textcoords='offset points')

        plt.xticks(rotation=-90)
        plt.title("MEM -- {}".format(mem_title),fontsize=25)
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
        _case, _instances = _title.split("s_")[1].split("_")
        _image = _title.split("_")[0]
        df = pd.read_csv(_sys_cpu_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["stress"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "stress":
            data_dict[_case][_instances]["stress"]["mean"] = df['CPU Mean'].mean()
            data_dict[_case][_instances]["stress"]["sd"] = df['CPU SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['CPU Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['CPU SD'].mean()            

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System CPU', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances), 
                    'CPU cirros mean': _instances_data['cirros']["mean"],
                    'CPU cirros sd': _instances_data['cirros']["sd"],
                    'CPU stress mean': _instances_data['stress']["mean"],
                    'CPU stress sd': _instances_data['stress']["sd"]
                })
        
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
            
            divisions = df['case']
            cpu_cirros = df['CPU cirros mean']
            cpu_cirros_sd = df['CPU cirros sd']
            cpu_stress = df['CPU stress mean']
            cpu_stress_sd = df['CPU stress sd']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-CPU"

            axs[_count].bar(index, cpu_cirros, width, yerr=cpu_cirros_sd, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, cpu_stress, width,yerr=cpu_stress_sd, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Stress')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System CPU Mean', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()


##############################################
# System LOAD Bar Chart 
##############################################

if SYSTEM_LOAD_BAR:

    data_dict = {}

    for _sys_load_files in sys_load_files:
        _title = (Path(_sys_load_files).name).split("-System-Load")[0]
        _case, _instances = _title.split("s_")[1].split("_")
        _image = _title.split("_")[0]
        df = pd.read_csv(_sys_load_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["stress"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "stress":
            data_dict[_case][_instances]["stress"]["mean"] = df['Load1 Mean'].mean()
            data_dict[_case][_instances]["stress"]["sd"] = df['Load1 SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['Load1 Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['Load1 SD'].mean()


    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System Load 1-min', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'Load1 cirros mean': _instances_data['cirros']["mean"],
                    'Load1 cirros sd': _instances_data['cirros']["sd"],
                    'Load1 stress mean': _instances_data['stress']["mean"],
                    'Load1 stress sd': _instances_data['stress']["sd"]
                })

            df = pd.DataFrame(data) 
            df = df.sort_values('case')

            divisions = df['case']    
            load1_cirros = df['Load1 cirros mean']
            load1_cirros_sd = df['Load1 cirros sd']
            load1_stress = df['Load1 stress mean']
            load1_stress_sd = df['Load1 stress sd']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-Load1"

            axs[_count].bar(index, load1_cirros, width, yerr=load1_cirros_sd, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, load1_stress, width,yerr=load1_stress_sd, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Stress')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1


    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System Load Mean', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

##############################################
# System RAM Bar Chart 
##############################################

if SYSTEM_RAM_BAR:

    data_dict = {}

    for _sys_ram_files in sys_ram_files:
        _title = (Path(_sys_ram_files).name).split("-System-RAM")[0]
        _case, _instances = _title.split("s_")[1].split("_")
        _image = _title.split("_")[0]
        df = pd.read_csv(_sys_ram_files)

        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["stress"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "stress":
            data_dict[_case][_instances]["stress"]["mean"] = df['RAM Mean'].mean()
            data_dict[_case][_instances]["stress"]["sd"] = df['RAM SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['RAM Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['RAM SD'].mean()

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System RAM', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'MEM cirros mean': _instances_data['cirros']["mean"],
                    'MEM cirros sd': _instances_data['cirros']["sd"],
                    'MEM stress mean': _instances_data['stress']["mean"],
                    'MEM stress sd': _instances_data['stress']["sd"]
                })
    
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
    
            divisions = df['case']
            mem_cirros = df['MEM cirros mean']
            mem_cirros_sd = df['MEM cirros sd']
            mem_stress = df['MEM stress mean']
            mem_stress_sd = df['MEM stress sd']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-MEM"

            axs[_count].bar(index, mem_cirros, width, yerr=mem_cirros_sd, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, mem_stress, width,yerr=mem_stress_sd, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Stress')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System RAM Mean', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

#########################################
# END
#########################################

print("Total time: {}".format(time.time() - start_time))

