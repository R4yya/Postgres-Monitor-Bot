from psutil import cpu_percent, disk_usage, virtual_memory


def get_cpu_usage():
    cpu_percentage = cpu_percent(interval=1)

    return cpu_percentage


def get_disk_space_info():
    disk = disk_usage('/')
    free_space = disk.free / (1024 ** 3)
    total_space = disk.total / (1024 ** 3)
    percentage_space = disk.percent

    return (free_space, total_space, percentage_space)


def get_virtual_memory_info():
    memory = virtual_memory()
    available_memory = memory.available / (1024 ** 3)
    total_memory = memory.total / (1024 ** 3)
    percent_memory = memory.percent

    return (available_memory, total_memory, percent_memory)
