app_id = 'cli_a83fafd0aa14d013'
app_secret = 'dy637jNB8N4v7bBbeHNA0eZveXizuZxH'

import requests
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    try:
        logger.info("开始获取飞书access_token")
        
        # 发送POST请求
        response = requests.post(
            url=url,
            json=data,
            headers={"Content-Type": "application/json; charset=utf-8"}
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
        if not force_refresh and self._access_token and current_time < self._token_expire_time - 300:
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
                    "Content-Type": "application/json; charset=utf-8"
                }
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
                        "Content-Type": "application/json; charset=utf-8"
                    }
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
        except requests.exceptions.RequestException as e:
            logger.error(f"获取部门信息时网络请求异常: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"获取部门信息时发生未知异常: {str(e)}")
            raise

    def batch_get_user_id(self, emails=None, mobiles=None, include_resigned=False, user_id_type="user_id"):
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
        request_body = {
            "include_resigned": include_resigned
        }
        
        # 添加邮箱和手机号（如果提供）
        if emails:
            request_body["emails"] = emails
        if mobiles:
            request_body["mobiles"] = mobiles
        
        # 获取access_token
        access_token = self.get_access_token()
        
        try:
            logger.info(f"开始批量获取用户ID，邮箱数量: {len(emails) if emails else 0}, 手机号数量: {len(mobiles) if mobiles else 0}")
            
            # 发送POST请求
            response = requests.post(
                url=url,
                json=request_body,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8"
                }
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
                        "Content-Type": "application/json; charset=utf-8"
                    }
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
            user_id_type="open_id"
        )
        print("批量获取的用户ID信息:", user_ids_info)
        
    except Exception as e:
        print(f"执行出错: {str(e)}")


