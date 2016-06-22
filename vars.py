# VARS
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
DAILY_BKP = "/backup/cpbackup/daily"

RSYNC_EXCLUDE = "rsync_excl.txt"
SERVERS_IPS_POOL = "servers_ip.txt"
ssh_test_cmd = "hostname"
number_of_threads = 16

files_to_bkp = [APACHE_CONF, USER_DOMAINS, PHPCONF, CSFCONF, PHPINI, MYCNF, DAILY_BKP, HOMEDIR, MYSQL]
