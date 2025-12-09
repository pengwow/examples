#!/usr/bin/env python3
"""
邮件UID生成和匹配工具
根据发送人、时间和标题生成唯一的邮件ID，用于后续匹配和回复操作
"""

import hashlib
import datetime
from typing import Optional


def generate_email_uid(sender: str, timestamp: str, subject: str) -> str:
    """
    根据三个参数进行hash计算，生成邮件UID
    
    Args:
        sender (str): 邮件发送人
        timestamp (str): 邮件时间戳（建议使用标准格式如：2024-12-09 10:30:00）
        subject (str): 邮件主题
        
    Returns:
        str: 32位MD5哈希值，作为邮件UID
        
    Raises:
        ValueError: 如果参数为空或无效
    """
    # 参数验证
    if not all([sender, timestamp, subject]):
        raise ValueError("所有参数（发送人、时间戳、主题）都不能为空")
    
    # 清理和标准化参数
    sender_clean = sender.strip().lower()
    timestamp_clean = timestamp.strip()
    subject_clean = subject.strip()
    
    # 组合参数进行哈希计算
    combined_string = f"{sender_clean}|{timestamp_clean}|{subject_clean}"
    
    # 计算MD5哈希值
    md5_hash = hashlib.md5(combined_string.encode('utf-8')).hexdigest()
    
    return md5_hash


def generate_email_uid_from_email_info(email_info: dict) -> str:
    """
    从邮件信息字典生成邮件UID
    
    Args:
        email_info (dict): 包含发送人、时间和主题的字典
            - from: 发送人邮箱
            - timestamp: 时间戳（可选，如未提供则使用当前时间）
            - subject: 邮件主题
            
    Returns:
        str: 32位MD5哈希值，作为邮件UID
    """
    sender = email_info.get('from', '')
    timestamp = email_info.get('timestamp') or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = email_info.get('subject', '')
    
    return generate_email_uid(sender, timestamp, subject)


def find_email_by_uid(email_list: list, target_uid: str) -> Optional[dict]:
    """
    根据UID在邮件列表中查找对应的邮件
    
    Args:
        email_list (list): 邮件列表，每个元素是包含邮件信息的字典
        target_uid (str): 要查找的邮件UID
        
    Returns:
        Optional[dict]: 找到的邮件信息字典，未找到则返回None
    """
    for email_info in email_list:
        # 为每个邮件生成UID
        email_uid = generate_email_uid_from_email_info(email_info)
        
        # 比较UID
        if email_uid == target_uid:
            return email_info
    
    return None


def reply_to_email_by_uid(email_list: list, target_uid: str, reply_content: str) -> bool:
    """
    根据UID找到对应邮件并进行回复操作
    
    Args:
        email_list (list): 邮件列表
        target_uid (str): 要回复的邮件UID
        reply_content (str): 回复内容
        
    Returns:
        bool: 是否成功找到并处理回复
    """
    # 查找目标邮件
    target_email = find_email_by_uid(email_list, target_uid)
    
    if target_email is None:
        print(f"未找到UID为 {target_uid} 的邮件")
        return False
    
    # 执行回复操作（这里只是示例，实际需要调用邮件发送API）
    print(f"回复邮件信息:")
    print(f"  原始邮件主题: {target_email.get('subject', 'N/A')}")
    print(f"  原始发件人: {target_email.get('from', 'N/A')}")
    print(f"  回复内容: {reply_content}")
    print(f"  回复时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 这里可以添加实际的邮件发送逻辑
    # 例如：send_reply_email(target_email, reply_content)
    
    return True


def test_email_uid_functionality():
    """测试邮件UID功能"""
    
    # 测试数据
    test_emails = [
        {
            'from': 'sender1@example.com',
            'timestamp': '2024-12-09 10:30:00',
            'subject': '测试邮件主题1'
        },
        {
            'from': 'sender2@example.com', 
            'timestamp': '2024-12-09 11:00:00',
            'subject': '测试邮件主题2'
        },
        {
            'from': 'sender1@example.com',
            'timestamp': '2024-12-09 10:30:00',
            'subject': '测试邮件主题1'  # 与第一个邮件相同，应该生成相同UID
        }
    ]
    
    print("=== 邮件UID生成测试 ===")
    
    # 生成每个邮件的UID
    for i, email_info in enumerate(test_emails, 1):
        uid = generate_email_uid_from_email_info(email_info)
        print(f"邮件{i} UID: {uid}")
        print(f"  发送人: {email_info['from']}")
        print(f"  时间: {email_info['timestamp']}")
        print(f"  主题: {email_info['subject']}")
        print()
    
    # 测试查找功能
    print("=== 邮件查找测试 ===")
    
    # 获取第一个邮件的UID
    first_email_uid = generate_email_uid_from_email_info(test_emails[0])
    
    # 查找邮件
    found_email = find_email_by_uid(test_emails, first_email_uid)
    if found_email:
        print(f"成功找到UID为 {first_email_uid} 的邮件")
        print(f"邮件主题: {found_email['subject']}")
    else:
        print("未找到邮件")
    
    # 测试回复功能
    print("\n=== 邮件回复测试 ===")
    reply_success = reply_to_email_by_uid(
        test_emails, 
        first_email_uid, 
        "这是回复内容，感谢您的邮件！"
    )
    
    print(f"回复操作结果: {'成功' if reply_success else '失败'}")


if __name__ == '__main__':
    test_email_uid_functionality()