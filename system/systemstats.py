import os
import time 
import logging

logger = logging.getLogger(__name__)

def GetCpuUsage(interval):
    """
    Returns the Cpu usage on a certain interval of time
    """
    if type(interval) == int or type(interval) == float: #Sanity Check of the interval to avoid further errors
        if os.path.isfile("/proc/stat"): #Check if stats file exist
            last_idle = last_total = 0
            with open('/proc/stat') as f:
                fields = [float(column) for column in f.readline().strip().split()[1:]] #Get fields to calculate the cpu usage
            idle, total = fields[3], sum(fields)
            idle_delta, total_delta = idle - last_idle, total - last_total
            last_idle, last_total = idle, total
            time.sleep(interval) #To calculate a cpu usage a interval of time must be given
            with open('/proc/stat') as f:
                fields = [float(column) for column in f.readline().strip().split()[1:]]
            idle, total = fields[3], sum(fields)
            idle_delta, total_delta = idle - last_idle, total - last_total
            last_idle, last_total = idle, total
            return round(100.0 * (1.0 - idle_delta / total_delta), 1)
    else:
        raise TypeError("Interval was in {} instead of int or float".format(type(interval)))

def GetFreeRam():
    """
    Returns the ram that can be used without using the swap
    """
    if os.path.isfile("/proc/meminfo"): #Check if meminfo is a file becaus /proc can be disabled
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        for i in lines: 
            if i.startswith("MemAvailable"): 
                return round(int(i.strip().replace("kB", "").split()[1]) / 1024, 2) #Divided by 1024 because we want the result in MB and not kB

def GetProcessList():
    if os.path.isdir("/proc"):
        filelist = os.listdir("/proc")
        remove = []
        for i in filelist: #Clean up filelist because processes are identified by an integer on a dir
            try:
                int(i)
            except:
                remove.append(i)
        for i in remove:
            filelist.remove(i)
        program_list = {}
        for i in filelist: #After, getting the pids, start get the process name which is located in /proc/<pid>/status 
            with open("/proc/" + i + "/status") as f:
                for e in f.readlines():
                    if e.startswith("Name:"):
                        program_list[i] = {'name': e.strip().replace("Name:\t", "")}
                        break
        return program_list
