Git-Bzr-NG or How I Learned to Stop Worrying and Love the Code
==============================================================

git-bzr-ng is a bidirectional bridge between git and bzr that lets you stop
worrying which version control the code you love is using -- as long as they
are using git or bzr ;) (hg coming soon?).

Easy to use and cleanly written (I hope (send patches!)). Check out the
examples below for basic usage.


Example usage
-------------

::

  Clone a launchpad repo

  $ git bzr clone lp:nova nova

  $ cd nova
  $ git branch -a

  # result ->
  #   bzr/master
  # * master

  Make a new branch

  $ git checkout -b touch_branch

  $ echo "TOUCH" >> README
  $ git commit -a -m "touch touch"
  $ git bzr push lp:~termie/nova/touch_branch

  Now you've got a cool new branch up on a server!
  Go ahead and do some more work and push again.
  It will go to the same place, and much faster now.

  $ echo "TOUCH" >> README
  $ git commit -a -m "touch touch"
  $ git bzr push

  How is trunk doing?
  Sync is a slow operation the first time, like push.
  They both speed up after they've done it once for a given branch.

  $ git checkout master
  $ git bzr sync
  $ git diff bzr/master

  Somebody else has a patch and you want to test it locally.

  $ git bzr import lp:~vishvananda/nova/fix-part fix-part
  $ git diff touch_branch

  Like those changes? Pull them into your own branch and push them
  $ git checkout touch_branch
  $ git pull . -- fix-part
  $ git bzr push


See test.sh for even more examples. Please try it out and report any issues to
the github tracker at http://github.com/termie/git-bzr-ng/issues so we can
sort them out quickly.


Extra Notes
-----------

I've tried to keep you from doing anything too weird, but since it is git I
am sure you can figure out someway to mess stuff up, so if you somehow manage
to push weird data to your bzr/* branches, you can always force an overwrite
with:

::

  $ git bzr sync --overwrite bzr/nova

It won't do anything to any branch except the one mentioned and on that one
it effectively does a `bzr pull --overwrite`.



Requirements
------------

* git (some recentish version)
* bzr 2.2 or bzr 2.3.0
* bzr-fastimport 0.10 http://launchpad.net/bzr-fastimport/trunk/0.10.0/+download/bzr-fastimport-0.10.0.tar.gz
* python-fastimport, for bzr-fastimport (bzr branch lp:python-fastimport)
* You also need to put the git-bzr script somewhere in your path


Troubleshooting
---------------

For other issues, please see: http://github.com/termie/git-bzr-ng/issues

------------------
don't use bzr 2.3b
------------------

If you see

`AttributeError: 'BTreeBuilder' object has no attribute '_find_ancestors'`

it means you have the bzr 2.3 beta installed, git-bzr-ng currently works
unpatched with bzr 2.2 and bzr 2.3.0. It is possible to patch bzr 2.3b to
correct the issue, but 2.3.0 is easy to install with pip.

-----------------------------------
tests run against multiple versions
-----------------------------------

If you are running the tests (`python run_tests.py`) keep in mind that one
set of tests is actually running against bzr-fastimport's HEAD so it doesn't
always work, so if you see failures check that they are in GitBzrTest or
GitBzrStableTarballTest first.


----------------------------------
when all else fails: git bzr clear
----------------------------------

Additionally there is a command `git bzr clear` that will wipe out the
bzr-related information for a given branch so if you have somehow found
yourself in a bind, it should help you wipe the slate to try again.


Kind thanks to
--------------

* bzr-fastimport: https://launchpad.net/bzr-fastimport
* Evan Martin's git-cl: http://neugierig.org/software/git/?r=git-cl
* kfish's git-bzr: http://github.com/kfish/git-bzr
