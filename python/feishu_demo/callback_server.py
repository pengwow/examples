from flask import Flask, request, jsonify
import logging
import hashlib
import base64
import hmac

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用实例
app = Flask(__name__)

# 配置信息（建议从环境变量或配置文件中读取）
# 这里的配置值需要根据实际情况修改
CONFIG = {
    # 飞书开放平台应用的Verification Token
    'VERIFICATION_TOKEN': 'AcRFMTCqTLvW6iFl6MVGpfs6uSE8WQQh',
    # 飞书开放平台应用的Encrypt Key（如果开启了加密）
    'ENCRYPT_KEY': 'your_encrypt_key_here',
    # 是否开启签名验证
    'ENABLE_SIGNATURE_VERIFICATION': False
}


def verify_signature(request_data, headers):
    """
    验证请求签名，确保请求来自飞书服务器
    :param request_data: 请求体数据
    :param headers: 请求头
    :return: bool 是否验证通过
    """
    if not CONFIG['ENABLE_SIGNATURE_VERIFICATION']:
        return True
    
    try:
        # 获取请求头中的签名信息
        timestamp = headers.get('X-Lark-Request-Timestamp')
        nonce = headers.get('X-Lark-Request-Nonce')
        signature = headers.get('X-Lark-Signature')
        
        if not all([timestamp, nonce, signature]):
            logger.warning("Missing signature headers")
            return False
        
        # 构建签名字符串
        sign_str = f"{timestamp}|{nonce}|{request_data.decode('utf-8')}"
        
        # 使用HMAC-SHA256算法计算签名
        h = hmac.new(CONFIG['ENCRYPT_KEY'].encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256)
        computed_signature = base64.b64encode(h.digest()).decode('utf-8')
        
        # 验证签名是否匹配
        return signature == computed_signature
    except Exception as e:
        logger.error(f"Error verifying signature: {e}", exc_info=True)
        return False


def decrypt_data(encrypted_data):
    """
    解密飞书推送的加密数据
    :param encrypted_data: 加密的数据
    :return: dict 解密后的数据
    """
    # 这里简化处理，实际需要根据飞书开放平台的加密算法进行解密
    # 完整实现需要使用ENCRYPT_KEY进行AES解密
    return encrypted_data


