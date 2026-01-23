#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python2/3兼容的HTTP服务器，功能与Go版本相同
提供/health和/processlist端点
"""

# 兼容Python2和Python3
try:
    import BaseHTTPServer
    import urlparse
    PY2 = True
except ImportError:
    import http.server as BaseHTTPServer
    import urllib.parse as urlparse
    PY2 = False

import json
import os
import subprocess
import time

# 数据目录
DATA_DIR = "/Users/liupeng/workspace/examples/go/slow_http"

class CustomHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def _set_headers(self, content_type="application/json"):
        """设置响应头"""
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == "/health":
            self.handle_health()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == "/processlist":
            self.handle_processlist()
        else:
            self.send_error(404, "Not Found")
    
    def handle_health(self):
        """处理/health端点"""
        self._set_headers()
        response = {"status": "ok"}
        response_data = json.dumps(response)
        if not PY2:
            response_data = response_data.encode('utf-8')
        self.wfile.write(response_data)
    
    def handle_processlist(self):
        """处理/processlist端点"""
        self._set_headers()
        
        # 读取请求体
        if PY2:
            content_length = int(self.headers.getheader('content-length', 0))
        else:
            content_length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_length)
        
        try:
            # 解析JSON参数
            params = json.loads(body)
            
            # 验证参数格式
            if not isinstance(params, list):
                self.send_error_response("Invalid JSON array: Expected list")
                return
            
            # 验证每个参数
            for i, config in enumerate(params):
                if not isinstance(config, dict):
                    self.send_error_response("Invalid JSON array: Each item must be an object")
                    return
                
                if not config.get("url") or not config.get("database"):
                    self.send_error_response("Missing required fields in record %d" % (i + 1))
                    return
                
                if not self.is_valid_port(config.get("port")):
                    self.send_error_response("Invalid port number in record %d" % (i + 1))
                    return
            
            # 生成文件名
            timestamp = str(int(time.time() * 1000000000))  # 纳秒时间戳
            filename = os.path.join(DATA_DIR, timestamp + ".json")
            
            # 写入文件
            try:
                # 确保目录存在
                if not os.path.exists(DATA_DIR):
                    os.makedirs(DATA_DIR)
                
                with open(filename, "w") as f:
                    json.dump(params, f)
            except Exception as e:
                self.send_error_response("Failed to write file: %s" % str(e))
                return
            
            # 执行Python脚本
            try:
                cmd = ["python", "/Users/liupeng/workspace/examples/go/processlist.py", filename]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate()
                
                if process.returncode != 0:
                    self.send_error_response("Python script execution failed: %s" % error)
                    return
                
                # 解析脚本输出
                try:
                    python_result = json.loads(output)
                except Exception as e:
                    self.send_error_response("Failed to parse Python output: %s" % str(e))
                    return
                
                # 检查是否有错误
                has_error, error_msg = self.has_error_in_python_result(python_result)
                if has_error:
                    self.send_error_response("Python script returned error: %s" % error_msg)
                    return
                
                # 检查是否有警告
                has_warn, warn_msg = self.has_warn_in_python_result(python_result)
                if has_warn:
                    self.send_warning_response("Python script get slowlog warnning: %s" % warn_msg)
                    # 清理文件
                    if os.path.exists(filename):
                        os.remove(filename)
                    return
                
                # 返回成功响应
                success_response = {
                    "existSlowSql": True,
                    "retCode": 0,
                    "retMsg": "success",
                    "rootCauseSlowSqlList": python_result
                }
                response_data = json.dumps(success_response)
                if not PY2:
                    response_data = response_data.encode('utf-8')
                self.wfile.write(response_data)
                
                # 清理文件
                if os.path.exists(filename):
                    os.remove(filename)
                    
            except Exception as e:
                self.send_error_response("Python script execution failed: %s" % str(e))
                return
                
        except Exception as e:
            self.send_error_response("Failed to read request body: %s" % str(e))
            return
    
    def send_error_response(self, message):
        """发送错误响应"""
        error_response = {
            "existSlowSql": False,
            "retCode": 999999,
            "retMsg": message
        }
        response_data = json.dumps(error_response)
        if not PY2:
            response_data = response_data.encode('utf-8')
        self.wfile.write(response_data)
    
    def send_warning_response(self, message):
        """发送警告响应"""
        warning_response = {
            "existSlowSql": False,
            "retCode": 0,
            "retMsg": message
        }
        response_data = json.dumps(warning_response)
        if not PY2:
            response_data = response_data.encode('utf-8')
        self.wfile.write(response_data)
    
    def is_valid_port(self, port):
        """验证端口号"""
        if port is None:
            return False
        
        if isinstance(port, (int, float)):
            return 0 < port <= 65535
        
        if isinstance(port, (str, unicode)) if PY2 else isinstance(port, str):
            try:
                p = int(port)
                return 0 < p <= 65535
            except ValueError:
                return False
        
        return False
    
    def has_error_in_python_result(self, result):
        """检查Python结果是否包含错误"""
        if isinstance(result, dict):
            if "error" in result:
                error_msg = result["error"]
                if isinstance(error_msg, (str, unicode)) if PY2 else isinstance(error_msg, str):
                    return True, error_msg
                return True, "Unknown error occurred"
        
        elif isinstance(result, list):
            for i, item in enumerate(result):
                if isinstance(item, dict):
                    if "error" in item:
                        error_msg = item["error"]
                        if isinstance(error_msg, (str, unicode)) if PY2 else isinstance(error_msg, str):
                            return True, "Error in item %d: %s" % (i, error_msg)
                        return True, "Error in item %d: Unknown error" % i
        
        return False, ""
    
    def has_warn_in_python_result(self, result):
        """检查Python结果是否包含警告"""
        if isinstance(result, dict):
            if "warnn" in result:
                warn_msg = result["warnn"]
                if isinstance(warn_msg, (str, unicode)) if PY2 else isinstance(warn_msg, str):
                    return True, warn_msg
                return True, "no slow log!"
        
        return False, ""

def run_server(port=8080):
    """启动HTTP服务器"""
    server_address = ('', port)
    httpd = BaseHTTPServer.HTTPServer(server_address, CustomHTTPRequestHandler)
    print("Starting server on port %d..." % port)
    print("Health check: http://localhost:%d/health" % port)
    print("Processlist endpoint: POST http://localhost:%d/processlist" % port)
    httpd.serve_forever()

if __name__ == "__main__":
    # run_server()
    import time
    print(int(time.time() * 1000000000))
