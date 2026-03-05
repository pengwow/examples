# 编写函数，参数1个data字典，用来校验窗口期时间并拦截，不符合规则者返回False, "错误信息"
# data = {
#     "auto_plan_starttime": "2025-11-12 23:59:59",
#     "auto_plan_endtime": "2025-11-13 00:00:00",
#     "auto_type": "2",   # 常规(2)或者重大(4),紧急(cr_type_urgent)
# }
# 1.计划开始时间（auto_plan_starttime）小于今天的23:59:59，且auto_type为"常规(2)或者重大(4),错误并提示 xxxx"
# 2.计划开始时间（auto_plan_starttime）大于今天的23:59:59，且auto_type为"紧急(cr_type_urgent)，错误并提示 xxxx"
# 3.计划开始时间（auto_plan_starttime）不能大于 计划结束时间（auto_plan_endtime），否则错误并提示 xxxx
# 4.计划开始时间（auto_plan_starttime）至 计划结束时间（auto_plan_endtime）间隔不能大于12小时，否则错误并提示 xxxx

from datetime import datetime, timedelta

def validate_maintenance_window(data):
    """
    校验窗口期时间是否符合规则
    
    参数：
        data (dict): 包含窗口期信息的字典，必须包含以下键：
            - auto_plan_starttime: 计划开始时间，格式为"YYYY-MM-DD HH:MM:SS"
            - auto_plan_endtime: 计划结束时间，格式为"YYYY-MM-DD HH:MM:SS"
            - auto_type: 任务类型，值为"2"(常规)、"4"(重大)或"cr_type_urgent"(紧急)
    
    返回：
        tuple: (是否通过验证, 错误信息)
            - 验证通过时返回 (True, "")
            - 验证失败时返回 (False, "具体错误信息")
    
    异常：
        KeyError: 当data字典缺少必要的键时
        ValueError: 当时间格式不正确时
    """
    # 参数完整性校验
    required_keys = ["auto_plan_starttime", "auto_plan_endtime", "auto_type"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"缺少必要的参数: {key}")
    
    try:
        # 解析时间字符串
        start_time = datetime.strptime(data["auto_plan_starttime"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(data["auto_plan_endtime"], "%Y-%m-%d %H:%M:%S")
        auto_type = data["auto_type"]
        
        # 获取今天的23:59:59
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        
        # 规则1: 计划开始时间小于今天的23:59:59，且auto_type为常规(2)或重大(4)
        if start_time < today_end and auto_type in ("2", "4"):
            return False, f"常规/重大任务的计划开始时间必须大于等于今天的23:59:59，当前时间为{data['auto_plan_starttime']}"
        
        # 规则2: 计划开始时间大于今天的23:59:59，且auto_type为紧急(cr_type_urgent)
        if start_time > today_end and auto_type == "cr_type_urgent":
            return False, f"紧急任务的计划开始时间必须小于等于今天的23:59:59，当前时间为{data['auto_plan_starttime']}"
        
        # 规则3: 计划开始时间不能大于计划结束时间
        if start_time > end_time:
            return False, f"计划开始时间({data['auto_plan_starttime']})不能大于计划结束时间({data['auto_plan_endtime']})"
        
        # 规则4: 计划开始时间至计划结束时间间隔不能大于12小时
        time_diff = end_time - start_time
        if time_diff > timedelta(hours=12):
            hours = time_diff.total_seconds() / 3600
            return False, f"计划时间间隔({hours:.2f}小时)不能大于12小时"
        
        # 所有规则验证通过
        return True, ""
        
    except ValueError as e:
        # 处理时间格式错误
        if "unconverted data remains" in str(e) or "does not match format" in str(e):
            raise ValueError("时间格式必须为YYYY-MM-DD HH:MM:SS")
        raise


# 测试代码
if __name__ == "__main__":
    # 测试用例1: 常规任务，开始时间小于今天23:59:59 - 应失败
    test1 = {
        "auto_plan_starttime": "2023-11-12 23:59:59",  # 假设今天是2023-11-13或之后
        "auto_plan_endtime": "2023-11-13 01:00:00",
        "auto_type": "2"
    }
    
    # 测试用例2: 紧急任务，开始时间大于今天23:59:59 - 应失败
    test2 = {
        "auto_plan_starttime": "2025-11-12 23:59:59",
        "auto_plan_endtime": "2025-11-13 01:00:00",
        "auto_type": "cr_type_urgent"
    }
    
    # 测试用例3: 开始时间大于结束时间 - 应失败
    test3 = {
        "auto_plan_starttime": "2025-11-13 01:00:00",
        "auto_plan_endtime": "2025-11-12 23:59:59",
        "auto_type": "2"
    }
    
    # 测试用例4: 时间间隔超过12小时 - 应失败
    test4 = {
        "auto_plan_starttime": "2025-11-12 00:00:00",
        "auto_plan_endtime": "2025-11-12 13:00:00",
        "auto_type": "2"
    }
    
    # 测试用例5: 合法的常规任务 - 应成功
    test5 = {
        "auto_plan_starttime": "2025-11-12 23:59:59",
        "auto_plan_endtime": "2025-11-13 00:00:00",
        "auto_type": "2"
    }
    
    # 测试用例6: 合法的紧急任务 - 应成功
    today = datetime.now().strftime("%Y-%m-%d")
    test6 = {
        "auto_plan_starttime": f"{today} 23:59:59",
        "auto_plan_endtime": f"{today} 23:59:59",
        "auto_type": "cr_type_urgent"
    }
    
    # 运行测试
    test_cases = [
        (test1, "测试用例1: 常规任务，开始时间小于今天23:59:59"),
        (test2, "测试用例2: 紧急任务，开始时间大于今天23:59:59"),
        (test3, "测试用例3: 开始时间大于结束时间"),
        (test4, "测试用例4: 时间间隔超过12小时"),
        (test5, "测试用例5: 合法的常规任务"),
        (test6, "测试用例6: 合法的紧急任务")
    ]
    
    print("=== 窗口期校验函数测试 ===")
    print()
    
    for test_data, description in test_cases:
        print(f"{description}:")
        print(f"  输入数据: {test_data}")
        try:
            result, message = validate_maintenance_window(test_data)
            if result:
                print("  结果: 通过 ✓")
            else:
                print(f"  结果: 失败 ✗ - {message}")
        except Exception as e:
            print(f"  结果: 异常 ⚠️ - {str(e)}")
        print()
    
    # 异常测试：缺少参数
    print("异常测试: 缺少参数:")
    try:
        validate_maintenance_window({"auto_plan_starttime": "2025-11-12 23:59:59"})
    except KeyError as e:
        print(f"  结果: 异常捕获成功 ✗ - {str(e)}")
    print()
    
    # 异常测试：时间格式错误
    print("异常测试: 时间格式错误:")
    try:
        validate_maintenance_window({
            "auto_plan_starttime": "2025/11/12 23:59:59",
            "auto_plan_endtime": "2025-11-13 00:00:00",
            "auto_type": "2"
        })
    except ValueError as e:
        print(f"  结果: 异常捕获成功 ✗ - {str(e)}")
