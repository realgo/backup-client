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
import subprocess
import StringIO
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

    def test_LengthRead(self):
        self.assertEqual(
            backup_client.length_read(StringIO.StringIO('5:Hello')), 'Hello')
        self.assertEqual(
            backup_client.length_read(
                StringIO.StringIO('5:Hello There')), 'Hello')
        with self.assertRaises(ValueError):
            backup_client.length_read(StringIO.StringIO('90000:Hello There'))
        self.assertEqual(
            backup_client.length_read(StringIO.StringIO('000000005:Hello')),
            'Hello')
        with self.assertRaises(ValueError):
            backup_client.length_read(StringIO.StringIO('0000000005:Hello'))
        self.assertEqual(
            backup_client.length_read(StringIO.StringIO('000000005:Hell\0')),
            'Hell\0')
        with self.assertRaises(ValueError):
            backup_client.length_read(StringIO.StringIO('000000005:Hell'))

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
        output = subprocess.check_output('test-bin/got-root')
        os.system('rm -rf test-bin')
        self.assertEqual(output.rstrip(), 'uid: 0')

    def test_ParseOptionBwlimit(self):
        self.assertEqual(
            backup_client.parse_option_bwlimit('bwlimit=1000'), 1000)
        self.assertEqual(backup_client.parse_option_bwlimit('bwlimit=05'), 5)
        self.assertEqual(backup_client.parse_option_bwlimit('bwlimit=08'), 8)
        with self.assertRaises(ValueError):
            backup_client.parse_option_bwlimit(
                'bwlimit=9999999999999999999999999')
        with self.assertRaises(ValueError):
            backup_client.parse_option_bwlimit('bwlimit=')

unittest.main()
