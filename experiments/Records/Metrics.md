## System overview

+ CPU utilization : amount of work handled by a CPU(all cores) example : No idle time if this metric shows 100%

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&format=json&points=500&after=1558810800&before=1558812600&options=jsonwrap


+ System load : average number of processes over a given time. This metric can be used together with CPU usage. In netdata, three values of load average refer to the past one, five, and fifteen minutes of system operation

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.load&format=json&points=500&after=1558810800&before=1558812600&options=jsonwrap

+ RAM : This tells how much of a computer's memory (RAM) is being used.

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.ram&format=json&points=500&after=1558810800&before=1558812600&options=jsonwrap%7Cpercentage


+ Network bandwidth : display real-time data such as download and upload speeds. In netdata, only the bandwidth of physical network interfaces is aggregated.

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.net&after=1558810800&before=1558812600&points=500&group=average&gtime=0&format=json&options=seconds,jsonwrap

+ Disk : rate of read/write operations on the disk.

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.io&after=1558810800&before=1558812600&points=500&group=average&gtime=0&format=json&options=seconds,jsonwrap

## Docker services

+ CPU usage : CPU Usage (800% = 8 cores) for each microservice

http://osmmano.cs.upb.de:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.cpu_limit&after=1558810800&before=1558812600&points=500&group=average&gtime=0&format=json&options=seconds,jsonwrap

+ Mem : Used Memory without Cache for each microservice

http://osmmano.cs.upb.de:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.mem&after=1558810800&before=1558812600&points=500&group=average&gtime=0&format=json&options=seconds,jsonwrap


+ Disk : Throttle serviced I/O operations for each microservice

http://osmmano.cs.upb.de:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.throttle_io&after=1558810800&before=1558812600&points=500&group=average&gtime=0&format=json&options=seconds,jsonwrap
