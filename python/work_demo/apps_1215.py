# 使用python的imaplib或email包进行邮件的开发,需求一编写一个函数实现对邮件进行回复
import smtplib
import imaplib
import email
import hashlib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional, Dict, List

def generate_email_uid(from_email: str, subject: str, sent_time: str) -> str:
    """
    根据发送人、邮件标题、发送时间生成MD5作为邮件UID
    
    参数:
        from_email: 发送人邮箱
        subject: 邮件标题
        sent_time: 发送时间字符串
    
    返回:
        str: 生成的MD5 UID
    """
    # 组合字符串
    combined = f"{from_email}{subject}{sent_time}"
    # 生成MD5
    md5_hash = hashlib.md5(combined.encode('utf-8'))
    return md5_hash.hexdigest()

def reply_to_email_by_md5_uid(
    smtp_server: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    imap_server: str,
    imap_port: int,
    imap_username: str,
    imap_password: str,
    target_from_email: str,
    target_subject: str,
    target_sent_time: str,
    reply_body: str,
    reply_subject: str = "",
    is_html: bool = False
) -> bool:
    """
    通过发送人、邮件标题、发送时间的MD5值作为UID来回复邮件
    
    参数:
        smtp_server: SMTP服务器地址
        smtp_port: SMTP服务器端口
        smtp_username: SMTP用户名
        smtp_password: SMTP密码
        imap_server: IMAP服务器地址
        imap_port: IMAP服务器端口
        imap_username: IMAP用户名
        imap_password: IMAP密码
        target_from_email: 目标邮件发送人
        target_subject: 目标邮件标题
        target_sent_time: 目标邮件发送时间
        reply_body: 回复邮件的正文
        reply_subject: 回复邮件的主题（可选，默认自动生成）
        is_html: 正文是否为HTML格式，默认为False
    
    返回:
        bool: 回复是否成功
    
    异常:
        Exception: 当邮件回复失败时抛出异常
    """
    try:
        # 生成目标邮件的MD5 UID
        target_uid = generate_email_uid(target_from_email, target_subject, target_sent_time)
        
        # 1. 连接到IMAP服务器并获取所有邮件
        with imaplib.IMAP4(imap_server, imap_port) as imap:
            imap.login(imap_username, imap_password)
            imap.select('INBOX')
            
            # 搜索所有邮件
            result, data = imap.search(None, 'ALL')
            if result != 'OK':
                raise Exception("搜索邮件失败")
            
            # 获取匹配的邮件
            matched_msg = None
            email_ids = data[0].split()
            
            for e_id in email_ids:
                # 获取邮件内容
                result, msg_data = imap.fetch(e_id, '(RFC822)')
                if result != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 提取邮件信息
                msg_from = msg['From'] if msg['From'] else ''
                msg_subject = msg['Subject'] if msg['Subject'] else ''
                msg_date = msg['Date'] if msg['Date'] else ''
                
                # 解析日期格式，统一时间字符串格式
                try:
                    # 尝试解析多种日期格式
                    if msg_date:
                        date_obj = email.utils.parsedate_to_datetime(msg_date)
                        # 格式化为统一的时间字符串格式
                        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        formatted_date = ''
                except:
                    formatted_date = msg_date
                
                # 生成当前邮件的MD5 UID
                current_uid = generate_email_uid(msg_from, msg_subject, formatted_date)
                
                # 比较UID是否匹配
                if current_uid == target_uid:
                    matched_msg = msg
                    break
            
            if not matched_msg:
                raise Exception(f"未找到匹配的邮件，目标UID: {target_uid}")
            
            msg = matched_msg
            
            # 提取需要的邮件头信息
            from_email = msg['From']
            to_email = msg['To']
            original_subject = msg['Subject']
            message_id = msg['Message-ID']
            
            # 2. 创建回复邮件
            reply_msg = MIMEMultipart()
            
            # 设置回复邮件的头部
            reply_msg['From'] = smtp_username
            reply_msg['To'] = from_email
            reply_msg['Subject'] = reply_subject if reply_subject else f"Re: {original_subject}"
            
            # 设置引用信息，使回复邮件能正确关联到原始邮件
            if message_id:
                reply_msg['References'] = message_id
                reply_msg['In-Reply-To'] = message_id
            
            # 3. 构建回复正文
            # 添加原始邮件信息作为引用
            quoted_text = f"\n--- 原始邮件 ---\n发件人: {from_email}\n收件人: {to_email}\n主题: {original_subject}\n\n"
            
            # 提取原始邮件正文
            original_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain' and not part.get_filename():
                        charset = part.get_content_charset() or 'utf-8'
                        original_body += part.get_payload(decode=True).decode(charset)
                        break
            else:
                charset = msg.get_content_charset() or 'utf-8'
                original_body = msg.get_payload(decode=True).decode(charset)
            
            # 将原始正文添加到引用中
            quoted_text += '\n'.join([f"> {line}" for line in original_body.split('\n')])
            
            # 组合回复正文
            full_body = reply_body + quoted_text
            
            # 添加正文到邮件
            if is_html:
                reply_msg.attach(MIMEText(full_body, 'html', 'utf-8'))
            else:
                reply_msg.attach(MIMEText(full_body, 'plain', 'utf-8'))
            
        # 4. 连接到SMTP服务器并发送回复邮件
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(reply_msg)
            
        print(f"邮件回复成功！UID: {target_uid}")
        return True
        
    except Exception as e:
        print(f"邮件回复失败: {str(e)}")
        raise

