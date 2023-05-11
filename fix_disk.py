from subprocess import run, check_output


# Handle mapper disks
def get_disk_list():
    df_output = check_output(['df', '-h'])
    disk_list = []

    lines = df_output.splitlines()
    for line in lines:
        parts = line.decode('utf-8').split()

        disk_name = parts[0]
        mapper_name = parts[-1]
        disk_usage = parts[-2]
        if("/dev/" in disk_name):

            if(not disk_usage):
                raise Exception(f'Invalid precentage for disk {disk_name}')
            
            # Remove '%' symbol from number
            disk_usage = int(disk_usage[:-1])
            disk_list.append([disk_name, disk_usage, mapper_name])

    return disk_list

def increase_disk_list(disk_list):
    for disk in disk_list:
        [disk_name, disk_usage, mapper_name] = disk
        if(disk_usage >= 85):
            increase_disk_size(disk_name, mapper_name)

def increase_disk_size(disk_name, mapper_name):
    print(f"Increase size for disk {disk_name}")
    new_disk_size = input("Enter a new allocated size (GB): ")

    if(new_disk_size == 0 or not new_disk_size.isdigit()):
        return
        
    run(["pvresize", "/dev/nvme1n1"])
    run(["lvextend", f"-L{new_disk_size}G" ,f"{disk_name}"])
    run(["xfs_growfs" ,f"{mapper_name}"])



def should_increase_for_root():
    # for path in optional_root_disk_names:
    # cmd = "df -h | grep {path}"
    cmd = "df -h | grep /dev/nvme0n1p1"
    output = check_output(cmd, shell=True)
    data = output.decode('utf-8').strip()
    # Get the precentage of the root
    usage = data.split()[4]
    # remove the precentage symbol and convert to number
    usage_num = int(usage[:-1]) 

    if usage_num >= 90:
        return True

    return False

def increase_for_root():
    # CLI command to increase size of disk
    run(["growpart", "/dev/nvme0n1" ,"1"], shell=True)

    # Apply new size available for disk
    run(["resize2fs", "/dev/nvme0n1p1"], shell=True)


if __name__ == "__main__":
    disk_list = get_disk_list()

    increase_disk_list(disk_list)

    if(should_increase_for_root()):
        increase_for_root()

    print("Finished successfully")