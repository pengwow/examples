# 获取门禁开通时间
# 1.获取门禁开通时间函数参数要求：函数名get_door_access_time
# 参数一：用户名，参数二：计划开始时间 参数三：开始时间偏移量（小时），默认为1 参数四：结束时间偏移量（小时），默认为1
# 返回值：开始时间，结束时间
# 2.根据用户名读取redis缓存：
# 当前用户是否在redis存在缓存
# 2.1 存在缓存则取出数据，判断缓存的开始时间计算结束时间
# 2.1.1 开始时间晚于09:00:00，则结束时间为第二天的09:00:00
# 2.1.2 开始时间是否早于09:00:00如果早于，则已09:00:00为结束时间
# 2.1.3 比如：用户开始时间："2025-01-01 17:19:00" 者结束时间"2025-01-02 09:00:00"
#       再比如：用户开始时间："2025-01-01 01:00:00" 者结束时间"2025-01-01 09:00:00"
# 2.2 缓存中开始时间和当前计划开始时间比较，取最早的开始时间作为新的开始时间
# 2.3 缓存中的结束时间和当前计划结束时间比较，取最晚的结束时间作为新的结束时间
# 2.4 不存在缓存，则将当前数据放到缓存中
# 2.5 以上缓存的过期时间按照结束时间为过期时间
# 2.6 以上开始时间结束时间为字符串格式，如："2025-01-01 17:19:00"
# 例子：
# 缓存中开始时间：2025-10-30 18:00:00 结束时间：2025-10-30 22:00:00
# 当前开始时间：2025-10-31 01:00:00 结束时间：2025-10-31 06:00:00
# 者最终时间为，开始时间：2025-10-30 18:00:00 结束时间：2025-10-31 09:00:00

import redis
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('door_access')

