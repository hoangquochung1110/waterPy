import os, time

def cpu_temp():
    dev = os.popen('/opt/vc/bin/vcgencmd measure_temp') 
    cpu_temp = dev.read()[5:-3]
    return cpu_temp


