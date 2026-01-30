#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pyzabbix获取的items数据中output中,name字段"xxxx[1122,dddd]" ,key_字段值有的是"cccc_$1"如何增加功能,对于zabbix的items做转换,在原有的返回数据中增加一个字段alias,alias字段值是"xxxx_1122" 如果有$2则将name中的dddd赋值给alias$2
# 或者pyzabbix有没有内置的方法将zabbix能获取显示名称的功能,这样就不用自己写函数转换了

"""
Zabbix items数据转换模块

本模块提供了处理Zabbix items数据的功能，特别是解析name字段和key_字段，
并根据规则生成alias字段。
"""
import pyzabbix
import re
from typing import Dict, List, Any, Optional


def parse_zabbix_item_name(name: str) -> List[str]:
    """
    解析Zabbix item名称中的参数
    
    Args:
        name: Zabbix item名称，格式如 "xxxx[1122,dddd]"
    
    Returns:
        参数列表，如 ["1122", "dddd"]
    """
    # 匹配方括号中的参数
    match = re.search(r'\[(.*?)\]', name)
    if match:
        params_str = match.group(1)
        # 分割参数
        params = [param.strip() for param in params_str.split(',')]
        return params
    return []


def generate_item_alias(name: str, key_: str) -> str:
    """
    根据name和key_生成alias字段
    
    Args:
        name: Zabbix item名称，格式如 "xxxx[1122,dddd]"
        key_: Zabbix item key，格式如 "cccc_$1"
    
    Returns:
        生成的alias字段值，如 "cccc_1122"
    """
    # 解析name中的参数
    params = parse_zabbix_item_name(name)
    
    # 替换key_中的$1, $2等占位符
    alias = key_
    
    # 查找所有$n占位符
    placeholders = re.findall(r'\$(\d+)', key_)
    
    for placeholder in placeholders:
        index = int(placeholder) - 1  # 转换为0-based索引
        if index < len(params):
            alias = alias.replace(f"${placeholder}", params[index])
    
    # 如果key_中没有占位符，尝试从name中提取前缀
    if not placeholders and '[' in name:
        # 提取name中[之前的部分
        prefix = name.split('[')[0].strip()
        if params:
            alias = f"{prefix}_{params[0]}"
    
    return alias


def enhance_zabbix_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    增强Zabbix items数据，为每个item增加alias字段
    
    Args:
        items: Zabbix items列表，每个item包含name和key_字段
    
    Returns:
        增强后的items列表，每个item增加了alias字段
    """
    enhanced_items = []
    
    for item in items:
        # 创建item的深拷贝
        enhanced_item = item.copy()
        
        # 获取name和key_字段
        name = item.get('name', '')
        key_ = item.get('key_', '')
        
        # 生成alias字段
        alias = generate_item_alias(name, key_)
        enhanced_item['alias'] = alias
        
        enhanced_items.append(enhanced_item)
    
    return enhanced_items


def get_zabbix_display_name(item: Dict[str, Any]) -> str:
    """
    获取Zabbix item的显示名称
    
    注意：pyzabbix没有直接的内置方法获取显示名称，
    但Zabbix API本身在item.get时可以通过output参数获取name字段，
    这里我们模拟实现显示名称的生成。
    
    Args:
        item: Zabbix item字典
    
    Returns:
        显示名称
    """
    # 优先使用alias字段
    if 'alias' in item:
        return item['alias']
    
    # 否则使用name字段
    if 'name' in item:
        return item['name']
    
    # 最后使用key_字段
    if 'key_' in item:
        return item['key_']
    
    return "Unknown Item"


# 示例用法
def example_usage():
    """
    示例用法
    """
    # 模拟从Zabbix API获取的items数据
    sample_items = [
        {
            "itemid": "12345",
            "name": "CPU Load [all,avg1]",
            "key_": "system.cpu.load[$1,$2]",
            "value_type": "0"
        },
        {
            "itemid": "12346",
            "name": "Memory Usage [used,percent]",
            "key_": "vm.memory.size[$1]",
            "value_type": "0"
        },
        {
            "itemid": "12347",
            "name": "Disk Usage [/boot,used]",
            "key_": "vfs.fs.size[$1,$2]",
            "value_type": "0"
        },
        {
            "itemid": "12348",
            "name": "Network Traffic [eth0,in]",
            "key_": "net.if.in[$1]",
            "value_type": "0"
        }
    ]
    
    print("原始items数据:")
    for item in sample_items:
        print(f"Item ID: {item['itemid']}, Name: {item['name']}, Key: {item['key_']}")
    
    # 增强items数据
    enhanced_items = enhance_zabbix_items(sample_items)
    
    print("\n增强后的items数据:")
    for item in enhanced_items:
        print(f"Item ID: {item['itemid']}, Name: {item['name']}, Key: {item['key_']}, Alias: {item['alias']}")
    
    # 测试显示名称获取
    print("\n显示名称测试:")
    for item in enhanced_items:
        display_name = get_zabbix_display_name(item)
        print(f"Item ID: {item['itemid']}, Display Name: {display_name}")


if __name__ == "__main__":
    example_usage()
