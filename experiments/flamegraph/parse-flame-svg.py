import os
from glob import glob

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import time
import matplotlib.dates as mdates
import numpy as np

import re
def sorted_nicely( l ):
    """ Sorts the given iterable in the way that is expected.
 
    Required arguments:
    l -- The iterable to be sorted.
 
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

_PATH = "/home/ashwin/Documents/MSc/pg-scramble/experiments/experiments/results/Common Results/Report/flame_graphs"
_OUT_PATH = "/home/ashwin/Documents/MSc/pg-scramble/experiments/experiments/results/Common Results/Report/"

lcm_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], 'lcm-*'))]
ro_files = [y for x in os.walk(_PATH) for y in glob(os.path.join(x[0], 'ro-openmanod-*'))]

lcm_data = []
for _lcm_file in sorted_nicely(lcm_files):
    with open(_lcm_file) as fp:
        line = fp.readline()
        cnt = 1
        instantiate = 0.0
        terminate = 0.0

        while line:
            if "instantiate" in line:
                instantiate += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1
            elif "terminate" in line:
                terminate += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1


            line = fp.readline()

    lcm_data.append({
        'time': int(os.path.basename(_lcm_file).split("-")[1].split(".")[0]), 
        'instantiate': instantiate,
        'terminate': terminate
    })

    print(os.path.basename(_lcm_file))
    print("instantiate", instantiate)
    print("terminate", terminate)
    print("\n\n")

print("#######################")
print("--- RO ---")
print("#######################")

ro_data = []
for _ro_files in sorted_nicely(ro_files):
    with open(_ro_files) as fp:
        line = fp.readline()
        cnt = 1
        _refres_elements = 0.0
        _proccess_pending_tasks = 0.0
        new_vm = 0.0
        del_vm = 0.0

        instantiate = 0.0
        terminate = 0.0

        while line:
            if "_refres_elements" in line:
                _refres_elements += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1
            elif "_proccess_pending_tasks" in line:
                _proccess_pending_tasks += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1
            elif "new_vm" in line:
                new_vm += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1
            elif "del_vm" in line:
                del_vm += float(line.split("samples")[1].split("%")[0].split(",")[1].strip())                
                # print("Line {}: {}".format(cnt, 
                #             line.split("samples")[1].split("%")[0].split(",")[1].strip()) )
                cnt += 1

            line = fp.readline()

    ro_data.append({
        'time': int(os.path.basename(_ro_files).split("-")[2].split(".")[0]), 
        '_refres_elements': _refres_elements,
        '_proccess_pending_tasks': _proccess_pending_tasks,
        'new_vm': new_vm,
        'del_vm': del_vm
    })

    print(os.path.basename(_ro_files))
    print("_refres_elements", _refres_elements)
    print("_proccess_pending_tasks", _proccess_pending_tasks)
    print("new_vm", new_vm)
    print("del_vm", del_vm)
    print("\n\n")


df_lcm = pd.DataFrame(lcm_data) 
df_lcm = df_lcm.sort_values('time')

instantiate = df_lcm['instantiate']
terminate = df_lcm['terminate']

# width = 0.30
# plt.figure(figsize=(10,6))

# # a2=plt.bar(docker_col, value_col_max, alpha=0.6, ecolor='black', capsize=2, color='red')
# # a=plt.bar(docker_col, value_col, xerr=value_col_t_mean, alpha=0.6, ecolor='black', capsize=2, color='blue')

# plt.plot(df['time'], instantiate, label = 'instantiate')
# plt.plot(df['time'], terminate, label = 'terminate')

# plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

# plt.show()

# plt.savefig('RO.png', bbox_inches='tight', dpi=100)

# ------------------------------

df = pd.DataFrame(ro_data) 
df = df.sort_values('time')

_refres_elements = df['_refres_elements']
_proccess_pending_tasks = df['_proccess_pending_tasks']
new_vm = df['new_vm']
del_vm = df['del_vm']

width = 0.30
plt.figure(figsize=(10,6))

fig, axs = plt.subplots(2, figsize=(6, 8), sharex=False, sharey=True)
fig.suptitle('Frequency Distribution of Functions', fontsize=25)

axs[0].set_title("RO Function Calls", fontsize=15)
axs[0].plot(df['time'], _refres_elements, label = 'refres_elements')
axs[0].plot(df['time'], _proccess_pending_tasks, label = 'proccess_pending_tasks')
axs[0].plot(df['time'], new_vm, label = 'new_vm')
axs[0].plot(df['time'], del_vm, label = 'del_vm')
axs[0].legend(loc='best', bbox_to_anchor=(1, 0.32))
axs[0].set_ylabel('Samples (%)', fontsize=12)

axs[1].set_title("LCM Function Calls", fontsize=15)
axs[1].plot(df['time'], instantiate, label = 'instantiate')
axs[1].plot(df['time'], terminate, label = 'terminate')
axs[1].legend(loc='best', bbox_to_anchor=(1, 0.2))
axs[1].set_ylabel('Samples (%)', fontsize=12)
axs[1].set_xlabel('Time (s)', fontsize=12)

fig.add_subplot(111, frameon=False)
# hide tick and tick label of the big axes
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
plt.grid(False)

# plt.ylabel('CPU Usage (%)\n', fontsize=20)
# plt.xlabel('MANO', fontsize=20)

plt.savefig('{}/function-samples.png'.format(_OUT_PATH) ,bbox_inches='tight',dpi=100)
plt.close()
