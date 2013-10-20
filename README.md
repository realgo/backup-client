backup-client for ssh+rsync Backups
===================================

This is a helper to allow secured rsync-over-SSH backups.  Usually you
would specify a "command=" argument in the `authorized_keys` file to limit
what can be done with this keys.  However, if you just specify a static
rsync command, you can't change arguments like "bwlimit" or "compress"
without changing the `authorized_keys` file.

Also, you would typically have to put this in the root `authorized_keys`
file, which requires that you allow root SSH logins.

backup-client will detect that it is not running as root, and will
re-invoke itself under sudo, and will look at the arguments that were
passed to rsync on the remote end, and preserve compression and bwlimit
arguments.

Future plans are to run scripts before starting the rsync so that you can
pick up things like system information, ACL information, and database
backups.

Features
--------

   * Re-invokes itself under sudo if not running as root.

   * Detect "-z", "--compress", and "--bwlimit=DDD" arguments from remote
     SSH invocation while limiting other arguments.

   * Unit tests.

Getting Started
---------------

Typically you would use this with a unique key for this backup, that has no
password associated with it.  You generate one of these keys using the
following OpenSSH command:

    ssh-keygen -t rsa -N '' -C backup-client -f id_backup-$HOSTNAME

The `$HOSTNAME` should be replaced by the host that is being backed up with
this key.  This generates a pair of files, `id_backup-$HOSTNAME` and
`id_backup-$HOSTNAME.pub`.  The first file needs to be kept secret, stored
on the backup server.  The other file you need to copy to the backup client
and put in an `.ssh/authorized_keys` file for either root or a non-root
user that is allowed to run "backup-client" under sudo.

The key line should be prefixed with something like:

    no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding,command="backup-client -- --server --sender -lHogDtpre.i --ignore-errors --numeric-ids --inplace . /"

This prevents the key from being used to do port forwarding, etc...

Note that the command-line has "--" in it and then is followed by the rsync
arguments you wan to be used.  The above are probably what you want for a
backup command.  backup-client will then detect whether the remote end was
called with compression and bwlimit options, and if so will prepend those
to the arguments after "--".

To enable sudo, you would create a file `/etc/sudoers.d/backup-client`
which contains something similar to:

    BACKUP_USERNAME ALL=(ALL) ALL, (root) NOPASSWD: backup-client

Where `BACKUP_USERNAME` is the name of the user you have created for
backups.  This is the home directory where the .ssh directory includes the
key generated above.  If you don't have backup-client in a directory on the
normal system PATH, you probably will need to specify the path, such as
`/usr/local/bin/backup-client`.

Contact Information
-------------------

Author: Sean Reifschneider <sean+opensource@realgo.com>  
Date: Sun Oct 20, 2013  
License: GPL v2 --
Code/Bugs: https://github.com/realgo/backup-client
