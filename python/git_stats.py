#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git 代码提交量统计脚本
可按天、周、月三个维度统计指定作者的提交次数和代码增删行数。
支持飞书通知。
"""

import subprocess
import re
import sys
import os
import requests
import json
import time
from datetime import datetime
from collections import defaultdict
import argparse


# --- 飞书API相关代码 --- #
# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_feishu_access_token(app_id, app_secret):
    """
    获取飞书API的access_token
    
    参数:
        app_id (str): 飞书应用的app_id
        app_secret (str): 飞书应用的app_secret
    
    返回:
        str: 有效的access_token
    
    异常:
        requests.exceptions.RequestException: 网络请求异常
        ValueError: 响应数据格式错误或获取token失败
    """
    # 飞书获取access_token的API地址
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"

    # 请求体
    data = {"app_id": app_id, "app_secret": app_secret}

    try:
        logger.info("开始获取飞书access_token")

        # 发送POST请求
        response = requests.post(
            url=url,
            json=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

        # 检查响应状态码
        response.raise_for_status()

        # 解析响应数据
        result = response.json()

        # 检查是否获取成功
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            logger.error(f"获取飞书access_token失败: {error_msg}")
            raise ValueError(f"获取飞书access_token失败: {error_msg}")

        # 获取access_token
        access_token = result.get("tenant_access_token")
        if not access_token:
            logger.error("飞书API响应中没有tenant_access_token字段")
            raise ValueError("飞书API响应中没有tenant_access_token字段")

        # 获取token过期时间（默认7200秒，即2小时）
        expire = result.get("expire", 7200)
        logger.info(f"成功获取飞书access_token，有效期: {expire}秒")

        return access_token

    except requests.exceptions.RequestException as e:
        logger.error(f"获取飞书access_token时网络请求异常: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"获取飞书access_token时数据解析异常: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"获取飞书access_token时发生未知异常: {str(e)}")
        raise


class FeishuAPI:
    """
    飞书API客户端类，包含获取部门信息等功能
    """

    def __init__(self, app_id, app_secret):
        """
        初始化飞书API客户端
        
        参数:
            app_id (str): 飞书应用的app_id
            app_secret (str): 飞书应用的app_secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = None
        self._token_expire_time = 0

    def get_access_token(self, force_refresh=False):
        """
        获取或刷新access_token（带缓存机制）
        
        参数:
            force_refresh (bool): 是否强制刷新token，默认False
        
        返回:
            str: 有效的access_token
        """
        # 检查token是否存在且未过期（提前300秒刷新）
        current_time = time.time()
        if (
            not force_refresh
            and self._access_token
            and current_time < self._token_expire_time - 300
        ):
            logger.info("使用缓存的飞书access_token")
            return self._access_token

        # 获取新token
        self._access_token = get_feishu_access_token(self.app_id, self.app_secret)
        # 设置过期时间（当前时间 + token有效期）
        self._token_expire_time = current_time + 7200  # 默认7200秒

        return self._access_token

    def get_department_info(self, department_id):
        """
        获取飞书部门信息
        
        参数:
            department_id (str): 部门ID，如 'od-64242a18099d3a31acd24d8fce8dxxxx'
        
        返回:
            dict: 部门信息
        
        异常:
            requests.exceptions.RequestException: 网络请求异常
            ValueError: API调用失败
        """
        url = f"https://open.feishu.cn/open-apis/contact/v3/departments/{department_id}"

        # 获取access_token
        access_token = self.get_access_token()

        try:
            logger.info(f"开始获取部门信息，部门ID: {department_id}")

            # 发送GET请求
            response = requests.get(
                url=url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )

            # 检查响应状态码
            response.raise_for_status()

            # 解析响应数据
            result = response.json()

            # 检查是否获取成功
            if result.get("code") != 0:
                error_msg = result.get("msg", "未知错误")
                logger.error(f"获取部门信息失败: {error_msg}")
                raise ValueError(f"获取部门信息失败: {error_msg}")

            logger.info(f"成功获取部门信息，部门ID: {department_id}")
            return result.get("data", {})

        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            if e.response.status_code == 401:
                # token过期，强制刷新token后重试一次
                logger.warning("飞书access_token已过期，尝试刷新token")
                self._access_token = None  # 清除旧token
                access_token = self.get_access_token(force_refresh=True)

                # 重新发送请求
                response = requests.get(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"刷新token后获取部门信息仍然失败: {error_msg}")
                    raise ValueError(f"刷新token后获取部门信息仍然失败: {error_msg}")

                logger.info(f"成功获取部门信息，部门ID: {department_id}")
                return result.get("data", {})
            else:
                logger.error(f"获取部门信息时HTTP请求异常: {str(e)}")
                raise

    def create_card(self, card_type, card_data):
        """
        创建飞书卡片实体
        
        参数:
            card_type (str): 卡片类型，支持 'card_json' 或 'template'
            card_data (str): 卡片数据，根据card_type的不同格式不同：
                - 当card_type为'card_json'时，card_data是卡片JSON字符串
                - 当card_type为'template'时，card_data是模板数据JSON字符串
        
        返回:
            dict: 创建卡片的结果
        
        异常:
            requests.exceptions.RequestException: 网络请求异常
            ValueError: API调用失败或参数错误
        """
        url = "https://open.feishu.cn/open-apis/cardkit/v1/cards"

        # 验证卡片类型
        if card_type not in ["card_json", "template"]:
            raise ValueError(
                f"不支持的卡片类型: {card_type}，仅支持 'card_json' 或 'template'"
            )

        # 获取access_token
        access_token = self.get_access_token()

        try:
            logger.info(f"开始创建飞书卡片，类型: {card_type}")

            # 构造请求体
            # 如果card_data是字典类型，直接使用；如果是字符串，尝试解析为字典
            if isinstance(card_data, dict):
                payload = {"type": card_type, "data": card_data}
            else:
                payload = {"type": card_type, "data": json.loads(card_data)}

            # 发送POST请求
            response = requests.post(
                url=url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # 检查响应状态码
            response.raise_for_status()

            # 解析响应数据
            result = response.json()

            # 检查是否创建成功
            if result.get("code") != 0:
                error_msg = result.get("msg", "未知错误")
                logger.error(f"创建卡片失败: {error_msg}")
                raise ValueError(f"创建卡片失败: {error_msg}")

            logger.info(f"成功创建飞书卡片，类型: {card_type}")
            return result.get("data", {})

        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            if e.response.status_code == 401:
                # token过期，强制刷新token后重试一次
                logger.warning("飞书access_token已过期，尝试刷新token")
                self._access_token = None  # 清除旧token
                access_token = self.get_access_token(force_refresh=True)

                # 重新发送请求，同样需要处理card_data的类型
                if isinstance(card_data, dict):
                    payload = {"type": card_type, "data": card_data}
                else:
                    payload = {"type": card_type, "data": json.loads(card_data)}
                response = requests.post(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"刷新token后创建卡片仍然失败: {error_msg}")
                    raise ValueError(f"刷新token后创建卡片仍然失败: {error_msg}")

                logger.info(f"成功创建飞书卡片，类型: {card_type}")
                return result.get("data", {})
            else:
                logger.error(f"创建卡片时HTTP请求异常: {str(e)}")
                # 打印详细的错误信息，包括响应内容
                try:
                    error_response = e.response.json()
                    logger.error(f"详细错误信息: {error_response}")
                    print(f"详细错误信息: {error_response}")
                except Exception as parse_error:
                    print(f"无法解析错误响应: {str(parse_error)}")
                    print(f"原始响应内容: {e.response.text}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"创建卡片时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"创建卡片时发生未知异常: {str(e)}")
            raise

    def batch_get_user_id(
        self, emails=None, mobiles=None, include_resigned=False, user_id_type="user_id"
    ):
        """
        批量获取飞书用户ID
        
        参数:
            emails (list, optional): 邮箱列表，如 ['zhangsan@z.com', 'lisi@a.com']
            mobiles (list, optional): 手机号列表，如 ['13011111111', '13022222222']
            include_resigned (bool, optional): 是否包含离职人员，默认False
            user_id_type (str, optional): 用户ID类型，如 'user_id', 'open_id', 'union_id'，默认 'user_id'
        
        返回:
            dict: 用户ID映射信息
        
        异常:
            requests.exceptions.RequestException: 网络请求异常
            ValueError: API调用失败或参数错误
        """
        # 验证至少提供了邮箱或手机号
        if not emails and not mobiles:
            logger.error("批量获取用户ID时，必须提供邮箱列表或手机号列表")
            raise ValueError("必须提供邮箱列表或手机号列表")

        # 构建API URL
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type={user_id_type}"

        # 构建请求体
        request_body = {"include_resigned": include_resigned}

        # 添加邮箱和手机号（如果提供）
        if emails:
            request_body["emails"] = emails
        if mobiles:
            request_body["mobiles"] = mobiles

        # 获取access_token
        access_token = self.get_access_token()

        try:
            logger.info(
                f"开始批量获取用户ID，邮箱数量: {len(emails) if emails else 0}, 手机号数量: {len(mobiles) if mobiles else 0}"
            )

            # 发送POST请求
            response = requests.post(
                url=url,
                data=json.dumps(request_body),
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )

            # 检查响应状态码
            response.raise_for_status()

            # 解析响应数据
            result = response.json()

            # 检查是否获取成功
            if result.get("code") != 0:
                error_msg = result.get("msg", "未知错误")
                logger.error(f"批量获取用户ID失败: {error_msg}")
                raise ValueError(f"批量获取用户ID失败: {error_msg}")

            logger.info(f"成功批量获取用户ID")
            return result.get("data", {})

        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            if e.response.status_code == 401:
                # token过期，强制刷新token后重试一次
                logger.warning("飞书access_token已过期，尝试刷新token")
                self._access_token = None  # 清除旧token
                access_token = self.get_access_token(force_refresh=True)

                # 重新发送请求
                response = requests.post(
                    url=url,
                    json=request_body,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"刷新token后批量获取用户ID仍然失败: {error_msg}")
                    raise ValueError(f"刷新token后批量获取用户ID仍然失败: {error_msg}")

                logger.info(f"成功批量获取用户ID")
                return result.get("data", {})
            else:
                logger.error(f"批量获取用户ID时HTTP请求异常: {str(e)}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"批量获取用户ID时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"批量获取用户ID时发生未知异常: {str(e)}")
            raise

    def send_card_message(self, receive_id_type, receive_id, card_id):
        """
        发送飞书交互式卡片消息
        
        参数:
            receive_id_type (str): 接收者ID类型，如 'open_id', 'user_id', 'union_id' 等
            receive_id (str): 接收者ID，根据receive_id_type的不同而变化
            card_id (str): 卡片ID，如 '7371713483664506900'
        
        返回:
            dict: 发送消息的结果
        
        异常:
            requests.exceptions.RequestException: 网络请求异常
            ValueError: API调用失败或参数错误
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"

        # 获取access_token
        access_token = self.get_access_token()

        try:
            logger.info(f"开始发送卡片消息，接收者ID: {receive_id}, 卡片ID: {card_id}")

            # 构建请求体
            # 根据飞书API文档，正确的请求格式应该是：
            # {"receive_id_type": "open_id", "receive_id": "xxx", "msg_type": "interactive", "content": "{\"card_id\": \"xxx\"}"}
            # 注意：content字段是一个JSON字符串，包含card_id
            content = {"type": "card", "data": {"card_id": card_id}}
            request_body = {
                "receive_id": receive_id,
                "msg_type": "interactive",
                "content": json.dumps(content),
            }

            # 发送POST请求，直接使用json参数，让requests库自动处理JSON编码
            response = requests.post(
                url=url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                params={"receive_id_type": receive_id_type},
                json=request_body,
            )

            # 检查响应状态码
            response.raise_for_status()

            # 解析响应数据
            result = response.json()

            # 检查是否发送成功
            if result.get("code") != 0:
                error_msg = result.get("msg", "未知错误")
                logger.error(f"发送卡片消息失败: {error_msg}")
                raise ValueError(f"发送卡片消息失败: {error_msg}")

            logger.info(f"成功发送卡片消息，接收者ID: {receive_id}, 卡片ID: {card_id}")
            return result.get("data", {})

        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            logger.error(f"发送卡片消息时HTTP请求异常: {str(e)}")
            # 打印详细的错误信息，包括响应内容
            try:
                error_response = e.response.json()
                logger.error(f"详细错误信息: {error_response}")
                print(f"详细错误信息: {error_response}")
            except Exception as parse_error:
                print(f"无法解析错误响应: {str(parse_error)}")
                print(f"原始响应内容: {e.response.text}")

            if e.response.status_code == 401:
                # token过期，强制刷新token后重试一次
                logger.warning("飞书access_token已过期，尝试刷新token")
                self._access_token = None  # 清除旧token
                access_token = self.get_access_token(force_refresh=True)

                content = {"type": "card", "data": {"card_id": card_id}}
                # 重新发送请求
                request_body = {
                    "receive_id": receive_id,
                    "msg_type": "interactive",
                    "content": json.dumps(content),
                }
                response = requests.post(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    params={"receive_id_type": receive_id_type},
                    json=request_body,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"刷新token后发送卡片消息仍然失败: {error_msg}")
                    raise ValueError(f"刷新token后发送卡片消息仍然失败: {error_msg}")

                logger.info(
                    f"成功发送卡片消息，接收者ID: {receive_id}, 卡片ID: {card_id}"
                )
                return result.get("data", {})
            else:
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"发送卡片消息时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"发送卡片消息时发生未知异常: {str(e)}")
            raise

    def gen_markdown(self, content):
        """
        生成飞书卡片的markdown内容
        
        参数:
            content: markdown格式的文本内容
        
        返回:
            dict: 飞书卡片的markdown内容
        """
        return {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ],
            "header": {
                "template": "blue",
                "title": {
                    "content": "Git代码提交统计",
                    "tag": "plain_text"
                }
            }
        }

    def send_card_banches(self, receive_id: list, card_dict: dict, msg_type="interactive"):
        """
        批量发送卡片消息

        参数:
            receive_id (list): 接收者ID列表
            card_dict (dict): 要发送的卡片字典，包含卡片ID和其他配置
            msg_type (str, optional): 消息类型，默认是 "interactive"

        返回:
            dict: 包含发送结果的字典

        异常:
            ValueError: 如果发送失败
        """
        url = "https://open.feishu.cn/open-apis/message/v4/batch_send/"
        request_body = {
            "open_ids": receive_id,
            "msg_type": msg_type,
            "card": card_dict,
        }
        access_token = self.get_access_token()
        # 发送POST请求，直接使用json参数，让requests库自动处理JSON编码
        response = requests.post(
            url=url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=request_body,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            logger.error(f"批量发送卡片消息失败: {error_msg}")
            raise ValueError(f"批量发送卡片消息失败: {error_msg}")
        logger.info(
            f"成功批量发送卡片消息，接收者ID数量: {len(receive_id)}"
        )
        return result.get("data", {})

# --- 核心功能函数 ---

def send_feishu_message(content, app_id, app_secret, receive_id_type, receive_id):
    """
    发送飞书消息通知
    :param content: markdown格式的通知内容
    :param app_id: 飞书应用app_id
    :param app_secret: 飞书应用app_secret
    :param receive_id_type: 接收者ID类型，如'open_id', 'user_id', 'union_id', 'email', 'chat_id'
    :param receive_id: 接收者ID
    :return: 响应结果
    """
    # 创建飞书API实例
    feishu_api = FeishuAPI(app_id, app_secret)
    markdown_content = feishu_api.gen_markdown(content)
    # 发送飞书消息
    result = feishu_api.send_card_banches(
        receive_id=[receive_id],
        card_dict=markdown_content
    )
    return result



def run_git_command(command, directory="."):
    """执行 git 命令并返回输出"""
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, cwd=directory
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error executing command: {command}")
            print(f"Error message: {stderr}")
            sys.exit(1)
        return stdout.strip()
    except Exception as e:
        print(f"An exception occurred: {e}")
        sys.exit(1)


def get_commit_stats(author_name, directory="."):
    """
    获取指定作者的所有提交记录，包括日期、新增行数、删除行数。
    返回格式: list of dicts
    """
    # Git 命令解释:
    # --author="...": 筛选指定作者的提交
    # --pretty=format:"...": 自定义输出格式，用于分隔元数据
    # --numstat: 显示每个文件的增删行数
    # -z: 使用 null 字符分隔文件名，处理含特殊字符的文件名
    git_command = f'git log --author="{author_name}" --pretty=format:"COMMIT_START%H%n%ad%n%an%nCOMMIT_END" --date=short --numstat -z'
    output = run_git_command(git_command, directory)

    commits = []
    
    # 重新构建完整的提交块
    all_parts = output.split('\0')
    current_commit = ""
    
    for part in all_parts:
        if part.startswith("COMMIT_START"):
            # 如果已有当前提交，先处理它
            if current_commit:
                # 处理当前提交
                commit_pattern = re.compile(r'COMMIT_START(.*?)\n(.*?)\n(.*?)\nCOMMIT_END(.*)', re.DOTALL)
                match = commit_pattern.search(current_commit)
                if match:
                    commit_hash, date, author, file_changes_str = match.groups()
                    
                    additions, deletions = 0, 0
                    # 使用 null 字符分割文件变更记录
                    file_changes = file_changes_str.split('\0')
                    for change in file_changes:
                        if not change.strip():
                            continue
                        parts = change.split()
                        # 格式: 增加行数 删除行数 文件名
                        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                            additions += int(parts[0])
                            deletions += int(parts[1])

                    commits.append({
                        "hash": commit_hash,
                        "date": date,
                        "author": author,
                        "additions": additions,
                        "deletions": deletions,
                        "total_changes": additions + deletions
                    })
            # 开始新提交
            current_commit = part
        else:
            # 添加到当前提交
            current_commit += "\0" + part
    
    # 处理最后一个提交
    if current_commit:
        commit_pattern = re.compile(r'COMMIT_START(.*?)\n(.*?)\n(.*?)\nCOMMIT_END(.*)', re.DOTALL)
        match = commit_pattern.search(current_commit)
        if match:
            commit_hash, date, author, file_changes_str = match.groups()
            
            additions, deletions = 0, 0
            # 使用 null 字符分割文件变更记录
            file_changes = file_changes_str.split('\0')
            for change in file_changes:
                if not change.strip():
                    continue
                parts = change.split()
                # 格式: 增加行数 删除行数 文件名
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    additions += int(parts[0])
                    deletions += int(parts[1])

            commits.append({
                "hash": commit_hash,
                "date": date,
                "author": author,
                "additions": additions,
                "deletions": deletions,
                "total_changes": additions + deletions
            })
    return commits


def aggregate_stats_by_period(commits, period):
    """
    根据不同的周期（天、周、月）聚合统计数据
    """
    stats = defaultdict(lambda: {"commits": 0, "additions": 0, "deletions": 0, "total_changes": 0})
    
    for commit in commits:
        commit_date = datetime.strptime(commit["date"], "%Y-%m-%d")
        
        if period == 'daily':
            key = commit_date.strftime("%Y-%m-%d") # 例如: 2023-10-27
        elif period == 'weekly':
            # ISO 周格式: 年份-周数, 例如 2023-43
            key = commit_date.strftime("%Y-W%V") 
        elif period == 'monthly':
            key = commit_date.strftime("%Y-%m")   # 例如: 2023-10
        else:
            raise ValueError("Invalid period. Choose 'daily', 'weekly', or 'monthly'.")

        stats[key]["commits"] += 1
        stats[key]["additions"] += commit["additions"]
        stats[key]["deletions"] += commit["deletions"]
        stats[key]["total_changes"] += commit["total_changes"]
        
    return stats


def print_stats(stats, period_name):
    """美化打印统计结果"""
    print(f"\n--- {period_name} 代码提交统计 ---")
    print(f"{'时间段':<12} | {'提交次数':<8} | {'新增行数':<10} | {'删除行数':<10} | {'总计变更':<10}")
    print("-" * 65)
    
    # 按时间段降序排序后输出（最新的在顶部）
    for key in sorted(stats.keys(), reverse=True):
        data = stats[key]
        print(f"{key:<12} | {data['commits']:<8} | {data['additions']:<10} | {data['deletions']:<10} | {data['total_changes']:<10}")


def generate_markdown_stats(stats, period_name):
    """
    生成markdown格式的统计结果
    :param stats: 统计数据字典
    :param period_name: 统计周期名称
    :return: markdown格式的字符串
    """
    markdown = []
    markdown.append(f"## {period_name} 代码提交统计")
    markdown.append("|")
    markdown.append("| 时间段 | 提交次数 | 新增行数 | 删除行数 | 总计变更 |")
    markdown.append("| ------ | ------- | ------- | ------- | ------- |")
    
    # 按时间段降序排序后输出（最新的在顶部）
    for key in sorted(stats.keys(), reverse=True):
        data = stats[key]
        markdown.append(f"| {key} | {data['commits']} | {data['additions']} | {data['deletions']} | {data['total_changes']} |")
    
    markdown.append("|")
    return "\n".join(markdown)


def main():
    parser = argparse.ArgumentParser(description="统计 Git 代码提交量。")
    parser.add_argument("-a", "--author", type=str, default=None, help="指定作者姓名。如果为空，则统计所有作者的提交。")
    parser.add_argument("-p", "--period", type=str, default="all", choices=["daily", "weekly", "monthly", "all"], 
                        help="指定统计维度：daily, weekly, monthly, all (默认)。")
    parser.add_argument("-d", "--directory", type=str, default=".", help="指定 Git 仓库目录。如果为空，则使用当前目录。")
    
    # 飞书通知参数
    parser.add_argument("--feishu-app-id", type=str, default=None, help="飞书应用的app_id。")
    parser.add_argument("--feishu-app-secret", type=str, default=None, help="飞书应用的app_secret。")
    parser.add_argument("--feishu-receive-id-type", type=str, default="user_id", choices=["open_id", "user_id", "union_id", "email", "chat_id"], 
                        help="飞书接收者ID类型，默认'user_id'。")
    parser.add_argument("--feishu-receive-id", type=str, default=None, help="飞书接收者ID。")
    parser.add_argument("--feishu-mobile", type=str, default=None, help="飞书用户的手机号，会自动获取openid进行发送。")
    
    args = parser.parse_args()
    
    # 验证目录存在
    if not os.path.exists(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在。")
        sys.exit(1)
    
    # 验证目录是 Git 仓库
    try:
        run_git_command("git rev-parse --is-inside-work-tree", args.directory)
        print(f"正在检查目录 '{args.directory}' 中的 Git 仓库...")
    except SystemExit:
        print(f"错误：目录 '{args.directory}' 不是一个 Git 仓库。")
        sys.exit(1)

    # 如果没有指定作者，则尝试从 git config 获取
    author = args.author
    if not author:
        author = run_git_command("git config user.name", args.directory).strip()
        if not author:
            print("错误：无法确定作者。请在命令行中使用 -a 参数指定，或设置 git user.name。")
            sys.exit(1)
        print(f"未指定作者，将统计当前 Git 用户 '{author}' 的提交。\n")

    print(f"正在统计作者 '{author}' 的提交记录...")
    all_commits = get_commit_stats(author, args.directory)
    
    if not all_commits:
        print(f"未找到作者 '{author}' 的任何提交记录。")
        return

    print(f"共找到 {len(all_commits)} 条提交记录。")

    # 计算所有提交的总计
    total_additions = sum(commit['additions'] for commit in all_commits)
    total_deletions = sum(commit['deletions'] for commit in all_commits)
    total_changes = sum(commit['total_changes'] for commit in all_commits)

    # 用于收集markdown内容
    markdown_content = []
    
    # 标题
    markdown_content.append("# Git 代码提交量统计")
    markdown_content.append(f"**统计时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append(f"**统计仓库**：{os.path.abspath(args.directory)}")
    markdown_content.append(f"**统计作者**：{author}")
    markdown_content.append("")
    
    # 根据参数进行不同维度的统计和输出
    if args.period in ['daily', 'all']:
        daily_stats = aggregate_stats_by_period(all_commits, 'daily')
        print_stats(daily_stats, "每日 (Daily)")
        markdown_content.append(generate_markdown_stats(daily_stats, "每日 (Daily)"))
    
    if args.period in ['weekly', 'all']:
        weekly_stats = aggregate_stats_by_period(all_commits, 'weekly')
        print_stats(weekly_stats, "每周 (Weekly)")
        markdown_content.append(generate_markdown_stats(weekly_stats, "每周 (Weekly)"))
        
    if args.period in ['monthly', 'all']:
        monthly_stats = aggregate_stats_by_period(all_commits, 'monthly')
        print_stats(monthly_stats, "每月 (Monthly)")
        markdown_content.append(generate_markdown_stats(monthly_stats, "每月 (Monthly)"))
    
    # 显示总计行
    print(f"\n--- 总计 (Total) 代码提交统计 ---")
    print(f"{'总计':<12} | {len(all_commits):<8} | {total_additions:<10} | {total_deletions:<10} | {total_changes:<10}")
    print("-" * 65)
    
    # 生成总计markdown
    total_markdown = [
        "## 总计 (Total) 代码提交统计",
        "|",
        "| 总计 | 提交次数 | 新增行数 | 删除行数 | 总计变更 |",
        "| ---- | ------- | ------- | ------- | ------- |",
        f"| 总计 | {len(all_commits)} | {total_additions} | {total_deletions} | {total_changes} |",
        "|",
        ""
    ]
    markdown_content.append("\n".join(total_markdown))
    
    # 处理飞书手机号参数
    if args.feishu_mobile:
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', args.feishu_mobile):
            print("错误：无效的手机号格式。")
            sys.exit(1)
        
        # 创建FeishuAPI实例
        feishu_api = FeishuAPI(args.feishu_app_id, args.feishu_app_secret)
        
        # 通过手机号获取openid
        try:
            user_ids = feishu_api.batch_get_user_id(mobiles=[args.feishu_mobile], user_id_type="open_id")
            if user_ids and user_ids.get("user_list"):
                user_info = user_ids["user_list"][0]
                args.feishu_receive_id = user_info["user_id"]
                args.feishu_receive_id_type = "open_id"
            else:
                print("错误：未找到该手机号对应的飞书用户。")
                sys.exit(1)
        except Exception as e:
            print(f"通过手机号获取飞书用户信息时发生错误：{e}")
            sys.exit(1)
    
    # 如果提供了飞书参数，则发送飞书通知
    if args.feishu_app_id and args.feishu_app_secret and args.feishu_receive_id:
        full_content = "\n".join(markdown_content)
        print(f"\n正在发送飞书通知...")
        try:
            response = send_feishu_message(
                full_content,
                args.feishu_app_id,
                args.feishu_app_secret,
                args.feishu_receive_id_type,
                args.feishu_receive_id
            )
            print(f"飞书通知发送结果：{response}")
        except Exception as e:
            print(f"发送飞书通知时发生错误：{e}")


if __name__ == "__main__":
    main()