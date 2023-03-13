#!/bin/sh
pattern=$(echo $$)-$(date +%s)
echo $pattern
cat pandaJobData.out.template | sed -e "s/000229/000229-${pattern}/g" > pandaJobData.out
cat job.xrsl.template | sed -e "s/000229/000229-${pattern}/g" > job.xrsl
arcsub -c https://arc-boinc-04.cern.ch/arex job.xrsl $@
