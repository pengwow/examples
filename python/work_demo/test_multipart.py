#!/usr/bin/env python3
"""测试multipart邮件结构"""

import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def create_test_email():
    """创建一个包含多种内容的测试邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = '测试邮件 - 多种内容类型'
    msg['From'] = 'test@example.com'
    msg['To'] = 'user@example.com'
    
    # 创建正文容器
    body_container = MIMEMultipart('alternative')
    
    # 添加纯文本正文
    text_part = MIMEText('这是纯文本正文内容', 'plain', 'utf-8')
    body_container.attach(text_part)
    
    # 添加HTML正文
    html_part = MIMEText('<p>这是HTML正文内容</p>', 'html', 'utf-8')
    body_container.attach(html_part)
    
    msg.attach(body_container)
    
    # 添加附件
    pdf_attachment = MIMEApplication(b'PDF file content', _subtype='pdf')
    pdf_attachment.add_header('Content-Disposition', 'attachment', filename='test.pdf')
    msg.attach(pdf_attachment)
    
    return msg

def analyze_email_structure(msg):
    """分析邮件结构"""
    print("=== 邮件结构分析 ===")
    for i, part in enumerate(msg.walk()):
        content_type = part.get_content_type()
        main_type = part.get_content_maintype()
        disposition = part.get('Content-Disposition', '')
        
        print(f"第{i+1}部分:")
        print(f"  内容类型: {content_type}")
        print(f"  主类型: {main_type}")
        print(f"  处置方式: {disposition}")
        
        if main_type == 'multipart':
            print("  → 这是容器部分，跳过处理")
            try:
                payload = part.get_payload()
                print(f"  → 容器包含 {len(payload)} 个子部分")
            except:
                print("  → 无法获取容器payload")
        else:
            print("  → 这是实际内容部分，需要处理")
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    print(f"  → 有效payload长度: {len(payload)} 字节")
                else:
                    print("  → 空payload")
            except Exception as e:
                print(f"  → 处理payload出错: {e}")
        print("-" * 40)

if __name__ == '__main__':
    # 创建测试邮件
    test_msg = create_test_email()
    
    # 分析邮件结构
    analyze_email_structure(test_msg)
    
    # 演示跳过容器的效果
    print("\n=== 跳过容器后的处理 ===")
    body_parts = []
    attachment_parts = []
    
    for part in test_msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue  # 跳过容器
            
        content_type = part.get_content_type()
        disposition = part.get('Content-Disposition', '')
        
        if 'attachment' in disposition:
            attachment_parts.append(content_type)
        elif content_type.startswith('text/'):
            body_parts.append(content_type)
    
    print(f"找到的正文部分: {body_parts}")
    print(f"找到的附件部分: {attachment_parts}")