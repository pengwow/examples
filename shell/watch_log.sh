#!/bin/bash
#配置保存天数,默认7天
save_day=7
#当前时间
current_date=$(date -d "${save_day} day ago"  +%Y%m%d)
#日志文件根目录
folder="/var/log/gse"
#获取agent日志文件
all_logs_floder=$(ls ${folder}|grep agent |grep -v agent-err.log)
for logs_name in ${all_logs_floder}
do
   log_path="${folder}/${logs_name}"
   log_date=`echo ${logs_name} | awk -F "-" '{print $2}'`
   if [[ ${current_date} -gt ${log_date} ]];
   then
       #删除日志文件
       rm ${log_path};
    fi
done
