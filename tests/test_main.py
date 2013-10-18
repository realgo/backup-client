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
import sys
import backup_client


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

        #  Examples:
        # self.assertEqual(fp.readline(), 'This is a test')
        # self.assertFalse(os.path.exists('a'))
        # self.assertTrue(os.path.exists('a'))
        # self.assertTrue('already a backup server' in c.stderr)
        # self.assertIn('fun', 'disfunctional')
        # self.assertNotIn('crazy', 'disfunctional')
        # with self.assertRaises(Exception):
        #	raise Exception('test')
        #
        # Unconditionally fail, for example in a try block that should raise
        # self.fail('Exception was not raised')

unittest.main()
