import os
import sys
import getopt
import subprocess
from multiprocessing.dummy import Pool as ThreadPool
import sqlite3
from itertools import repeat
from vars import *

# Create Log dir
if not os.path.exists(BACKUPDIR_LOG):
    os.makedirs(BACKUPDIR_LOG)


# Update the server status to down in the database
def mark_host_db_down(serverip):
    conn = sqlite3.connect(sqlite_file, timeout=10)
    c = conn.cursor()
    c.execute("""UPDATE serversmanage_servers SET backupstatus = 'ERROR' WHERE ip = ? """, (serverip, ))
    conn.commit()
    conn.close()


# Get a list of up and down servers
def check_alive_hosts(ssh_cmd):
    hosts_up_list = []
    hosts_down_list = []
    hosts_ping_up_list = []
    hosts_ping_down_list = []
    conn = sqlite3.connect(sqlite_file, timeout=10)
    c = conn.cursor()
    c.execute("select ip from serversmanage_servers where serverstatus='Enabled';")
    all_rows = c.fetchall()

    ip_list = []
    for ip in all_rows:
        ip_list.append(", ".join(ip))

    for server_ip in ip_list:
        ping_chk = os.system("ping -c 5 " + server_ip)
        if ping_chk == 0:
            hosts_ping_up_list.append(server_ip)
        else:
            hosts_ping_down_list.append(server_ip)
            hosts_down_list.append(server_ip)
            mark_host_db_down(server_ip)

    for server in hosts_ping_up_list:
        # GET SSH Port from database
        c.execute("select sshport from serversmanage_servers where ip='%s';" % server)
        all_rows = c.fetchall()

        ssh_port = str(all_rows[0]).replace("(", "").replace(",)", "")
        # Check SSH Connection
        ssh = subprocess.Popen(
            ["ssh", '-p' '%s' % ssh_port, '-o', 'UserKnownHostsFile=/root/.ssh/known_hosts', '-o',
             'StrictHostKeyChecking=no', 'root@%s' % server, ssh_cmd],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        ssh_result = ssh.stdout.readlines()
        if not ssh_result:
            error = ssh.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
            hosts_down_list.append(server.rstrip())
            mark_host_db_down(server)
        else:
            hosts_up_list.append(server.rstrip())
    conn.close()
    return hosts_up_list, hosts_down_list


# Core function for Rsync process
def rsync_start(server_ip, rsync_stdout):
    # GET SSH Port from database
    conn = sqlite3.connect(sqlite_file, timeout=10)
    c = conn.cursor()
    c.execute("select sshport from serversmanage_servers where ip='%s';" % server_ip)
    all_rows = c.fetchall()
    conn.close()
    ssh_port = str(all_rows[0]).replace("(", "").replace(",)", "")

    # Get FQDN from inside the server
    ssh_hostname_cmd = "hostname"
    ssh = subprocess.Popen(["ssh", '-p' '%s' % ssh_port, '-o', 'UserKnownHostsFile=/root/.ssh/known_hosts', '-o',
                            'StrictHostKeyChecking=no', "%s" % server_ip, ssh_hostname_cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    server_hostname = str(ssh.stdout.readlines()).replace("[b'", "").replace('\\n\']', "")
    BKPDIR_HOSTNAME = BACKUPDIR + server_hostname

    def rsync_threaded(files_to_bkp):
        print("Start backup for : %s On %s" % (files_to_bkp, server_hostname))
        if rsync_stdout == 1:
            start_backup = os.system("rsync -axSq --delete --exclude-from=%s -e 'ssh -p %s' %s:%s %s"
                                     % (RSYNC_EXCLUDE, ssh_port, server_ip, files_to_bkp, BKPDIR_HOSTNAME) + "/")
            print("Finished backup for : %s On %s" % (files_to_bkp, server_hostname))
        else:
            start_backup = os.system("rsync -axSq --delete --exclude-from=%s -e 'ssh -p %s' %s:%s %s"
                                     % (RSYNC_EXCLUDE, ssh_port, server_ip, files_to_bkp, BKPDIR_HOSTNAME) + "/ &")
            print("Background process is running for : %s On %s" % (files_to_bkp, server_hostname))

        # Set backup status in the database
        conn = sqlite3.connect(sqlite_file, timeout=10)
        c = conn.cursor()
        c.execute("""UPDATE serversmanage_servers SET lastbackup = CURRENT_TIMESTAMP WHERE ip = ? """, (server_ip, ))
        c.execute("""UPDATE serversmanage_servers SET backupstatus = 'Good' WHERE ip = ? """, (server_ip, ))
        conn.commit()
        conn.close()

    # Make the Pool of workers
    pool = ThreadPool(number_of_threads)
    results = pool.map(rsync_threaded, files_to_bkp)
    pool.close()
    pool.join()


# Monitor the backup status whether it's Ok or errors found an send mail notification
def bkp_monitor():
    import datetime
    from smtplib import SMTP_SSL
    from email.mime.text import MIMEText
    # GET a list of servers with backup errors
    conn = sqlite3.connect(sqlite_file, timeout=10)
    c = conn.cursor()
    c.execute("select ip, hostname, backupstatus from serversmanage_servers where backupstatus='ERROR';")
    all_rows = c.fetchall()
    try:
        os.remove(email_file)
    except FileNotFoundError:
        pass

    with open(email_file, "a") as myfile:
        myfile.write("Backup Status for: " + datetime.datetime.now().strftime("%B %d, %Y - %I:%M%p") + "\n\n")

    # IF backup errors found, include it's information in the msg.
    if all_rows:
        for ip, hostname, backupstatus in all_rows:
            with open(email_file, "a") as myfile:
                myfile.write("IP: %s" % ip + "\n")
                myfile.write("Hostname: %s" % hostname + "\n")
                myfile.write("Backup Status: %s" % backupstatus + "\n============================\n")
    else:
        # IF all is awesome, return success msg
        with open(email_file, "a") as myfile:
            myfile.write(success_message_content)
    conn.close()

    if os.path.isfile(email_file):
        content = open(email_file).read()
        try:
            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = "RsyncHero %s" % sender
            msg['To'] = destination[0]
            conn = SMTP_SSL(SMTPserver)
            conn.set_debuglevel(False)
            conn.login(USERNAME, PASSWORD)
            conn.sendmail(sender, destination, msg.as_string())
            conn.close()
        except EOFError:
            print("mail failed")

    os.remove(email_file)


def backup_all_servers():
    # Get a list of up and down servers
    hosts_up, hosts_down = check_alive_hosts(ssh_test_cmd)

    # Prepare the list for starmap two arguments.
    hosts_up_two_args = []

    # Add the argument to hosts list and append to separate list.
    # Output should be something like [('a', 1), ('b', 1), ('c', 1)]
    for i in zip(hosts_up, repeat(rsync_stdout)):
        hosts_up_two_args.append(i)

    # Make the Pool of workers
    pool = ThreadPool(number_of_threads)
    results = pool.starmap(rsync_start, hosts_up_two_args)
    pool.close()
    pool.join()


def backup_one_server(server_ip):
    # This function need the parameter as a list
    # Prepare the list for starmap two arguments.
    hosts_up = []
    hosts_up_two_args = []

    hosts_up.append(server_ip)

    # Add the argument to hosts list and append to separate list.
    # Output should be something like [('a', 1), ('b', 1), ('c', 1)]
    # Always run backup one server in background ( append 0 )
    for i in zip(hosts_up, repeat(0)):
        hosts_up_two_args.append(i)

    # Make the Pool of workers
    pool = ThreadPool(number_of_threads)
    results = pool.starmap(rsync_start, hosts_up_two_args)
    pool.close()
    pool.join()


try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:as:o:", ["help", "all", "ip="])
except getopt.GetoptError as err:
    print("Please enter the correct opt")
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("Usage : python3 main.py --ACTION")
        print("Available actions are : --all, --ip")

    elif opt in ("-a", "--all"):
        backup_all_servers()
        bkp_monitor()

    if opt in ("-o", "--ip"):
        value = arg
        backup_one_server(value)
