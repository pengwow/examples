#!/usr/bin/env python3
"""测试不同的邮件搜索条件"""

import datetime

def test_search_criteria():
    """测试不同的搜索条件"""
    
    now = datetime.datetime.now()
    
    # 不同的时间范围选项
    criteria_options = {
        "最近24小时": {
            "description": "过去24小时的邮件",
            "criteria": f'SINCE {(now - datetime.timedelta(days=1)).strftime("%d-%b-%Y")}'
        },
        "最近7天": {
            "description": "过去7天的邮件",
            "criteria": f'SINCE {(now - datetime.timedelta(days=7)).strftime("%d-%b-%Y")}'
        },
        "最近30天": {
            "description": "过去30天的邮件",
            "criteria": f'SINCE {(now - datetime.timedelta(days=30)).strftime("%d-%b-%Y")}'
        },
        "今天": {
            "description": "今天收到的邮件",
            "criteria": f'ON {now.strftime("%d-%b-%Y")}'
        },
        "昨天": {
            "description": "昨天收到的邮件",
            "criteria": f'ON {(now - datetime.timedelta(days=1)).strftime("%d-%b-%Y")}'
        },
        "本周": {
            "description": "本周的邮件",
            "criteria": f'SINCE {(now - datetime.timedelta(days=now.weekday())).strftime("%d-%b-%Y")}'
        },
        "本月": {
            "description": "本月的邮件",
            "criteria": f'SINCE {now.replace(day=1).strftime("%d-%b-%Y")}'
        }
    }
    
    print("可用的邮件搜索条件:")
    print("=" * 60)
    
    for key, option in criteria_options.items():
        print(f"{key}:")
        print(f"  描述: {option['description']}")
        print(f"  搜索条件: {option['criteria']}")
        print()
    
    print("=" * 60)
    print("IMAP搜索条件说明:")
    print("- SINCE date: 搜索指定日期及之后的邮件")
    print("- ON date: 搜索指定日期的邮件")
    print("- BEFORE date: 搜索指定日期之前的邮件")
    print("- SINCE 和 BEFORE 可以组合使用")
    print("日期格式: DD-Mon-YYYY (例如: 08-Dec-2024)")
    
    # 显示当前时间信息
    print("\n当前时间信息:")
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"昨天: {(now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}")
    print(f"一周前: {(now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')}")
    print(f"一月前: {(now - datetime.timedelta(days=30)).strftime('%Y-%m-%d')}")

if __name__ == '__main__':
    test_search_criteria()