import glob
import logging
import os
import shutil
import subprocess
import sys
import unittest
import time

from os import chdir as cd
from os import mkdir


TESTDIR='/tmp/git-bzr-test'
BZRBRANCHNAME='bzrtest'
BZRBRANCH='%s/%s' % (TESTDIR, BZRBRANCHNAME)
ROOTDIR=os.path.dirname(os.path.dirname(__file__))
VENDOR=os.path.join(ROOTDIR, 'vendor')
GITBZR=os.path.join(ROOTDIR, 'git-bzr')
PYFASTIMPORT=os.path.join(VENDOR, 'python-fastimport')
PLUGINDIR=os.path.join(VENDOR, 'plugins')
BZRFASTIMPORT=os.path.join(PLUGINDIR, 'fastimport')
BZRFASTIMPORT_STABLE=os.path.join(VENDOR, 'fastimport_stable')
BZRFASTIMPORT_STABLE_TARBALL=os.path.join(VENDOR, 'bzr-fastimport-0.10.0')
BZRFASTIMPORT_HEAD=os.path.join(VENDOR, 'fastimport_head')
BZRPATH = os.path.join(VENDOR, 'bzr-%s')
BZR = os.path.join(VENDOR, 'bzr')


VERSIONS = [
    ('2.2', '2.2.0'),
    ('2.2', '2.2.1'),
    ('2.2', '2.2.2'),
    ('2.2', '2.2.3'),
    ('2.2', '2.2.4'),
    ('2.3', '2.3.0'),
    ('2.3', '2.3.1')
    ]

