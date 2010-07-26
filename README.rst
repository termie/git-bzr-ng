Git to Bzr to Git to Bzr...
===========================

This tool lets you use git's day-to-day functionality for your
development but still be able to interact with bzr and launchpad.

Easy to use and cleanly written (I hope (send patches!))


Example usage
-------------

::

  Clone a launchpad repo
  
  $ git bzr clone lp:nova nova

  $ cd nova
  $ git branch -a  

  # result -> 
  #   bzr/nova
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
  $ git diff bzr/nova

  Somebody else has a patch and you want to test it locally.

  $ git bzr import lp:~vishvananda/nova/fix-part fix-part
  $ git diff touch_branch

Disclaimer
----------

Due to some quirks in fast-import / fast-export it looks like you can currently
only push in a "write-only" way, meaning from your initial push of a new branch
you can't merge any further bzr commits in (git and bzr seem to be fighting
over how to name the commit), so you won't be able to push from any branches
you have pulled changes in from (this goes for master, too).

The examples above still work fine, and you can push multiple times to a pushed
branch, you just can't merge histories :/

I am working on resolving this currently because it is quite annoying.


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

Also, output is a little verbose right now since things are rather fresh.


Requirements
------------

* git (some recent version)
* bzr 2.2+ (pip install bzr)
* bzr-fastimport (bzr branch lp:bzr-fastimport)
* You also need to put the git-bzr script somewhere in your path


Troubleshooting
---------------

If you get a traceback from bzr about BTreeIndex it means you are using an
old version of bzr. You need bzr 2.2+


Kind thanks to
--------------

* Evan Martin's git-cl: http://neugierig.org/software/git/?r=git-cl
* kfish's git-bzr: http://github.com/kfish/git-bzr
