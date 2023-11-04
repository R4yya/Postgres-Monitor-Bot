from psutil import cpu_percent, disk_usage


def get_cpu_usage():
    cpu_percentage = cpu_percent(interval=1)

    return cpu_percentage


def get_disk_space_info():
    disk = disk_usage('/')
    free_space = disk.free / (1024 ** 3)
    total_space = disk.total / (1024 ** 3)
    percentage_space = disk.percent

    return (free_space, total_space, percentage_space)
