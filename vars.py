# VARS
##############################################################################
# -- Dirs Paths and Dirs Selection --
# Add/Remove/Modify the following variables based on your needs and finally add them to files_to_bkp list.
# Note : Please DO NOT add more than one trailing slash to paths. Trailing slashes are optional
BACKUPDIR = "/backup/servers/"
BACKUPDIR_LOG = BACKUPDIR + 'logs'

# This variable declares the default paths to backup and fill in web console - Add server - form
backuppaths_initial = '/home,' \
                      '/usr/local/apache/conf,' \
                      '/etc/userdomains,' \
                      '/usr/local/apache/conf/php.conf,' \
                      '/etc/csf/csf.conf,' \
                      '/usr/local/lib/php.ini,' \
                      '/etc/my.cnf,' \
                      '/backup/cpbackup/daily,' \
                      '/var/lib/mysql'

RSYNC_EXCLUDE = "rsync_excl.txt"
##############################################################################

# -- Integrity --
# The command that we will execute on the remote server to make sure it's connected properly.
ssh_test_cmd = "hostname"

# --- Logs ---
# Set 0 to run in background
rsync_stdout = 1

# -- Performance --
# Change this according to the backup server resource ( CPU - RAM - Network )
# Mostly we set it to the number of total threads per CPU. Get the number with `nproc`
# or `grep processor /proc/cpuinfo | wc -l` command
number_of_threads = 16

# -- DataBase --
sqlite_file_name = 'db.sqlite3'

# DO NOT CHANGE #
# This var is called outside django
sqlite_file_path = './rsynchero_web/' + sqlite_file_name
# This var is called from django
sqlite_file_path_django = './' + sqlite_file_name
# DO NOT CHANGE #
##############################################################################
# -- Email --
email_file = "email.txt"
text_subtype = 'plain'

# The message subject
subject = "RsyncHero Backup Report"
success_message_content = "Awesome! Backup is working properly."

# MailServer IP or Hostname, Please make sure it supports SMTPoverSSL
# Ex. server.mail.org:465
SMTPserver = 'HOSTNAME:465'

# From : user@domain.tld
sender = ''

# To : user@domain.tld
destination = ['']

# SMTP Username
USERNAME = ""

# SMTP Password
PASSWORD = ""
##############################################################################
