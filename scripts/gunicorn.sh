#!/bin/bash
HOMEDIR="/var/www"
VENVDIR="$HOMEDIR/venvs/homepage"

# Load venv
. $VENVDIR/bin/activate


HOST="127.0.0.1"
PORT=10023
BASEDIR="$HOMEDIR/vhosts/sanca"
PIDFILE="$BASEDIR/tmp/gunicorn.pid"
LOGFILE="$BASEDIR/logs/gunicorn.log"
APPMODULE="production_wsgi:application"
DAEMONSCRIPT="gunicorn"
DAEMONOPTIONS="--pid=$PIDFILE --log-file=$LOGFILE --bind=$HOST:$PORT --workers=2 --daemon $APPMODULE"

case "$1" in
  start)
    mkdir -p $BASEDIR/logs
    mkdir -p $BASEDIR/tmp
    PYTHONPATH=$BASEDIR/scripts $DAEMONSCRIPT $DAEMONOPTIONS
    ;;
  stop)
    kill `cat -- $PIDFILE`
    ;;
  reload)
    if [ -e $PIDFILE ]; then
        PID=`cat -- $PIDFILE`
    fi 
    if [ ! $PID ] || ! ps -p $PID > /dev/null; then
        mkdir -p $BASEDIR/logs
        mkdir -p $BASEDIR/tmp
        PYTHONPATH=$BASEDIR/scripts $DAEMONSCRIPT $DAEMONOPTIONS
    else
        kill -s HUP $PID
    fi 
    ;;
  restart)
    kill `cat -- $PIDFILE`
    sleep 3
    PYTHONPATH=$BASEDIR/scripts $DAEMONSCRIPT $DAEMONOPTIONS
    ;;
  *)
    echo "Usage: gunicorn.sh {start|stop|restart}"
    exit 1
esac

exit 0
