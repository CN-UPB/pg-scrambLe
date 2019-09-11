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
# from scipy.interpolate import spline


from scipy.stats import t # sudo pip3 install scipy
from math import sqrt

start_time = time.time()

# Horizontal Top Mean Graph
DOCKER_CPU_BAR = False
DOCKER_MEM_BAR = False

# Graph grouped by images
DOCKER_CASE_GROUPED = False

# Old docker cases
DOCKER_CASE_CPU_BAR = False
DOCKER_CASE_MEM_BAR = False

# System Wide Graphs
SYSTEM_CPU_BAR = False
SYSTEM_LOAD_BAR = False
SYSTEM_RAM_BAR = False

# one-on-one graphs
ONE_ON_ONE_SYSTEM_BAR = False
ONE_ON_ONE_OTHER_BAR = False

TOP_LIFECYCLE_GRAPH = True
TOP_SCALABILITY_LIFECYCLE_GRAPH = False

SUCCESS_RATIO_LINE = False
END_TO_END_TIME_BAR = False
I_END_TO_END_TIME_BAR = False
LIFECYCLE_GRAPH = False

CPU_MAX_SCALE = 125
MEM_MAX_SCALE = 2750
LIMIT_DOCKERS_IN_GRAPH = -10

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Comparison-VM-Docker"
_OUT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Lifecycle-Graphs-Top-3/graphs"
_COMMON_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Comparison-VM-Docker"

_OSM_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Lifecycle-Graphs-Top-5/osm"
_PISHAHANG_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Lifecycle-Graphs-Top-5/pishahang"

TOP_OSM_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Lifecycle-Graphs-Top-3/osm"
TOP_PISHAHANG_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Lifecycle-Graphs-Top-3/pishahang"

CHILD_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Scalability-Evaluation/child"
PARENT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Scalability-Evaluation/parent"


_SUCCESS_RATIO_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/OSM Results/data_csv"
_I_E2E_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/Common Results/data_csv/OSM Results/data_csv"
_LIFECYCLE_PATH = "/home/bhargavi/Documents/PG-SCRAMBLE/pg-scrambLe/experiments/results/test"


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
i_e2e_file = [y for x in os.walk(_I_E2E_PATH) for y in glob(os.path.join(x[0], 'individual-build-times.csv'))]
cpu_lifecycle_file = [y for x in os.walk(_LIFECYCLE_PATH) for y in glob(os.path.join(x[0], 'system-cpu.csv'))]


