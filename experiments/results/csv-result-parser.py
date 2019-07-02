# import csv
from collections import Counter
import ntpath
import pandas as pd # pip install pandas
import os
from glob import glob
import time
from pathlib import Path
import json

def average_cpu (csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    df['totalcpu'] = df['user'] + df['system'] 

    _max = df['totalcpu'].max()
    _min = df['totalcpu'].min()
    _mean = df['totalcpu'].mean()

    print("CPU Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": _mean, "min": _min, "max": _max} 


def average_mem(csv_filepath):
    # print(ntpath.basename(csv_filepath))
    df=pd.read_csv(csv_filepath)

    _max = df['ram'].max()
    _min = df['ram'].min()
    _mean = df['ram'].mean()

    print("MEM Mean: {} \t Min: {} \t Max: {} \n".format( _mean, _min, _max))
    return {"mean": _mean, "min": _min, "max": _max} 

# def average_cpu2 (csv_filepath):
#     print(ntpath.basename(csv_filepath))
#     with open(csv_filepath, "r") as f:
#         reader = csv.reader(f)
#         next(reader, None)
#         row_count = 0
#         cpu_running_sum = 0.0
#         for row in reader:
#             # print(row)
#             cpu_running_sum += float(row[1]) + float(row[2])
#             row_count += 1            

#     print("CPU Average: {} \n".format(cpu_running_sum/row_count))

#     return cpu_running_sum/row_count

# def average_mem(csv_filepath):
#     print(ntpath.basename(csv_filepath))
#     with open(csv_filepath, "r") as f:
#         reader = csv.reader(f)
#         next(reader, None)
#         row_count = 0
#         mem_running_sum = 0.0
#         for row in reader:
#             # print(row)
#             mem_running_sum += float(row[1])
#             row_count += 1            

#     print("MEM Average: {} \n".format(mem_running_sum/row_count))

#     return mem_running_sum/row_count

start_time = time.time()

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/experiments/results/OSM Results/"
cpu_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-cpu.csv'))]
mem_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], '*-mem_usage.csv'))]

result_cpu_dict = {}
result_mem_dict = {}

for _cpu_file in cpu_files:
    print(Path(_cpu_file).parent.name)
    print(Path(_cpu_file).name)

    _case, _run = Path(_cpu_file).parent.name.split("_Run")
    _case = _case.split("-")[1]
    _docker = Path(_cpu_file).name

    if not _case in result_cpu_dict:
        result_cpu_dict[_case] = {}

    if not _docker in result_cpu_dict[_case]:
        result_cpu_dict[_case][_docker] = {}

    if ntpath.basename(_cpu_file) == "system-cpu.csv":
        continue

    # average_cpu(_cpu_file)

    result_cpu_dict[_case][_docker][_run] = average_cpu(_cpu_file)

for _mem_file in mem_files:
    print(Path(_mem_file).parent.name)
    print(Path(_mem_file).name)

    _case, _run = Path(_mem_file).parent.name.split("_Run")
    _case = _case.split("-")[1]
    _docker = Path(_mem_file).name

    if not _case in result_mem_dict:
        result_mem_dict[_case] = {}

    if not _docker in result_mem_dict[_case]:
        result_mem_dict[_case][_docker] = {}

    result_mem_dict[_case][_docker][_run] = average_mem(_mem_file)
    
    
print("Total time: {}".format(time.time() - start_time))

print(json.dumps(result_cpu_dict, sort_keys=True, indent=4))
print(json.dumps(result_mem_dict, sort_keys=True, indent=4))