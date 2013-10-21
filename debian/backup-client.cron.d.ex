#
# Regular cron jobs for the backup-client package
#
0 4	* * *	root	[ -x /usr/bin/backup-client_maintenance ] && /usr/bin/backup-client_maintenance
