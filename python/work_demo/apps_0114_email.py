#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP邮箱文件夹名解码工具
简化版实现IMAP修改版UTF-7编码的解码逻辑
用于将修改版UTF-7编码的邮箱文件夹名转换为正常中文格式
例如：&Ti1lhw-other_test -> 中文other_test
"""

import base64


def decode_modified_utf7(s: str) -> str:
    """
    简化版IMAP修改版UTF-7编码解码
    
    Args:
        s: 待解码的字符串，如"&Ti1lhw-other_test"
        
    Returns:
        解码后的字符串，如"中文other_test"
    """
    import base64
    
    # 分割字符串，处理每个编码段
    parts = s.split('&')
    result = [parts[0]]
    
    for part in parts[1:]:
        if '-' in part:
            # 提取编码部分和剩余部分
            encoded, rest = part.split('-', 1)
            if encoded:
                try:
                    # 1. 将,替换为+
                    # 2. 添加base64填充
                    # 3. 解码base64和UTF-16BE
                    encoded = encoded.replace(',', '+')
                    padding = 4 - len(encoded) % 4
                    if padding < 4:
                        encoded += '=' * padding
                    decoded = base64.b64decode(encoded).decode('utf-16be')
                    result.extend([decoded, rest])
                except Exception:
                    # 解码失败，保留原始编码
                    result.append(f"&{part}")
            else:
                # &- 表示字面意义的 &
                result.extend(['&', rest])
        else:
            # 没有结束符，将&作为普通字符处理
            result.append(f"&{part}")
    
    return ''.join(result)


def encode_modified_utf7(s: str) -> str:
    """
    简化版IMAP修改版UTF-7编码
    
    Args:
        s: 待编码的字符串，如"中文other_test"
        
    Returns:
        编码后的字符串，如"&Ti1lhw-other_test"
    """
    result = []
    
    for c in s:
        if 0x20 <= ord(c) <= 0x7e and c != '&':
            # ASCII可打印字符且不是&，直接添加
            result.append(c)
        else:
            # 编码为UTF-16BE + base64
            try:
                utf16 = c.encode('utf-16be')
                b64 = base64.b64encode(utf16).decode('ascii').rstrip('=').replace('+', ',')
                result.append(f"&{b64}-")
            except Exception:
                # 编码失败，直接添加字符
                result.append(c)
    
    return ''.join(result)


def process_email_folders(folders: list) -> list:
    """
    批量处理邮箱文件夹列表
    
    Args:
        folders: 原始文件夹列表
        
    Returns:
        解码后的文件夹列表
    """
    return [decode_modified_utf7(folder) for folder in folders]


# 测试示例
if __name__ == "__main__":
    print("=== IMAP邮箱文件夹名解码测试 ===")
    
    # 测试用户提供的示例
    example = "&Ti1lhw-other_test"
    decoded = decode_modified_utf7(example)
    print(f"1. 用户示例测试:")
    print(f"   原始: {example!r}")
    print(f"   解码: {decoded!r}")
    print(f"   结果: {'✓ 成功' if decoded == '中文other_test' else '✗ 失败'}")
    
    # 测试编码功能
    original = "中文other_test"
    encoded = encode_modified_utf7(original)
    decoded_back = decode_modified_utf7(encoded)
    print(f"\n2. 编码测试:")
    print(f"   原始: {original!r}")
    print(f"   编码: {encoded!r}")
    print(f"   解码回: {decoded_back!r}")
    print(f"   结果: {'✓ 成功' if decoded_back == original else '✗ 失败'}")
    
    # 测试imaplib集成示例
    print(f"\n3. imaplib集成示例:")
    print(f"   import imaplib")
    print(f"   from apps_0114_email import decode_modified_utf7")
    print(f"   ")
    print(f"   # 模拟从IMAP服务器获取的文件夹名")
    print(f"   imap_folders = [b'&Ti1lhw-other_test', b'INBOX']")
    print(f"   ")
    print(f"   # 解码文件夹名")
    print(f"   decoded = [decode_modified_utf7(f.decode()) for f in imap_folders]")
    print(f"   # 输出: ['中文other_test', 'INBOX']")
    print(f"   ")
    print(f"=== 测试完成 ===")