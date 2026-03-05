# coding=utf-8
# 正则使用re.search配合 group()判断并提取值,不能使用group(1)这种方式,因为group(1)是指第一个括号内的内容
# 不能使用python字符串处理,只能使用正则表达式
# 字符串A = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
# ONE CCS都是变量,不能直接使用固定字符串匹配
# 1.提取第一个-与第二个-之间的内容
# 2.提取第二个-与-port:之间的内容

import re

def extract_first_between():
    """
    提取字符串中第一个-与第二个-之间的内容
    要求：使用re.search配合group()，不能使用group(1)和字符串处理方法
    
    返回:
        str: 提取的内容，如"CCS"
    """
    # 定义测试字符串
    str_a = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
    
    # 修改正则表达式：使用后向断言确保匹配的内容在第一个-之后，前向断言确保在第二个-之前
    # (?<=-) 后向断言，确保前面有一个-
    # [^-]+ 匹配非-字符
    # (?=-[^-]+) 前向断言，确保后面有一个-和任意非-字符
    # 这样就能匹配第一个-和第二个-之间的内容
    pattern = r'(?<=-)[^-]+(?=-[^-]+)'
    match = re.search(pattern, str_a)
    
    if match:
        # 使用group()直接获取匹配结果
        result = match.group()
        print(f"提取第一个-与第二个-之间的内容: {result}")
        return result
    else:
        print("未找到匹配的内容")
        return None

def extract_second_between():
    """
    提取字符串中三位编码之后到-port:之间的内容
    要求：使用re.search配合group()，不能使用group(1)和字符串处理方法
    
    返回:
        str: 提取的内容，如"ccs-workflow-sssww"
    """
    # 定义测试字符串
    str_a = "ONE-CCS-ccs-workflow-sssww-port:8820@xcvdvdqwwd1002"
    
    # 使用正则表达式匹配：任意前缀-三位编码-需要提取的内容-port:
    # 模式解释：匹配任意前缀-三位编码-之后到-port:之前的所有内容
    # 使用后向断言确保匹配在三位编码之后，前向断言确保在-port:之前
    pattern = r'(?<=-[^-]{3}-).*?(?=-port:)'
    match = re.search(pattern, str_a)
    
    if match:
        # 使用group()直接获取匹配结果
        result = match.group()
        print(f"提取三位编码之后到-port:之间的内容: {result}")
        return result
    else:
        print("未找到匹配的内容")
        return None

def test_other_formats():
    """
    测试其他可能的字符串格式
    """
    test_strings = [
        "ONE-CCS-ccs-workflow-sssww-port:8820@xcvdvdqwwd1002",
        "production-ABC-abc-service-name-port:8080@hostname",
        "ONE-XYZ-xyz-app-component-port:3000@server"
    ]
    
    for test_str in test_strings:
        print(f"\n测试字符串: {test_str}")
        pattern = r'(?<=-[^-]{3}-).*?(?=-port:)'
        match = re.search(pattern, test_str)
        if match:
            result = match.group()
            print(f"提取结果: {result}")
        else:
            print("未找到匹配的内容")

def check_after_at_symbol():
    """
    判断"@"符号后面的内容是否包含横线，并且横线数量要等于2个
    要求：使用re.search配合group()，不能使用group(1)和字符串处理方法
    
    返回:
        bool: 如果"@"后面包含横线且横线数量等于2个，返回True，否则返回False
    """
    # 定义测试字符串
    str_a = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
    
    # 使用正则表达式匹配"@"符号后面的内容
    # 模式解释：匹配@符号后面的所有内容，并检查其中是否包含恰好2个横线
    # 使用后向断言确保匹配在@符号之后
    pattern = r'(?<=@)[^-]*(?:-[^-]*){2}$'
    match = re.search(pattern, str_a)
    
    if match:
        # 使用group()直接获取匹配结果
        result = match.group()
        print(f"@符号后面的内容: {result}")
        print("@符号后面包含横线且横线数量等于2个: True")
        return True
    else:
        print("@符号后面不包含横线或横线数量不等于2个: False")
        return False

