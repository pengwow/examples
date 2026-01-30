from pyzabbix import ZabbixAPI
import re

def generate_alias(item):
    """根据item的name和key_生成alias字段"""
    # 提取name中的参数（如"xxxx[1122,dddd]" → ["1122", "dddd"]）
    match = re.search(r'\[(.*?)\]', item['name'])
    if not match:
        return None
    params = match.group(1).split(',')
    
    # 提取key_中的占位符（如"cccc_$1" → ["cccc_", "$1"]）
    key_parts = item['key_'].split('$')
    alias = key_parts[0]  # 基础部分（如"cccc_"）
    
    # 遍历占位符，替换为参数值
    for i, part in enumerate(key_parts[1:], start=1):
        if i <= len(params):
            alias += f"{params[i-1]}"
        else:
            alias += f"${i}"  # 保留未匹配的占位符
    
    return alias

def get_items_with_alias(zapi, hostid):
    """获取带alias字段的监控项"""
    items = zapi.item.get(
        hostids=hostid,
        output='extend',
        selectApplications=True
    )
    
    # 为每个item生成alias
    for item in items:
        item['alias'] = generate_alias(item)
    return items

# 示例用法
zapi = ZabbixAPI("http://zabbix-server/zabbix")
zapi.login("Admin", "zabbix")
items = get_items_with_alias(zapi, "10084")
for item in items:
    print(f"Name: {item['name']}, Key: {item['key_']}, Alias: {item['alias']}")