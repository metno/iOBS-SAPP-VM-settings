#!/bin/bash
# Copyright 2005-2016 ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction

# start/stop/check cmdline utility

set -a

. local.sh

####################################################################################
start() {
    echo "#######Starting SAPP $app"

if [ $app = "db" -o $app = "all" ]
then
    echo "####### "
    if [ $force_flag = "force" ]
    then
        echo "####### Forcing DB shutdown on all $CLU cluster nodes ... "
        cd $SAPP_ROOT/scripts
        fab --parallel cl:c=$CLU stop:app=db,user=$db_user && rm -f */data/mysql_sandbox*pid        
    fi
    echo "####### Starting mysql instances:"
    cd $GPFS_ROOT/mysql/msb
    ./start_all
fi
if [ $app = "sv" -o $app = "all" ]
then
    echo "####### Starting supervisord:"
    cd $SAPP_ROOT/scripts
    supervisord -c local.supervisord.conf
fi
if [ $app = "acq" -o $app = "all" ]
then
    echo "####### Starting $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf start python:acq_scanner 
fi
if [ $app = "proc" -o $app = "all" ]
then
    echo "####### Starting $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf start python:proc_dispatcher 
fi
if [ $app = "dj" -o $app = "all" ]
then
    echo "####### Starting $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf start django_web
fi
if [ $app = "ecflow" -o $app = "all" ]
then
    echo "####### Starting ecflow server and logserver:"
    cd ${SAPP_ROOT}ecflow
    export LOGMAP=${SAPP_ROOT}ecflow/:${SAPP_ROOT}ecflow/
    export LOGPATH=${SAPP_ROOT}ecflow/
    sleep 1
    ecflow_start.sh -p $ECF_PORT -d $ECF_HOME
    sleep 1
    ecflow_client --port $ECF_PORT --host $CLU --log=new $SAPP_ROOT/logs/ecflow.log
    sleep 1
    ecflow_client --port $ECF_PORT --host $CLU --check_pt 120
    sleep 1
    nohup ecflow_logsvr.pl > ../logs/ecflow_logsvr.log 2>&1 &
fi
if [[ mars_server -eq 1 ]] && [[ "$app" = "mars" || "$app" = "all" ]]
then
    echo "####### Starting  $app:"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf start mars_server 

fi
}


####################################################################################
stop() {
    echo "####### Stopping SAPP ..."

if [ $app = "ecflow" -o $app = "all" ]
then
    echo "####### Stopping ecflow server and logserver:"    
    $SAPP_ROOT/scripts/check_cmn.sh &&  cd $SAPP_ROOT/ecflow && ecflow_stop.sh -p $ECF_PORT &&  pkill -f  ecflow_logsvr
fi
if [ $app = "proc" -o $app = "all" ]
then
    echo "####### Stopping $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf stop python:proc_dispatcher   
fi
if [ $app = "acq" -o $app = "all" ]
then
    echo "####### Stopping $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf stop python:acq_scanner    
fi
if [[ mars_server -eq 1 ]] && [[ "$app" = "mars" || "$app" = "all" ]]
then
    echo "####### Stopping $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf stop mars_server    
fi
if [ $app = "dj" -o $app = "all" ]
then
    echo "####### Stopping $app"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf stop django_web 
    pkill -f runserver # not sure  supervisorctl can stop webserver .
fi
if [ $app = "sv" -o $app = "all" ]
then
    echo "####### Stopping supervisord and apps"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf shutdown   
fi
if [ $app = "db" -o $app = "all" ]
then
    echo "####### Stopping mysql instances:"
    cd $GPFS_ROOT/mysql/msb
    ./stop_all
fi
}

####################################################################################
restart() {
        stop
        start
}

####################################################################################
status() {
    echo "####### Checking SAPP status ..."

    echo "####### checking ecflow server:"    
    ecflow_client --port=$ECF_PORT --host=$CLU --ping && ecflow_client --port=$ECF_PORT  --host=$CLU --stats && echo "ECFLOW SERVER RUNNING" || echo "ECFLOW SERVER NOT RUNNING"

    echo "####### checking ecflow logserver:"    
    ps aux | grep ecflow_logsvr | grep -v grep && echo "LOGSERV RUNNING" || echo "LOGSERV NOT RUNNING"

    echo "####### checking supervisord and apps"
    cd $SAPP_ROOT/scripts
    supervisorctl -c local.supervisord.conf status  

    echo "####### checking mysql instances:"
    cd $GPFS_ROOT/mysql/msb
    ./status_all

    echo "####### checking db/acq/proc instances running on each node:" 
    cd $SAPP_ROOT/scripts   
    fab --parallel cl:c=$CLU status:app=db,user=$db_user &
    fab --parallel cl:c=$CLU status:app=acq,user=$app_user &
    fab --parallel cl:c=$CLU status:app=proc,user=$app_user  
    
    echo "#######last monitor.txt:"
    cd $SAPP_ROOT/logs    
    cat $CLU.monitor.txt | grep -v msb
}

####################################################################################
log() {
    echo "####### Checking SAPP logs ..."
    set -x
    cd $SAPP_ROOT/logs
    
    tail -n 10  supervisord.log  
    tail -n 10  ecpds-acq.log 
    tail -n 10  proc.$CLU*.log
    tail -n 10  acq.$CLU*.log
    tail -n 10  db.master.err.log
    tail -n 10  db.node1.err.log
    tail -n 10  django.log
    tail -n 10  ecflow.log
    egrep 'ERRO|WARNI|Trace|ecCodes|Backtrace|disabled|configured|attempt'  acq?.log
    egrep 'ERRO|WARNI|Trace|ecCodes|Backtrace|attempt'  proc?.log

} 

####################################################################################
# input arguments
action=$1
app=${2:-help} # set default values
force_flag=${3:-off} # set default values

case "$1" in
    start)
        start
        RETVAL=$?
        ;;
    stop)
        stop
        RETVAL=$?
        ;;
    restart|force-reload)
        restart
        RETVAL=$?
        ;;
    status)
        status
        RETVAL=$?
        ;;
    log)
        log
        RETVAL=$?
        ;;
    *)
        echo $"Usage: $0 <action> <app> [force]"
        echo $"where: action in {start|stop|restart|status|log}"
        echo $"       app    in {all|db|ecflow|sv|dj|acq|proc|mars}"
        echo $"       use force flag to stop any cluster DB instance before an all|db (re)start"
        exit 1
esac

exit $RETVAL
