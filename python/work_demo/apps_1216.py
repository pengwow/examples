# 编写两个函数一个get_lock一个un_lock, 使用redis执行锁,value为时间戳,字符串格式,过期时间固定10分钟.如果获取到锁,返回True,否则返回False

import redis
import time
from datetime import datetime
from typing import Optional


class RedisLock:
    def __init__(self, redis_client: redis.Redis, failure_threshold: int = 5):
        """
        初始化Redis锁实例
        
        参数:
            redis_client: Redis客户端实例
            failure_threshold: 失败计数阈值，超过该值触发告警，默认5次
        """
        self.redis_client = redis_client
        self.expire_time = 600  # 固定过期时间10分钟(600秒)
        self.failure_threshold = failure_threshold
        self.failure_count_prefix = "lock_failure_count:"  # 失败计数键前缀
    
    def get_lock(self, lock_key: str) -> bool:
        """
        获取Redis锁
        
        参数:
            lock_key: 锁的键名
            
        返回:
            bool: 获取到锁返回True，否则返回False
            
        异常:
            redis.RedisError: Redis操作失败时抛出异常
        """
        try:
            # 生成当前时间字符串（年月日时分秒格式）
            current_time = datetime.now()
            # 格式：年月日小时分钟，如202312161430
            lock_value = current_time.strftime("%Y%m%d%H%M")
            
            # 使用SETNX命令获取锁，设置过期时间
            result = self.redis_client.setnx(lock_key, lock_value)
            
            if result:
                # 设置过期时间
                self.redis_client.expire(lock_key, self.expire_time)
                # 成功获取锁后重置失败计数
                self._reset_failure_count(lock_key)
                return True
            else:
                # 失败计数加1
                failure_count = self._increment_failure_count(lock_key)
                # 检查是否超过阈值
                if failure_count >= self.failure_threshold:
                    self._trigger_alert(lock_key, failure_count)
                return False
                
        except redis.RedisError as e:
            print(f"获取锁失败: {str(e)}")
            # Redis操作失败也计入失败次数
            try:
                failure_count = self._increment_failure_count(lock_key)
                if failure_count >= self.failure_threshold:
                    self._trigger_alert(lock_key, failure_count)
            except:
                # 忽略告警触发失败的异常
                pass
            raise
            
    def _increment_failure_count(self, lock_key: str) -> int:
        """
        增加失败计数
        
        参数:
            lock_key: 锁的键名
            
        返回:
            int: 增加后的失败计数
        """
        failure_count_key = f"{self.failure_count_prefix}{lock_key}"
        # 使用INCR命令原子增加计数
        count = self.redis_client.incr(failure_count_key)
        # 设置失败计数的过期时间为锁过期时间的2倍
        self.redis_client.expire(failure_count_key, self.expire_time * 2)
        return count
        
    def _reset_failure_count(self, lock_key: str) -> None:
        """
        重置失败计数
        
        参数:
            lock_key: 锁的键名
        """
        failure_count_key = f"{self.failure_count_prefix}{lock_key}"
        self.redis_client.delete(failure_count_key)
        
    def _trigger_alert(self, lock_key: str, failure_count: int) -> None:
        """
        触发告警
        
        参数:
            lock_key: 锁的键名
            failure_count: 当前失败计数
        """
        alert_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🚨 告警：锁 {lock_key} 获取失败次数已达 {failure_count} 次，超过阈值 {self.failure_threshold} 次！")
        print(f"   告警时间：{alert_time}")
        print(f"   建议：检查锁的使用情况或延长锁的过期时间")
    
    def un_lock(self, lock_key: str) -> bool:
        """
        释放Redis锁
        
        参数:
            lock_key: 锁的键名
            
        返回:
            bool: 释放锁成功返回True，否则返回False
            
        异常:
            redis.RedisError: Redis操作失败时抛出异常
        """
        try:
            # 删除锁
            result = self.redis_client.delete(lock_key)
            return result > 0
            
        except redis.RedisError as e:
            print(f"释放锁失败: {str(e)}")
            # Redis操作失败也计入失败次数
            try:
                failure_count = self._increment_failure_count(lock_key)
                if failure_count >= self.failure_threshold:
                    self._trigger_alert(lock_key, failure_count)
            except:
                # 忽略告警触发失败的异常
                pass
            raise


