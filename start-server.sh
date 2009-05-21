#!/bin/bash
path=`dirname $0`
path=`cd $path; pwd`

echo "Shutting down server"
kill `cat $path/paster.pid`

echo "Starting new server deamon"
paster setup-app development.ini
paster serve --reload --pid-file=$path/paster.pid --log-file=$path/paster.log $path/development.ini

echo "Done!"
