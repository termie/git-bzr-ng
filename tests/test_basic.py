import os
import shutil
import subprocess
import sys
import unittest

from os import chdir as cd
from os import mkdir


TESTDIR='/tmp/git-bzr-test'
BZRBRANCHNAME='bzrtest'
BZRBRANCH='%s/%s' % (TESTDIR, BZRBRANCHNAME)
ROOTDIR=os.path.dirname(os.path.dirname(__file__))
VENDOR=os.path.join(ROOTDIR, 'vendor')
GITBZR=os.path.join(ROOTDIR, 'git-bzr')
PYFASTIMPORT=os.path.join(VENDOR, 'python-fastimport')
BZRFASTIMPORT=os.path.join(VENDOR, 'fastimport')


# From python 2.7
def check_output(*popenargs, **kwargs):
  r"""Run command with arguments and return its output as a byte string.

  If the exit code was non-zero it raises a CalledProcessError.  The
  CalledProcessError object will have the return code in the returncode
  attribute and output in the output attribute.

  The arguments are the same as for the Popen constructor.  Example:

  >>> check_output(["ls", "-l", "/dev/null"])
  'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

  The stdout argument is not allowed as it is used internally.
  To capture standard error in the result, use stderr=STDOUT.

  >>> check_output(["/bin/sh", "-c",
  ...               "ls -l non_existent_file ; exit 0"],
  ...              stderr=STDOUT)
  'ls: non_existent_file: No such file or directory\n'
  """
  if 'stdout' in kwargs:
    raise ValueError('stdout argument not allowed, it will be overridden.')
  print ' '.join(popenargs[0])
  process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
  output, unused_err = process.communicate()
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get("args")
    if cmd is None:
      cmd = popenargs[0]
    raise subprocess.CalledProcessError(retcode, cmd)
  return output


def bzr(*args):
  return check_output(['bzr'] + list(args))


def git(*args):
  return check_output(['git'] + list(args))


def gitbzr(*args):
  return check_output([GITBZR] + list(args))


def rmdir(path):
  try:
    shutil.rmtree(path)
  except Exception:
    pass


class GitBzrTest(unittest.TestCase):
  def setUp(self):
    self._ensure_checkouts()
    self._setup_bzr_branches()

  def tearDown(self):
    pass

  def _ensure_checkouts(self):
    if not os.path.exists(PYFASTIMPORT):
      cd(VENDOR)
      bzr('branch', 'lp:python-fastimport')
    if not os.path.exists(BZRFASTIMPORT):
      cd(VENDOR)
      bzr('branch', 'lp:bzr-fastimport', BZRFASTIMPORT)
    python_path = ('PYTHONPATH' in os.environ
                   and os.environ['PYTHONPATH']
                   or '')
    if not python_path.startswith(PYFASTIMPORT):
      os.environ['PYTHONPATH'] = PYFASTIMPORT
    os.environ['BZR_PLUGIN_PATH'] = VENDOR
    os.environ['BZR_PDB'] = '1'

  def _setup_bzr_branches(self):
    # make a bzr branch to interact with
    rmdir(TESTDIR)
    mkdir(TESTDIR)
    cd(TESTDIR)
    bzr('init', BZRBRANCH)
    cd(BZRBRANCH)
    open('touch.txt', 'w').write('touch')
    print "hmm?"
    bzr('add', '-v', 'touch.txt')
    bzr('commit', '-v', '-m', 'touch test')
    print "hmm2?"
    open('touch2.txt', 'w').write('touch2')
    bzr('add', 'touch2.txt')
    bzr('commit', '-m', 'touch2 test')

    # make another branch to test import later
    cd(TESTDIR)
    bzr('branch', BZRBRANCH, '%s_imported' % BZRBRANCH)

  def test_all(self):
    # TEST: clone with git-bzr-ng
    # it should guess the name correctly but notice that the directory already
    # exists and failed
    cd(TESTDIR)
    self.assertRaises(subprocess.CalledProcessError,
                      gitbzr, 'clone', BZRBRANCH)

    # TEST: clone it again with a better name
    gitbzr('clone', BZRBRANCH, '%s_git' % BZRBRANCHNAME)

    # Check for the branches we want
    cd('%s_git' % BZRBRANCH)
    branches = git('branch', '-a')
    if 'bzr/master' not in branches:
      self.fail('no bzr/master branch')
    if '* master' not in branches:
      self.fail('not on master branch')
    
    # Check for files we expect
    self.assertEqual('touch', open('touch.txt').read())
    
    # push to a new branch
    git('checkout', '-b', 'pushed')
    open('touch2.txt', 'w').write('touch3')
    git('add', 'touch2.txt')
    git('commit', '-m', 'touch3 test')
    gitbzr('push', '%s_pushed' % BZRBRANCH)
    
    # do it again
    open('touch2.txt', 'w').write('touch4')
    git('add', 'touch2.txt')
    git('commit', '-m', 'touch4 test')
    gitbzr('push')

    # update the bzr branch and sync the changes
    # that bzr repo is not a working tree repo so we need to branch it in bzr
    # and then push the changes back
    cd(TESTDIR)
    bzr('branch', '%s_pushed' % BZRBRANCH, '%s_branched' % BZRBRANCH)
    cd('%s_branched' % BZRBRANCH)
    open('touch2.txt', 'w').write('touch5')
    bzr('commit', '-m', 'touch5')
    bzr('push', '%s_pushed' % BZRBRANCH)
    cd('%s_git' % BZRBRANCH)
    gitbzr('sync')
    
    # try to push again from git, should fail because we have not merged the
    # changes
    self.assertEquals('touch4', open('touch2.txt').read())
    self.assertRaises(subprocess.CalledProcessError, gitbzr, 'push')

    # this one should fail since there is nothing to commit
    git('pull', '.', '--', 'bzr/pushed')
    self.assertEquals('touch5', open('touch2.txt').read())
    self.assertRaises(subprocess.CalledProcessError, gitbzr, 'push')
    
    # edit a file and try to push
    open('touch2.txt', 'w').write('touch6')
    git('add', 'touch2.txt')
    git('commit', '-m', 'touch6')
    gitbzr('push')
    
    # pull in our bzr branch and make sure we get the change
    cd('%s_branched' % BZRBRANCH)
    bzr('pull')
    self.assertEquals('touch6', open('touch2.txt').read())

    # TEST: import another branch and pull changes from `pushed`
    cd('%s_git' % BZRBRANCH)
    gitbzr('import', '%s_imported' % BZRBRANCH, 'imported')
    git('checkout', 'imported')
    git('pull', '.', '--', 'pushed')
    gitbzr('push')
