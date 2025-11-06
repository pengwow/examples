#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CMDB资源关系查找工具

功能：
- 根据资源名称和方向（上游/下游）递归查找所有相关资源
- 支持双向关系遍历（up/down）
- 避免循环引用导致的无限递归
"""

# 数据关系列表（新的数据结构）
flow_relation_data = {
    "CCS_abc": {"up":[
        {'syscode': 'aaa', 'deployunit': 'eee', 'direction': 'up'},
        {'syscode': 'aom', 'deployunit': '', 'direction': 'up'},
        ], "down":[]},
    "AOM_bcc": {"up":[
        {'syscode': 'ccs', 'deployunit': 'abc', 'direction': 'up'}], "down":[]},
    "DDD_qqq": {"up":[
        {'syscode': 'ccs', 'deployunit': 'abc', 'direction': 'up'},
        {'syscode': 'aom', 'deployunit': '', 'direction': 'up'}
        ], "down":[]},
}
# flow_relation_data的是字典，每个key为 syscode_deployunit，value为一个字典，包含up和down两个列表
# 编写函数，传递syscode和deployunit查找所有上游key
# 比如:
# syscode = ddd
# deployunit = qqq
# xxxx(syscode=str(syscode).upper(),deployunit=qqq)
# 返回:
# ['AOM_bcc', 'CCS_abc', 'AAA_eee']
#

def find_upstream_keys(syscode, deployunit, visited=None, upstream_keys=None):
    """
    递归查找指定资源的所有上游key
    
    参数:
        syscode: 系统编码（大写）
        deployunit: 部署单元
        visited: 已访问的资源集合，用于避免循环引用
        upstream_keys: 收集到的上游key列表
    
    返回:
        list: 所有上游key的列表，按层级顺序排列
    """
    # 初始化默认值
    if upstream_keys is None:
        upstream_keys = []
    
    # 参数验证，当参数无效时直接返回上游key列表
    if not syscode or not deployunit:
        return upstream_keys
    
    # 转换syscode为大写
    syscode = str(syscode).upper()
    
    # 构建当前资源的key
    current_key = f"{syscode}_{deployunit}"
    
    # 初始化已访问集合和上游key列表
    if visited is None:
        visited = set()
    if upstream_keys is None:
        upstream_keys = []
    
    # 检查是否已访问过该资源，避免循环引用
    if current_key in visited:
        return upstream_keys
    visited.add(current_key)
    
    # 检查当前资源是否存在于数据中
    if current_key not in flow_relation_data:
        return upstream_keys
    
    # 获取当前资源的上游关系
    upstream_relations = flow_relation_data[current_key].get('up', [])
    
    # 递归查找每个上游关系
    for relation in upstream_relations:
        # 获取上游资源的syscode和deployunit
        upstream_syscode = relation.get('syscode', '').upper()
        upstream_deployunit = relation.get('deployunit', '')
        
        if upstream_syscode and upstream_deployunit:
            # 构建上游资源的key
            upstream_key = f"{upstream_syscode}_{upstream_deployunit}"
            
            # 添加所有找到的上游key，无论是否存在于flow_relation_data中
            if upstream_key not in upstream_keys:
                upstream_keys.append(upstream_key)
                
            # 递归查找上游的上游
            find_upstream_keys(upstream_syscode, upstream_deployunit, visited, upstream_keys)
    
    return upstream_keys


def main():
    """
    主函数，提供示例用法
    """
    print("CMDB资源上游关系查找演示")
    print("=" * 50)
    
    # 示例1：查找 'DDD_qqq' 的上游资源
    print("\n示例1：查找 'ddd_qqq' 的上游资源:")
    try:
        result = find_upstream_keys(syscode='ddd', deployunit='qqq')
        print(f"上游key列表: {result}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例2：查找不存在的资源
    print("\n示例2：查找不存在的资源:")
    try:
        result = find_upstream_keys(syscode='unknown', deployunit='test')
        print(f"上游key列表: {result}")
    except Exception as e:
        print(f"查询出错: {e}")
    
    # 示例3：查找 'AOM_bcc' 的上游资源
    print("\n示例3：查找 'aom_bcc' 的上游资源:")
    try:
        result = find_upstream_keys(syscode='aom', deployunit='bcc')
        print(f"上游key列表: {result}")
    except Exception as e:
        print(f"查询出错: {e}")


if __name__ == "__main__":
    main()