def get_lock(redis_client: redis.Redis, lock_key: str, failure_threshold: int = 5) -> bool:
    """
    获取Redis锁的独立函数
    
    参数:
        redis_client: Redis客户端实例
        lock_key: 锁的键名
        failure_threshold: 失败计数阈值，超过该值触发告警，默认5次
        
    返回:
        bool: 获取到锁返回True，否则返回False
        
    异常:
        redis.RedisError: Redis操作失败时抛出异常
    """
    lock = RedisLock(redis_client, failure_threshold)
    return lock.get_lock(lock_key)


def un_lock(redis_client: redis.Redis, lock_key: str, failure_threshold: int = 5) -> bool:
    """
    释放Redis锁的独立函数
    
    参数:
        redis_client: Redis客户端实例
        lock_key: 锁的键名
        failure_threshold: 失败计数阈值，超过该值触发告警，默认5次
        
    返回:
        bool: 释放锁成功返回True，否则返回False
        
    异常:
        redis.RedisError: Redis操作失败时抛出异常
    """
    lock = RedisLock(redis_client, failure_threshold)
    return lock.un_lock(lock_key)


# 示例用法
if __name__ == "__main__":
    try:
        # 创建Redis客户端连接
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # 测试Redis连接
        redis_client.ping()
        print("Redis连接成功！")
        
        # 测试RedisLock类 - 失败计数和告警功能
        print("\n=== 测试RedisLock类 - 失败计数和告警 ===")
        # 创建锁实例，设置较低的失败阈值以便快速看到告警
        lock = RedisLock(redis_client, failure_threshold=3)
        test_lock_key = "test_lock_key"
        
        # 第一个客户端获取锁
        print("\n1. 客户端1尝试获取锁...")
        if lock.get_lock(test_lock_key):
            print("   客户端1: 成功获取锁！")
            
            # 模拟第二个客户端多次尝试获取同一锁
            print("\n2. 客户端2尝试多次获取同一锁...")
            for i in range(5):
                print(f"   客户端2: 第{i+1}次尝试获取锁...")
                lock2 = RedisLock(redis_client, failure_threshold=3)
                if lock2.get_lock(test_lock_key):
                    print("   客户端2: 成功获取锁！")
                    break
                else:
                    print("   客户端2: 获取锁失败！")
            
            # 释放锁
            if lock.un_lock(test_lock_key):
                print("\n3. 客户端1: 成功释放锁！")
            else:
                print("\n3. 客户端1: 释放锁失败！")
        else:
            print("客户端1: 获取锁失败！")
        
        # 测试独立函数 - 失败计数和告警功能
        print("\n=== 测试独立函数 - 失败计数和告警 ===")
        # 使用独立函数获取锁
        if get_lock(redis_client, "test_function_lock", failure_threshold=2):
            print("1. 使用独立函数: 成功获取锁！")
            
            # 多次尝试获取同一锁，触发告警
            print("\n2. 多次尝试获取同一锁...")
            for i in range(3):
                print(f"   第{i+1}次尝试获取锁...")
                if get_lock(redis_client, "test_function_lock", failure_threshold=2):
                    print("   成功获取锁！")
                    break
                else:
                    print("   获取锁失败！")
            
            # 释放锁
            if un_lock(redis_client, "test_function_lock"):
                print("\n3. 使用独立函数: 成功释放锁！")
            else:
                print("\n3. 使用独立函数: 释放锁失败！")
        else:
            print("使用独立函数: 获取锁失败！")
            
    except redis.RedisError as e:
        print(f"示例运行失败: {str(e)}")
        print("请确保Redis服务器正在运行！")
        print("\n=== 失败计数和告警功能说明 ===")
        print("1. 失败计数功能: 每次获取锁失败时，Redis会记录失败次数")
        print("2. 告警触发条件: 当失败次数超过设置的阈值时")
        print("3. 告警方式: 使用print语句输出告警信息")
        print("4. 锁超时时间: 保持固定的10分钟过期时间")
        print("5. 成功重置: 获取锁成功后，自动重置失败计数")
    except Exception as e:
        print(f"发生其他错误: {str(e)}")