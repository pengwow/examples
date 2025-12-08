import imaplib
import email
from email.header import decode_header

def parse_email(raw_email: bytes) -> dict:
    """修正后的邮件解析函数"""
    msg = email.message_from_bytes(raw_email)
    
    # 解析主题（正确处理字符集）
    subject, encoding = decode_header(msg['Subject'])[0]
    if isinstance(subject, bytes):
        try:
            subject = subject.decode(encoding or 'utf-8', errors='replace')
        except (TypeError, LookupError):
            subject = subject.decode('utf-8', errors='replace')  # 强制使用utf-8
    
    # 解析发件人
    from_ = email.utils.parseaddr(msg['From'])[1]
    
    # 解析正文和附件（递归处理多部分内容）
    body = []
    html_body = []
    attachments = []
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = part.get('Content-Disposition', '')
        
        # 跳过multipart容器部分
        if part.get_content_maintype() == 'multipart':
            continue
        
        # 处理纯文本正文
        if content_type == 'text/plain' and 'attachment' not in content_disposition:
            charset = part.get_content_charset() or 'utf-8'
            try:
                payload = part.get_payload(decode=True).decode(charset, errors='replace')
            except (UnicodeDecodeError, AttributeError):
                payload = part.get_payload(decode=True).decode('utf-8', errors='replace')
            body.append(payload)
        
        # 处理HTML正文
        elif content_type == 'text/html' and 'attachment' not in content_disposition:
            charset = part.get_content_charset() or 'utf-8'
            try:
                payload = part.get_payload(decode=True).decode(charset, errors='replace')
            except (UnicodeDecodeError, AttributeError):
                payload = part.get_payload(decode=True).decode('utf-8', errors='replace')
            html_body.append(payload)
        
        # 处理其他文本类型（如RTF、XML等）
        elif content_type.startswith('text/') and 'attachment' not in content_disposition:
            charset = part.get_content_charset() or 'utf-8'
            try:
                payload = part.get_payload(decode=True).decode(charset, errors='replace')
            except (UnicodeDecodeError, AttributeError):
                payload = part.get_payload(decode=True).decode('utf-8', errors='replace')
            body.append(f"[{content_type}] {payload}")
        
        # 处理图片内嵌内容
        elif content_type.startswith('image/') and 'inline' in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode('utf-8', errors='replace')
                # 将内嵌图片作为特殊内容处理
                body.append(f"[内嵌图片: {filename}]")
        
        # 处理附件
        elif 'attachment' in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode('utf-8', errors='replace')
                attachments.append({
                    'filename': filename,
                    'content_type': content_type,
                    'payload': part.get_payload(decode=True)
                })
    
    # 优先使用纯文本正文，如果没有则使用HTML正文（去除HTML标签）
    main_body = '\n'.join(body) if body else ''
    if not main_body and html_body:
        import re
        # 简单去除HTML标签并清理多余换行符
        html_content = '\n'.join(html_body)
        # 去除HTML标签
        main_body = re.sub(r'<[^>]+>', '', html_content)
        # 清理多余换行符：替换多个连续换行符为单个换行符
        main_body = re.sub(r'\n{3,}', '\n\n', main_body)
        # 清理行首和行尾的空白字符
        main_body = re.sub(r'^\s+|\s+$', '', main_body, flags=re.MULTILINE)
        # 清理行内的多余空白字符
        main_body = re.sub(r'\s{2,}', ' ', main_body)
    
    return {
        'subject': subject.strip(),
        'from': from_,
        'body': main_body,
        'html_body': '\n'.join(html_body) if html_body else '',
        'attachments': attachments,
        'content_types': {
            'has_plain_text': len(body) > 0,
            'has_html': len(html_body) > 0,
            'total_parts': len(list(msg.walk())) - 1  # 减去multipart容器
        }
    }

def fetch_emails(days_back=1):
    """
    获取指定天数内的邮件
    
    Args:
        days_back (int): 获取多少天内的邮件，默认1天（昨天到现在）
    """
    # 连接邮箱
    mail = imaplib.IMAP4_SSL('imap.example.com')
    mail.login('user@example.com', 'password')
    mail.select('INBOX')
    
    # 计算指定天数前的日期
    import datetime
    target_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
    search_date = target_date.strftime('%d-%b-%Y')
    
    # 搜索指定日期到现在的邮件
    search_criteria = f'SINCE {search_date}'
    status, messages = mail.search(None, search_criteria)
    if status != 'OK':
        raise Exception("搜索邮件失败")
    
    print(f"搜索条件: {search_criteria}")
    print(f"时间范围: 过去{days_back}天内的邮件")
    print(f"找到邮件数量: {len(messages[0].split()) if messages[0] else 0}")
    
    # 遍历邮件并解析
    for num in messages[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        if status != 'OK':
            continue
        
        raw_email = data[0][1]
        try:
            email_info = parse_email(raw_email)
            print(f"主题: {email_info['subject']}")
            print(f"发件人: {email_info['from']}")
            print("正文预览:", email_info['body'][:200] + '...' if len(email_info['body']) > 200 else '')
            print("内容类型:", f"纯文本: {email_info['content_types']['has_plain_text']}, HTML: {email_info['content_types']['has_html']}, 总部分数: {email_info['content_types']['total_parts']}")
            print("附件数量:", len(email_info['attachments']))
            if email_info['attachments']:
                for i, attachment in enumerate(email_info['attachments']):
                    print(f"  附件{i+1}: {attachment['filename']} ({attachment['content_type']})")
            print('-' * 50)
        except Exception as e:
            print(f"解析邮件 {num} 失败: {str(e)}")

if __name__ == '__main__':
    # 可以通过修改days_back参数来调整搜索的时间范围
    # 例如：fetch_emails(7) 获取最近7天的邮件
    # 例如：fetch_emails(30) 获取最近30天的邮件
    fetch_emails(days_back=1)  # 默认获取最近1天的邮件