import time
import subprocess

TOTALTIME = 1500
DIVIDER = 60
SAMPLERATE = 0.001

PID_DICT = {
    "ro-openmanod": "19658",
    "lcm": "26717"
}

# PID_DICT = {
#     "osm-mon-server": "11996", 
#     "osm-mon-evaluator": "11997", 
#     "osm-mon-collector": "11998", 
#     "lcm": "11386",
#     "osm-policy-agent": "9209",
#     "lightui-nginx-master": "6124",
#     "nbi": "3733",
#     "ro-openmanod": "7298"
# }

_cmd_template = "sudo pyflame34 -s {totaltime} -r {samplerate} -p {pid} -x --threads  | flamegraph.pl > ./results/{svgname}-{counter}-{id}.svg"

counter = 0
_id = 0
while (counter < TOTALTIME):
    for _name, _pid  in PID_DICT.items():
        _cmd_tmp = _cmd_template.format(
            totaltime = DIVIDER,
            samplerate = SAMPLERATE,
            pid = _pid,
            svgname = _name,
            counter = counter,
            id=_id
        )
        print(_cmd_tmp)
        subprocess.Popen(_cmd_tmp, shell=True)
    counter += DIVIDER
    _id += 1
    time.sleep(DIVIDER+1)