# Set a timestamp at load time so that we can memoize our setup step
TIMESTAMP = time.time()


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
  logging.debug(' '.join(popenargs[0]))
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
  BZR = BZRPATH % '2.3.1'
  BZRFASTIMPORT = BZRFASTIMPORT_STABLE

  def setUp(self):
    self._ensure_checkouts()
    self._symlink_plugin()
    self._setup_bzr_branches()

  def tearDown(self):
    pass

  def _symlink_plugin(self):
    try:
      os.unlink(BZRFASTIMPORT)
    except Exception:
      pass
    os.symlink(self.BZRFASTIMPORT, BZRFASTIMPORT)

  def _symlink_bzr(self, force=None):
    try:
      os.unlink(BZR)
    except Exception:
      pass
    path = force and force or self.BZR
    os.symlink(path, BZR)

  def _ensure_checkouts(self):
    exec_path = ('PATH' in os.environ
                 and os.environ['PATH']
                 or '')
    if not exec_path.startswith(BZR):
      os.environ['PATH'] = '%s:%s' % (BZR, exec_path)

    download_url = 'http://launchpad.net/bzr/%s/%s/+download/bzr-%s.tar.gz'
    tarball = 'bzr-%s.tar.gz'
    for v in VERSIONS:
      if not os.path.exists(BZRPATH % v[1]):
        cd(VENDOR)
        check_output(['curl', '-O', '-L',
                      download_url % (v[0], v[1], v[1])
                      ])
        check_output(['tar', '-xzf', tarball % v[1]])

    # we need a functional bzr on our path to get anything else
    self._symlink_bzr(BZRPATH % '2.3.1')

    bzr_head = BZRPATH % 'head'
    if not os.path.exists(bzr_head):
      cd(VENDOR)
      bzr('branch', 'lp:bzr', BZRPATH % 'head')

    if not os.path.exists(PYFASTIMPORT):
      cd(VENDOR)
      bzr('branch', 'lp:python-fastimport')

    if not os.path.exists(PLUGINDIR):
      os.mkdir(PLUGINDIR)

    if not os.path.exists(BZRFASTIMPORT_STABLE):
      cd(VENDOR)
      bzr('branch', 'lp:bzr-fastimport', '-r', '307', BZRFASTIMPORT_STABLE)

    if not os.path.exists(BZRFASTIMPORT_HEAD):
      cd(VENDOR)
      bzr('branch', 'lp:bzr-fastimport', BZRFASTIMPORT_HEAD)

    if not os.path.exists(BZRFASTIMPORT_STABLE_TARBALL):
      cd(VENDOR)
      check_output(['curl', '-O', '-L',
                    'http://launchpad.net/bzr-fastimport/trunk/'
                    '0.10.0/+download/bzr-fastimport-0.10.0.tar.gz'
                    ])
      check_output(['tar', '-xzf', 'bzr-fastimport-0.10.0.tar.gz'])

    python_path = ('PYTHONPATH' in os.environ
                   and os.environ['PYTHONPATH']
                   or '')
    if not python_path.startswith(PYFASTIMPORT):
      os.environ['PYTHONPATH'] = '%s:%s' % (PYFASTIMPORT, BZR)

    os.environ['BZR_PLUGIN_PATH'] = PLUGINDIR
    os.environ['BZR_PDB'] = '1'

  def _setup_bzr_branches(self):
    memo = '%s_%s_%s' % (TESTDIR, self.__class__.__name__, TIMESTAMP)
    if os.path.exists(memo):
      rmdir(TESTDIR)
      shutil.copytree(memo, TESTDIR)
    else:
      # make a bzr branch to interact with
      rmdir(TESTDIR)
      mkdir(TESTDIR)
      cd(TESTDIR)
      bzr('init', BZRBRANCH)
      cd(BZRBRANCH)
      open('touch.txt', 'w').write('touch')
      bzr('add', '-v', 'touch.txt')
      bzr('commit', '-v', '-m', 'touch test')
      open('touch2.txt', 'w').write('touch2')
      bzr('add', 'touch2.txt')
      bzr('commit', '-m', 'touch2 test')
      bzr('tag', 'some_tag')

      # make another branch to test import later
      cd(TESTDIR)
      bzr('branch', BZRBRANCH, '%s_imported' % BZRBRANCH)

      # make a default clone
      cd(TESTDIR)
      gitbzr('clone', BZRBRANCH, '%s_cloned' % BZRBRANCHNAME)

      # clear old memos and copy it to our memo
      old_memo_glob = '%s_%s_*' % (TESTDIR, self.__class__.__name__)
      old_memos = glob.iglob(old_memo_glob)
      for path in old_memos:
        shutil.rmtree(path)
      shutil.copytree(TESTDIR, memo)


  def test_all(self):
    """Test most of the functionality.

    This test is a bit large, it is ported directly from a shell script.
    """
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

  def test_push_relative_path(self):
    cd('%s_cloned' % BZRBRANCH)
    open('touch2.txt', 'w').write('CLONED')
    git('add', 'touch2.txt')
    git('commit', '-m', 'touched touch2')

    # push back to previous bzr branch
    gitbzr('push', '../%s' % BZRBRANCHNAME)
    self.assertEqual('CLONED', open('%s/touch2.txt' % BZRBRANCH).read())

    open('touch2.txt', 'w').write('CLONED2')
    git('add', 'touch2.txt')
    git('commit', '-m', 'touched2 touch2')
    gitbzr('push')
    self.assertEqual('CLONED2', open('%s/touch2.txt' % BZRBRANCH).read())

    # push to a new repo
    gitbzr('push', '../%s_new' % BZRBRANCHNAME)
    cd('%s_new' % BZRBRANCH)
    bzr('checkout', '.')
    self.assertEqual('CLONED2', open('%s_new/touch2.txt' % BZRBRANCH).read())

  def test_import_no_url(self):
    self.assertRaises(subprocess.CalledProcessError, gitbzr, 'import')

  def test_import_strip_tags(self):
    # assert that the imported repo has our tag
    cd(TESTDIR)
    cd('%s_cloned' % BZRBRANCHNAME)
    rv = git('tag')
    self.assert_('some_tag' in rv)

    # add an invalid tag and make sure it doesn't get imported
    cd('%s_imported' % BZRBRANCH)
    bzr('tag', 'some~invalid!tag')
    cd(TESTDIR)
    cd('%s_cloned' % BZRBRANCHNAME)

    # the first try should fail due to an invalid tag
    self.assertRaises(subprocess.CalledProcessError,
                      gitbzr,
                      'import',
                      '%s_imported' % BZRBRANCH,
                      'import_fail')
    gitbzr('import', '--strip_tags', '%s_imported' % BZRBRANCH, 'import_win')
    rv = git('tag')
    self.assert_('some~invalid!tag' not in rv)

    # test that clone supports the flag also
    cd(TESTDIR)
    self.assertRaises(subprocess.CalledProcessError,
                      gitbzr, 'clone', '%s_imported' % BZRBRANCH, 'import_fail')
    gitbzr('clone', '--strip_tags', '%s_imported' % BZRBRANCH, 'import_win')

  def test_gitbzr_init_master(self):
    # make a new git repo
    INITGIT = os.path.join(TESTDIR, 'init_master_git')
    INITBZR = os.path.join(TESTDIR, 'init_master_bzr')
    cd(TESTDIR)
    git('init', INITGIT)
    cd(INITGIT)
    open('touch.txt', 'w').write('touch')
    git('add', 'touch.txt')
    git('commit', '-a', '-m', 'touch1')
    gitbzr('init')
    gitbzr('push', INITBZR)
    cd(TESTDIR)
    bzr('branch', INITBZR, '%s_working' % INITBZR)
    cd('%s_working' % INITBZR)
    self.assertEquals('touch', open('touch.txt').read())

  def test_gitbzr_init_branch(self):
    # make a new git repo
    INITGIT = os.path.join(TESTDIR, 'init_branch_git')
    INITBZR = os.path.join(TESTDIR, 'init_branch_bzr')
    cd(TESTDIR)
    git('init', INITGIT)
    cd(INITGIT)
    open('touch.txt', 'w').write('touch')
    git('add', 'touch.txt')
    git('commit', '-a', '-m', 'touch1')
    git('checkout', '-b', 'new_branch')
    open('touch.txt', 'w').write('touch2')
    git('commit', '-a', '-m', 'touch2')
    gitbzr('init')
    gitbzr('push', INITBZR)
    cd(TESTDIR)
    bzr('branch', INITBZR, '%s_working' % INITBZR)
    cd('%s_working' % INITBZR)
    self.assertEquals('touch2', open('touch.txt').read())


class GitBzrHeadTest(GitBzrTest):
  BZRFASTIMPORT = BZRFASTIMPORT_HEAD


class GitBzrHeadHeadTest(GitBzrTest):
  BZR = BZRPATH % 'head'
  BZRFASTIMPORT = BZRFASTIMPORT_HEAD


class GitBzrStableTarballTest(GitBzrTest):
  BZRFASTIMPORT = BZRFASTIMPORT_STABLE_TARBALL


class GitBzrStable_2_2_0(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.0'


class GitBzrStable_2_2_1(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.1'


class GitBzrStable_2_2_2(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.2'


class GitBzrStable_2_2_3(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.3'


class GitBzrStable_2_2_4(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.4'


class GitBzrStable_2_3_0(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.3.0'


class GitBzrStable_2_2_0(GitBzrStableTarballTest):
  BZR = BZRPATH % '2.2.0'
