from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from . models import servers
from . forms import ServerAddForm, ServerUpdateForm
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect


class IndexView(generic.ListView):
    template_name = 'serversmanage/index.html'

    def get_queryset(self):
        return servers.objects.all()


class ServerInfo(generic.DetailView):
    model = servers
    template_name = 'serversmanage/serverinfo.html'


class ServerAdd(CreateView):
    form_class = ServerAddForm
    model = servers
    template_name = 'serversmanage/server_form.html'


class ServerUpdate(UpdateView):
    form_class = ServerUpdateForm
    model = servers
    template_name = 'serversmanage/server_form.html'


class ServerDelete(DeleteView):
    model = servers
    # Return to the index vide in the url.py file after deleting
    success_url = reverse_lazy('serversmanage:index')


def request_page_cmd(request):
    server_id = request.GET.get('serverid')
    if request.GET.get('runbackup'):
        import os
        server_ip = request.GET.get('serverip')
        main_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../")
        os.system("cd %s ; python3 main.py --ip=%s &" % (main_dir, server_ip))
    return HttpResponseRedirect('/server/' + server_id)


def serverdisable(request, server_id):
    server = get_object_or_404(servers, pk=server_id)
    server.serverstatus = 'Disabled'
    server.save()
    return HttpResponseRedirect('/server/' + server_id)


def serverenable(request, server_id):
    server = get_object_or_404(servers, pk=server_id)
    server.serverstatus = 'Enabled'
    server.save()
    return HttpResponseRedirect('/server/' + server_id)


def list_backup(request, server_id):
    import os
    import sys
    import sqlite3
    server = get_object_or_404(servers, pk=server_id)
    id = server.id
    ip = server.ip
    hostname = server.hostname
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

    # GET the configured dirs to backup from variable file
    from vars import sqlite_file_path_django, BACKUPDIR_LOG, BACKUPDIR
    conn = sqlite3.connect(sqlite_file_path_django, timeout=10)
    c = conn.cursor()
    c.execute("select backuppaths from serversmanage_servers where ip='%s';" % ip)

    # ssh_port_rows = List
    files_to_bkp_rows = c.fetchall()

    # Final LIST to use
    files_to_bkp = []

    for item_in_list in files_to_bkp_rows:
        # Iterating through ssh_port_rows will return a tuple
        # AFTER LOOP : item_in_list = tuple
        # Iterate through item_in_list tuple
        for item_in_tuple in item_in_list:
            # # AFTER LOOP : item_in_tuple = List
            # Remove the blank values from item_in_tuple using filter
            # files_to_bkp_pre type AFTER filter is object
            # split is used to get separate values based on ,
            files_to_bkp_pre = filter(None, item_in_tuple.split(','))

            # Iterate through object
            for i in files_to_bkp_pre:
                files_to_bkp.append(i)

    # Check if Paths found on the backup server
    # Ex. short path = /home
    # Ex. Full path = /backup/servers/HOSTNAME/home
    files_to_bkp_found = []
    for short_path in files_to_bkp:
        full_path = BACKUPDIR + "/" + hostname + "/" + short_path
        if os.path.isfile(full_path) or os.path.isdir(full_path):
            files_to_bkp_found.append(short_path)
    output = files_to_bkp_found
    return render(request, 'serversmanage/list_backup.html', {'list_backup_dirs': output, 'server_id': id, 'server_ip': ip,
                                                              'BACKUPDIR_LOG': BACKUPDIR_LOG, 'hostname': hostname})


