# coding=utf-8
# 正则使用re.search配合 group()判断并提取值
# 字符串A = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
# 1.提取字符串A的CCS,也就是@之前,第一个-之间的和第二个之间
# 2. 提取字符串A的ccs-workflow,也就是@之前,第二个-之间的和第三个之间
# 3. 提取字符串A的port:8820端口的,8820,也就是port:之后@之前
# 4. 提取字符串A的最后@之后xcvdvdqwwd1002
# 5. 如果字符串A中最后@后面带-并且-等于两个,则@和第一个-之间的提取出来,如字符串A = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002-cccccsss-ddddd" 则提取出xcvdvdqwwd1002
#    如果最后@后面不带-或者-不等于两个,则不提取
# 6. 根据字符串B = '["1.1.1.1"]' 提取出ip地址,如1.1.1.1
# 7. 提取字符串A的ONE,也就是@之前第一个-之前
# 按照上面编写7个正则并验证,以上A和B都是变量,里面的内容会发生变化,不变的是结构,不要编写固定比如CCS什么不变的只有@和-和:
# 使用正则group()提取值,不要group(1)提取, 直接提取后不需要编写python二次处理

import re

def extract_info(str_a, str_b=None):
    """
    根据提供的字符串A和字符串B，使用正则表达式提取所需信息
    
    Args:
        str_a: 待处理的字符串A，结构为"XXX-XXX-XXX-XXX:XXX@XXX"
        str_b: 待处理的字符串B，可选，结构为'["XXX.XXX.XXX.XXX"]'
    
    Returns:
        None
    """
    print(f"原始字符串A: {str_a}")
    if str_b:
        print(f"原始字符串B: {str_b}")
    print("-" * 60)
    
    # 1. 提取字符串A的CCS,也就是@之前,第一个-之间的和第二个之间
    # 使用正向肯定前瞻断言，匹配第一个-和第二个-之间的内容
    pattern1 = r"[^-]+(?=-[^-]+-[^-]+-port:.*@)"
    match1 = re.search(pattern1, str_a)
    if match1:
        print(f"1. 提取字符串A中@之前，第一个-和第二个-之间的内容: {match1.group()}")
    
    # 2. 提取字符串A的ccs-workflow,也就是@之前,第二个-之间的和第三个之间
    # 使用正向肯定前瞻断言，匹配目标内容后的结构
    pattern2 = r"[^-]+-[^-]+(?=-port:.*@)"
    match2 = re.search(pattern2, str_a)
    if match2:
        print(f"2. 提取字符串A中@之前，第二个-和第三个-之间的内容: {match2.group()}")
    
    # 3. 提取字符串A的port:8820端口的,8820,也就是port:之后@之前
    # 使用正向肯定前瞻和后瞻断言，由于port:是固定宽度，可以使用后瞻
    pattern3 = r"(?<=port:)\d+(?=@)"
    match3 = re.search(pattern3, str_a)
    if match3:
        print(f"3. 提取字符串A中port:之后@之前的端口: {match3.group()}")
    
    # 4. 提取字符串A的最后@之后xcvdvdqwwd1002
    # 使用正向肯定后瞻断言，@是固定宽度
    pattern4 = r"(?<=@)[^@]+$"
    match4 = re.search(pattern4, str_a)
    if match4:
        print(f"4. 提取字符串A中@之后的内容: {match4.group()}")
    
    # 5. 如果字符串A中最后@后面带-并且-等于两个,则@和第一个-之间的提取出来
    # 使用正则表达式判断@后面是否带两个-
    has_two_hyphens = re.search(r"@[^-]+-[^-]+-[^-]+$", str_a)
    if has_two_hyphens:
        # 使用正向肯定后瞻和前瞻断言，@和-都是固定宽度
        pattern5 = r"(?<=@)[^-]+(?=-)"
        match5 = re.search(pattern5, str_a)
        if match5:
            print(f"5. 提取字符串A中@和第一个-之间的内容: {match5.group()}")
    
    # 6. 根据字符串B提取出ip地址
    if str_b:
        pattern6 = r"\d+\.\d+\.\d+\.\d+"
        match6 = re.search(pattern6, str_b)
        if match6:
            print(f"6. 提取字符串B中的IP地址: {match6.group()}")
    
    # 7. 提取字符串A的ONE,也就是@之前第一个-之前
    # 使用正向肯定前瞻断言，匹配目标内容后的结构
    pattern7 = r"^[^-]+(?=-)"
    match7 = re.search(pattern7, str_a)
    if match7:
        print(f"7. 提取字符串A中@之前第一个-之前的内容: {match7.group()}")

if __name__ == "__main__":
    # 测试用例1: 基本格式
    str_a_1 = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002"
    str_b_1 = '["1.1.1.1"]'
    
    # 测试用例2: @后带一个-
    str_a_2 = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002-cccccsss"
    
    # 测试用例3: @后带两个-
    str_a_3 = "ONE-CCS-ccs-workflow-port:8820@xcvdvdqwwd1002-cccccsss-ddddd"
    
    # 测试用例4: 不同内容但相同结构
    str_a_4 = "TWO-DDD-ddd-service-port:9930@abcdefg2003"
    str_b_4 = '["2.2.2.2"]'
    
    print("=== 测试用例1: 基本格式 ===")
    extract_info(str_a_1, str_b_1)
    print("\n" + "="*60 + "\n")
    
    print("=== 测试用例2: @后带一个- ===")
    extract_info(str_a_2)
    print("\n" + "="*60 + "\n")
    
    print("=== 测试用例3: @后带两个- ===")
    extract_info(str_a_3)
    print("\n" + "="*60 + "\n")
    
    print("=== 测试用例4: 不同内容但相同结构 ===")
    extract_info(str_a_4, str_b_4)