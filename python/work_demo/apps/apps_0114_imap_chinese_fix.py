#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何使用 apps_0114_email.py 解决中文邮箱文件夹选择报错问题

问题：当尝试选择中文邮箱文件夹时，imaplib 会报错
解决方案：
1. 从服务器获取文件夹列表时，将编码后的文件夹名解码为中文
2. 选择文件夹前，将中文文件夹名编码为 IMAP 修改版 UTF-7
"""

from apps_0114_email import decode_modified_utf7, encode_modified_utf7


def solve_chinese_folder_issue():
    """
    解决中文邮箱文件夹选择报错问题的核心方法
    """
    print("=== 解决中文邮箱文件夹选择报错问题 ===")
    
    # ------------------------------
    # 场景1：从服务器获取文件夹列表
    # ------------------------------
    print("\n1. 从服务器获取文件夹列表时的处理：")
    print("   实际代码：")
    print("   import imaplib")
    print("   from apps_0114_email import decode_modified_utf7")
    print()
    print("   # 连接到IMAP服务器")
    print("   # imap_server = imaplib.IMAP4_SSL('imap.example.com')")
    print("   # imap_server.login('username', 'password')")
    print()
    print("   # 获取文件夹列表")
    print("   # status, folders = imap_server.list()")
    print()
    print("   # 模拟从服务器获取的编码文件夹列表")
    print("   encoded_folders = [")
    print("       b'INBOX',")
    print("       b'&Ti1lhw-other_test',  # 编码后的 '中文other_test'")
    print("       b'&U,BTFw-',           # 编码后的 '中'")
    print("   ]")
    print()
    print("   # 解码为中文显示")
    print("   for folder in encoded_folders:")
    print("       folder_str = folder.decode()")
    print("       chinese_name = decode_modified_utf7(folder_str)")
    print("       print(f'文件夹: {chinese_name}')")
    
    # ------------------------------
    # 场景2：选择中文文件夹时的处理
    # ------------------------------
    print("\n2. 选择中文文件夹时的处理：")
    print("   实际代码：")
    print("   import imaplib")
    print("   from apps_0114_email import encode_modified_utf7")
    print()
    print("   # 连接到IMAP服务器")
    print("   # imap_server = imaplib.IMAP4_SSL('imap.example.com')")
    print("   # imap_server.login('username', 'password')")
    print()
    print("   # 用户选择的中文文件夹名")
    print("   chinese_folder = '中文other_test'")
    print()
    print("   # 编码为IMAP修改版UTF-7")
    print("   encoded_folder = encode_modified_utf7(chinese_folder)")
    print()
    print("   # 选择文件夹 - 不会报错")
    print("   # status, response = imap_server.select(encoded_folder)")
    
    # ------------------------------
    # 核心函数使用示例
    # ------------------------------
    print("\n3. 核心函数使用示例：")
    
    # 示例1：解码函数
    print("   # 解码示例：")
    encoded = "&Ti1lhw-other_test"
    decoded = decode_modified_utf7(encoded)
    print(f"   decode_modified_utf7('{encoded}') = '{decoded}'")
    
    # 示例2：编码函数
    print("   # 编码示例：")
    chinese = "中文other_test"
    encoded = encode_modified_utf7(chinese)
    print(f"   encode_modified_utf7('{chinese}') = '{encoded}'")
    
    # 示例3：完整流程
    print("   # 完整流程示例：")
    original = "中文收件箱"
    encoded = encode_modified_utf7(original)
    decoded_back = decode_modified_utf7(encoded)
    print(f"   原始: '{original}'")
    print(f"   编码: '{encoded}'")
    print(f"   解码: '{decoded_back}'")
    print(f"   结果: {'成功' if original == decoded_back else '失败'}")
    
    # ------------------------------
    # 总结
    # ------------------------------
    print("\n4. 总结：")
    print("   - 从服务器获取文件夹名时，使用 decode_modified_utf7() 解码为中文")
    print("   - 向服务器发送文件夹名时，使用 encode_modified_utf7() 编码为 IMAP 修改版 UTF-7")
    print("   - 这样可以完全避免中文文件夹选择报错")
    print()
    print("=== 解决方案结束 ===")


if __name__ == "__main__":
    solve_chinese_folder_issue()