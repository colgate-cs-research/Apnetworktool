#!/bin/bash

# Determine path to scripts
if [[ $(uname) == "Darwin" ]]; then
    SCRIPTPATH=`greadlink -f $0`
else
    SCRIPTPATH=`readlink -f $0`
fi
BASEDIR="`dirname $SCRIPTPATH`"

TIMESTAMP=`date +%F-%H-%M-%S` 
OUTDIR="/shared/wireless/colgate-airwave/heatmaps/$TIMESTAMP"
mkdir -p $OUTDIR
cd $OUTDIR

PASSWORD=`cat $HOME/.airwave-credentials`

$BASEDIR/airwave_heatmaps.py -u research -p $PASSWORD -s $BASEDIR/sites.csv > capture.log 2>&1