def get_door_access_time(username, planned_start_time, planned_end_time=None, start_offset_hours=1, end_offset_hours=1):
    """
    获取门禁开通时间函数
    
    参数：
    username (str): 用户名
    planned_start_time (str): 计划开始时间，格式为"YYYY-MM-DD HH:MM:SS"
    planned_end_time (str, optional): 计划结束时间，格式为"YYYY-MM-DD HH:MM:SS"。若未提供，则根据开始时间自动计算
    start_offset_hours (float, optional): 开始时间偏移量（小时），默认为1
    end_offset_hours (float, optional): 结束时间偏移量（小时），默认为1
    
    返回：
    dict: 包含开始时间和结束时间的门禁信息
    
    异常：
    ValueError: 当输入参数无效时
    redis.RedisError: 当Redis操作失败时
    """
    from datetime import timedelta
    
    # 参数验证
    if not username or not isinstance(username, str):
        raise ValueError("用户名必须是非空字符串")
    
    # 验证计划开始时间格式
    try:
        dt_planned_start = datetime.strptime(planned_start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("时间格式必须为'YYYY-MM-DD HH:MM:SS'")
    
    # 验证偏移量参数
    if not isinstance(start_offset_hours, (int, float)) or not isinstance(end_offset_hours, (int, float)):
        raise ValueError("时间偏移量必须是数字类型")
    
    # 处理计划结束时间
    if planned_end_time is not None:
        # 如果提供了计划结束时间，验证并使用它
        try:
            dt_planned_end = datetime.strptime(planned_end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("计划结束时间格式必须为'YYYY-MM-DD HH:MM:SS'")
        
        # 验证结束时间不能早于开始时间
        if dt_planned_end <= dt_planned_start:
            raise ValueError("计划结束时间必须晚于计划开始时间")
        
        logger.info(f"使用提供的计划结束时间: {planned_end_time}")
    else:
        # 计算计划结束时间
        # 开始时间晚于09:00:00，则结束时间为第二天的09:00:00
        # 开始时间早于09:00:00，则结束时间为当天的09:00:00
        if dt_planned_start.hour >= 9:
            # 开始时间晚于等于9点，结束时间为第二天9点
            dt_planned_end = dt_planned_start.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            # 开始时间早于9点，结束时间为当天9点
            dt_planned_end = dt_planned_start.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # 格式化为字符串
    planned_start_str = dt_planned_start.strftime("%Y-%m-%d %H:%M:%S")
    planned_end_str = dt_planned_end.strftime("%Y-%m-%d %H:%M:%S")
    
    # 连接Redis
    try:
        # 使用默认Redis配置
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        # 测试连接
        r.ping()
        logger.info("成功连接到Redis: localhost:6379")
        
    except redis.RedisError as e:
        logger.error(f"Redis连接失败: {str(e)}")
        raise redis.RedisError(f"Redis连接失败: {str(e)}")
    
    # 缓存键名
    cache_key = f"door_access:{username}"
    updated_data = None
    
    try:
        # 尝试从缓存获取数据
        cached_data = r.get(cache_key)
        
        if cached_data:
            try:
                # 缓存存在，解析数据
                cached_info = json.loads(cached_data)
                cached_start = cached_info['start_time']
                cached_end = cached_info['end_time']
                
                # 转换为datetime对象进行比较
                dt_cached_start = datetime.strptime(cached_start, "%Y-%m-%d %H:%M:%S")
                dt_cached_end = datetime.strptime(cached_end, "%Y-%m-%d %H:%M:%S")
                
                # 缓存中开始时间和当前计划开始时间比较，取最早的开始时间
                min_start = min(dt_cached_start, dt_planned_start).strftime("%Y-%m-%d %H:%M:%S")
                
                # 缓存中的结束时间和当前计划结束时间比较，取最晚的结束时间
                max_end = max(dt_cached_end, dt_planned_end).strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新缓存数据
                updated_data = {
                    'username': username,
                    'start_time': min_start,
                    'end_time': max_end
                }
                logger.info(f"用户 {username} 存在缓存，合并时间范围: {cached_start}-{cached_end} 与 {planned_start_str}-{planned_end_str}")
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"解析缓存数据失败: {str(e)}，将覆盖缓存")
                # 解析失败，使用当前数据
                updated_data = {
                    'username': username,
                    'start_time': planned_start_str,
                    'end_time': planned_end_str
                }
        else:
            # 缓存不存在，使用当前数据
            updated_data = {
                'username': username,
                'start_time': planned_start_str,
                'end_time': planned_end_str
            }
            logger.info(f"用户 {username} 不存在缓存，创建新的门禁时间: {planned_start_str}-{planned_end_str}")
        
        # 计算过期时间（以秒为单位）
        dt_end_final = datetime.strptime(updated_data['end_time'], "%Y-%m-%d %H:%M:%S")
        expire_seconds = int((dt_end_final - datetime.now()).total_seconds())
        
        # 确保过期时间不为负数
        if expire_seconds < 0:
            expire_seconds = 0
            logger.warning(f"结束时间已过期，设置缓存永不过期（0秒）")
        
        # 将数据存入缓存
        r.setex(cache_key, expire_seconds, json.dumps(updated_data))
        logger.info(f"成功更新缓存: {cache_key}, 过期时间: {expire_seconds}秒")
        
    except redis.RedisError as e:
        logger.error(f"Redis操作失败: {str(e)}")
        raise redis.RedisError(f"Redis操作失败: {str(e)}")
    finally:
        # 关闭Redis连接
        try:
            r.close()
        except:
            pass
    
    # 应用时间偏移量
    dt_start_original = datetime.strptime(updated_data['start_time'], "%Y-%m-%d %H:%M:%S")
    dt_end_original = datetime.strptime(updated_data['end_time'], "%Y-%m-%d %H:%M:%S")
    
    # 计算偏移后的时间
    dt_start_offset = dt_start_original + timedelta(hours=start_offset_hours)
    dt_end_offset = dt_end_original + timedelta(hours=end_offset_hours)
    
    # 构建返回数据
    result_data = {
        'username': updated_data['username'],
        'start_time': dt_start_offset.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': dt_end_offset.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"门禁时间获取成功：用户名={username}, 开始时间={result_data['start_time']}, 结束时间={result_data['end_time']}")
    
    return result_data

# 示例调用
if __name__ == "__main__":
    # 定义测试场景
    test_scenarios = [
        {
            "name": "首次获取门禁时间（下午开始时间，默认偏移量）",
            "params": {
                "username": "zhangsan",
                "planned_start_time": "2025-10-30 18:00:00"
                # 应该自动计算结束时间为：2025-10-31 09:00:00
            }
        },
        {
            "name": "时间合并（凌晨开始时间，默认偏移量）",
            "params": {
                "username": "zhangsan",
                "planned_start_time": "2025-10-31 01:00:00"
                # 应该自动计算结束时间为：2025-10-31 09:00:00
                # 合并后应该是：2025-10-30 18:00:00 - 2025-10-31 09:00:00
            }
        },
        {
            "name": "新用户获取门禁时间（早上9点开始，自定义偏移量）",
            "params": {
                "username": "lisi",
                "planned_start_time": "2025-11-01 09:00:00",
                "start_offset_hours": 2,
                "end_offset_hours": 3
                # 应该自动计算结束时间为：2025-11-02 09:00:00
            }
        },
        {
            "name": "时间合并（晚上开始时间，自定义偏移量）",
            "params": {
                "username": "lisi",
                "planned_start_time": "2025-10-31 20:00:00",
                "start_offset_hours": 0.5,
                "end_offset_hours": 0.5
                # 应该自动计算结束时间为：2025-11-01 09:00:00
                # 合并后应该是：2025-10-31 20:00:00 - 2025-11-02 09:00:00
            }
        },
        {
            "name": "零偏移量测试（早上8点开始）",
            "params": {
                "username": "wangwu",
                "planned_start_time": "2025-11-10 08:00:00",
                "start_offset_hours": 0,
                "end_offset_hours": 0
                # 应该自动计算结束时间为：2025-11-10 09:00:00
            }
        },
        {
            "name": "使用计划结束时间参数（自定义时间范围）",
            "params": {
                "username": "zhaoliu",
                "planned_start_time": "2025-11-15 09:30:00",
                "planned_end_time": "2025-11-15 18:30:00"
                # 使用提供的结束时间，不再自动计算
            }
        },
        {
            "name": "使用计划结束时间与缓存合并",
            "params": {
                "username": "zhaoliu",
                "planned_start_time": "2025-11-15 12:00:00",
                "planned_end_time": "2025-11-16 10:00:00"
                # 应该使用提供的结束时间并与之前的时间合并
                # 合并后应该是：2025-11-15 09:30:00 - 2025-11-16 10:00:00
            }
        },
        {
            "name": "使用计划结束时间（长时间段）",
            "params": {
                "username": "sunqi",
                "planned_start_time": "2025-11-20 08:00:00",
                "planned_end_time": "2025-11-22 17:00:00",
                "start_offset_hours": 0.5,
                "end_offset_hours": 1.5
                # 使用提供的长时间段结束时间
            }
        },
        # 以下是异常测试用例，默认注释掉，需要测试时可以取消注释
        # {
        #     "name": "无效时间格式",
        #     "params": {
        #         "username": "zhaoliu",
        #         "planned_start_time": "2025/10/30 18:00:00"  # 错误格式
        #     }
        # },
        # {
        #     "name": "空用户名",
        #     "params": {
        #         "username": "",
        #         "planned_start_time": "2025-10-30 18:00:00"
        #     }
        # },
        # {
        #     "name": "无效偏移量类型",
        #     "params": {
        #         "username": "zhaoliu",
        #         "planned_start_time": "2025-10-30 18:00:00",
        #         "start_offset_hours": "invalid",  # 错误类型
        #         "end_offset_hours": 1
        #     }
        # },
        # {
        #     "name": "无效计划结束时间格式",
        #     "params": {
        #         "username": "zhaoliu",
        #         "planned_start_time": "2025-10-30 18:00:00",
        #         "planned_end_time": "2025/10/30 22:00:00"  # 错误格式
        #     }
        # },
        # {
        #     "name": "计划结束时间早于开始时间",
        #     "params": {
        #         "username": "zhaoliu",
        #         "planned_start_time": "2025-10-30 18:00:00",
        #         "planned_end_time": "2025-10-30 17:00:00"  # 结束时间早于开始时间
        #     }
        # }
    ]
    
    # 运行测试场景
    for scenario in test_scenarios:
        print(f"\n========== 测试场景: {scenario['name']} ==========")
        try:
            # 调用函数
            result = get_door_access_time(**scenario['params'])
            print(f"测试成功! 结果: {result}")
            print(f"门禁时间范围: {result['start_time']} - {result['end_time']}")
        except Exception as e:
            print(f"测试失败! 错误: {str(e)}")
    
    # 提示用户如何测试异常场景
    print("\n注意：代码中包含了异常测试用例（已注释），您可以取消注释来测试异常处理逻辑。")
    print("实际运行时，如果Redis服务器不可用，程序会捕获并显示相应的错误信息。")
    print("函数现在支持时间偏移量参数，默认偏移1小时，并新增计划结束时间参数：")
    print("- 如果提供了计划结束时间，将直接使用该时间作为结束时间（需验证格式和有效性）")
    print("- 如果未提供计划结束时间，结束时间根据开始时间自动计算：")
    print("  * 开始时间晚于等于09:00:00：结束时间为第二天09:00:00")
    print("  * 开始时间早于09:00:00：结束时间为当天09:00:00")
    print("函数会自动合并Redis缓存中的时间范围，取最早的开始时间和最晚的结束时间。")
