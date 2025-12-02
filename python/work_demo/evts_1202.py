# coding=utf-8
# 正则使用re.search配合 group()判断并提取值,不能使用group(1)这种方式,因为group(1)是指第一个括号内的内容
# 不能使用python字符串处理,只能使用正则表达式
# 字符串A = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
# 1.提取第一个-与第二个-之间的内容

import re

def extract_content():
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

# 测试函数
if __name__ == "__main__":
    extract_content()