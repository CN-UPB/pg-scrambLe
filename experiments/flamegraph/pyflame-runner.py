import time
import subprocess

TOTALTIME = 100
SAMPLERATE = 0.01

PID_DICT = {
    "osm-mon-server": "11996", 
    "osm-mon-evaluator": "11997", 
    "osm-mon-collector": "11998", 
    "lcm": "11386",
    "osm-policy-agent": "9209",
    "lightui-nginx-master": "6124",
    "nbi": "3733",
    "ro-openmanod": "7298"
}

_cmd_template = "pyflame34 -s {totaltime} -r {samplerate} -p {pid} -x --threads  | flamegraph.pl > {svgname}.svg"

for _name, _pid  in PID_DICT.items():
    _cmd_tmp = _cmd_template.format(
        totaltime = TOTALTIME,
        samplerate = SAMPLERATE,
        pid = _pid,
        svgname = _name
    )
    print(_cmd_tmp)
    subprocess.Popen(_cmd_tmp, shell=True)






