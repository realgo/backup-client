backup-client for ssh+rsync Backups
===================================

This is an rsync helper to improve the usability of rsync backups over SSH,
particularly in the case of securing the backups with public key identities.
It provides these benefits:

* Allows running from a non-root user.  If started as a non-root user it will
  re-invoke itself under sudo.  So you can use SSH for backups while limiting
  root logins.

* Runs scripts in "/etc/backup-client/helpers.d" before and after the backup
  to run databases dumps or the like.  For example, on one of my
  virtualization clusters, I have it create snapshots of the Windows drives
  and mount them read-only.

* Detects the remote end use of "--bwlimit" and "--compress", so the same
  command-line (in an `authorized_keys` file) can be used with compression and
  rate limiting.

Overview
--------

When running backups using rsync over SSH, typically you would use a
SSH public/private key-pair that doesn't have a password on it.  To secure
that, on the remote server you would typically add a line to the
`authorized_keys` file which limits that key to only running a specific
command.

In that case, the `authorized_keys` file must be modified if you want to
enable compression, because compression is not negotiated in rsync protocol.

`backup-client` is a command that can be listed in the `authorized_keys` file
and will detect if the remote end is using compression or a bandwidth limit,
and appropriately configure the rsync command that is started.

Getting Started
---------------

To run an rsync backup using backup-client, you would typically do these
steps:

* Install backup-client somewhere on the machine to be backed up.

* Create a passwordless SSH keypair:

    ssh-keygen -t rsa -N '' -C Backups -f id_backup-$HOSTNAME

* On the machine to be backed up, create a `~/.ssh/authorized_keys` file (if
  it doesn't already exist) and place the `backup-identity.pub` file contents
  in that file.  This must all be done as a single very long line.  This
  typically is done for the "root" or some sort of "backup" user:

    cd ~backup_user       #  go to the backup user home directory
    mkdir .ssh
    cp /tmp/backup-identity.pub >>.ssh/authorized_keys
    chown -R backup_user .ssh
    chmod -R g=,o= .ssh

* Edit the `.ssh/authorized_keys` file and prefix the key with this to prevent
  the key from being used for anything but a backup.  Again, note that the
  result must be a single very long line and must not be split up:

    no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding,command="exec /path/to/backup-client" [SSH KEY HERE]

* If you used a non-root user above, you will need to allow that user to use
  sudo to re-run backup-client with no password.  Add the following to
  `/etc/sudoers.d/backup-client`, replacing `BACKUP_USERNAME` with the user
  you wrote the `authorized_keys` file entry for:

    BACKUP_USERNAME ALL=(root)NOPASSWD: /path/to/backup-client

At this point, on the server, you should be able to run an rsync job with:

    rsync -avzP -e 'ssh -i /path/to/id_backup-$HOSTNAME' \
        --delete --delete-excluded --hard-links --numeric-ids \
        --exclude=/proc/ --exclude=/dev/ --exclude=/sys/ \
        backup_user@$HOSTNAME:/ /path/to/backups/$HOSTNAME

Helper Scripts
--------------

Any scripts in "/etc/backup-client/helpers.d" will be run, in lexical order
before and after the rsync is done.  Before the rsync, they are run with the
single argument "start".  After rsync exits, they are run in reverse order
with the argument "stop".

If any of the "start" scripts exit with non-zero status, a message will be
written to syslog, the scripts that were called with "start" are run,
including the script that exited with non-zero, in reverse order,
with "stop", and the rsync command is never run.

The backup is aborted if any of the helper scripts exit with non-zero
status to ensure that failures in the helpers are caught rather than
silently ignored.

Exit Codes
----------

In most cases the exit code will be whatever the rsync process exits.
However, in the case of an error in backup-client, the following exit
codes may be generated:

* 248: A pre-backup script exited non-zero.  See syslog for details.
* 249: An attempt was made to use sudo to gain root, which failed.
* 250: Failed during exec() of rsync command.  Syslog should contain more
       information on the error.

Contact Information
-------------------

Author: Sean Reifschneider <sean+opensource@realgo.com>  
Date: Sun Oct 20, 2013  
License: GPL v2 --
Code/Bugs: https://github.com/realgo/backup-client
