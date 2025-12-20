app_id = "cli_a83fafd0aa14d013"
app_secret = "dy637jNB8N4v7bBbeHNA0eZveXizuZxH"

import requests
import logging
import time
import json

# 配置日志
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
        if card_type not in ['card_json', 'template']:
            raise ValueError(f"不支持的卡片类型: {card_type}，仅支持 'card_json' 或 'template'")

        # 获取access_token
        access_token = self.get_access_token()

        try:
            logger.info(f"开始创建飞书卡片，类型: {card_type}")

            # 构造请求体
            payload = {
                "type": card_type,
                "data": card_data
            }

            # 发送POST请求
            response = requests.post(
                url=url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload
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

                # 重新发送请求
                payload = {
                    "type": card_type,
                    "data": card_data
                }
                response = requests.post(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload
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
                raise
        except Exception as e:
            logger.error(f"创建卡片时发生异常: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"获取部门信息时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"获取部门信息时发生未知异常: {str(e)}")
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
            content = {
                    "type": "card",
                    "data": {
                        "card_id": card_id
                    }
                }
            request_body = {
                "receive_id": receive_id,
                "msg_type": "interactive",
                "content": json.dumps(content)
            }

            # 发送POST请求，直接使用json参数，让requests库自动处理JSON编码
            response = requests.post(
                url=url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                params={
                    "receive_id_type": receive_id_type
                },
                json=request_body
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

    
                content = {
                    "type": "card",
                    "data": {
                        "card_id": card_id
                    }
                }
                # 重新发送请求
                request_body = {
                    "receive_id": receive_id,
                    "msg_type": "interactive",
                    "content": json.dumps(content)
                }
                response = requests.post(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=utf-8",
                    },
                    params={
                        "receive_id_type": receive_id_type
                    },
                    json=request_body
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"刷新token后发送卡片消息仍然失败: {error_msg}")
                    raise ValueError(f"刷新token后发送卡片消息仍然失败: {error_msg}")

                logger.info(f"成功发送卡片消息，接收者ID: {receive_id}, 卡片ID: {card_id}")
                return result.get("data", {})
            else:
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"发送卡片消息时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"发送卡片消息时发生未知异常: {str(e)}")
            raise


# 示例用法
if __name__ == "__main__":
    try:
        # 创建飞书API客户端
        feishu_api = FeishuAPI(app_id=app_id, app_secret=app_secret)

        # 示例1: 获取部门信息（替换为实际的部门ID）
        # department_id = "od-64242a18099d3a31acd24d8fce8dxxxx"
        # department_info = feishu_api.get_department_info(department_id=department_id)
        # print("部门信息:", department_info)

        # 示例2: 批量获取用户ID
        emails = []
        mobiles = ["15810260321"]

        # 调用批量获取用户ID的方法
        user_ids_info = feishu_api.batch_get_user_id(
            emails=emails,
            mobiles=mobiles,
            include_resigned=True,
            user_id_type="open_id",
        )
        print("批量获取的用户ID信息:", user_ids_info)

    except Exception as e:
        print(f"执行出错: {str(e)}")

    # 定义示例卡片数据
    demo_dict = {
        "schema": "2.0",
        "config": {
            "update_multi": True
        },
        "body": {
            "direction": "vertical",
            "elements": [
                {
                    "tag": "markdown",
                    "content": "**请选择邮件类型查看详情**",
                    "text_align": "left",
                    "margin": "0px 0px 0px 0px"
                },
                {
                    "tag": "column_set",
                    "flex_mode": "stretch",
                    "horizontal_align": "left",
                    "columns": [],
                    "margin": "0px 0px 0px 0px"
                },
                {
                    "tag": "column_set",
                    "flex_mode": "stretch",
                    "horizontal_spacing": "8px",
                    "horizontal_align": "left",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "审批 (1)"
                                    },
                                    "type": "primary_filled",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {
                                                "action": "view_approval"
                                            }
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px"
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top"
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "关注 (3)"
                                    },
                                    "type": "default",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {
                                                "action": "view_follow"
                                            }
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px"
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top"
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "不处理 (1)"
                                    },
                                    "type": "default",
                                    "width": "default",
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {
                                                "action": "view_ignore"
                                            }
                                        }
                                    ],
                                    "margin": "4px 0px 4px 0px"
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top"
                        }
                    ],
                    "margin": "0px 0px 0px 0px"
                },
                {
                    "tag": "hr",
                    "margin": "0px 0px 0px 0px"
                },
                {
                    "tag": "column_set",
                    "flex_mode": "stretch",
                    "background_style": "blue-50",
                    "horizontal_align": "left",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": "**<font color='blue'>📋 邮件详情</font>**",
                                    "text_align": "left"
                                },
                                {
                                    "tag": "markdown",
                                    "content": "• **发件人** ：张三 (zhang.san@example.com)\n• **主题** ：关于XX项目预算审批的申请\n• **日期** ：2023-10-27 09:30\n• **摘要** ：申请XX项目第三季度预算，金额15万元，用于采购新设备\n• **审批建议** ：建议批准，符合本季度预算规划",
                                    "text_align": "left",
                                    "text_size": "notation"
                                },
                                {
                                    "tag": "column_set",
                                    "horizontal_align": "left",
                                    "columns": [
                                        {
                                            "tag": "column",
                                            "width": "weighted",
                                            "elements": [
                                                {
                                                    "tag": "input",
                                                    "name": "approval_comment",
                                                    "placeholder": {
                                                        "tag": "plain_text",
                                                        "content": "请输入您的审批意见..."
                                                    },
                                                    "default_value": "",
                                                    "width": "default",
                                                    "label": {
                                                        "tag": "plain_text",
                                                        "content": "审批意见"
                                                    },
                                                    "label_position": "top",
                                                    "disabled": True,
                                                    "behaviors": [
                                                        {
                                                            "type": "callback",
                                                            "value": ""
                                                        }
                                                    ],
                                                    "margin": "8px 0px 8px 0px",
                                                    "element_id": "custom_id"
                                                },
                                                {
                                                    "tag": "button",
                                                    "text": {
                                                        "tag": "plain_text",
                                                        "content": "处理选中邮件"
                                                    },
                                                    "type": "primary_filled",
                                                    "width": "fill",
                                                    "disabled": True,
                                                    "behaviors": [
                                                        {
                                                            "type": "callback",
                                                            "value": {
                                                                "action": "process_email"
                                                            }
                                                        }
                                                    ],
                                                    "margin": "4px 0px 4px 0px"
                                                }
                                            ],
                                            "vertical_spacing": "8px",
                                            "horizontal_align": "left",
                                            "vertical_align": "top",
                                            "weight": 1
                                        }
                                    ]
                                }
                            ],
                            "vertical_spacing": "8px",
                            "horizontal_align": "left",
                            "vertical_align": "top",
                            "weight": 1
                        }
                    ],
                    "margin": "0px 0px 0px 0px"
                }
            ]
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "邮件分类处理中心"
            },
            "subtitle": {
                "tag": "plain_text",
                "content": ""
            },
            "template": "blue",
            "padding": "12px 12px 12px 12px"
        }
    }

    try:
        # 创建飞书API客户端
        feishu_api = FeishuAPI(app_id=app_id, app_secret=app_secret)

        # 示例3: 创建card_json类型卡片
        print("\n=== 示例3: 创建card_json类型卡片 ===")
        
        # 使用已有的demo_dict作为card_json数据
        card_json_data = json.dumps(demo_dict)
        
        # 调用创建卡片方法
        card_id = None
        try:
            card_result = feishu_api.create_card(
                card_type="card_json",
                card_data=card_json_data
            )
            print("创建card_json类型卡片结果:", card_result)
            # 获取创建的卡片ID
            card_id = card_result.get("card_id")
            if card_id:
                print(f"成功获取卡片ID: {card_id}")
            else:
                print("创建卡片成功，但未返回card_id")
        except Exception as e:
            print(f"创建card_json类型卡片失败: {str(e)}")
        
        # 示例4: 创建template类型卡片（需要替换为实际的模板ID和版本）
        print("\n=== 示例4: 创建template类型卡片 ===")
        
        # # 模板数据（实际使用时需要替换为真实的模板ID和变量）
        # template_data = json.dumps({
        #     "template_id": "AAqIi1B8abcef",
        #     "template_version_name": "1.0.0",
        #     "template_variable": {
        #         "open_id": "ou_5c6d1637498e704f541095bba3dabcef"
        #     }
        # })
        
        # # 调用创建卡片方法
        # # 注意：由于这是示例模板ID，实际执行可能会失败
        # try:
        #     card_result = feishu_api.create_card(
        #         card_type="template",
        #         card_data=template_data
        #     )
        #     print("创建template类型卡片结果:", card_result)
        # except Exception as e:
        #     print(f"创建template类型卡片失败（预期行为，因为模板ID是示例）: {str(e)}")
        
        # 示例5: 发送卡片消息
        print("\n=== 示例5: 发送卡片消息 ===")
        if card_id:
            try:
                # 先使用手机号获取用户open_id
                print("\n=== 获取用户open_id ===")
                mobiles = ["15810260321"]
                user_ids_info = feishu_api.batch_get_user_id(
                    mobiles=mobiles,
                    include_resigned=True,
                    user_id_type="open_id",
                )
                print("批量获取的用户ID信息:", user_ids_info)
                
                # 获取open_id
                open_id = None
                if user_ids_info.get("user_list"):
                    open_id = user_ids_info["user_list"][0].get("user_id")
                    if open_id:
                        print(f"成功获取用户open_id: {open_id}")
                    else:
                        print("未获取到用户open_id")
                
                # 使用真实创建的卡片ID和获取到的open_id发送消息
                if open_id:
                    send_result = feishu_api.send_card_message(
                        receive_id_type="open_id",
                        receive_id=open_id,
                        card_id=card_id
                    )
                    print("发送卡片消息结果:", send_result)
            except Exception as e:
                print(f"发送卡片消息失败: {str(e)}")
        else:
            print("未获取到卡片ID，跳过发送卡片消息")
            
    except Exception as e:
        print(f"执行出错: {str(e)}")

