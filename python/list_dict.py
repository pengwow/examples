# coding=utf-8
import hashlib
import copy
import time
import random
import datetime

new_list = [
    {
        "status":"1",
        "file_time":"",
        "field_name":"脚本",
        "operate":"script",
        "file_path":"/tmp/liupeng1.sh"
    },
    {
        "status":"1",
        "file_time":"",
        "field_name":"脚本",
        "operate":"script",
        "file_path":"/tmp/liupeng2.sh"
    },
    {
        "status":"0",
        "file_time":"",
        "field_name":"kssee",
        "operate":"file",
        "file_path":"/tmp/liupeng1.sh"
    },
        {
        "status":"1",
        "file_time":"",
        "field_name":"脚本",
        "operate":"script",
        "file_path":"/tmp/liupeng3.sh"
    },

]

def get_is_finish_srcipt(id):
    ra = random.randint(1,5)
    if ra == 3:
        return 1
    return 0

def execute_script_by_status(item):
    re = random.randint(16000,20000)
    return re

def wait_last_script_finish(old_data, new_data):
    all_new_wait_script_list = list()
    all_old_script_list = list()
    all_old_script_dict = dict()
    for item in old_data:
        # 旧数据进行解析，将未完成的更新状态
        if 'script' in item.get('operate'):
            field_name = item.get('field_name')
            file_path = item.get('file_path')
            label_hash = hash(field_name + file_path)
            job_instance_id = item.get('job_instance_id',0)
            job_status = int(item.get('job_status', 0))
            if not job_status and job_instance_id:
                job_status = get_is_finish_srcipt(job_instance_id)
                item['job_status'] = job_status
                if int(job_status):
                    item['status'] = 1
            if not job_status and not job_instance_id:
                item['status'] = 0
            all_old_script_dict[label_hash] = item
    for item in range(len(new_data)):
        # 新数据解析，找到待执行的脚本
        if 'script' in new_data[item].get('operate') and int(new_data[item].get('status',0)):
            field_name = new_data[item].get('field_name')
            file_path = new_data[item].get('file_path')
            label_hash = hash(field_name + file_path)
            old_item = all_old_script_dict.get(label_hash)
            # 如果此条脚本 存在旧数据中，则使用数据进行操作
            if old_item:
                new_data[item] = old_item
                # 判断是否有未完成的old中的脚本，相当于上一个脚本未完成
                job_instance_id = new_data[item].get('job_instance_id', 0)
                job_status = int(new_data[item].get('job_status', 0))
                if not job_instance_id and not int(job_status):
                    job_instance_id = execute_script_by_status(new_data[item])
                    new_data[item]['job_instance_id'] = job_instance_id
                    job_status = get_is_finish_srcipt(job_instance_id)
                    new_data[item]['job_status'] = job_status
                    new_data[item]['file_time'] = datetime.datetime.now().strftime('%Y-%m-%d%H:%M')
                    new_data[item]['status'] = 0
                    break
                # 存在未完成的数据，获取新的状态后跳出整个循环
                if job_instance_id and not int(job_status):
                    job_status = get_is_finish_srcipt(job_instance_id)
                    new_data[item]['job_status'] = job_status
                    new_data[item]['status'] = 0
                    break
                if job_instance_id and int(job_status):
                    new_data[item]['status'] = 1
            else:
                # 没有旧数据 则 此条数据是新数据，新数据的
                new_data[item]['status'] = 0
                job_instance_id = new_data[item].get('job_instance_id', 0)
                job_status = int(new_data[item].get('job_status', 0))
                if not job_instance_id and not int(job_status):
                    job_instance_id = execute_script_by_status(new_data[item])
                    new_data[item]['job_instance_id'] = job_instance_id
                    new_data[item]['file_time'] = datetime.datetime.now().strftime('%Y-%m-%d%H:%M')
                    job_status = get_is_finish_srcipt(job_instance_id)
                    new_data[item]['job_status'] = job_status
                    break
                # 存在未完成的数据，获取新的状态后跳出整个循环
                if job_instance_id and not int(job_status):
                    job_status = get_is_finish_srcipt(job_instance_id)
                    new_data[item]['job_status'] = job_status
                    break
                if job_instance_id and int(job_status):
                    new_data[item]['status'] = 1
                    continue
    for item in range(len(new_data)):
        if 'script' in new_data[item].get('operate'):
            if not int(new_data[item].get('job_status',0)):
                new_data[item]['status'] = 0
            if new_data[item].get('job_instance_id',0):
                new_data[item]['status'] = 1
    return new_data



old_data = None
new_data = None
while True:

    new_data = copy.deepcopy(new_list)
    if not old_data:
        old_data = copy.deepcopy(new_data)
    temp_data = wait_last_script_finish(old_data, new_data)
    old_data = temp_data
    for item in temp_data:
        if 'script' in item.get('operate'):
            print(item)

    time.sleep(2)
