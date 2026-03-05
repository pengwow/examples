#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP邮箱文件夹名解码工具
修复版实现IMAP修改版UTF-7编码的解码和编码逻辑
用于将修改版UTF-7编码的邮箱文件夹名转换为正常中文格式
例如：&Ti1lhw-other_test -> 中文other_test
"""

import base64

def decode_modified_utf7(s: str) -> str:
    """
    修复版IMAP修改版UTF-7编码解码
    
    Args:
        s: 待解码的字符串，如"&Ti1lhw-other_test"
        
    Returns:
        解码后的字符串，如"中文other_test"
    """
    result = []
    i = 0
    n = len(s)
    
    while i < n:
        if s[i] == '&':
            # 查找编码段结束符'-'
            end = s.find('-', i + 1)
            if end == -1:
                # 没有找到结束符，将&作为普通字符处理
                result.append('&')
                i += 1
                continue
            
            # 提取编码部分
            encoded = s[i+1:end]
            
            if not encoded:
                # &- 表示字面意义的 &
                result.append('&')
            else:
                try:
                    # 1. 将,替换为+（修改版UTF-7的特殊处理）
                    encoded = encoded.replace(',', '+')
                    
                    # 2. 添加base64填充
                    padding = 4 - len(encoded) % 4
                    if padding < 4:
                        encoded += '=' * padding
                    
                    # 3. 解码base64
                    bytes_data = base64.b64decode(encoded)
                    
                    # 4. 解码UTF-16BE
                    decoded = bytes_data.decode('utf-16be')
                    result.append(decoded)
                except Exception as e:
                    # 解码失败，保留原始编码
                    result.append(f"&{s[i+1:end]}-")
            
            # 跳过编码段
            i = end + 1
        else:
            # 普通字符，直接添加
            result.append(s[i])
            i += 1
    
    return ''.join(result)

def encode_modified_utf7(s: str) -> str:
    """
    修复版IMAP修改版UTF-7编码
    正确实现IMAP修改版UTF-7编码规则：
    1. 分离ASCII字符和非ASCII字符
    2. 对非ASCII字符部分进行UTF-16BE编码
    3. 对编码结果进行base64编码
    4. 将base64结果中的'+'替换为','
    5. 移除base64填充字符'='
    6. 用'&'和'-'包裹编码部分
    7. ASCII字符保持原样
    
    Args:
        s: 待编码的字符串，如"中文other_test"
        
    Returns:
        编码后的字符串，如"&Ti1lhw-other_test"
    """
    result = []
    current_ascii = ""
    current_encoded = ""
    
    def flush_encoded():
        nonlocal current_encoded, result
        if current_encoded:
            # 1. 编码为UTF-16BE
            utf16_data = current_encoded.encode('utf-16be')
            # 2. 编码为base64
            b64_data = base64.b64encode(utf16_data).decode('ascii')
            # 3. 将+替换为,
            b64_data = b64_data.replace('+', ',')
            # 4. 移除填充
            b64_data = b64_data.rstrip('=')
            # 5. 添加到结果
            result.append(f"&{b64_data}-")
            current_encoded = ""
    
    def flush_ascii():
        nonlocal current_ascii, result
        if current_ascii:
            result.append(current_ascii)
            current_ascii = ""
    
    for c in s:
        if 0x20 <= ord(c) <= 0x7e:
            # ASCII可打印字符，保持原样
            if current_encoded:
                flush_encoded()
            current_ascii += c
        else:
            # 非ASCII字符，需要编码
            if current_ascii:
                flush_ascii()
            current_encoded += c
    
    # 处理剩余的ASCII字符和编码字符
    if current_encoded:
        flush_encoded()
    if current_ascii:
        flush_ascii()
    
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
    expected_enc = "&Ti1lhw-other_test"
    encoded = encode_modified_utf7(original)
    decoded_back = decode_modified_utf7(encoded)
    print(f"\n2. 编码测试:")
    print(f"   原始: {original!r}")
    print(f"   编码: {encoded!r}")
    print(f"   期望: {expected_enc!r}")
    print(f"   解码回: {decoded_back!r}")
    print(f"   编码匹配: {'✓ 成功' if encoded == expected_enc else '✗ 失败'}")
    print(f"   解码匹配: {'✓ 成功' if decoded_back == original else '✗ 失败'}")
    
    # 测试更多示例
    print(f"\n3. 更多示例测试:")
    test_cases = [
        ("&Ti1lhw-other_test", "中文other_test"),
        ("&-", "&"),
        ("INBOX", "INBOX"),
    ]
    
    all_passed = True
    for i, (input_str, expected) in enumerate(test_cases, 1):
        result = decode_modified_utf7(input_str)
        status = "✓ 成功" if result == expected else "✗ 失败"
        if result != expected:
            all_passed = False
        print(f"   {i:2d}. {input_str!r} -> {result!r} {status}")
    
    print(f"\n   总体结果: {'✓ 全部通过' if all_passed else '✗ 部分失败'}")
    
    # 测试编码解码循环
    print(f"\n4. 编码解码循环测试:")
    test_strs = ["中文", "中文test", "test中文", "中文other_test", "中文文件夹"]
    for test_str in test_strs:
        enc = encode_modified_utf7(test_str)
        dec = decode_modified_utf7(enc)
        status = "✓ 成功" if dec == test_str else "✗ 失败"
        print(f"   {test_str!r} -> {enc!r} -> {dec!r} {status}")
    print()
    print("=== 测试完成 ===")