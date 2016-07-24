# VARS
##############################################################################
# -- Dirs Paths and Dirs Selection --
# Add/Remove/Modify the following variables based on your needs and finally add them to files_to_bkp list.
BACKUPDIR = "/backup/servers/"
BACKUPDIR_LOG = BACKUPDIR + 'logs'
MYSQL = "/var/lib/mysql"
PHPINI = "/usr/local/lib/php.ini"
MYCNF = "/etc/my.cnf"
APACHE_CONF = "/usr/local/apache/conf"
PHPCONF = "/usr/local/apache/conf/php.conf"
USER_DOMAINS = "/etc/userdomains"
CSFCONF = "/etc/csf/csf.conf"
HOMEDIR = "/home"
cPanel_DAILY_BKP = "/backup/cpbackup/daily"
RSYNC_EXCLUDE = "rsync_excl.txt"
files_to_bkp = [APACHE_CONF, USER_DOMAINS, PHPCONF, CSFCONF, PHPINI, MYCNF, cPanel_DAILY_BKP, HOMEDIR, MYSQL]
##############################################################################

# -- Integrity --
# The command that we will execute on the remote server to make sure it's connected properly.
ssh_test_cmd = "hostname"


# -- Performance --
# Change this according to the backup server resource ( CPU - RAM - Network )
# Mostly we set it to the number of total threads per CPU. Get the number with `nproc`
# or `grep processor /proc/cpuinfo | wc -l` command
number_of_threads = 16


# -- DataBase --
sqlite_file = './rsynchero_web/db.sqlite3'

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
