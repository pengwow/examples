import hmac
import hashlib
import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timezone  # 修改导入
from flask import Flask, request, jsonify, abort

# ===== 配置区域 =====
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'your_default_secret_123')
DEPLOY_PATH = os.environ.get('DEPLOY_PATH', '/var/www/myapp')
REPO_BRANCH = os.environ.get('DEPLOY_BRANCH', 'main')
ALLOWED_EVENTS = os.environ.get('ALLOWED_EVENTS', 'push').split(',')
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/webhook_deploy.log')
# ===================

# 初始化日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GitHubWebhookHandler')

app = Flask(__name__)

def verify_signature(payload, signature):
    """更安全的签名验证函数"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    received_sig = signature.split('=')[1]
    computed_sig = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_sig, computed_sig)

def run_deployment(event_data):
    """执行部署任务（在单独线程中运行）"""
    start_time = time.time()
    repo_name = event_data['repository']['full_name']
    ref = event_data.get('ref', '')
    branch = ref.split('/')[-1] if '/' in ref else ref
    
    logger.info(f"开始部署: {repo_name}@{branch}")
    
    try:
        # 1. 拉取最新代码
        logger.info("拉取最新代码...")
        fetch_result = subprocess.run(
            ["git", "-C", DEPLOY_PATH, "fetch", "--all"],
            capture_output=True,
            text=True,
            check=True,
            timeout=120  # 添加超时
        )
        logger.debug(f"Fetch 输出: {fetch_result.stdout[:200]}...")  # 截断长输出
        
        reset_result = subprocess.run(
            ["git", "-C", DEPLOY_PATH, "reset", "--hard", f"origin/{REPO_BRANCH}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.debug(f"Reset 输出: {reset_result.stdout[:200]}...")
        
        # 2. 安装依赖（根据项目类型）
        requirements_path = os.path.join(DEPLOY_PATH, 'requirements.txt')
        package_path = os.path.join(DEPLOY_PATH, 'package.json')
        
        if os.path.exists(requirements_path):
            logger.info("安装Python依赖...")
            subprocess.run(
                ["pip", "install", "-r", requirements_path],
                cwd=DEPLOY_PATH,
                check=True,
                timeout=300
            )
        elif os.path.exists(package_path):
            logger.info("安装Node.js依赖...")
            subprocess.run(
                ["npm", "install", "--production"],
                cwd=DEPLOY_PATH,
                check=True,
                timeout=300
            )
        
        # 3. 执行自定义部署命令
        custom_cmd = os.environ.get('CUSTOM_DEPLOY_CMD')
        if custom_cmd:
            logger.info(f"执行自定义命令: {custom_cmd}")
            subprocess.run(
                custom_cmd,
                shell=True,
                cwd=DEPLOY_PATH,
                check=True,
                timeout=600
            )
        
        # 4. 重启服务
        service_name = os.environ.get('SERVICE_NAME')
        if service_name:
            logger.info(f"重启服务: {service_name}")
            subprocess.run(
                ["sudo", "systemctl", "restart", service_name],
                check=True,
                timeout=30
            )
        
        duration = time.time() - start_time
        logger.info(f"部署成功! 耗时: {duration:.2f}秒")
        return True, "部署成功"
    
    except subprocess.CalledProcessError as e:
        error_msg = f"命令执行失败: {e.cmd}\n错误输出: {e.stderr.strip()}"
        logger.error(error_msg)
        return False, error_msg
    except subprocess.TimeoutExpired as e:
        error_msg = f"命令执行超时: {e.cmd}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"部署过程中出错: {str(e)}"
        logger.exception(error_msg)
        return False, error_msg

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """处理GitHub Webhook请求的主函数"""
    # 1. 获取请求头
    event_type = request.headers.get('X-GitHub-Event', 'ping')
    signature = request.headers.get('X-Hub-Signature-256', '')
    delivery_id = request.headers.get('X-GitHub-Delivery', 'unknown')
    
    # 2. 记录请求信息
    logger.info(f"收到Webhook请求: Event={event_type}, DeliveryID={delivery_id}")
    
    # 3. 验证事件类型
    if event_type not in ALLOWED_EVENTS:
        logger.warning(f"忽略不支持的事件类型: {event_type}")
        return jsonify({
            "status": "ignored",
            "reason": f"事件类型 {event_type} 未启用"
        }), 200
    
    # 4. 获取并验证签名
    payload = request.data
    if not verify_signature(payload, signature):
        logger.error(f"签名验证失败! DeliveryID={delivery_id}")
        abort(403, description="无效的签名")
    
    # 5. 解析有效载荷
    try:
        payload_data = request.get_json()
    except Exception as e:
        logger.error(f"JSON解析失败: {str(e)}")
        abort(400, description="无效的JSON载荷")
    
    # 6. 处理ping事件
    if event_type == 'ping':
        logger.info("处理ping事件")
        return jsonify({
            "status": "pong",
            "zen": payload_data.get('zen', ''),
            "hook_id": payload_data.get('hook_id', ''),
            "timestamp": datetime.now(timezone.utc).isoformat()  # 修复弃用警告
        }), 200
    
    # 7. 处理push事件
    if event_type == 'push':
        ref = payload_data.get('ref', '')
        branch = ref.split('/')[-1] if '/' in ref else ref
        
        # 检查分支
        if branch != REPO_BRANCH:
            logger.info(f"忽略非{REPO_BRANCH}分支的推送: {branch}")
            return jsonify({
                "status": "ignored",
                "reason": f"仅部署{REPO_BRANCH}分支，当前分支: {branch}"
            }), 200
        
        # 8. 异步执行部署
        thread = threading.Thread(
            target=run_deployment,
            args=(payload_data,),
            daemon=True
        )
        thread.start()
        
        logger.info(f"已启动部署线程: ThreadID={thread.ident}")
        return jsonify({
            "status": "accepted",
            "message": f"开始部署{branch}分支",
            "timestamp": datetime.now(timezone.utc).isoformat()  # 修复弃用警告
        }), 202
    
    # 9. 处理其他事件类型
    logger.info(f"处理事件: {event_type}")
    return jsonify({
        "status": "unhandled",
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat()  # 修复弃用警告
    }), 200

@app.errorhandler(400)
def bad_request(error):
    logger.error(f"错误请求: {error.description}")
    return jsonify({"error": error.description}), 400

@app.errorhandler(403)
def forbidden(error):
    logger.error(f"禁止访问: {error.description}")
    return jsonify({"error": error.description}), 403

@app.errorhandler(404)
def not_found(error):
    logger.error(f"资源未找到: {request.url}")
    return jsonify({"error": "资源未找到"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("服务器内部错误")
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    # 生产环境应使用Gunicorn+Nginx
    app.run(host='0.0.0.0', port=8000, debug=False)