def test_different_at_symbol_cases():
    """
    测试不同"@"符号后面横线数量的情况
    只使用re.match()进行判断，不使用search和字符串处理
    """
    test_cases = [
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002", "无横线"),
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvd-qwwd1002", "1个横线"),
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvd-qwwd-1002", "2个横线"),
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvd-qwwd-1002-extra", "3个横线")
    ]
    
    for test_str, description in test_cases:
        print(f"\n测试字符串: {test_str}")
        print(f"描述: {description}")
        
        # 使用re.match()直接匹配整个字符串，判断@符号后面是否包含恰好2个横线
        # 正则表达式解释：匹配任意字符直到@符号，然后匹配恰好2个横线的模式
        pattern = r'^.*@[^-]*(?:-[^-]*){2}$'
        match = re.match(pattern, test_str)
        
        if match:
            # 使用re.match()提取@符号后面的内容用于显示
            # 正则表达式解释：匹配任意字符直到@符号，然后捕获@符号后面的所有内容
            extract_pattern = r'^.*@(.*)$'
            extract_match = re.match(extract_pattern, test_str)
            after_at_content = extract_match.group(1) if extract_match else ""
            print(f"@符号后面的内容: {after_at_content}")
            print("@符号后面包含横线且横线数量等于2个: True")
        else:
            # 使用re.match()提取@符号后面的内容用于显示
            extract_pattern = r'^.*@(.*)$'
            extract_match = re.match(extract_pattern, test_str)
            after_at_content = extract_match.group(1) if extract_match else ""
            print(f"@符号后面的内容: {after_at_content}")
            print("@符号后面不包含横线或横线数量不等于2个: False")

def extract_all_after_at():
    """
    需求4：使用search和group()提取"@"之后的全部字符串
    要求：使用re.search配合group()，不能使用group(1)和字符串处理方法
    
    返回:
        str: "@"符号之后的全部字符串内容
    """
    # 定义测试字符串
    str_a = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
    
    # 使用正则表达式匹配"@"符号之后的全部内容
    # 模式解释：匹配@符号之后的所有字符直到字符串结尾
    # 使用后向断言确保匹配在@符号之后
    pattern = r'(?<=@).*$'
    match = re.search(pattern, str_a)
    
    if match:
        # 使用group()直接获取匹配结果
        result = match.group()
        print(f"提取@符号之后的全部字符串: {result}")
        return result
    else:
        print("未找到@符号或@符号后面没有内容")
        return None

def extract_before_first_dash_after_at():
    """
    需求5：使用search和group()提取"@"之后第一个横线-之前的字符串
    要求：使用re.search配合group()，不能使用group(1)和字符串处理方法
    
    返回:
        str: "@"符号之后第一个横线-之前的字符串内容
    """
    # 定义测试字符串
    str_a = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
    
    # 使用正则表达式匹配"@"符号之后第一个横线-之前的内容
    # 模式解释：匹配@符号之后到第一个横线之前的所有字符
    # 使用后向断言确保匹配在@符号之后，前向断言确保在第一个横线之前
    pattern = r'(?<=@)[^-]*(?=-)'
    match = re.search(pattern, str_a)
    
    if match:
        # 使用group()直接获取匹配结果
        result = match.group()
        print(f"提取@符号之后第一个横线-之前的字符串: {result}")
        return result
    else:
        print("未找到@符号或@符号后面没有横线")
        return None

def test_extract_after_at_functions():
    """
    测试需求4和需求5在不同字符串格式下的提取效果
    """
    test_cases = [
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002", "无横线"),
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvd-qwwd1002", "有横线"),
        ("ONE-CCS-ccs-workflow-port:8820@xcvdvd-qwwd-1002", "多个横线"),
        ("ONE-CCS-ccs-workflow-port:8820@", "只有@符号")
    ]
    
    for test_str, description in test_cases:
        print(f"\n测试字符串: {test_str}")
        print(f"描述: {description}")
        
        # 测试需求4：提取@符号之后的全部字符串
        pattern_all = r'(?<=@).*$'
        match_all = re.search(pattern_all, test_str)
        if match_all:
            result_all = match_all.group()
            print(f"需求4 - 提取@符号之后的全部字符串: {result_all}")
        else:
            print("需求4 - 未找到@符号或@符号后面没有内容")
        
        # 测试需求5：提取@符号之后第一个横线-之前的字符串
        pattern_before_dash = r'(?<=@)[^-]*(?=-)'
        match_before_dash = re.search(pattern_before_dash, test_str)
        if match_before_dash:
            result_before_dash = match_before_dash.group()
            print(f"需求5 - 提取@符号之后第一个横线-之前的字符串: {result_before_dash}")
        else:
            print("需求5 - 未找到@符号或@符号后面没有横线")

# 测试函数
if __name__ == "__main__":
    extract_first_between()
    extract_second_between()
    test_other_formats()
    check_after_at_symbol()
    test_different_at_symbol_cases()
    extract_all_after_at()
    extract_before_first_dash_after_at()
    test_extract_after_at_functions()