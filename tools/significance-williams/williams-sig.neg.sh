#!/bin/bash
CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"  && pwd )"
R --slave --no-save --args $1 $2 $3 $4 < $CURDIR/williams-sig.neg.R