##############################################
# One on One Comparison graphs  
##############################################
if ONE_ON_ONE_SYSTEM_BAR:
    data_dict = {
        "pishahang" : {
            "cpu_mean" : "",
            "cpu_max" : "",
            "cpu_sd" : "",
            "ram_mean" : "",
            "ram_max" : "",
            "ram_sd" : "",
            "load1m_mean" : "",
            "load1m_max" : "",
            "load1m_sd" : ""
        },
        "osm" : {
            "cpu_mean" : "",
            "cpu_max" : "",
            "cpu_sd" : "",
            "ram_mean" : "",
            "ram_max" : "",
            "ram_sd" : "",
            "load1m_mean" : "",
            "load1m_max" : "",
            "load1m_sd" : ""
        }
    }

    for _sys_cpu_files in sys_cpu_files:
        _title = (Path(_sys_cpu_files).name).split("-System-CPU")[0]
        _image, _case, _instances = _title.split("_")
        _mano = Path(_sys_cpu_files).parent.parent.name

        df = pd.read_csv(_sys_cpu_files)

        if _mano == "osm":
            data_dict["osm"]["cpu_mean"] = df["CPU Mean"][0]
            data_dict["osm"]["cpu_max"] = df["CPU Max"][0]
            data_dict["osm"]["cpu_sd"] = df["CPU SD"][0]
        elif _mano == "pishahang":
            data_dict["pishahang"]["cpu_mean"] = df["CPU Mean"][0]
            data_dict["pishahang"]["cpu_max"] = df["CPU Max"][0]
            data_dict["pishahang"]["cpu_sd"] = df["CPU SD"][0]

    for _sys_ram_files in sys_ram_files:
        _title = (Path(_sys_ram_files).name).split("-System-RAM")[0]
        _image, _case, _instances = _title.split("_")
        _mano = Path(_sys_ram_files).parent.parent.name

        df = pd.read_csv(_sys_ram_files)

        if _mano == "osm":
            data_dict["osm"]["ram_mean"] = df["RAM Mean"][0]
            data_dict["osm"]["ram_max"] = df["RAM Max"][0]
            data_dict["osm"]["ram_sd"] = df["RAM SD"][0]
        elif _mano == "pishahang":
            data_dict["pishahang"]["ram_mean"] = df["RAM Mean"][0]
            data_dict["pishahang"]["ram_max"] = df["RAM Max"][0]
            data_dict["pishahang"]["ram_sd"] = df["RAM SD"][0]

    for _sys_load_files in sys_load_files:
        _title = (Path(_sys_load_files).name).split("-System-Load")[0]
        _image, _case, _instances = _title.split("_")
        _mano = Path(_sys_load_files).parent.parent.name

        df = pd.read_csv(_sys_load_files)

        if _mano == "osm":
            data_dict["osm"]["load1m_mean"] = df["Load1 Mean"][0]
            data_dict["osm"]["load1m_max"] = df["Load1 Max"][0]
            data_dict["osm"]["load1m_sd"] = df["Load1 SD"][0]
        elif _mano == "pishahang":
            data_dict["pishahang"]["load1m_mean"] = df["Load1 Mean"][0]
            data_dict["pishahang"]["load1m_max"] = df["Load1 Max"][0]
            data_dict["pishahang"]["load1m_sd"] = df["Load1 SD"][0]

    data = []
    for _manoName, _values in sorted(data_dict.items()):
        data.append({
            'mano': _manoName, 
            "cpu_mean": _values["cpu_mean"],
            "cpu_max": _values["cpu_max"],
            "cpu_sd": _values["cpu_sd"],
            "ram_mean": _values["ram_mean"],
            "ram_max": _values["ram_max"],
            "ram_sd": _values["ram_sd"],
            "load1m_mean": _values["load1m_mean"],
            "load1m_max": _values["load1m_max"],
            "load1m_sd": _values["load1m_sd"]
        })

    df = pd.DataFrame(data)

    fig, axs = plt.subplots(3, figsize=(6, 8), sharex=False, sharey=False)
    fig.suptitle('OSM (VM) vs Pishahang (Docker) - 90 Instances', fontsize=25)

    index = np.arange(len(data))
    width = 0.30

    divisions = df['mano']

    df['cpu_mean T'] = abs(T_BOUNDS[1] * df['cpu_sd'] / sqrt(RUNS))
    df['ram_mean T'] = abs(T_BOUNDS[1] * df['ram_sd'] / sqrt(RUNS))
    df['load1m_mean T'] = abs(T_BOUNDS[1] * df['load1m_sd'] / sqrt(RUNS))

    axs[0].bar(index, df['cpu_max'], width, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Max')
    axs[0].bar(index, df['cpu_mean'], width,yerr=df['cpu_mean T'], alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Mean')
    axs[0].set_title("System CPU", fontsize=15)
    axs[0].set_xticks(index)
    axs[0].set_xticklabels(divisions)
    axs[0].set_ylim([0, 100])
    axs[0].set_ylabel('CPU Usage (%)', fontsize=12)
    # axs[0].set_xlabel('# VNFs Instantiated', fontsize=20)

    axs[1].bar(index, df['load1m_max'], width, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Max')
    axs[1].bar(index, df['load1m_mean'], width,yerr=df['load1m_mean T'], alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Mean')
    axs[1].set_title("System Load", fontsize=15)
    axs[1].set_xticks(index)
    axs[1].set_xticklabels(divisions)
    axs[1].set_ylim([0, 5])
    axs[1].set_ylabel('System Load', fontsize=12)
    # axs[0].set_xlabel('# VNFs Instantiated', fontsize=20)

    axs[2].bar(index, df['ram_max'], width, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Max')
    axs[2].bar(index, df['ram_mean'], width,yerr=df['ram_mean T'], alpha=0.6, ecolor='black', capsize=5, color='b', label = 'Mean')
    axs[2].set_title("System RAM", fontsize=15)
    axs[2].set_xticks(index)
    axs[2].set_xticklabels(divisions)
    # axs[2].set_ylim([0, 100])
    axs[2].set_ylabel('MEM Usage (MiB)', fontsize=12)
    # axs[0].set_xlabel('# VNFs Instantiated', fontsize=20)

    plt.legend(loc='best', bbox_to_anchor=(1, 0.3))
    # plt.ylim([0, 50])

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    # plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('MANO', fontsize=20)

    plt.savefig('{}/System_metrics_comparison.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()

    print("")


##############################################
# One on One Comparison graphs  
##############################################
if ONE_ON_ONE_OTHER_BAR:
    ono_i_build_file = [y for x in os.walk(_COMMON_PATH) for y in glob(os.path.join(x[0], 'individual-build-times.csv'))]
    ono_e2e_file = [y for x in os.walk(_COMMON_PATH) for y in glob(os.path.join(x[0], 'end-to-end-time.csv'))]

    # end_to_end_path = Path(_success_ratio_file).parent / "end-to-end-time.csv"
    # etime = (pd.read_csv(end_to_end_path)["end-to-end-time"][0])/360
    # etime = "{:.3}".format(etime)

    data_dict = {
        "pishahang" : {
            "mano_time_mean" : [],
            "mano_time_sd" : [],
            "vim_time_mean" : [],
            "vim_time_sd" : [],
            "end_to_end_mean" : [],
            "end_to_end_sd" : []
        },
        "osm" : {
            "mano_time_mean" : [],
            "mano_time_sd" : [],
            "vim_time_mean" : [],
            "vim_time_sd" : [],
            "end_to_end_mean" : [],
            "end_to_end_sd" : []
        }
    }

    for _ono_i_build_file in ono_i_build_file:
        _mano = Path(_ono_i_build_file).parent.parent.parent.name

        df = pd.read_csv(_ono_i_build_file)

        if _mano == "osm":
            data_dict["osm"]["mano_time_mean"].append(df["mano_time"].mean())
            data_dict["osm"]["vim_time_mean"].append(df["vim_time"].mean())
        elif _mano == "pishahang":
            data_dict["pishahang"]["mano_time_mean"].append(df["mano_time"].mean())
            data_dict["pishahang"]["vim_time_mean"].append(df["vim_time"].mean())

    for _ono_e2e_file in ono_e2e_file:
        _mano = Path(_ono_e2e_file).parent.parent.parent.name

        df = pd.read_csv(_ono_e2e_file)

        if _mano == "osm":
            data_dict["osm"]["end_to_end_mean"].append(df["end-to-end-time"][0])
        elif _mano == "pishahang":
            data_dict["pishahang"]["end_to_end_mean"].append(df["end-to-end-time"][0])


    data = []
    for _manoName, _values in sorted(data_dict.items()):
        data.append({
            'mano': _manoName, 
            "mano_time_mean": statistics.mean(_values["mano_time_mean"]),
            "mano_time_sd": statistics.pstdev(_values["mano_time_mean"]),
            "vim_time_mean": statistics.mean(_values["vim_time_mean"]),
            "vim_time_sd": statistics.pstdev(_values["vim_time_mean"]),
            "end_to_end_mean": statistics.mean(_values["end_to_end_mean"]),
            "end_to_end_sd": statistics.pstdev(_values["end_to_end_mean"]),
        })

    df = pd.DataFrame(data)

    fig, axs = plt.subplots(2, figsize=(6, 8), sharex=False, sharey=False)
    fig.suptitle('OSM (VM) vs Pishahang (Docker) - 90 Instances', fontsize=25)

    index = np.arange(len(data))
    width = 0.30

    divisions = df['mano']

    axs[0].bar(index, df['mano_time_mean'], width, yerr=df['mano_time_sd'], alpha=0.6, ecolor='black', capsize=5, color='r', label = 'MANO Time')
    axs[0].bar(index+width, df['vim_time_mean'], width,yerr=df['vim_time_sd'], alpha=0.6, ecolor='black', capsize=5, color='b', label = 'VIM Time')
    axs[0].set_title("Time Distribution", fontsize=15)
    axs[0].set_xticks(index)
    axs[0].set_xticklabels(divisions)
    # axs[0].set_ylim([0, 100])
    axs[0].set_ylabel('Time (s)', fontsize=12)
    # axs[0].set_xlabel('# VNFs Instantiated', fontsize=20)

    axs[0].legend(loc='best', bbox_to_anchor=(1, 0.2))

    # axs[1].bar(index, df['load1m_max'], width, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'Max')
    axs[1].bar(index, df['end_to_end_mean'], width,yerr=df['end_to_end_sd'], alpha=0.6, ecolor='black', capsize=5, color='b')
    axs[1].set_title("End-to-End Time", fontsize=15)
    axs[1].set_xticks(index)
    axs[1].set_xticklabels(divisions)
    # axs[1].set_ylim([0, 5])
    axs[1].set_ylabel('Time (s)', fontsize=12)
    # axs[0].set_xlabel('# VNFs Instantiated', fontsize=20)

    # plt.ylim([0, 50])

    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    # plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('MANO', fontsize=20)

    plt.savefig('{}/Time_comparison.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()

    print("")


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
        docker_col = df["Docker Container"].str.split('-cpu').str[0]
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

        a2=plt.barh(docker_col, value_col_max, alpha=0.6, ecolor='black', capsize=2, color='red')
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


        # plt.yticks(rotation=30)
        plt.title("OSM - CPU Usage - 180 Instances (30 rpm)\n".format(cpu_title), fontsize=25)
        plt.xlabel("CPU Usage (%)", fontsize=20)
        plt.ylabel("Docker Services", fontsize=20)
        plt.legend((a2[2],a[2]),(header[0],header[1]),loc='lower right')
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
        docker_col = df['Docker Container'].str.split('-mem').str[0]
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
        plt.xlim([0, MEM_MAX_SCALE])

        a2=plt.barh(docker_col, value_col_max, alpha=0.6, ecolor='black', capsize=5, color='red')
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
        plt.title("Pishahang - Memory Usage - 180 Instances (30 rpm)\n", fontsize=25)
        # plt.title("MEM -- {}".format(mem_title),fontsize=25)
        plt.xlabel("Memory Usage (MiB)",fontsize=20)
        plt.ylabel("Docker Services",fontsize=20)
        plt.legend((a2[2],a[2]),(header[0],header[1]),loc='lower right')
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

        fig, axs = plt.subplots(IMAGES, figsize=(6, 8), sharex=False, sharey=True)
        fig.suptitle('{}\nCPU Usage - Different NS'.format(_title.split("-cpu")[0]), y=1.05, fontsize=25)
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
                

                axs[_count].bar(index-width, cpu_case1_mean, width, yerr=case1_t_mean, alpha=0.6, ecolor='black', capsize=5, color='b', label = 'NS 1 VNF')
                axs[_count].bar(index, cpu_case2_mean, width,yerr=case2_t_mean, alpha=0.6, ecolor='black', capsize=5, color='r', label = 'NS 3 VNF')
                axs[_count].bar(index+width, cpu_case3_mean, width,yerr=case3_t_mean, alpha=0.6, ecolor='black', capsize=5, color='y', label = 'NS 5 VNF')
                axs[_count].set_title("{} Image (VNF)".format(_image), fontsize=15)
                axs[_count].set_xticks(index+width/4)
                axs[_count].set_xticklabels(divisions)
                _count += 1

        # plt.xticks(index+width/2, divisions)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylim([0, 50])

        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axes
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)

        plt.ylabel('CPU Usage (%)\n', fontsize=20)
        plt.xlabel('# VNFs Instantiated', fontsize=20)

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
# Individual E2E
#########################################

if I_END_TO_END_TIME_BAR:
    for _i_e2e_file in i_e2e_file:
        print(Path(_i_e2e_file).parent.name)
        print(Path(_i_e2e_file).name)

        _case, _run = Path(_i_e2e_file).parent.name.split("_Run")
        _case = _case.split("-")[1]
        print(_case)
        _docker = Path(_i_e2e_file).name
        _docker = _docker.split(".")[0]
        print(_docker)
        _docker = _docker+"-"+_case+"-"+_run
        print(_docker)
        df = pd.read_csv(_i_e2e_file)

        manotime = df['mano_time']
        vimtime = df['vim_time']
        manoid = df['id']

        fig = plt.figure()
        plt.figure(figsize=(11,6))
        plt.suptitle('Individual build times'.format(_docker), fontsize=22)
        ax = fig.add_subplot(1,1,1) 
        plt.xlabel('MANO ID', fontsize=18)
        plt.ylabel('Time (s)', fontsize=16) 
        plt.plot(manoid, manotime,label = 'mano_time')
        plt.plot(manoid, vimtime, label = 'vim_time')
    
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))


        plt.xticks(rotation=-45)

        # ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))   #to get a tick every 15 minutes
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        plt.savefig('{}/{}.png'.format(_OUT_PATH, _docker) ,bbox_inches='tight',dpi=100)

#########################################
# Life cycle graphs
#########################################

if LIFECYCLE_GRAPH:
    for _cpu_lifecycle_file in cpu_lifecycle_file:
        print(Path(_cpu_lifecycle_file).parent.name)
        print(Path(_cpu_lifecycle_file).name)

        _case, _run = Path(_cpu_lifecycle_file).parent.name.split("_Run")
        _case = _case.split("-")[1]
        print(_case)
        _docker = Path(_cpu_lifecycle_file).name
        _docker = _docker.split(".")[0]
        print(_docker)
        _docker = _docker+"-"+_case+"-"+_run
        print(_docker)
        df = pd.read_csv(_cpu_lifecycle_file)

        unix_time = df['time']
        user = df['user']
        system = df['system']
        # unix_time = np.array(unix_time)
        # user = np.array(user)
        # system = np.array(system)

        # unix_time_smooth = np.linspace(unix_time.min(),unix_time.max(),600)
        # user_smooth = spline(unix_time,user,unix_time_smooth)
        # system_smooth = spline(unix_time,system,system_smooth)
        fig = plt.figure()
        plt.figure(figsize=(15,6))
        plt.suptitle('{}'.format(_docker), fontsize=22)
        ax = fig.add_subplot(1,1,1) 
        plt.xlabel('Time', fontsize=18)
        plt.ylabel('VNF instances', fontsize=16) 
        plt.plot(unix_time[0::250], user[0::250],'ro-',label = 'user')
        plt.plot(unix_time[0::250] , system[0::250],'bo-',label = 'system')
        plt.plot(unix_time,user,'ro-',markevery=250)
        plt.plot(unix_time,system,'bo-',markevery=250)
        
        frequency = 10
    
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=-90)
        plt.xticks(unix_time[::frequency])

       
        
        # ax.xaxis.set_major_locator(plt.MaxNLocator(30))
        #ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=20))   #to get a tick every 15 minutes
        #ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        plt.savefig('{}/{}.png'.format(_OUT_PATH, _docker) ,bbox_inches='tight',dpi=100)

#########################################
# Top Life cycle graphs
#########################################

if TOP_LIFECYCLE_GRAPH:
    osm_cpu_lifecycle_files = [y for x in os.walk(TOP_OSM_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]
    pishahang_cpu_lifecycle_files = [y for x in os.walk(TOP_PISHAHANG_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]

    fig, axs = plt.subplots(3, figsize=(12, 10), sharex=True, sharey=True)
    _count = 0

    for _cpu_lifecycle_file in sorted(osm_cpu_lifecycle_files):
        _docker = Path(_cpu_lifecycle_file).name
        _docker = _docker.split(".")[1]
        print(_docker)

        df = pd.read_csv(_cpu_lifecycle_file)
        df['total_cpu'] =  df['user'] + df['system']

        # df.plot()
        # df['total_cpu'].plot()

        df['time'] = pd.to_datetime(df['time'],format= '%Y-%m-%d %H:%M:%S' ).dt.time
        df['total_cpu'] = df['total_cpu'].ewm(span =3).mean()
        # df['total_cpu'].ewm(span =5).mean().plot()
        # plt.plot(df['time'], df['total_cpu'])
        # plt.show()

        axs[_count].plot(df['time'], df['total_cpu'])
        axs[_count].set_title(_docker, fontsize=25)

        # axs[0].set_xticks(index)
        axs[_count].set_ylim([0, 100])
        axs[_count].get_xaxis().set_visible(False)
        # axs[0].set_ylabel('CPU Usage (%)', fontsize=12)
       
        _count += 1

    fig.suptitle('OSM - CPU Usage - Lifecycle Graphs Top 3\n({} - {})'.format(df["time"].iloc[-1], df["time"].iloc[0]), y=1.01, fontsize=25)

    axs[2].get_xaxis().set_visible(True)
    axs[2].set_xlabel('\nTime series', fontsize=20)
    axs[2].tick_params(axis='x', labelsize=15)

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('Time', fontsize=20)

    plt.subplots_adjust(hspace=0.3)
    plt.savefig('{}/OSM-TOP-3-Lifecycle.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()

    # ######################################
    # For Pishahang 
    # ######################################


    fig, axs = plt.subplots(3, figsize=(12, 10), sharex=True, sharey=True)
    _count = 0

    for _cpu_lifecycle_file in sorted(pishahang_cpu_lifecycle_files):
        _docker = Path(_cpu_lifecycle_file).name
        _docker = _docker.split(".")[1]
        print(_docker)

        df = pd.read_csv(_cpu_lifecycle_file)
        df['total_cpu'] =  df['user'] + df['system']

        # df.plot()
        # df['total_cpu'].plot()

        df['time'] = pd.to_datetime(df['time'],format= '%Y-%m-%d %H:%M:%S' ).dt.time
        df['total_cpu'] = df['total_cpu'].ewm(span =3).mean()
        # df['total_cpu'].ewm(span =5).mean().plot()
        # plt.plot(df['time'], df['total_cpu'])
        # plt.show()

        axs[_count].plot(df['time'], df['total_cpu'])
        axs[_count].set_title(_docker, fontsize=25)

        # axs[0].set_xticks(index)
        axs[_count].set_ylim([0, 100])
        axs[_count].get_xaxis().set_visible(False)
        # axs[0].set_ylabel('CPU Usage (%)', fontsize=12)
       
        _count += 1

    fig.suptitle('Pishahang - CPU Usage - Lifecycle Graphs Top 3\n({} - {})'.format(df["time"].iloc[-1], df["time"].iloc[0]), y=1.01, fontsize=25)

    axs[2].get_xaxis().set_visible(True)
    axs[2].set_xlabel('\nTime series', fontsize=20)
    axs[2].tick_params(axis='x', labelsize=15)

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('Time', fontsize=20)

    plt.subplots_adjust(hspace=0.3)
    plt.savefig('{}/Pishahang-TOP-3-Lifecycle.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()


#########################################
# Scalability Life cycle graphs
#########################################

if TOP_SCALABILITY_LIFECYCLE_GRAPH:
    child_cpu_lifecycle_files = [y for x in os.walk(CHILD_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]
    parent_cpu_lifecycle_files = [y for x in os.walk(PARENT_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]

    fig, axs = plt.subplots(3, figsize=(12, 10), sharex=True, sharey=True)
    _count = 0

    for _cpu_lifecycle_file in sorted(child_cpu_lifecycle_files):
        _docker = Path(_cpu_lifecycle_file).name
        _docker = _docker.split(".")[1]
        print(_docker)

        df = pd.read_csv(_cpu_lifecycle_file)
        df['total_cpu'] =  df['user'] + df['system']

        # df.plot()
        # df['total_cpu'].plot()

        df['time'] = pd.to_datetime(df['time'],format= '%Y-%m-%d %H:%M:%S' ).dt.time
        df['total_cpu'] = df['total_cpu'].ewm(span =3).mean()
        # df['total_cpu'].ewm(span =5).mean().plot()
        # plt.plot(df['time'], df['total_cpu'])
        # plt.show()

        axs[_count].plot(df['time'], df['total_cpu'])
        axs[_count].set_title(_docker, fontsize=25)

        # axs[0].set_xticks(index)
        axs[_count].set_ylim([0, 100])
        axs[_count].get_xaxis().set_visible(False)
        # axs[0].set_ylabel('CPU Usage (%)', fontsize=12)
       
        _count += 1

    fig.suptitle('Child - CPU Usage - Lifecycle Graphs Top 3\n({} - {})'.format(df["time"].iloc[-1], df["time"].iloc[0]), y=1.01, fontsize=25)

    axs[2].get_xaxis().set_visible(True)
    axs[2].set_xlabel('\nTime series', fontsize=20)

    axs[2].tick_params(axis='x', labelsize=15)

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('Time', fontsize=20)

    plt.subplots_adjust(hspace=0.3)
    plt.savefig('{}/Child-TOP-3-Lifecycle.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()

    # ######################################
    # For Parent 
    # ######################################


    fig, axs = plt.subplots(3, figsize=(12, 10), sharex=True, sharey=True)
    _count = 0

    for _cpu_lifecycle_file in sorted(parent_cpu_lifecycle_files):
        _docker = Path(_cpu_lifecycle_file).name
        _docker = _docker.split(".")[1]
        print(_docker)

        df = pd.read_csv(_cpu_lifecycle_file)
        df['total_cpu'] =  df['user'] + df['system']

        # df.plot()
        # df['total_cpu'].plot()

        df['time'] = pd.to_datetime(df['time'],format= '%Y-%m-%d %H:%M:%S' ).dt.time
        df['total_cpu'] = df['total_cpu'].ewm(span =3).mean()
        # df['total_cpu'].ewm(span =5).mean().plot()
        # plt.plot(df['time'], df['total_cpu'])
        # plt.show()

        axs[_count].plot(df['time'], df['total_cpu'])
        axs[_count].set_title(_docker, fontsize=25)

        # axs[0].set_xticks(index)
        axs[_count].set_ylim([0, 100])
        axs[_count].get_xaxis().set_visible(False)
        # axs[0].set_ylabel('CPU Usage (%)', fontsize=12)
       
        _count += 1

    fig.suptitle('Parent - CPU Usage - Lifecycle Graphs Top 3\n({} - {})'.format(df["time"].iloc[-1], df["time"].iloc[0]), y=1.01, fontsize=25)

    axs[2].get_xaxis().set_visible(True)
    axs[2].set_xlabel('\nTime series', fontsize=20)

    axs[2].tick_params(axis='x', labelsize=15)
    
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)

    plt.ylabel('CPU Usage (%)\n', fontsize=20)
    # plt.xlabel('Time', fontsize=20)

    plt.subplots_adjust(hspace=0.3)
    plt.savefig('{}/Parent-TOP-3-Lifecycle.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
    plt.close()







#########################################
#########################################
# END
#########################################
#########################################




print("Total time: {}".format(time.time() - start_time))

