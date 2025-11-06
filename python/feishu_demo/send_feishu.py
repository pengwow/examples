import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 模拟requests模块，避免依赖外部库
try:
    import requests
except ImportError:
    logger.warning("未找到requests模块，使用模拟实现")
    
    class MockResponse:
        """模拟requests.Response对象"""
        def __init__(self, status_code=200, headers=None, json_data=None):
            self.status_code = status_code
            self.headers = headers or {}
            self._json_data = json_data or {}
            
        def json(self):
            return self._json_data
    
    class MockRequests:
        """模拟requests模块"""
        
        @staticmethod
        def post(*args, **kwargs):
            # 模拟成功响应
            return MockResponse(status_code=200, headers={"Content-Type": "application/json"})
    
    requests = MockRequests()

class MockResponse:
    """模拟requests.Response对象"""
    def __init__(self, status_code=200, headers=None, json_data=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._json_data = json_data or {}
        
    def json(self):
        return self._json_data

class FSAPI(object):
    """飞书API类，作为占位"""
    
    def __init__(self):
        self.call_count = 0
    def feishu_send_msg_batch(self, open_ids:list[str], content=""):
        """
        批量发送飞书消息
        
        参数:
            open_ids: 用户open_id列表
            content: 消息内容
            
        返回:
            模拟的响应对象
        """
        logger.info(f"批量发送消息到 {len(open_ids)} 个用户")
        
        # 模拟批量发送响应
        # 在实际应用中，这里应该调用飞书的批量发送API
        return MockResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            json_data={"code": 0, "msg": "success", "data": {"task_id": "mock_task_123"}}
        )

    def feishu_send_msg(self, open_id: str, content=""):
        """
        发送飞书消息（占位实现）
        
        参数:
            open_id: 单个用户open_id
            content: 消息内容
            
        返回:
            模拟的响应对象
        """
        self.call_count += 1
        
        # 模拟前两次调用触发限流，第三次调用成功
        if self.call_count <= 2:
            logger.warning(f"模拟限流响应，第{self.call_count}次调用")
            # 模拟限流响应，包含x-ogw-ratelimit-reset头
            return MockResponse(
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "x-ogw-ratelimit-limit": "100",
                    "x-ogw-ratelimit-reset": "1"  # 等待1秒
                },
                json_data={"code": 99991400, "msg": "request trigger frequency limit"}
            )
        else:
            # 第三次调用成功
            logger.info(f"模拟成功响应，第{self.call_count}次调用")
            return MockResponse(status_code=200, headers={"Content-Type": "application/json"})

