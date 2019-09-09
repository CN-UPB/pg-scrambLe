# import csv
from collections import Counter
import ntpath
import pandas as pd # pip install pandas
import os
from glob import glob
import time
from pathlib import Path
import json
import statistics
import csv

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Comparison-VM-Docker/osm/data_csv"
_OUT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/Common Results/FinalDemo/Comparison-VM-Docker/osm/final"

def average_cpu (csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    df['totalcpu'] = df['user'] + df['system'] 

    _max = df['totalcpu'].max()
    _min = df['totalcpu'].min()
    _mean = df['totalcpu'].mean()

    print("CPU Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": float(_mean), "min": float(_min), "max": float(_max)} 


def average_mem(csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    _max = df['ram'].max()
    _min = df['ram'].min()
    _mean = df['ram'].mean()

    print("MEM Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": float(_mean), "min": float(_min), "max": float(_max)} 

def average_sys_cpu(csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    df['totalsyscpu'] = df['user'] + df['system'] 

    _max = df['totalsyscpu'].max()
    _min = df['totalsyscpu'].min()
    _mean = df['totalsyscpu'].mean()

    print("System CPU Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": float(_mean), "min": float(_min), "max": float(_max)} 

def average_sys_load(csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    load1_max = df['load1'].max()
    load1_min = df['load1'].min()
    load1_mean = df['load1'].mean()

    load5_max = df['load5'].max()
    load5_min = df['load5'].min()
    load5_mean = df['load5'].mean()

    load15_max = df['load15'].max()
    load15_min = df['load15'].min()
    load15_mean = df['load15'].mean()

    print("Load1 Mean: {} \t Min: {} \t Max: {} \n".format( load1_mean, load1_min, load1_max))
    return {"mean1": float(load1_mean), "min1": float(load1_min), "max1": float(load1_max),
            "mean5": float(load5_mean), "min5": float(load5_min), "max5": float(load5_max),
            "mean15": float(load15_mean), "min15": float(load15_min), "max15": float(load15_max)} 

    

def average_sys_ram(csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    _min = df['used'].min()
    _max = df['used'].max()
    _mean = df['used'].mean()

    print("MEM Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": float(_mean), "min": float(_min), "max": float(_max)} 


start_time = time.time()

cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-mem_usage.csv'))]
sys_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], 'system-*.csv'))]

result_cpu_dict = {}
result_mem_dict = {}
result_docker_cpu_dict = {}
result_docker_mem_dict = {}
result_sys_cpu_dict = {}
result_sys_load_dict = {}
result_sys_ram_dict = {}

for _sys_file in sys_files:
    print(Path(_sys_file).parent.name)
    print(Path(_sys_file).name)

    _case, _run = Path(_sys_file).parent.name.split("_Run")
    _case = _case.split("-")[1]
    _docker = Path(_sys_file).name
    _docker = _docker.split(".")[0]

    if ntpath.basename(_sys_file) == "system-cpu.csv":

        if not _case in result_sys_cpu_dict:
            result_sys_cpu_dict[_case] = {}

        if not _docker in result_sys_cpu_dict[_case]:
            result_sys_cpu_dict[_case][_docker] = {}

        # average_cpu(_cpu_file)

        result_sys_cpu_dict[_case][_docker][_run] = average_sys_cpu(_sys_file)

    if ntpath.basename(_sys_file) == "system-load.csv":

        if not _case in result_sys_load_dict:
            result_sys_load_dict[_case] = {}

        if not _docker in result_sys_load_dict[_case]:
            result_sys_load_dict[_case][_docker] = {}

        # average_cpu(_cpu_file)

        result_sys_load_dict[_case][_docker][_run] = average_sys_load(_sys_file)

    if ntpath.basename(_sys_file) == "system-ram.csv":

        if not _case in result_sys_ram_dict:
            result_sys_ram_dict[_case] = {}

        if not _docker in result_sys_ram_dict[_case]:
            result_sys_ram_dict[_case][_docker] = {}

        # average_cpu(_cpu_file)

        result_sys_ram_dict[_case][_docker][_run] = average_sys_ram(_sys_file)

for _cpu_file in cpu_files:
    print(Path(_cpu_file).parent.name)
    print(Path(_cpu_file).name)

    if ntpath.basename(_cpu_file) == "system-cpu.csv":
        continue

    _case, _run = Path(_cpu_file).parent.name.split("_Run")
    _case = _case.split("-")[1]
    _docker = Path(_cpu_file).name
    _docker = _docker.split(".")[0]

    if not _docker in result_docker_cpu_dict:
        result_docker_cpu_dict[_docker] = {}

    if not _case in result_docker_cpu_dict[_docker]:
        result_docker_cpu_dict[_docker][_case] = {}

    if not _case in result_cpu_dict:
        result_cpu_dict[_case] = {}

    if not _docker in result_cpu_dict[_case]:
        result_cpu_dict[_case][_docker] = {}

    # average_cpu(_cpu_file)

    result_cpu_dict[_case][_docker][_run] = average_cpu(_cpu_file)
    result_docker_cpu_dict[_docker][_case][_run] = average_cpu(_cpu_file)

for _mem_file in mem_files:
    print(Path(_mem_file).parent.name)
    print(Path(_mem_file).name)

    _case, _run = Path(_mem_file).parent.name.split("_Run")
    _case = _case.split("-")[1]
    _docker = Path(_mem_file).name
    _docker = _docker.split(".")[0]

    if not _docker in result_docker_mem_dict:
        result_docker_mem_dict[_docker] = {}

    if not _case in result_docker_mem_dict[_docker]:
        result_docker_mem_dict[_docker][_case] = {}

    if not _case in result_mem_dict:
        result_mem_dict[_case] = {}

    if not _docker in result_mem_dict[_case]:
        result_mem_dict[_case][_docker] = {}

    result_mem_dict[_case][_docker][_run] = average_mem(_mem_file)
    result_docker_mem_dict[_docker][_case][_run] = average_mem(_mem_file)


# print(json.dumps(result_cpu_dict, sort_keys=True, indent=4))
# print(json.dumps(result_mem_dict, sort_keys=True, indent=4))

for _case, _caseValue in result_sys_cpu_dict.items():
    print(_case)
    with open('{outpath}/{case}-System-CPU-Final-Results.csv'.format(outpath=_OUT_PATH, case=_case), mode='w') as system_cpu_resultsfile:
        fieldnames = ['CPU Run1', 'CPU Run2', 'CPU Run3', 'CPU Mean', 'CPU SD', 'CPU Max', 'CPU Min', 'CPU Max SD']
        writer = csv.writer(system_cpu_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _docker, _dockerValue in _caseValue.items():
            _dockerName = _docker
            _meanofMeans = statistics.mean([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMax = statistics.mean([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMin = statistics.mean([_dockerValue["1"]["min"], _dockerValue["2"]["min"], _dockerValue["3"]["min"]])

            writer.writerow([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])

for _case, _caseValue in result_sys_load_dict.items():
    print(_case)
    with open('{outpath}/{case}-System-Load-Final-Results.csv'.format(outpath=_OUT_PATH, case=_case), mode='w') as system_load_resultsfile:
        fieldnames = ['Load1 Run1', 'Load5 Run1', 'Load15 Run1', 'Load1 Run2', 'Load5 Run2', 'Load15 Run2', 'Load1 Run3', 'Load5 Run3', 'Load15 Run3', 'Load1 Mean', 'Load1 SD', 'Load5 Mean', 'Load5 SD', 'Load15 Mean', 'Load15 SD','Load1 Max', 'Load1 Min','Load5 Max', 'Load5 Min','Load15 Max', 'Load15 Min', 'Load1 Max SD', 'Load5 Max SD', 'Load15 Max SD']
        writer = csv.writer(system_load_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _docker, _dockerValue in _caseValue.items():
            _dockerName = _docker
            _meanofMeans1 = statistics.mean([_dockerValue["1"]["mean1"], _dockerValue["2"]["mean1"], _dockerValue["3"]["mean1"]])
            _meanofMeans5 = statistics.mean([_dockerValue["1"]["mean5"], _dockerValue["2"]["mean5"], _dockerValue["3"]["mean5"]])
            _meanofMeans15 = statistics.mean([_dockerValue["1"]["mean15"], _dockerValue["2"]["mean15"], _dockerValue["3"]["mean15"]])

            _stddevofMeans1 = statistics.pstdev([_dockerValue["1"]["mean1"], _dockerValue["2"]["mean1"], _dockerValue["3"]["mean1"]])
            _stddevofMeans5 = statistics.pstdev([_dockerValue["1"]["mean5"], _dockerValue["2"]["mean5"], _dockerValue["3"]["mean5"]])
            _stddevofMeans15 = statistics.pstdev([_dockerValue["1"]["mean15"], _dockerValue["2"]["mean15"], _dockerValue["3"]["mean15"]])
            _stddevofMax1 = statistics.pstdev([_dockerValue["1"]["max1"], _dockerValue["2"]["max1"], _dockerValue["3"]["max1"]])
            _stddevofMax5 = statistics.pstdev([_dockerValue["1"]["max5"], _dockerValue["2"]["max5"], _dockerValue["3"]["max5"]])
            _stddevofMax15 = statistics.pstdev([_dockerValue["1"]["max15"], _dockerValue["2"]["max15"], _dockerValue["3"]["max15"]])

            _meanofMax1 = statistics.mean([_dockerValue["1"]["max1"], _dockerValue["2"]["max1"], _dockerValue["3"]["max1"]])
            _meanofMax5 = statistics.mean([_dockerValue["1"]["max5"], _dockerValue["2"]["max5"], _dockerValue["3"]["max5"]])
            _meanofMax15 = statistics.mean([_dockerValue["1"]["max15"], _dockerValue["2"]["max15"], _dockerValue["3"]["max15"]])

            _meanofMin1 = statistics.mean([_dockerValue["1"]["min1"], _dockerValue["2"]["min1"], _dockerValue["3"]["min1"]])
            _meanofMin5 = statistics.mean([_dockerValue["1"]["min5"], _dockerValue["2"]["min5"], _dockerValue["3"]["min5"]])
            _meanofMin15 = statistics.mean([_dockerValue["1"]["min15"], _dockerValue["2"]["min15"], _dockerValue["3"]["min15"]])

            # print(_dockerName)
            # print(_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"])
            # print(_meanofMeans)
            # print(_stddevofMeans)
            # print(_meanofMax)
            # print(_meanofMin)

            writer.writerow([_dockerValue["1"]["mean1"], _dockerValue["1"]["mean5"], _dockerValue["1"]["mean15"],_dockerValue["2"]["mean1"], _dockerValue["2"]["mean5"], _dockerValue["2"]["mean15"],_dockerValue["3"]["mean1"], _dockerValue["3"]["mean5"], _dockerValue["3"]["mean15"],_meanofMeans1, _stddevofMeans1,_meanofMeans5, _stddevofMeans5,_meanofMeans15, _stddevofMeans15,
            _meanofMax1, _meanofMin1, _meanofMax5, _meanofMin5,_meanofMax15, _meanofMin15, _stddevofMax1, _stddevofMax5, _stddevofMax15])
            
            #_meanofMeans, _stddevofMeans, _meanofMax, _meanofMin,

for _case, _caseValue in result_sys_ram_dict.items():
    print(_case)
    with open('{outpath}/{case}-System-RAM-Final-Results.csv'.format(outpath=_OUT_PATH, case=_case), mode='w') as system_ram_resultsfile:
        fieldnames = ['RAM Run1', 'RAM Run2', 'RAM Run3', 'RAM Mean', 'RAM SD', 'RAM Max', 'RAM Min', 'RAM Max SD']
        writer = csv.writer(system_ram_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _docker, _dockerValue in _caseValue.items():
            _dockerName = _docker
            _meanofMeans = statistics.mean([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMax = statistics.mean([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMin = statistics.mean([_dockerValue["1"]["min"], _dockerValue["2"]["min"], _dockerValue["3"]["min"]])

            # print(_dockerName)
            # print(_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"])
            # print(_meanofMeans)
            # print(_stddevofMeans)
            # print(_meanofMax)
            # print(_meanofMin)

            writer.writerow([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])   

for _case, _caseValue in result_cpu_dict.items():
    print(_case)
    with open('{outpath}/{case}-CPU-Final-Results.csv'.format(outpath=_OUT_PATH, case=_case), mode='w') as cpu_resultsfile:
        fieldnames = ['Docker Container', 'CPU Run1', 'CPU Run2', 'CPU Run3', 'CPU Mean', 'CPU SD', 'CPU Max', 'CPU Min', 'CPU Max SD']
        writer = csv.writer(cpu_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _docker, _dockerValue in _caseValue.items():
            _dockerName = _docker
            _meanofMeans = statistics.mean([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMax = statistics.mean([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMin = statistics.mean([_dockerValue["1"]["min"], _dockerValue["2"]["min"], _dockerValue["3"]["min"]])

            # print(_dockerName)
            # print(_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"])
            # print(_meanofMeans)
            # print(_stddevofMeans)
            # print(_meanofMax)
            # print(_meanofMin)

            writer.writerow([_dockerName, _dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])

for _case, _caseValue in result_mem_dict.items():
    print(_case)
    with open('{outpath}/{case}-MEM-Final-Results.csv'.format(outpath=_OUT_PATH, case=_case), mode='w') as mem_resultsfile:
        fieldnames = ['Docker Container', 'MEM Run1', 'MEM Run2', 'MEM Run3', 'MEM Mean', 'MEM SD', 'MEM Max', 'MEM Min', 'MEM Max SD']
        writer = csv.writer(mem_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _docker, _dockerValue in _caseValue.items():

            _dockerName = _docker
            _meanofMeans = statistics.mean([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMax = statistics.mean([_dockerValue["1"]["max"], _dockerValue["2"]["max"], _dockerValue["3"]["max"]])
            _meanofMin = statistics.mean([_dockerValue["1"]["min"], _dockerValue["2"]["min"], _dockerValue["3"]["min"]])

            # print(_dockerName)
            # print(_dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"])
            # print(_meanofMeans)
            # print(_stddevofMeans)
            # print(_meanofMax)
            # print(_meanofMin)

            writer.writerow([_dockerName, _dockerValue["1"]["mean"], _dockerValue["2"]["mean"], _dockerValue["3"]["mean"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])


for _docker, _dockerValue in result_docker_cpu_dict.items():
    print(_docker)
    with open('{outpath}/{docker}-CPU-Docker-Final-Results.csv'.format(outpath=_OUT_PATH, docker=_docker), mode='w') as cpu_resultsfile:
        fieldnames = ['Case', 'CPU Run1', 'CPU Run2', 'CPU Run3', 'CPU Mean', 'CPU SD', 'CPU Max', 'CPU Min', 'CPU Max SD']
        writer = csv.writer(cpu_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _case, _caseValue in _dockerValue.items():
            _caseName = _case
            _meanofMeans = statistics.mean([_caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_caseValue["1"]["max"], _caseValue["2"]["max"], _caseValue["3"]["max"]])
            _meanofMax = statistics.mean([_caseValue["1"]["max"], _caseValue["2"]["max"], _caseValue["3"]["max"]])
            _meanofMin = statistics.mean([_caseValue["1"]["min"], _caseValue["2"]["min"], _caseValue["3"]["min"]])

            writer.writerow([_caseName, _caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])


for _docker, _dockerValue in result_docker_mem_dict.items():
    print(_docker)
    with open('{outpath}/{docker}-MEM-Docker-Final-Results.csv'.format(outpath=_OUT_PATH, docker=_docker), mode='w') as mem_resultsfile:
        fieldnames = ['Case', 'MEM Run1', 'MEM Run2', 'MEM Run3', 'MEM Mean', 'MEM SD', 'MEM Max', 'MEM Min', 'MEM Max SD']
        writer = csv.writer(mem_resultsfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)

        for _case, _caseValue in _dockerValue.items():
            _caseName = _case
            _meanofMeans = statistics.mean([_caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"]])
            _stddevofMeans = statistics.pstdev([_caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"]])
            _stddevofMax = statistics.pstdev([_caseValue["1"]["max"], _caseValue["2"]["max"], _caseValue["3"]["max"]])
            _meanofMax = statistics.mean([_caseValue["1"]["max"], _caseValue["2"]["max"], _caseValue["3"]["max"]])
            _meanofMin = statistics.mean([_caseValue["1"]["min"], _caseValue["2"]["min"], _caseValue["3"]["min"]])

            writer.writerow([_caseName, _caseValue["1"]["mean"], _caseValue["2"]["mean"], _caseValue["3"]["mean"], _meanofMeans, _stddevofMeans, _meanofMax, _meanofMin, _stddevofMax])



print("Total time: {}".format(time.time() - start_time))

