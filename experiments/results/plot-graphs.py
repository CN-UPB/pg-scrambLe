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
import matplotlib.dates as mdates
import datetime as dt
import statistics

from scipy.stats import t # sudo pip3 install scipy
from math import sqrt

start_time = time.time()

DOCKER_CPU_BAR = False
DOCKER_CASE_CPU_BAR = False
SYSTEM_CPU_BAR = False
DOCKER_CASE_GROUPED = False
END_TO_END_TIME_BAR = True
SYSTEM_LOAD_BAR = False
DOCKER_MEM_BAR = False
DOCKER_CASE_MEM_BAR = False
SYSTEM_RAM_BAR = False
SUCCESS_RATIO_LINE = False
END_TO_END_TIME_BAR = True

CPU_MAX_SCALE = 150
LIMIT_DOCKERS_IN_GRAPH = -10

_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/OSM Results/Final"
_OUT_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/Graphs"
_SUCCESS_RATIO_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/OSM Results/data_csv"

_COMMON_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv"
_OSM_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/OSM Results/data_csv"
_PISHAHANG_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/Pishahang Results/data_csv"


RUNS = 3 # Not fully supported
CASES = 3 # Not fully supported
IMAGES = 2

CONFIDENCE = 0.95
T_BOUNDS = t.interval(CONFIDENCE, RUNS - 1)

cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-CPU-Final-Results.csv')) if "System" not in y]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-MEM-Final-Results.csv'))]
docker_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-CPU-Docker-Final-Results.csv')) if "System" not in y]
docker_mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-MEM-Docker-Final-Results.csv'))]
sys_cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-CPU-Final-Results.csv'))]
sys_load_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-Load-Final-Results.csv'))]
sys_ram_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-System-RAM-Final-Results.csv'))]
success_ratio_file = [y for x in os.walk(_SUCCESS_RATIO_PATH) for y in glob(os.path.join(x[0], 'success-ratio.csv'))]

##############################################
# Docker Case CPU Bar Chart 
##############################################