def send_msg(open_ids=None, content="", max_retries=3):
    """
    发送飞书消息，包含异常处理和限流重试机制
    
    参数:
        open_ids: 用户open_id列表
        content: 消息内容
        max_retries: 最大重试次数
        
    返回:
        dict: 包含成功和失败信息的字典
        
    异常:
        Exception: 当参数验证失败时抛出
    """
    # 参数验证
    if open_ids is None:
        open_ids = []
    
    if not isinstance(open_ids, list):
        logger.error("open_ids参数必须是列表类型")
        raise TypeError("open_ids参数必须是列表类型")
    
    # 过滤空的open_id
    filtered_open_ids = [oid for oid in open_ids if oid]
    if not filtered_open_ids:
        logger.warning("没有有效的open_id，跳过发送")
        return {"success": True, "message": "没有有效的open_id，跳过发送", "failed_ids": []}
    
    fs_api = FSAPI()
    all_failed_ids = []
    batch_size = 50
    
    # 将用户ID分批处理
    for i in range(0, len(filtered_open_ids), batch_size):
        batch_ids = filtered_open_ids[i:i+batch_size]
        logger.info(f"处理第 {i//batch_size + 1} 批，共 {len(batch_ids)} 个用户")
        
        # 当前批次的失败ID列表
        batch_failed_ids = batch_ids.copy()
        
        # 对当前批次进行重试
        current_retry = 0
        while current_retry <= max_retries and batch_failed_ids:
            logger.info(f"批次 {i//batch_size + 1} 重试次数: {current_retry}/{max_retries}")
            
            # 记录本次重试中失败的ID
            current_failed_ids = []
            
            # 逐个发送用户消息（因为feishu_send_msg只接受单个用户ID）
            for open_id in batch_failed_ids:
                try:
                    # 发送消息给单个用户
                    res = fs_api.feishu_send_msg(open_id=open_id, content=content)
                    
                    # 检查响应状态码
                    if res.status_code != 200:
                        # 发送失败，添加到当前失败列表
                        current_failed_ids.append(open_id)
                        if res.status_code == 400:
                            logger.warning(f"用户 {open_id} 发送失败，状态码: 400")
                        elif res.status_code == 429:
                            # 处理限流情况
                            try:
                                wait_time = int(res.headers.get('x-ogw-ratelimit-reset', 1))
                                logger.warning(f"用户 {open_id} 触发飞书API限流，将等待 {wait_time} 秒")
                                time.sleep(wait_time)
                            except (ValueError, TypeError):
                                logger.warning(f"用户 {open_id} 无法获取限流等待时间，默认等待1秒")
                                time.sleep(1)
                        else:
                            logger.error(f"用户 {open_id} 发送失败，状态码: {res.status_code}")
                    
                except Exception as e:
                    logger.error(f"用户 {open_id} 发送时发生异常: {str(e)}")
                    current_failed_ids.append(open_id)
            
            # 更新下一次重试的失败ID列表
            batch_failed_ids = current_failed_ids
            
            # 如果还有失败的ID，且未达到最大重试次数，增加重试计数
            if batch_failed_ids and current_retry < max_retries:
                current_retry += 1
                # 无论是否是最后一批，都等待1秒后重试
                logger.info("等待1秒后重试当前批次失败的用户")
                time.sleep(1)
            # 如果达到最大重试次数，跳出循环
            elif current_retry >= max_retries:
                logger.warning(f"已达到最大重试次数 {max_retries}，停止重试当前批次")
                break
        
        # 将当前批次最终失败的ID添加到总失败列表
        if batch_failed_ids:
            all_failed_ids.extend(batch_failed_ids)
            logger.warning(f"批次 {i//batch_size + 1} 有 {len(batch_failed_ids)} 个用户发送失败")
        
        # 如果不是最后一批，等待1秒后处理下一批
        if i + batch_size < len(filtered_open_ids):
            logger.info("等待1秒后处理下一批用户")
            time.sleep(1)
    
    # 对所有重试后仍然失败的ID进行批量发送
    if all_failed_ids:
        logger.info(f"对 {len(all_failed_ids)} 个失败的用户进行批量发送")
        try:
            # 调用批量发送方法
            res = fs_api.feishu_send_msg_batch(open_ids=all_failed_ids, content=content)
            logger.info("批量发送完成")
        except Exception as e:
            logger.error(f"批量发送时发生异常: {str(e)}")
    
    return {
        "success": len(all_failed_ids) == 0,
        "message": f"发送完成，成功 {len(filtered_open_ids) - len(all_failed_ids)} 个，失败 {len(all_failed_ids)} 个",
        "failed_ids": all_failed_ids
    }

if __name__ == "__main__":
    try:
        # 测试场景1：少量用户
        print("\n=== 测试场景1：少量用户 ===")
        user_phone = ['user1', 'user2']  # 示例open_id
        res = send_msg(open_ids=user_phone, content="测试消息")
        print(f"测试场景1 结果: {res}")
        
        # 测试场景2：大量用户（超过50个）
        print("\n=== 测试场景2：大量用户 ===")
        large_user_list = [f'user{i}' for i in range(1, 60)]  # 59个用户
        res = send_msg(open_ids=large_user_list, content="大量用户测试消息")
        print(f"测试场景2 结果: {res}")
        
    except Exception as e:
        print(f"执行出错: {str(e)}")
