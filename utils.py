from psutil import cpu_percent, disk_usage


def get_cpu_usage():
    cpu_percentage = cpu_percent(interval=1)
    return cpu_percentage


def get_disk_free_space():
    disk = disk_usage('/')
    free_space = disk.free / (1024 ** 3)
    return free_space
