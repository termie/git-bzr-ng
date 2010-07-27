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
* bzr 2.2+ (pip install --upgrade bzr)
* bzr-fastimport (bzr branch lp:bzr-fastimport)
* You also need to put the git-bzr script somewhere in your path


Troubleshooting
---------------

If you get a traceback from bzr about BTreeIndex it means you are using an
old version of bzr. You need bzr 2.2+ unfortunately 2.1.1 seems to be the
default package in Ubuntu Lucid right now so you may need to uninstall it
first, `pip install --upgrade bzr` should do the right thing.

For other issues, please see: http://github.com/termie/git-bzr-ng/issues


Kind thanks to
--------------

* bzr-fastimport: https://launchpad.net/bzr-fastimport
* Evan Martin's git-cl: http://neugierig.org/software/git/?r=git-cl
* kfish's git-bzr: http://github.com/kfish/git-bzr
