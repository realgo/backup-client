#!/usr/bin/env python
#
#  Test of the backup-client functions.
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest

import os
import sys
import time
import subprocess
import tempfile
import backup_client


def can_run_sudo():
    '''Try running "sudo true" to see if sudo tests should work.'''
    try:
        subprocess.check_call(
            ['sudo', '-n', 'true'],
            stdout=os.open(os.devnull, os.O_RDWR),
            stderr=os.open(os.devnull, os.O_RDWR))
        return True
    except subprocess.CalledProcessError:
        return False


class test_BackupClient_Main(unittest.TestCase):
    def test_GetProgramName(self):
        self.assertEqual(
            backup_client.get_program_path(),
            os.path.join(os.getcwd(), 'test_main.py'))

        #  test running via the path
        os.system('rm -rf test-bin; mkdir test-bin')
        with open('test-bin/test-with-path', 'w') as fp:
            fp.write('#!/usr/bin/env python\n')
            fp.write('import sys\n')
            fp.write('sys.path.append(".")\n')
            fp.write('import backup_client\n')
            fp.write('print backup_client.get_program_path()\n')
        os.system('chmod 755 test-bin/test-with-path')
        old_path = os.environ['PATH']
        os.environ['PATH'] = os.environ['PATH'] + ':test-bin'
        output = subprocess.check_output('test-with-path', shell=True)
        os.environ['PATH'] = old_path
        os.system('rm -rf test-bin')
        self.assertEqual(
            output.rstrip(),
            os.path.join(os.getcwd(), 'test-bin/test-with-path'))

    @unittest.skipUnless(can_run_sudo(), 'Sudo call failed')
    def test_RunAsRoot(self):
        #  test running via the path
        os.system('rm -rf test-bin; mkdir test-bin')
        with open('test-bin/got-root', 'w') as fp:
            fp.write('#!/usr/bin/env python\n')
            fp.write('import sys, os\n')
            fp.write('sys.path.append(".")\n')
            fp.write('import backup_client\n')
            fp.write('backup_client.run_as_root()\n')
            fp.write('print "uid:", os.getuid()\n')
        os.system('chmod 755 test-bin/got-root')
        output = subprocess.check_output(['test-bin/got-root', '--'])
        os.system('rm -rf test-bin')
        self.assertEqual(output.rstrip(), 'uid: 0')

    def test_ParseSshOptions(self):
        self.assertEqual(
            backup_client.parse_ssh_command(
                'rsync --server --sender -vlogDtpre.iLsf --bwlimit=100 . /'),
            ['--bwlimit=100'])
        self.assertEqual(
            sorted(backup_client.parse_ssh_command(
                'rsync --server --sender -vlogDtzpre.iLsf --bwlimit=100 . /')),
            ['--bwlimit=100', '--compress'])
        self.assertEqual(
            backup_client.parse_ssh_command(
                'rsync --server --sender --compress -vlogDtpre.iLsf . /'),
            ['--compress'])
        self.assertEqual(
            backup_client.parse_ssh_command(
                'rsync --server --sender -vlogDtpre.iLsf . /'), [])
        self.assertEqual(
            backup_client.parse_ssh_command('rsync'), [])
        self.assertEqual(
            backup_client.parse_ssh_command('rsync --server --sender'), [])

    def test_GetRsyncArguments(self):
        self.assertEqual(
            backup_client.get_rsync_arguments(
                ['--foo', '--', '--server', '--sender', '-vlogDtpre.iLsf',
                    '--bwlimit=100', '.', '/']),
            ['--server', '--sender', '-vlogDtpre.iLsf', '--bwlimit=100',
                '.', '/'])

    def test_RunScript(self):
        self.assertEqual(backup_client.run_script(['true']), None)
        with self.assertRaises(backup_client.RunDirError):
            backup_client.run_script(['false'])


class test_DirectoryRunner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ['DIRRUNTMPDIR'] = self.tmpdir

    def tearDown(self):
        os.system('rm -rf "%s"' % self.tmpdir)

    def test_Dir1(self):
        os.stat_float_times(True)
        s1tmp = os.path.join(self.tmpdir, 's1')
        s2tmp = os.path.join(self.tmpdir, 's2')
        s3tmp = os.path.join(self.tmpdir, 's3')

        dr = backup_client.DirectoryRunner(
            os.path.join(os.getcwd(), 'dirrunner1'))

        dr.start()
        self.assertEqual(os.path.exists(s1tmp), True)
        self.assertEqual(os.path.exists(s2tmp), True)
        self.assertEqual(os.path.exists(s3tmp), True)
        self.assertTrue(os.stat(s1tmp).st_mtime < os.stat(s2tmp).st_mtime)
        self.assertTrue(os.stat(s2tmp).st_mtime < os.stat(s3tmp).st_mtime)
        os.remove(s1tmp)
        os.remove(s2tmp)
        os.remove(s3tmp)

        dr.stop()
        self.assertEqual(os.path.exists(s1tmp), True)
        self.assertEqual(os.path.exists(s2tmp), True)
        self.assertEqual(os.path.exists(s3tmp), True)
        self.assertTrue(os.stat(s1tmp).st_mtime > os.stat(s2tmp).st_mtime)
        self.assertTrue(os.stat(s2tmp).st_mtime > os.stat(s3tmp).st_mtime)

    def test_Dir1Fork(self):
        os.stat_float_times(True)
        s1tmp = os.path.join(self.tmpdir, 's1')
        s2tmp = os.path.join(self.tmpdir, 's2')
        s3tmp = os.path.join(self.tmpdir, 's3')

        dr = backup_client.DirectoryRunner(
            os.path.join(os.getcwd(), 'dirrunner1'))

        dr.start()
        os.remove(s1tmp)
        os.remove(s2tmp)
        os.remove(s3tmp)

        forked_pid = os.fork()
        if forked_pid == 0:
            sys.exit = os._exit
            dr.fork_background_stop()
            time.sleep(0.1)
            os._exit(0)

        self.assertEqual(os.path.exists(s1tmp), False)
        self.assertEqual(os.path.exists(s2tmp), False)
        self.assertEqual(os.path.exists(s3tmp), False)
        os.waitpid(forked_pid, 0)
        time.sleep(0.1)
        self.assertEqual(os.path.exists(s1tmp), True)
        self.assertEqual(os.path.exists(s2tmp), True)
        self.assertEqual(os.path.exists(s3tmp), True)
        self.assertTrue(os.stat(s1tmp).st_mtime > os.stat(s2tmp).st_mtime)
        self.assertTrue(os.stat(s2tmp).st_mtime > os.stat(s3tmp).st_mtime)
        os.remove(s1tmp)
        os.remove(s2tmp)
        os.remove(s3tmp)

    def test_Dir2(self):
        os.stat_float_times(True)
        s1tmp = os.path.join(self.tmpdir, 's1')
        s2tmp = os.path.join(self.tmpdir, 's2')
        s3tmp = os.path.join(self.tmpdir, 's3')

        dr = backup_client.DirectoryRunner(
            os.path.join(os.getcwd(), 'dirrunner2'))

        with self.assertRaises(backup_client.RunDirError):
            dr.start()
        self.assertEqual(os.path.exists(s1tmp), True)
        self.assertEqual(os.path.exists(s2tmp), True)
        self.assertEqual(os.path.exists(s3tmp), False)
        self.assertTrue(os.stat(s1tmp).st_mtime > os.stat(s2tmp).st_mtime)
        self.assertEqual(open(s1tmp, 'r').read(), 'start\nstop\n')
        self.assertEqual(open(s2tmp, 'r').read(), 'start\nstop\n')

unittest.main()
