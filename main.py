import os
import sys
import subprocess
from multiprocessing.dummy import Pool as ThreadPool
from vars import *


# Create Log dir
if not os.path.exists(BACKUPDIR_LOG):
    os.makedirs(BACKUPDIR_LOG)


def check_alive_hosts(servers_pool_file, ssh_cmd):
    hosts_up_list = []
    hosts_down_list = []
    hosts_ping_up_list = []
    hosts_ping_down_list = []

    with open(servers_pool_file) as f:
        for server_ip in f.readlines():
            ping_chk = os.system("ping -c 1 " + server_ip)
            if ping_chk == 0:
                hosts_ping_up_list.append(server_ip)
            else:
                hosts_ping_down_list.append(server_ip)
                hosts_down_list.append(server_ip)
    for server in hosts_ping_up_list:
        ssh = subprocess.Popen(["ssh", '-o', 'UserKnownHostsFile=/root/.ssh/known_hosts', '-o',
                                'StrictHostKeyChecking=no', "%s" % server, ssh_cmd],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        ssh_result = ssh.stdout.readlines()
        if not ssh_result:
            error = ssh.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
            hosts_down_list.append(server.rstrip())
        else:
            hosts_up_list.append(server.rstrip())

    return hosts_up_list, hosts_down_list

hosts_up, hosts_down = check_alive_hosts(SERVERS_IPS_POOL, ssh_test_cmd)


def rsync_start(server_ip):
    ssh_hostname_cmd = "hostname"
    ssh = subprocess.Popen(["ssh", '-o', 'UserKnownHostsFile=/root/.ssh/known_hosts', '-o',
                            'StrictHostKeyChecking=no', "%s" % server_ip, ssh_hostname_cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    server_hostname = str(ssh.stdout.readlines()).replace("[b'", "").replace('\\n\']', "")
    BKPDIR_HOSTNAME = BACKUPDIR + server_hostname

    def rsync_threaded(files_to_bkp):
        print("Start backup for : %s On %s" % (files_to_bkp, server_hostname))
        start_backup = os.system("rsync -axSq --delete --exclude-from=%s -e 'ssh -p 22' %s:%s %s"
                                 % (RSYNC_EXCLUDE, server_ip, files_to_bkp, BKPDIR_HOSTNAME) + "/")
        print("Finished backup for : %s On %s" % (files_to_bkp, server_hostname))

    # Make the Pool of workers
    pool = ThreadPool(number_of_threads)
    results = pool.map(rsync_threaded, files_to_bkp)
    pool.close()
    pool.join()

# Make the Pool of workers
pool = ThreadPool(number_of_threads)
results = pool.map(rsync_start, hosts_up)
pool.close()
pool.join()
