#!/bin/bash
path=`dirname $0`
path=`cd $path; pwd`
ppath=`cd $path; cd ..; pwd`

echo "Path is $path. Entering enviroment"
source $ppath/bin/activate

echo "Shutting down server"
kill `cat $path/paster.pid`

echo "Starting new server deamon"
paster setup-app development.ini
paster serve --pid-file=$path/paster.pid --log-file=$path/paster.log $path/development.ini

echo "Done!"
