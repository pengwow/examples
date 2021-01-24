#!/bin/bash

OLD_IFS="$IFS"
IFS=$'\n'
PARAMS="
process|com.docker.osxfs serve
process|python
"
for i in $PARAMS
do
    IFS=OLD_IFS
    process_key=`echo $i | awk -F "|" {'print $1'}`
    process_name=`echo $i | awk -F "|" {'print $2'}`
    if [ $process_key == 'process' ]
    then

        ps_str=`ps aux |grep -v grep | grep "$process_name"`
        echo $ps_str
    fi
    IFS=$'\n'
done
# ps_list=`ps aux |grep ''`