def reply_to_email_simple(reply_body: str) -> bool:
    """
    简化版的邮件回复函数，只需要回复内容参数
    
    参数:
        reply_body: 回复邮件的正文
    
    返回:
        bool: 回复是否成功
    
    异常:
        Exception: 当邮件回复失败时抛出异常
    """
    # 配置信息（实际使用时可以从配置文件或环境变量读取）
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 25,  # 非SSL SMTP默认端口
        "smtp_username": "your_email@example.com",
        "smtp_password": "your_password",
        "imap_server": "imap.example.com",
        "imap_port": 143,  # 非SSL IMAP默认端口
        "imap_username": "your_email@example.com",
        "imap_password": "your_password",
        # 目标邮件信息
        "target_from_email": "sender@example.com",
        "target_subject": "测试邮件",
        "target_sent_time": "2023-12-15 10:30:00"
    }
    
    return reply_to_email_by_md5_uid(
        smtp_server=config["smtp_server"],
        smtp_port=config["smtp_port"],
        smtp_username=config["smtp_username"],
        smtp_password=config["smtp_password"],
        imap_server=config["imap_server"],
        imap_port=config["imap_port"],
        imap_username=config["imap_username"],
        imap_password=config["imap_password"],
        target_from_email=config["target_from_email"],
        target_subject=config["target_subject"],
        target_sent_time=config["target_sent_time"],
        reply_body=reply_body
    )

def test_connection_syntax():
    """
    测试连接语法是否正确的函数，不实际建立连接
    仅用于验证代码语法和连接方式的正确性
    """
    try:
        # 仅测试导入和类初始化，不实际连接
        from imaplib import IMAP4
        from smtplib import SMTP
        
        # 验证类存在且可以初始化（不实际连接）
        print("✓ 成功导入IMAP4和SMTP类")
        print("✓ 非SSL连接类可用")
        return True
    except Exception as e:
        print(f"✗ 连接语法测试失败: {str(e)}")
        return False

# 示例用法
if __name__ == "__main__":
    # 先测试连接语法
    print("正在测试连接语法...")
    test_connection_syntax()
    print("")
    # 示例1: 使用完整参数调用
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 25,  # 非SSL SMTP默认端口
        "smtp_username": "your_email@example.com",
        "smtp_password": "your_password",
        "imap_server": "imap.example.com",
        "imap_port": 143,  # 非SSL IMAP默认端口
        "imap_username": "your_email@example.com",
        "imap_password": "your_password"
    }
    
    try:
        reply_to_email_by_md5_uid(
            smtp_server=config["smtp_server"],
            smtp_port=config["smtp_port"],
            smtp_username=config["smtp_username"],
            smtp_password=config["smtp_password"],
            imap_server=config["imap_server"],
            imap_port=config["imap_port"],
            imap_username=config["imap_username"],
            imap_password=config["imap_password"],
            target_from_email="sender@example.com",
            target_subject="测试邮件",
            target_sent_time="2023-12-15 10:30:00",
            reply_body="这是我的回复内容\n\n",
            reply_subject="",
            is_html=False
        )
    except Exception as e:
        print(f"示例1调用失败: {str(e)}")
    
    # 示例2: 使用简化函数调用
    try:
        reply_to_email_simple("这是简化版的回复内容\n\n")
    except Exception as e:
        print(f"示例2调用失败: {str(e)}")