if DOCKER_CASE_CPU_BAR:
    data_dict = {}
    for _docker_cpu_files in docker_cpu_files:
        _title = (Path(_docker_cpu_files).name).split("-CPU")[0]
        df = pd.read_csv(_docker_cpu_files)
        
        for index, row in df.iterrows():
            _image, _case, _instances = row['Case'].split("_")

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["ubuntu"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "ubuntu":
                data_dict[_case][_instances]["ubuntu"]["mean"] = row['CPU Mean']
                data_dict[_case][_instances]["ubuntu"]["sd"] = row['CPU SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["mean"] = row['CPU Mean']
                data_dict[_case][_instances]["cirros"]["sd"] = row['CPU SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{} - Mean'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'CPU cirros mean': _instances_data['cirros']["mean"],
                        'CPU cirros sd': _instances_data['cirros']["sd"],
                        'CPU ubuntu mean': _instances_data['ubuntu']["mean"],
                        'CPU ubuntu sd': _instances_data['ubuntu']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                cpu_cirros = df['CPU cirros mean']
                cpu_cirros_sd = df['CPU cirros sd']
                cpu_ubuntu = df['CPU ubuntu mean']
                cpu_ubuntu_sd = df['CPU ubuntu sd']

                df['CPU cirros mean T'] = abs(T_BOUNDS[1] * df['CPU cirros sd'] / sqrt(RUNS))
                df['CPU ubuntu mean T'] = abs(T_BOUNDS[1] * df['CPU ubuntu sd'] / sqrt(RUNS))

                cirros_t_mean = df['CPU cirros mean T']
                ubuntu_t_mean = df['CPU ubuntu mean T']

        
                index = np.arange(len(data))
                width = 0.30
                

                axs[_count].bar(index, cpu_cirros, width, yerr=cirros_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, cpu_ubuntu, width,yerr=ubuntu_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('CPU Mean (percentage)', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-Mean-CPU-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

    # For Max Graph
    data_dict = {}
    for _docker_cpu_files in docker_cpu_files:
        _title = (Path(_docker_cpu_files).name).split("-CPU")[0]
        df = pd.read_csv(_docker_cpu_files)
        
        for index, row in df.iterrows():
            _image, _case, _instances = row['Case'].split("_")

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["ubuntu"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "ubuntu":
                data_dict[_case][_instances]["ubuntu"]["max"] = row['CPU Max']
                data_dict[_case][_instances]["ubuntu"]["sd"] = row['CPU Max SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["max"] = row['CPU Max']
                data_dict[_case][_instances]["cirros"]["sd"] = row['CPU Max SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{} - Max'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'CPU cirros max': _instances_data['cirros']["max"],
                        'CPU cirros sd': _instances_data['cirros']["sd"],
                        'CPU ubuntu max': _instances_data['ubuntu']["max"],
                        'CPU ubuntu sd': _instances_data['ubuntu']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                cpu_cirros = df['CPU cirros max']
                cpu_cirros_sd = df['CPU cirros sd']
                cpu_ubuntu = df['CPU ubuntu max']
                cpu_ubuntu_sd = df['CPU ubuntu sd']

                df['CPU cirros max T'] = abs(T_BOUNDS[1] * df['CPU cirros sd'] / sqrt(RUNS))
                df['CPU ubuntu max T'] = abs(T_BOUNDS[1] * df['CPU ubuntu sd'] / sqrt(RUNS))

                cirros_t_max = df['CPU cirros max T']
                ubuntu_t_max = df['CPU ubuntu max T']
        
                index = np.arange(len(data))
                width = 0.30

                axs[_count].bar(index, cpu_cirros, width, yerr=cirros_t_max, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, cpu_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('CPU Max (percentage)', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-Max-CPU-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
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
            _image, _case, _instances = row['Case'].split("_")

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["ubuntu"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "ubuntu":
                data_dict[_case][_instances]["ubuntu"]["mean"] = row['MEM Mean']
                data_dict[_case][_instances]["ubuntu"]["sd"] = row['MEM SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["mean"] = row['MEM Mean']
                data_dict[_case][_instances]["cirros"]["sd"] = row['MEM SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{} - Mean'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'MEM cirros mean': _instances_data['cirros']["mean"],
                        'MEM cirros sd': _instances_data['cirros']["sd"],
                        'MEM ubuntu mean': _instances_data['ubuntu']["mean"],
                        'MEM ubuntu sd': _instances_data['ubuntu']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                mem_cirros = df['MEM cirros mean']
                mem_cirros_sd = df['MEM cirros sd']
                mem_ubuntu = df['MEM ubuntu mean']
                mem_ubuntu_sd = df['MEM ubuntu sd']

                df['MEM cirros mean T'] = abs(T_BOUNDS[1] * df['MEM cirros sd'] / sqrt(RUNS))
                df['MEM ubuntu mean T'] = abs(T_BOUNDS[1] * df['MEM ubuntu sd'] / sqrt(RUNS))

                cirros_t_mean = df['MEM cirros mean T']
                ubuntu_t_mean = df['MEM ubuntu mean T']
        
                index = np.arange(len(data))
                width = 0.30

                axs[_count].bar(index, mem_cirros, width, yerr=cirros_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, mem_ubuntu, width,yerr=ubuntu_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('MEM Mean (MiB)', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-Mean-MEM-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

    # For Max Graph
    data_dict = {}
    for _docker_mem_files in docker_mem_files:
        _title = (Path(_docker_mem_files).name).split("-MEM")[0]
        df = pd.read_csv(_docker_mem_files)
        
        for index, row in df.iterrows():
            _image, _case, _instances = row['Case'].split("_")

            if not _case in data_dict:
                data_dict[_case] = {}

            if not _instances in data_dict[_case]: 
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances] = {}
                data_dict[_case][_instances]["ubuntu"] = {}
                data_dict[_case][_instances]["cirros"] = {}

            if _image == "ubuntu":
                data_dict[_case][_instances]["ubuntu"]["max"] = row['MEM Max']
                data_dict[_case][_instances]["ubuntu"]["sd"] = row['MEM Max SD']
            elif _image == "cirros":
                data_dict[_case][_instances]["cirros"]["max"] = row['MEM Max']
                data_dict[_case][_instances]["cirros"]["sd"] = row['MEM Max SD']

        fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{} - Max'.format(_title), fontsize=25)
        _count = 0

        while(_count < CASES):
            for _case, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'case': int(_instances), 
                        'MEM cirros max': _instances_data['cirros']["max"],
                        'MEM cirros sd': _instances_data['cirros']["sd"],
                        'MEM ubuntu max': _instances_data['ubuntu']["max"],
                        'MEM ubuntu sd': _instances_data['ubuntu']["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('case')

                divisions = df['case']
                mem_cirros = df['MEM cirros max']
                mem_cirros_sd = df['MEM cirros sd']
                mem_ubuntu = df['MEM ubuntu max']
                mem_ubuntu_sd = df['MEM ubuntu sd']

                df['MEM cirros max T'] = abs(T_BOUNDS[1] * df['MEM cirros sd'] / sqrt(RUNS))
                df['MEM ubuntu max T'] = abs(T_BOUNDS[1] * df['MEM ubuntu sd'] / sqrt(RUNS))

                cirros_t_max = df['MEM cirros max T']
                ubuntu_t_max = df['MEM ubuntu max T']
        
                index = np.arange(len(data))
                width = 0.30

                axs[_count].bar(index, mem_cirros, width, yerr=cirros_t_max, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
                axs[_count].bar(index+width, mem_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

                axs[_count].set_title(_case, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('MEM Max (MiB)', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}--Max-MEM-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# Docker CPU Bar Chart 
##############################################

if DOCKER_CPU_BAR:
    for _cpu_files in cpu_files:
        cpu_title = (Path(_cpu_files).name).split("-CPU")[0]
        print(cpu_title)
        print(_cpu_files)
        header = ['Max', 'Mean']

        df = pd.read_csv(_cpu_files)
        df = df.sort_values('CPU Mean')
        df = df[LIMIT_DOCKERS_IN_GRAPH:]
        docker_col = df['Docker Container']
        value_col = df['CPU Mean']
        value_col_max = df['CPU Max']
        value_col_max_sd = df['CPU Max SD']
        value_sd_col = df['CPU SD']

        # sum mean to the confidence interval
        df['CPU Mean T'] = abs(T_BOUNDS[1] * df['CPU SD'] / sqrt(RUNS))
        df['CPU Max T'] = abs(T_BOUNDS[1] * df['CPU Max SD'] / sqrt(RUNS))

        value_col_t_mean = df['CPU Mean T']
        value_col_t_max = df['CPU Max T']

        width = 0.30
        plt.figure(figsize=(10,6))
        plt.xlim([0, CPU_MAX_SCALE])

        a2=plt.barh(docker_col, value_col_max, xerr=value_col_t_max, alpha=0.6, ecolor='black', capsize=2, color='red')
        a=plt.barh(docker_col, value_col, xerr=value_col_t_mean, alpha=0.6, ecolor='black', capsize=2, color='blue')

        # for rect in a.patches:
        #     width = rect.get_width()
        #     plt.text(1.05*rect.get_width(), rect.get_y()+0.75*rect.get_height(),
        #             '%d' % int(width),
        #             ha='center', va='center', fontsize=9, color='black',fontweight='bold')

        # for rect in a2.patches:
        #     width = rect.get_width()
        #     plt.text(1.05*rect.get_width(), rect.get_y()+0.75*rect.get_height(),
        #             '%d' % int(width),
        #             ha='center', va='center', fontsize=9, color='black',fontweight='bold')


        # plt.xticks(rotation=-90)
        plt.title("CPU -- {}".format(cpu_title), fontsize=25)
        plt.xlabel("CPU Mean (percentage)", fontsize=20)
        plt.ylabel("Dockers", fontsize=20)
        plt.legend((a2[2],a[2]),(header[0],header[1]),loc='center left', bbox_to_anchor=(1, 0.5))
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
        header = ['Max','Mean']

        df = pd.read_csv(_mem_files)
        df = df.sort_values('MEM Max')
        df = df[LIMIT_DOCKERS_IN_GRAPH:]
        docker_col = df['Docker Container']
        value_col = df['MEM Mean']
        value_col_max = df['MEM Max']
        value_col_max_sd = df['MEM Max SD']
        value_sd_col = df['MEM SD']

        # sum mean to the confidence interval
        df['MEM Mean T'] = abs(T_BOUNDS[1] * df['MEM SD'] / sqrt(RUNS))
        df['MEM Max T'] = abs(T_BOUNDS[1] * df['MEM Max SD'] / sqrt(RUNS))

        value_col_t_mean = df['MEM Mean T']
        value_col_t_max = df['MEM Max T']

        width = 0.30
        plt.figure(figsize=(10,6))

        a2=plt.barh(docker_col, value_col_max, xerr=value_col_t_max, alpha=0.6, ecolor='black', capsize=5, color='red')
        a=plt.barh(docker_col, value_col, xerr=value_col_t_mean, alpha=0.6, ecolor='black', capsize=5, color='blue')

        # for rect in a.patches:
        #     width = rect.get_width()
        #     plt.text(1.05*rect.get_width(), rect.get_y()+0.75*rect.get_height(),
        #             '%d' % int(width),
        #             ha='center', va='center', fontsize=9, color='black',fontweight='bold')

        # for rect in a2.patches:
        #     width = rect.get_width()
        #     plt.text(1.05*rect.get_width(), rect.get_y()+0.75*rect.get_height(),
        #             '%d' % int(width),
        #             ha='center', va='center', fontsize=9, color='black',fontweight='bold')


        # plt.xticks(rotation=-90)
        plt.title("MEM -- {}".format(mem_title),fontsize=25)
        plt.xlabel("MEM Mean (MiB)",fontsize=20)
        plt.ylabel("Dockers",fontsize=20)
        plt.legend((a2[2],a[2]),(header[0],header[1]),loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig('{}/{}-MEM.png'.format(_OUT_PATH, mem_title),bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# System CPU Bar Chart 
##############################################

if SYSTEM_CPU_BAR:
    data_dict = {}

    for _sys_cpu_files in sys_cpu_files:
        _title = (Path(_sys_cpu_files).name).split("-System-CPU")[0]
        _image, _case, _instances = _title.split("_")

        df = pd.read_csv(_sys_cpu_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["mean"] = df['CPU Mean'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['CPU SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['CPU Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['CPU SD'].mean()            

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System CPU Mean', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances), 
                    'CPU cirros mean': _instances_data['cirros']["mean"],
                    'CPU cirros sd': _instances_data['cirros']["sd"],
                    'CPU ubuntu mean': _instances_data['ubuntu']["mean"],
                    'CPU ubuntu sd': _instances_data['ubuntu']["sd"]
                })
        
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
            
            divisions = df['case']
            df = df[LIMIT_DOCKERS_IN_GRAPH:]
            cpu_cirros = df['CPU cirros mean']
            cpu_cirros_sd = df['CPU cirros sd']
            cpu_ubuntu = df['CPU ubuntu mean']
            cpu_ubuntu_sd = df['CPU ubuntu sd']

            df['CPU cirros mean T'] = abs(T_BOUNDS[1] * df['CPU cirros sd'] / sqrt(RUNS))
            df['CPU ubuntu mean T'] = abs(T_BOUNDS[1] * df['CPU ubuntu sd'] / sqrt(RUNS))

            cirros_t_mean = df['CPU cirros mean T']
            ubuntu_t_mean = df['CPU ubuntu mean T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-CPU"

            axs[_count].bar(index, cpu_cirros, width, yerr=cirros_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, cpu_ubuntu, width,yerr=ubuntu_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System CPU Mean (percentage)', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}-Mean.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

    # For Max
    data_dict = {}

    for _sys_cpu_files in sys_cpu_files:
        _title = (Path(_sys_cpu_files).name).split("-System-CPU")[0]
        _image, _case, _instances = _title.split("_")
        df = pd.read_csv(_sys_cpu_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["max"] = df['CPU Max'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['CPU Max SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["max"] = df['CPU Max'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['CPU Max SD'].mean()            

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System CPU Max', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances), 
                    'CPU cirros max': _instances_data['cirros']["max"],
                    'CPU cirros sd': _instances_data['cirros']["sd"],
                    'CPU ubuntu max': _instances_data['ubuntu']["max"],
                    'CPU ubuntu sd': _instances_data['ubuntu']["sd"]
                })
        
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
            
            divisions = df['case']
            cpu_cirros = df['CPU cirros max']
            cpu_cirros_sd = df['CPU cirros sd']
            cpu_ubuntu = df['CPU ubuntu max']
            cpu_ubuntu_sd = df['CPU ubuntu sd']

            df['CPU cirros max T'] = abs(T_BOUNDS[1] * df['CPU cirros sd'] / sqrt(RUNS))
            df['CPU ubuntu max T'] = abs(T_BOUNDS[1] * df['CPU ubuntu sd'] / sqrt(RUNS))

            cirros_t_max = df['CPU cirros max T']
            ubuntu_t_max = df['CPU ubuntu max T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-CPU"

            axs[_count].bar(index, cpu_cirros, width, yerr=cirros_t_max, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, cpu_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System CPU Max (percentage)', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}-Max.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()
##############################################
# System LOAD Bar Chart 
##############################################

if SYSTEM_LOAD_BAR:

    data_dict = {}

    for _sys_load_files in sys_load_files:
        _title = (Path(_sys_load_files).name).split("-System-Load")[0]
        _image, _case, _instances = _title.split("_")
        df = pd.read_csv(_sys_load_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["mean"] = df['Load1 Mean'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['Load1 SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['Load1 Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['Load1 SD'].mean()


    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System Load 1m Mean', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'Load1 cirros mean': _instances_data['cirros']["mean"],
                    'Load1 cirros sd': _instances_data['cirros']["sd"],
                    'Load1 ubuntu mean': _instances_data['ubuntu']["mean"],
                    'Load1 ubuntu sd': _instances_data['ubuntu']["sd"]
                })

            df = pd.DataFrame(data) 
            df = df.sort_values('case')

            divisions = df['case']    
            load1_cirros = df['Load1 cirros mean']
            load1_cirros_sd = df['Load1 cirros sd']
            load1_ubuntu = df['Load1 ubuntu mean']
            load1_ubuntu_sd = df['Load1 ubuntu sd']

            df['Load1 cirros mean T'] = abs(T_BOUNDS[1] * df['Load1 cirros sd'] / sqrt(RUNS))
            df['Load1 ubuntu mean T'] = abs(T_BOUNDS[1] * df['Load1 ubuntu sd'] / sqrt(RUNS))

            cirros_t_mean = df['Load1 cirros mean T']
            ubuntu_t_max = df['Load1 ubuntu mean T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-Load1"

            axs[_count].bar(index, load1_cirros, width, yerr=cirros_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, load1_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

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

    plt.savefig('{}/{}-Mean.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

    # For Max
    data_dict = {}

    for _sys_load_files in sys_load_files:
        _title = (Path(_sys_load_files).name).split("-System-Load")[0]
        _image, _case, _instances = _title.split("_")

        df = pd.read_csv(_sys_load_files)
        
        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["max"] = df['Load1 Max'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['Load1 Max SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["max"] = df['Load1 Max'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['Load1 Max SD'].mean()


    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System Load 1m Max', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'Load1 cirros max': _instances_data['cirros']["max"],
                    'Load1 cirros sd': _instances_data['cirros']["sd"],
                    'Load1 ubuntu max': _instances_data['ubuntu']["max"],
                    'Load1 ubuntu sd': _instances_data['ubuntu']["sd"]
                })

            df = pd.DataFrame(data) 
            df = df.sort_values('case')

            divisions = df['case']    
            load1_cirros = df['Load1 cirros max']
            load1_cirros_sd = df['Load1 cirros sd']
            load1_ubuntu = df['Load1 ubuntu max']
            load1_ubuntu_sd = df['Load1 ubuntu sd']

            df['Load1 cirros max T'] = abs(T_BOUNDS[1] * df['Load1 cirros sd'] / sqrt(RUNS))
            df['Load1 ubuntu max T'] = abs(T_BOUNDS[1] * df['Load1 ubuntu sd'] / sqrt(RUNS))

            cirros_t_max = df['Load1 cirros max T']
            ubuntu_t_max = df['Load1 ubuntu max T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-Load1"

            axs[_count].bar(index, load1_cirros, width, yerr=cirros_t_max, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, load1_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1


    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System Load Max', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}-Max.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

##############################################
# System RAM Bar Chart 
##############################################

if SYSTEM_RAM_BAR:

    data_dict = {}

    for _sys_ram_files in sys_ram_files:
        _title = (Path(_sys_ram_files).name).split("-System-RAM")[0]
        _image, _case, _instances = _title.split("_")
        df = pd.read_csv(_sys_ram_files)

        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["mean"] = df['RAM Mean'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['RAM SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["mean"] = df['RAM Mean'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['RAM SD'].mean()

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System RAM Mean', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'MEM cirros mean': _instances_data['cirros']["mean"],
                    'MEM cirros sd': _instances_data['cirros']["sd"],
                    'MEM ubuntu mean': _instances_data['ubuntu']["mean"],
                    'MEM ubuntu sd': _instances_data['ubuntu']["sd"]
                })
    
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
    
            divisions = df['case']
            mem_cirros = df['MEM cirros mean']
            mem_cirros_sd = df['MEM cirros sd']
            mem_ubuntu = df['MEM ubuntu mean']
            mem_ubuntu_sd = df['MEM ubuntu sd']

            df['MEM cirros mean T'] = abs(T_BOUNDS[1] * df['MEM cirros sd'] / sqrt(RUNS))
            df['MEM ubuntu mean T'] = abs(T_BOUNDS[1] * df['MEM ubuntu sd'] / sqrt(RUNS))

            cirros_t_mean = df['MEM cirros mean T']
            ubuntu_t_mean = df['MEM ubuntu mean T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-MEM"

            axs[_count].bar(index, mem_cirros, width, yerr=cirros_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, mem_ubuntu, width,yerr=ubuntu_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System RAM (MiB)', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}-Mean.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

    # For Max

    data_dict = {}

    for _sys_ram_files in sys_ram_files:
        _title = (Path(_sys_ram_files).name).split("-System-RAM")[0]
        _image, _case, _instances = _title.split("_")
        df = pd.read_csv(_sys_ram_files)

        if not _case in data_dict:
            data_dict[_case] = {}

        if not _instances in data_dict[_case]: 
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances] = {}
            data_dict[_case][_instances]["ubuntu"] = {}
            data_dict[_case][_instances]["cirros"] = {}

        if _image == "ubuntu":
            data_dict[_case][_instances]["ubuntu"]["max"] = df['RAM Max'].mean()
            data_dict[_case][_instances]["ubuntu"]["sd"] = df['RAM Max SD'].mean()
        elif _image == "cirros":
            data_dict[_case][_instances]["cirros"]["max"] = df['RAM Max'].mean()
            data_dict[_case][_instances]["cirros"]["sd"] = df['RAM Max SD'].mean()

    fig, axs = plt.subplots(CASES, figsize=(6, 8), sharex=True, sharey=True)
    fig.suptitle('System RAM Max', fontsize=25)
    _count = 0

    while(_count < CASES):
        for _case, _data in sorted(data_dict.items()):
            data = []
            for _instances, _instances_data in sorted(_data.items()):
                data.append({
                    'case': int(_instances),
                    'MEM cirros max': _instances_data['cirros']["max"],
                    'MEM cirros sd': _instances_data['cirros']["sd"],
                    'MEM ubuntu max': _instances_data['ubuntu']["max"],
                    'MEM ubuntu sd': _instances_data['ubuntu']["sd"]
                })
    
            df = pd.DataFrame(data) 
            df = df.sort_values('case')
    
            divisions = df['case']
            mem_cirros = df['MEM cirros max']
            mem_cirros_sd = df['MEM cirros sd']
            mem_ubuntu = df['MEM ubuntu max']
            mem_ubuntu_sd = df['MEM ubuntu sd']

            df['MEM cirros max T'] = abs(T_BOUNDS[1] * df['MEM cirros sd'] / sqrt(RUNS))
            df['MEM ubuntu max T'] = abs(T_BOUNDS[1] * df['MEM ubuntu sd'] / sqrt(RUNS))

            cirros_t_max = df['MEM cirros max T']
            ubuntu_t_max = df['MEM ubuntu max T']

            index = np.arange(len(data))
            width = 0.30

            _title = "System-MEM"

            axs[_count].bar(index, mem_cirros, width, yerr=cirros_t_max, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Cirros')
            axs[_count].bar(index+width, mem_ubuntu, width,yerr=ubuntu_t_max, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'ubuntu')

            axs[_count].set_title(_case, fontsize=15)

            _count += 1

    plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('System RAM (MiB)', fontsize=20)
    plt.xlabel('Cases', fontsize=20)

    plt.savefig('{}/{}-Max.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

##############################################
# Success ratio Line Chart 
##############################################



if SUCCESS_RATIO_LINE:
    for _success_ratio_file in success_ratio_file:
        print(Path(_success_ratio_file).parent.name)
        print(Path(_success_ratio_file).name)

        _case, _run = Path(_success_ratio_file).parent.name.split("_Run")
        _case = _case.split("-")[1]
        print(_case)
        _docker = Path(_success_ratio_file).name
        _docker = _docker.split(".")[0]
        print(_docker)
        _docker = _docker+"-"+_case+"-"+_run
        print(_docker)
        end_to_end_path = Path(_success_ratio_file).parent / "end-to-end-time.csv"
        etime = (pd.read_csv(end_to_end_path)["end-to-end-time"][0])/360
        etime = "{:.3}".format(etime)
        df = pd.read_csv(_success_ratio_file)



        unix_time = pd.to_datetime(df['Time'],unit = 's')

        total = df['Total']
        active = df['Active']
        build = df['Build']
        error = df['Error']


        fig = plt.figure()
        plt.figure(figsize=(11,6))
        plt.suptitle('{} in {} minutes'.format(_docker,etime), fontsize=22)
        ax = fig.add_subplot(1,1,1) 
        plt.xlabel('Time', fontsize=18)
        plt.ylabel('VNF instances', fontsize=16) 
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.plot(unix_time, total,label = 'Total')
        plt.plot(unix_time, active, label = 'Active')
        plt.plot(unix_time, build, label = 'Build')
        plt.plot(unix_time, error,label = 'Error')

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))


        plt.xticks(rotation=-45)

        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))   #to get a tick every 15 minutes
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        plt.savefig('{}/{}.png'.format(_OUT_PATH, _docker) ,bbox_inches='tight',dpi=100)



##############################################
# Dockers grouped
##############################################

if DOCKER_CASE_GROUPED:
    data_dict = {}
    for _docker_cpu_files in docker_cpu_files:
        _title = (Path(_docker_cpu_files).name).split("-CPU")[0]
        df = pd.read_csv(_docker_cpu_files)
        
        for index, row in df.iterrows():
            _image, _case, _instances = row['Case'].split("_")

            if not _image in data_dict:
                data_dict[_image] = {}

            if not _instances in data_dict[_image]: 
                data_dict[_image][_instances] = {}
                data_dict[_image][_instances] = {}
                data_dict[_image][_instances]["case1"] = {}
                data_dict[_image][_instances]["case2"] = {}
                data_dict[_image][_instances]["case3"] = {}

            if _case == "case1":
                data_dict[_image][_instances][_case]["mean"] = row['CPU Mean']
                data_dict[_image][_instances][_case]["sd"] = row['CPU SD']
            elif _case == "case2":
                data_dict[_image][_instances][_case]["mean"] = row['CPU Mean']
                data_dict[_image][_instances][_case]["sd"] = row['CPU SD']
            elif _case == "case3":
                data_dict[_image][_instances][_case]["mean"] = row['CPU Mean']
                data_dict[_image][_instances][_case]["sd"] = row['CPU SD']

        fig, axs = plt.subplots(IMAGES, figsize=(6, 8), sharex=True, sharey=True)
        fig.suptitle('{} - Mean'.format(_title), fontsize=25)
        _count = 0

        while(_count < IMAGES):
            for _image, _data in sorted(data_dict.items()):
                data = []
                for _instances, _instances_data in sorted(_data.items()):
                    data.append({
                        'instance': int(_instances), 
                        'CPU case1 mean': _instances_data["case1"]["mean"],
                        'CPU case1 sd': _instances_data["case1"]["sd"],
                        'CPU case2 mean': _instances_data["case2"]["mean"],
                        'CPU case2 sd': _instances_data["case2"]["sd"],
                        'CPU case3 mean': _instances_data["case3"]["mean"],
                        'CPU case3 sd': _instances_data["case3"]["sd"]
                    })


                df = pd.DataFrame(data) 
                df = df.sort_values('instance')

                divisions = df['instance']
                cpu_case1_mean = df['CPU case1 mean']
                cpu_case1_sd = df['CPU case1 sd']
                cpu_case2_mean = df['CPU case2 mean']
                cpu_case2_sd = df['CPU case2 sd']
                cpu_case3_mean = df['CPU case3 mean']
                cpu_case3_sd = df['CPU case3 sd']

                df['CPU case1 mean T'] = abs(T_BOUNDS[1] * df['CPU case1 sd'] / sqrt(RUNS))
                df['CPU case2 mean T'] = abs(T_BOUNDS[1] * df['CPU case2 sd'] / sqrt(RUNS))
                df['CPU case3 mean T'] = abs(T_BOUNDS[1] * df['CPU case3 sd'] / sqrt(RUNS))

                case1_t_mean = df['CPU case1 mean T']
                case2_t_mean = df['CPU case2 mean T']
                case3_t_mean = df['CPU case3 mean T']

        
                index = np.arange(len(data))
                width = 0.30
                

                axs[_count].bar(index-width, cpu_case1_mean, width, yerr=case1_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'case1')
                axs[_count].bar(index, cpu_case2_mean, width,yerr=case2_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'case2')
                axs[_count].bar(index+width, cpu_case3_mean, width,yerr=case3_t_mean, alpha=0.6, ecolor='black', capsize=5, color='y', label = 'case3')
                axs[_count].set_title(_image, fontsize=15)

                _count += 1

        plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('CPU Mean (percentage)', fontsize=20)
        plt.xlabel('Cases', fontsize=20)

        plt.savefig('{}/{}-Mean-CPU-Cases.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
        plt.close()

##############################################
# End to End Time Graphs
##############################################

if END_TO_END_TIME_BAR:
    osm_e2e_files = [y for x in os.walk(_OSM_PATH) for y in glob(os.path.join(x[0], 'end-to-end-time.csv'))]
    pishahang_e2e_files = [y for x in os.walk(_PISHAHANG_PATH) for y in glob(os.path.join(x[0], 'end-to-end-time.csv'))]
    osm_data_dict = {}
    pishahang_data_dict = {}
    for _e2e_file in osm_e2e_files:
        print(Path(_e2e_file).parent.name)
        print(Path(_e2e_file).name)
        _case, _run = Path(_e2e_file).parent.name.split("_Run")
        _image, _case, _instances = _case.split("_")
        _image = _image.split("-")[1]
        print(_case)
        etime = (pd.read_csv(_e2e_file)["end-to-end-time"][0])

        if not _image in osm_data_dict:
            osm_data_dict[_image] = {}

        if _image == "ubuntu":
            if not _instances in osm_data_dict[_image]: 
                osm_data_dict[_image][_instances] = {}
            if not _case in osm_data_dict[_image][_instances]: 
                osm_data_dict[_image][_instances][_case] = {}
                osm_data_dict[_image][_instances][_case]["e2e"] = []
            osm_data_dict[_image][_instances][_case]["e2e"].append(etime)
            
        elif _image == "cirros":
            if not _instances in osm_data_dict[_image]: 
                osm_data_dict[_image][_instances] = {}
            if not _case in osm_data_dict[_image][_instances]: 
                osm_data_dict[_image][_instances][_case] = {}
                osm_data_dict[_image][_instances][_case]["e2e"] = []
            osm_data_dict[_image][_instances][_case]["e2e"].append(etime)

    for _e2e_file in pishahang_e2e_files:
        print(Path(_e2e_file).parent.name)
        print(Path(_e2e_file).name)
        _case, _run = Path(_e2e_file).parent.name.split("_Run")
        _image, _case, _instances = _case.split("_")
        _image = _image.split("-")[1]
        print(_case)
        etime = (pd.read_csv(_e2e_file)["end-to-end-time"][0])
        if not _image in pishahang_data_dict:
            pishahang_data_dict[_image] = {}
        if _image == "ubuntu":
            if not _instances in pishahang_data_dict[_image]: 
                pishahang_data_dict[_image][_instances] = {}
            if not _case in pishahang_data_dict[_image][_instances]: 
                pishahang_data_dict[_image][_instances][_case] = {}
                pishahang_data_dict[_image][_instances][_case]["e2e"] = []
            pishahang_data_dict[_image][_instances][_case]["e2e"].append(etime)
        elif _image == "cirros":
            if not _instances in pishahang_data_dict[_image]: 
                pishahang_data_dict[_image][_instances] = {}
            if not _case in pishahang_data_dict[_image][_instances]: 
                pishahang_data_dict[_image][_instances][_case] = {}
                pishahang_data_dict[_image][_instances][_case]["e2e"] = []
            pishahang_data_dict[_image][_instances][_case]["e2e"].append(etime)

    final_dict = {"osm" : {}, 
                    "pishahang" : {}}

    for _image, _data in sorted(osm_data_dict.items()):
        if not _image in final_dict["osm"]:
            final_dict["osm"][_image] = {}
        data = []
        
        for _instances, _instances_data in sorted(_data.items()):
            data.append({
                'instances': int(_instances),
                'case1 mean': statistics.mean(_instances_data["case1"]["e2e"]),
                'case1 sd': statistics.pstdev(_instances_data["case1"]["e2e"]),
                'case2 mean': statistics.mean(_instances_data["case2"]["e2e"]),
                'case2 sd': statistics.pstdev(_instances_data["case2"]["e2e"]),
                'case3 mean': statistics.mean(_instances_data["case3"]["e2e"]),
                'case3 sd': statistics.pstdev(_instances_data["case3"]["e2e"])
            })
        final_dict["osm"][_image] = data

    for _image, _data in sorted(pishahang_data_dict.items()):
        if not _image in final_dict["pishahang"]:
            final_dict["pishahang"][_image] = {}
        data = []
        for _instances, _instances_data in sorted(_data.items()):
            data.append({
                'instances': int(_instances),
                'case1 mean': statistics.mean(_instances_data["case1"]["e2e"]),
                'case1 sd': statistics.pstdev(_instances_data["case1"]["e2e"]),
                'case2 mean': statistics.mean(_instances_data["case2"]["e2e"]),
                'case2 sd': statistics.pstdev(_instances_data["case2"]["e2e"]),
                'case3 mean': statistics.mean(_instances_data["case3"]["e2e"]),
                'case3 sd': statistics.pstdev(_instances_data["case3"]["e2e"])
            })
        final_dict["pishahang"][_image] = data

    # -------------------------------- 
    fig, axs = plt.subplots(2, figsize=(6, 8), sharex=False, sharey=True)
    fig.suptitle('End to end deployment times', fontsize=25)
    _count = 0
    
    # while(_count < IMAGES):

    for _mano, _data in sorted(final_dict.items()):
        for _image, _image_data in sorted(_data.items()):
            if _image == "ubuntu":
                continue
            df = pd.DataFrame.from_dict(_image_data) 
            df = df.sort_values('instances')
            divisions = df['instances']    
            case1_mean = df["case1 mean"]            
            case1_sd = df["case1 sd"]
            case2_mean = df["case2 mean"]
            case2_sd = df["case2 sd"]
            case3_mean = df["case3 mean"]
            case3_sd = df["case3 sd"]
            df['case1 mean T'] = abs(T_BOUNDS[1] * df['case1 sd'] / sqrt(RUNS))
            df['case2 mean T'] = abs(T_BOUNDS[1] * df['case2 sd'] / sqrt(RUNS))
            df['case3 mean T'] = abs(T_BOUNDS[1] * df['case3 sd'] / sqrt(RUNS))
            case1_mean_t = df['case1 mean T']
            case2_mean_t = df['case2 mean T']
            case3_mean_t = df['case3 mean T']
            index = np.arange(len(data))
            width = 0.30
            _title = "E2E Times"
            axs[_count].bar(index-width, case1_mean, width, yerr=case1_mean_t, alpha=0.6, ecolor='black', capsize=5, color='g', label = 'case1')
            axs[_count].bar(index, case2_mean, width, yerr=case2_mean_t, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'case2')
            axs[_count].bar(index+width, case3_mean, width,yerr=case3_mean_t, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'case3')
            if _mano == "osm":
                axs[_count].set_title(_mano+"-"+_image+"-vm", fontsize=15)
            else:
                axs[_count].set_title(_mano+"-"+_image+"-container", fontsize=15)
            axs[_count].set_xticks(index+width/2)
            axs[_count].set_xticklabels(divisions)
            _count += 1
    # plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.ylabel('Sec', fontsize=20)
    plt.xlabel('Instances', fontsize=20)
    plt.savefig('{}/{}-cirros-E2E.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()

    fig, axs = plt.subplots(2, figsize=(6, 8), sharex=False, sharey=True)
    fig.suptitle('End to end deployment times', fontsize=25)
    _count = 0
    
    # while(_count < IMAGES):

    for _mano, _data in sorted(final_dict.items()):
        for _image, _image_data in sorted(_data.items()):
            if _image == "cirros":
                continue
            df = pd.DataFrame.from_dict(_image_data) 
            df = df.sort_values('instances')
            divisions = df['instances']    
            case1_mean = df["case1 mean"]            
            case1_sd = df["case1 sd"]
            case2_mean = df["case2 mean"]
            case2_sd = df["case2 sd"]
            case3_mean = df["case3 mean"]
            case3_sd = df["case3 sd"]
            df['case1 mean T'] = abs(T_BOUNDS[1] * df['case1 sd'] / sqrt(RUNS))
            df['case2 mean T'] = abs(T_BOUNDS[1] * df['case2 sd'] / sqrt(RUNS))
            df['case3 mean T'] = abs(T_BOUNDS[1] * df['case3 sd'] / sqrt(RUNS))
            case1_mean_t = df['case1 mean T']
            case2_mean_t = df['case2 mean T']
            case3_mean_t = df['case3 mean T']
            index = np.arange(len(data))
            width = 0.30
            _title = "E2E Times"
            axs[_count].bar(index-width, case1_mean, width, yerr=case1_mean_t, alpha=0.6, ecolor='black', capsize=5, color='g', label = 'case1')
            axs[_count].bar(index, case2_mean, width, yerr=case2_mean_t, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'case2')
            axs[_count].bar(index+width, case3_mean, width,yerr=case3_mean_t, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'case3')
            if _mano == "osm":
                axs[_count].set_title(_mano+"-"+_image+"-vm", fontsize=15)
            else:
                axs[_count].set_title(_mano+"-"+_image+"-container", fontsize=15)
            axs[_count].set_xticks(index+width/2)
            axs[_count].set_xticklabels(divisions)
            _count += 1
    # plt.xticks(index+width/2, divisions)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.ylabel('Sec', fontsize=20)
    plt.xlabel('Instances', fontsize=20)
    plt.savefig('{}/{}-ubuntu-E2E.png'.format(_OUT_PATH, _title) ,bbox_inches='tight',dpi=100)
    plt.close()





#########################################
# END
#########################################




print("Total time: {}".format(time.time() - start_time))

