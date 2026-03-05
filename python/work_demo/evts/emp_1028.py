from typing import Any


aio_list = [
    {"id":'1', "name":'xxx',"e_id":"1,2","syscode":"","source":"aio"},
    {"id":'2', "name":'xxx',"e_id":"1,2,3","syscode":"","source":"aio"},
    {"id":'3', "name":'xxx',"e_id":"5,6","syscode":"","source":"aio"}
]

evts_list = [
    {"id":'1', "name":'xxx',"e_id":"1","syscode":"","source":"evt"},
    {"id":'1', "name":'xxx',"e_id":"2","syscode":"","source":"evt"},
    {"id":'2', "name":'xxx',"e_id":"2","syscode":"","source":"evt"},
    {"id":'3', "name":'xxx',"e_id":"1","syscode":"","source":"evt"},
    {"id":'4', "name":'xxx',"e_id":"1","syscode":"","source":"evt"},
]

# 比较两个列表，根据e_id字段是否有交集，其中evts_list中的e_id字段为单个值，aio_list中的e_id字段为多个值，用逗号分隔
# evts_list的e_id为aio_list列表中的id值，aio_list的e_id为evts_list的id值
# 比较两个列表，如果evts_list的e_id在aio_list中id匹配后，如果aio_list的e_id不包含evts_list的id值，这说明两侧数据异常，反之aio_list的e_id在evts_list中id匹配后，的e_id不包含evts_list的id值，也是异常
# 区分出异常数据和正常数据
# 如上数据，evts_list中的异常数据为"id":'3'和"id":'4'
# aio_list中的异常数据为"id":'1'和id":'2'，因为"id":'1'时e_id中有个2，evts_list的id：2的eid没有1则也是异常的，并且"id":'2'的e_id为"2,3"，在evts_list中id:3的e_id为1不包含2，则也是异常的，所有aio_list中的异常数据为"id":'1'和id":'2'

