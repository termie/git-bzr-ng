#!/bin/bash

# This is kind of a slow test because it uses the network in parts.
CWD=`pwd`
TESTDIR=/tmp/git-bzr-test
LP_LOGIN=`bzr lp-login`
BZRBRANCHNAME=bzrtest
BZRBRANCH=$TESTDIR/$BZRBRANCHNAME
GITBZR=$CWD/git-bzr

if [ -d "$TESTDIR" ];
then
  rm -rf $TESTDIR
fi

mkdir $TESTDIR
cd $TESTDIR

die () {
  echo $1
  exit 1
}

expect_failure () {
  if [ $? -eq 0 ];
  then
    die $1
  fi
}

expect_success () {
  if [ $? -ne 0 ];
  then
    die $1
  fi
}

# Make a bzr branch to interact with
bzr init $BZRBRANCH
cd $BZRBRANCH
echo "touch" > touch.txt
bzr add touch.txt
bzr commit -m "touch test"
echo "touch2" > touch2.txt
bzr add touch2.txt
bzr commit -m "touch2 test"

# Make another branch to test import later
cd $TESTDIR
bzr branch $BZRBRANCH ${BZRBRANCH}_imported

# TEST: clone with git-bzr-ng
cd $TESTDIR
$GITBZR clone $BZRBRANCH
expect_failure "clone should have failed"

# it should have guessed the name correctly but noticed the directory exists
# so clone it again
$GITBZR clone $BZRBRANCH ${BZRBRANCHNAME}_git
expect_success "failed to clone"

# make sure we have the branches we expect
cd ${BZRBRANCH}_git
if [ -z "$(git branch -a | sed -n '/bzr\/master/ p')" ];
then
  die "no bzr/master branch"
fi
if [ -z "$(git branch -a | sed -n '/\* master/ p')" ];
then
  die "not on master branch"
fi

# make sure we have the files we expect
if [ "touch" != "$(cat touch.txt)" ];
then
  die "checkout is not correct (touch.txt)"
fi

# TEST: push to new branch
git checkout -b pushed
echo "touch3" > touch2.txt
git add touch2.txt
git commit -m "touch3 test"
git bzr push ${BZRBRANCH}_pushed
expect_success "pushing new branch failed"

echo "touch4" > touch2.txt
git add touch2.txt
git commit -m "touch4 test"
git bzr push
expect_success "pushing new branch twice failed"

# update the bzr branch and sync the changes
cd ${BZRBRANCH}_pushed
echo "touch5" > touch2.txt
bzr commit -m "touch5"

cd ${BZRBRANCH}_git
git bzr sync

git bzr push
expect_failure "should not be able to push when not a fast-forward"

git pull . -- bzr/pushed

git bzr push
expect_failure "should not be able to push if no changes"

# edit and try to push back
echo "touch6" > touch2.txt
git add touch2.txt
git commit -m "touch6"
git bzr push


# TEST: import another branch
git bzr import ${BZRBRANCH}_imported imported
git checkout imported

git pull . -- pushed
git bzr push

