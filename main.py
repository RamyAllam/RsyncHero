import os
import sys
import subprocess
from multiprocessing.dummy import Pool as ThreadPool
import sqlite3
from vars import *

# Create Log dir
if not os.path.exists(BACKUPDIR_LOG):
    os.makedirs(BACKUPDIR_LOG)


def mark_host_db_down(serverip):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("""UPDATE serversmanage_servers SET backupstatus = 'ERROR' WHERE ip = ? """, (serverip, ))
    conn.commit()
    conn.close()


def check_alive_hosts(ssh_cmd):
    hosts_up_list = []
    hosts_down_list = []
    hosts_ping_up_list = []
    hosts_ping_down_list = []
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("select ip from serversmanage_servers where serverstatus='Enabled';")
    all_rows = c.fetchall()
    conn.close()

    ip_list = []
    for ip in all_rows:
        ip_list.append(", ".join(ip))

    for server_ip in ip_list:
        ping_chk = os.system("ping -c 1 " + server_ip)
        if ping_chk == 0:
            hosts_ping_up_list.append(server_ip)
        else:
            hosts_ping_down_list.append(server_ip)
            hosts_down_list.append(server_ip)
            mark_host_db_down(server_ip)

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
            mark_host_db_down(server)
        else:
            hosts_up_list.append(server.rstrip())

    return hosts_up_list, hosts_down_list

hosts_up, hosts_down = check_alive_hosts(ssh_test_cmd)


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

        conn = sqlite3.connect(sqlite_file)
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


def bkp_monitor():
    import datetime
    from smtplib import SMTP_SSL
    from email.mime.text import MIMEText
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("select ip, hostname, backupstatus from serversmanage_servers where backupstatus='ERROR';")
    all_rows = c.fetchall()
    try:
        os.remove(email_file)
    except FileNotFoundError:
        pass

    with open(email_file, "a") as myfile:
        myfile.write("Backup Status for: " + datetime.datetime.now().strftime("%B %d, %Y - %I:%M%p") + "\n\n")

    for ip, hostname, backupstatus in all_rows:
        with open(email_file, "a") as myfile:
            myfile.write("IP: %s" % ip + "\n")
            myfile.write("Hostname: %s" % hostname + "\n")
            myfile.write("Backup Status: %s" % backupstatus + "\n============================\n")
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

# Make the Pool of workers
pool = ThreadPool(number_of_threads)
results = pool.map(rsync_start, hosts_up)
pool.close()
pool.join()
bkp_monitor()