# 最后编写函数，用来输出两个列表aio_list，evts_list，在其数据结构中增加，status字段，值为"异常"或"正常"，remark字段，值为异常的原因
def compare_and_identify_data(aio_list, evts_list):
    """
    比较两个列表，根据e_id字段是否有交集，其中evts_list中的e_id字段可能是多个值，aio_list中的e_id字段为多个值，用逗号分隔
    :param aio_list: aio_list列表
    :param evts_list: evts_list列表
    :return: aio_list，evts_list，在其数据结构中增加，status字段，值为"异常"或"正常"，remark字段，值为异常的原因
    """
    # 预处理：合并evts_list中相同id的项，将它们的e_id拼接成多个值
    merged_evts_list = []
    evts_id_to_indices = {}
    
    for i, evt_item in enumerate(evts_list):
        evt_id = evt_item['id']
        if evt_id not in evts_id_to_indices:
            # 如果是新id，复制并添加到合并列表
            merged_item = evt_item.copy()
            # 确保e_id是字符串格式
            if not isinstance(merged_item['e_id'], str):
                merged_item['e_id'] = str(merged_item['e_id'])
            merged_evts_list.append(merged_item)
            evts_id_to_indices[evt_id] = len(merged_evts_list) - 1
        else:
            # 如果是已存在的id，合并e_id
            existing_index = evts_id_to_indices[evt_id]
            existing_e_ids = set(merged_evts_list[existing_index]['e_id'].split(','))
            # 添加新的e_id（如果不存在）
            new_e_id = evt_item['e_id']
            if not isinstance(new_e_id, str):
                new_e_id = str(new_e_id)
            existing_e_ids.add(new_e_id)
            # 重新拼接e_id
            merged_evts_list[existing_index]['e_id'] = ','.join(sorted(existing_e_ids))
    
    # 创建ID到对象的映射，方便查找
    aio_id_map = {item['id']: item for item in aio_list}
    evts_id_map = {item['id']: item for item in merged_evts_list}
    
    # 复制列表以避免修改原始数据
    updated_aio_list = [item.copy() for item in aio_list]
    updated_evts_list = [item.copy() for item in merged_evts_list]
    
    # 初始化状态和备注
    for item in updated_aio_list + updated_evts_list:
        item['status'] = "正常"
        item['remark'] = ""
    
    # 处理evts_list中的异常数据
    # 规则：evts项引用的所有aio项的e_id应包含当前evts项的id
    for evt_item in updated_evts_list:
        evt_id = evt_item['id']
        # evts的e_id可能包含多个aio引用，以逗号分隔
        aio_ref_ids = evt_item['e_id'].split(',')
        
        # 检查每个引用的aio项
        for aio_ref_id in aio_ref_ids:
            # 检查引用的aio项是否存在
            if aio_ref_id in aio_id_map:
                aio_ref = aio_id_map[aio_ref_id]
                aio_e_ids = set(aio_ref['e_id'].split(','))
                
                # 如果aio项的e_id不包含当前evts项的id，则evts项异常
                if evt_id not in aio_e_ids:
                    evt_item['status'] = "异常"
                    evt_item['remark'] = f"引用的aio项(id:{aio_ref_id})的e_id({aio_ref['e_id']})不包含当前evts项的id({evt_id})"
                    break  # 只要有一个引用异常，就标记为异常
    
    # 处理aio_list中的异常数据
    # 规则：所有引用该aio项的evts项的e_id应包含当前aio项的id
    for aio_item in updated_aio_list:
        aio_id = aio_item['id']
        aio_e_ids = set(aio_item['e_id'].split(','))
        
        # 找到所有引用当前aio项的evts项（考虑e_id可能包含多个值）
        referencing_evts = []
        for evt in evts_list:
            evt_e_ids = str(evt['e_id']).split(',')  # 确保转换为字符串再分割
            if aio_id in evt_e_ids:
                referencing_evts.append(evt)
        
        # 检查：如果aio项引用了evts项（e_id不为空），但没有evts项引用它，则异常
        if aio_e_ids and not referencing_evts:
            aio_item['status'] = "异常"
            aio_item['remark'] = f"aio项(id:{aio_id})的e_id({aio_item['e_id']})引用了evts项，但没有任何evts项引用该aio项"
        
        # 继续检查每个引用该aio项的evts项
        for evt in referencing_evts:
            evt_id = evt['id']
            # 如果aio项的e_id中包含某个evts项的id，但该evts项的e_id不包含aio项的id，则aio项异常
            if evt_id in aio_e_ids:
                # 查找对应的evts对象
                for updated_evt in updated_evts_list:
                    if updated_evt['id'] == evt_id:
                        # 检查evts项的e_id是否包含当前aio项的id
                        updated_evt_e_ids = set(updated_evt['e_id'].split(','))
                        if aio_id not in updated_evt_e_ids:
                            aio_item['status'] = "异常"
                            aio_item['remark'] = f"e_id中包含evts项(id:{evt_id})的id，但该evts项的e_id({updated_evt['e_id']})不包含当前aio项的id({aio_id})"
                            break
                
            # 检查aio项引用的evts项是否都正确引用了它
                for referenced_evt_id in aio_e_ids:
                    if referenced_evt_id in evts_id_map:
                        referenced_evt = evts_id_map[referenced_evt_id]
                        # 现在evts的e_id可能包含多个值，需要检查是否包含当前aio项的id
                        referenced_evt_e_ids = set(referenced_evt['e_id'].split(','))
                        if aio_id not in referenced_evt_e_ids:
                            aio_item['status'] = "异常"
                            aio_item['remark'] = f"e_id中包含evts项(id:{referenced_evt_id})的id，但该evts项的e_id({referenced_evt['e_id']})不包含当前aio项的id({aio_id})"
                            break
            if aio_item['status'] == "异常":
                break
    
    return updated_aio_list, updated_evts_list

# 执行比较并输出结果
def print_comparison_results():
    updated_aio, updated_evts = compare_and_identify_data(aio_list, evts_list)
    print(updated_aio)
    print(updated_evts)
    print("=== 比较结果 ===")
    print("\n1. aio_list 数据:")
    for item in updated_aio:
        print(f"ID: {item['id']}, E_ID: {item['e_id']}, Status: {item['status']}")
        if item['remark']:
            print(f"  原因: {item['remark']}")
    
    print("\n2. evts_list 数据:")
    for item in updated_evts:
        print(f"ID: {item['id']}, E_ID: {item['e_id']}, Status: {item['status']}")
        if item['remark']:
            print(f"  原因: {item['remark']}")

# 运行并打印结果
print_comparison_results()
