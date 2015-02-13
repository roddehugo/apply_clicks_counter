#!/bin/sh
set -e

ROOTDIR=`pwd`
MAKE="make -C $ROOTDIR"

if [ ! -d "$ROOTDIR/venv" ]; then
  $MAKE install
fi

if [[ `$MAKE status` == "[Running]" ]]; then
	$MAKE stop
	sleep 180
	$MAKE start
else
	$MAKE start
fi