def restore_backup(request, server_id):
    import os
    import sys
    import datetime

    # GET values from database
    server = get_object_or_404(servers, pk=server_id)
    hostname = server.hostname
    ssh_port = server.sshport
    server_ip = server.ip

    # GET logged-in username
    username = None
    if request.user.is_authenticated():
        username = request.user.username

    # Parse the GET request from the form and get the required values
    if request.GET.get('restore_backup'):
        # Dirs available for backup, Full paths.
        # Ex. dir_to_restore_remote = /backup/cpbackup/daily
        # Security
        dir_to_restore_remote = str(request.GET.get('dir_to_restore'))\
            .replace("..", '').replace("$", "").replace(";", "").replace("\n", "").replace("&&", "")\
            .replace(")", "").replace("(", "")

        # Add syspath of the main project directory to import the required files.
        sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
        from vars import BACKUPDIR, BACKUPDIR_LOG
        # Files available locally, Ex. BKPDIR_HOSTNAME = /backup/servers/HOSTNAME/daily
        BKPDIR_HOSTNAME = BACKUPDIR + hostname + "/"

        # Append '/backup/servers/HOSTNAME/' to the gotten path from web console and remove / at the end of line
        if dir_to_restore_remote.endswith('/'):
            # Remove the last /
            # The reason is the user may add / at the end of file path and this will break rsync command
            dir_to_restore_remote = dir_to_restore_remote[:-1]
        dir_to_restore_local = BKPDIR_HOSTNAME + dir_to_restore_remote

        # Rsync commands logs Ex. /backup/servers/logs/hostname
        cmd_logs = BACKUPDIR_LOG + "/" + hostname + '.txt'
        cmd_logs_errors = BACKUPDIR_LOG + "/" + hostname + '_errors.txt'
        time_now = datetime.datetime.now().strftime("%B %d, %Y - %I:%M%p")

        # Rsync for file should not contain a trailing slash
        # rsync -axSq /backup/servers/HOSTNAME/etc/php.ini -e 'ssh -p 22' 1.1.1.1:/etc/php.ini
        if os.path.isfile(dir_to_restore_local):
            rsync_cmd = "rsync -axSq %s -e 'ssh -p %s' root@%s:%s 2>>%s &" \
                        % (dir_to_restore_local, ssh_port, server_ip, dir_to_restore_remote, cmd_logs_errors)

            # Log action details
            with open(cmd_logs, "a") as myfile:
                myfile.write("\n============================================================="
                             "\nUser : %s"
                             "\nHostname : %s"
                             "\nIP : %s"
                             "\nCommand : %s"
                             "\nAction: RESTORE"
                             "\nTime: %s" % (username, hostname, server_ip, rsync_cmd, time_now))
            restore = os.system(rsync_cmd)

        # To prevent against creating new folders Rsync command for dirs should contain a trailing /
        # rsync -axSq /backup/servers/HOSTNAME/home/ -e 'ssh -p 22' 1.1.1.1:/home/
        elif os.path.isdir(dir_to_restore_local):
            rsync_cmd = "rsync -axSq %s/ -e 'ssh -p %s' root@%s:%s/ 2>>%s &" \
                        % (dir_to_restore_local, ssh_port, server_ip, dir_to_restore_remote, cmd_logs_errors)

            # Log action details
            with open(cmd_logs, "a") as myfile:
                myfile.write("\n============================================================="
                             "\nUser : %s"
                             "\nHostname : %s"
                             "\nIP : %s"
                             "\nCommand : %s"
                             "\nAction: RESTORE"
                             "\nTime: %s" % (username, hostname, server_ip, rsync_cmd, time_now))
            restore = os.system(rsync_cmd)

        # If there are no files or folders exist
        else:
            # Log action details
            with open(cmd_logs, "a") as myfile:
                myfile.write("\n============================================================="
                             "\nUser : %s"
                             "\nHostname : %s"
                             "\nIP : %s"
                             "\nSource : %s"
                             "\nResults: Dir not found"
                             "\nTime: %s" % (username, hostname, server_ip, dir_to_restore_local, time_now))

        return HttpResponseRedirect('/server/' + server_id + '/list_backup')


def view_logs(request, server_id):
    import os
    import sys
    server = get_object_or_404(servers, pk=server_id)
    hostname = server.hostname
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))

    # GET the configured dirs from variable file
    from vars import BACKUPDIR_LOG
    cmd_logs = BACKUPDIR_LOG + "/" + hostname + '.txt'

    if os.path.isfile(cmd_logs):
        with open(cmd_logs, "r") as myfile:
            content = myfile.read()

        return render(request, 'serversmanage/view_logs.html', {'logs_content': content,
                                                                  'BACKUPDIR_LOG': BACKUPDIR_LOG, 'hostname': hostname})
    else:
        return render(request, 'serversmanage/view_logs.html', {'BACKUPDIR_LOG': BACKUPDIR_LOG, 'hostname': hostname})


def test_ssh(request, server_id):
    import subprocess
    server = get_object_or_404(servers, pk=server_id)
    id = server.id
    ip = server.ip
    ssh_port = server.sshport

    # Test SSH connection and timeout after 10 seconds
    ssh = subprocess.Popen(
        ["ssh", '-p' '%s' % ssh_port, '-o', 'ConnectTimeout=10', '-o', 'UserKnownHostsFile=/root/.ssh/known_hosts', '-o',
         'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', 'root@%s' % ip, 'echo "Hi, I am still alive :)"'],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    ssh_result = ssh.stdout.readlines()
    if not ssh_result:
        error = ssh.stderr.readlines()
        return render(request, 'serversmanage/test_ssh.html', {'ssh_output_error': error})
    else:
        return render(request, 'serversmanage/test_ssh.html', {'ssh_output': ssh_result})


def view_running_jobs(request, server_id):
    import subprocess
    server = get_object_or_404(servers, pk=server_id)
    id = server.id
    ip = server.ip
    ssh = subprocess.Popen(
        ["ps aux | grep -v grep | grep %s" % ip],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    ssh_result = ssh.stdout.readlines()
    if ssh_result:
        return render(request, 'serversmanage/view_running_jobs.html', {'ssh_output_found': ssh_result})
    else:
        return render(request, 'serversmanage/view_running_jobs.html')


def kill_running_jobs(request, server_id):
    import subprocess
    server = get_object_or_404(servers, pk=server_id)
    id = server.id
    ip = server.ip
    ssh = subprocess.Popen(
        ["for i in {1..5}; do for process in $(ps aux | grep -v grep | grep %s | awk '{print $2}');"
         " do kill -9 $process;done;done" % ip],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return HttpResponseRedirect('/server/' + server_id)
