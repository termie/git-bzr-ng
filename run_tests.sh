#!/bin/sh
if [ ! -f "run_tests.log" ];
then
  echo "The first time you run this will most likely take quite a while"
  echo "as it will be checking out quite a lot of different vendor"
  echo "packages to test against."
  echo ""
  echo "Running some preliminary setup in 5 seconds."
  sleep 5
  python run_tests.py tests.test_basic:SetupVendorOnly.setup_vendor
fi
python run_tests.py $@ 2> run_tests.log
