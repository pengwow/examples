from flask import Flask, request, abort
import hmac
import hashlib
import subprocess
import os

app = Flask(__name__)
SECRET = "your_webhook_secret_123"  # 与 GitHub 配置中的 Secret 一致
DEPLOY_PATH = "/var/www/qc-site"  # 代码部署目录
REPO_URL = "git@github.com:your-username/your-repo.git"  # 仓库 SSH 地址（用部署密钥拉取）

def verify_signature(payload, signature):
    """验证 GitHub 请求签名"""
    mac = hmac.new(SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. 获取请求头和载荷
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.data  # 原始请求体（bytes）

    # 2. 验证签名（防伪造请求）
    if not verify_signature(payload, signature):
        abort(403, "Invalid signature")

    # 3. 解析事件类型（可选，这里仅处理 push 事件）
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return "Ignored event", 200

    # 4. 执行部署命令（切换到部署用户执行）
    try:
        # 拉取最新代码（用 deployer 用户权限）
        subprocess.run(
            ["sudo", "-u", "deployer", "git", "-C", DEPLOY_PATH, "pull", "origin", "main"],
            check=True,
            capture_output=True,
            text=True
        )
        # 可选：重启服务（如 Node.js/PM2、Python/uWSGI）
        subprocess.run(["sudo", "systemctl", "restart", "myapp.service"], check=True)
        return "Deployment succeeded", 200
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e.stderr}")
        abort(500, f"Deployment error: {e.stderr}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 监听 5000 端口（生产环境建议用 gunicorn + nginx）