# 定义回调路由，只接受POST请求
@app.route('/callback', methods=['POST'])
def callback():
    try:
        # 获取原始请求数据
        request_data = request.get_data()
        
        # 解析JSON请求数据
        data: dict = request.get_json()
        logger.info(f"Received callback request: {data}")
        action_tag = data.get('action', {}).get('tag')
        action_name = data.get('action', {}).get('name')
        action_from_value = data.get('action', {}).get('form_value', {})
        if action_tag == 'button':
            if action_name == 'email_submit_approval':
                input_value = action_from_value.get('notes_input', {})
                if input_value:
                    logger.info(f"Email submitted: {input_value}")
                else:
                    logger.warning("Email field is empty")
            elif action_name == 'email_reset_pwd_submit_button':
                input_value = action_from_value.get('confirm_password', '')
                if input_value:
                    logger.info(f"Email reset password submitted: {input_value}")
                else:
                    logger.warning("Email reset password field is empty")
            logger.info("Confirm button clicked")

        if action_tag == 'input':
            print(data['action']['input_value'])
            return jsonify({'code': 200, 'msg': 'ok'})

        # 获取请求类型
        request_type = data.get('type')
        
        # 处理URL验证请求
        if request_type == 'url_verification':
            # 验证token是否匹配
            if data.get('token') != CONFIG['VERIFICATION_TOKEN']:
                logger.warning(f"Invalid verification token: {data.get('token')}")
                return jsonify({'code': 401, 'msg': 'invalid token'})
            
            challenge = data.get('challenge')
            logger.info(f"URL verification request, challenge: {challenge}")
            # 1秒内返回challenge值
            return jsonify({'challenge': challenge})
        
        # 处理事件回调请求
        elif request_type == 'event_callback':
            # 验证token是否匹配
            if data.get('token') != CONFIG['VERIFICATION_TOKEN']:
                logger.warning(f"Invalid event token: {data.get('token')}")
                return jsonify({'code': 401, 'msg': 'invalid token'})
            
            # 获取事件类型
            event = data.get('event', {})
            event_type = event.get('type')
            logger.info(f"Event callback received, type: {event_type}")
            
            # 根据不同的事件类型进行详细处理
            if event_type == 'message':
                # 处理消息事件
                message = event.get('message', {})
                message_type = message.get('type')
                sender = event.get('sender', {})
                
                logger.info(f"Message event details: type={message_type}, sender={sender}, content={message.get('content')}")
                
                # 根据消息类型进行不同处理
                if message_type == 'text':
                    # 处理文本消息
                    pass
                elif message_type == 'image':
                    # 处理图片消息
                    pass
                elif message_type == 'post':
                    # 处理富文本消息
                    pass
            
            elif event_type == 'interactive':
                # 处理交互事件（如点击卡片按钮）
                action = event.get('action', {})
                action_type = action.get('type')
                value = action.get('value', {})
                trigger_id = event.get('trigger_id')
                open_id = event.get('open_id')
                
                logger.info(f"Interactive event details: type={action_type}, value={value}, open_id={open_id}")
                
                # 根据交互类型进行不同处理
                if action_type == 'button':
                    # 处理按钮点击事件
                    button_key = value.get('key')
                    logger.info(f"Button clicked: {button_key}")
                    # 可以根据button_key执行不同的业务逻辑
                elif action_type == 'select':
                    # 处理选择器事件
                    select_value = value.get('value')
                    logger.info(f"Select value: {select_value}")
            
            elif event_type == 'message_read':
                # 处理消息已读事件
                reader = event.get('reader', {})
                message_id = event.get('message_id')
                logger.info(f"Message read event: reader={reader}, message_id={message_id}")
            
            elif event_type == 'user_add':
                # 处理用户加入事件
                user = event.get('user', {})
                logger.info(f"User add event: user={user}")
            
            elif event_type == 'user_leave':
                # 处理用户离开事件
                user = event.get('user', {})
                logger.info(f"User leave event: user={user}")
            
            # 可以根据需要添加更多事件类型的处理
            else:
                logger.info(f"Unhandled event type: {event_type}")
            
            # 立即返回响应，反馈用户操作
            return jsonify({'code': 0, 'msg': 'success'})
        
        # 处理加密回调请求（如果开启了加密）
        elif request_type == 'encrypt':
            # 验证token是否匹配
            if data.get('token') != CONFIG['VERIFICATION_TOKEN']:
                logger.warning(f"Invalid encrypt token: {data.get('token')}")
                return jsonify({'code': 401, 'msg': 'invalid token'})
            
            # 解密数据
            encrypted_data = data.get('encrypt')
            decrypted_data = decrypt_data(encrypted_data)
            
            # 递归处理解密后的数据
            # 注意：这里需要根据实际解密后的数据结构进行调整
            logger.info(f"Encrypted request received and decrypted")
            return jsonify({'code': 0, 'msg': 'success'})
        
        # 处理其他未知类型的请求
        else:
            logger.warning(f"Unknown request type: {request_type}")
            return jsonify({'code': 0, 'msg': 'success'})
            
    except Exception as e:
        logger.error(f"Error processing callback: {e}", exc_info=True)
        # 即使发生异常，也要返回成功响应，避免飞书服务器重复推送
        return jsonify({'code': 0, 'msg': 'success'})


# 健康检查路由（可选）
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'feishu-callback-server'})


# 启动服务器
if __name__ == '__main__':
    # 配置服务器监听地址和端口
    # 0.0.0.0表示监听所有网络接口
    app.run(host='0.0.0.0', port=48080, debug=True)
