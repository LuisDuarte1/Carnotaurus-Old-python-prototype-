import platform
import os
import logging

logger = logging.getLogger(__name__)

def GetSystem():
    pc = platform.uname()
    return {'system': pc.system, 'arch': pc.machine, 'dist': platform.dist()} #return a dictionary for easier use

def GetCpu():
    if os.path.isfile("/proc/cpuinfo"): #Check if /proc/cpuinfo exists because CONFIG_PROC_FS can be disabled
        cpu_dict = {}
        with open("/proc/cpuinfo", "r") as f:
            lines = f.readlines()
            for i in lines:
                if 'model name' in i:
                    cpu_dict['model_name'] = i.strip().replace("\t", "").replace("model name: ", "") #Get the model and remove useless information
                    continue
                if 'cpu cores' in i:
                    cpu_dict['cpu_cores'] = int(i.strip().replace("\t", "").replace("cpu cores: ", "")) #Get the cpu cores and remove useless info
        return cpu_dict

def GetPatitions():
    if os.path.isfile("/proc/filesystems"): #Check if /proc/filesystems exists because CONFIG_PROC_FS can be disabled
        valid_fstypes = []
        with open("/proc/filesystems", "r") as f: #Get Filesystem types that can be used on actual partitions
            for i in f.readlines():
                if not i.startswith("nodev"):
                    valid_fstypes.append(i.strip())
        partitions = []
        if os.path.isfile("/proc/mounts"): #Another sanity check
            with open("/proc/mounts") as f: # /proc/mounts has every partition mounted in the system
                for i in f.readlines():
                    e = i.split()
                    if any(x in valid_fstypes for x in e): #Check if partition is one of the valid filesystem types 
                        partitions.append((i.strip().split(" ")[0], i.strip().split(" ")[1]))
        return partitions

def GetDiskUsage(partitions):
    if type(partitions) == list:
        disk_usage = {}
        for i in partitions:
            fs = os.statvfs(i[1])
            block_size = fs.f_frsize
            total_blocks=fs.f_blocks
            free_blocks=fs.f_bfree
            gb = 1024 * 1024 * 1024
            disk_usage[i[1]] = {'total': round(block_size*total_blocks/gb, 4), 'free': round(block_size*free_blocks/gb, 4)}
        return disk_usage 
    else:
        raise TypeError("partitions must be in a list and not in {}".format(type(partitions)))


def GetSpecs():
    ram = round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024.**3)) #Get RAM on GB
    cpu = GetCpu()
    system = GetSystem()
    disk_usage = GetDiskUsage(GetPatitions())
    return {'system': system, 'ram': ram, 'cpu': cpu, 'disk_usage':disk_usage}

print(GetSpecs())