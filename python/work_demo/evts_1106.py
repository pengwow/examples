# 维护期规则拆分处理
# conditions_list = [{"A": [{"con": "xxx", 'sno':'A'}]}, {"A or B": [{"con": "xxx", 'sno':'A'}, {"con": "xxx", 'sno':'B"}]}, {"C or D": [{"con": "xxx", 'sno':'C'}, {"con": "xxx", 'sno':'D"}]}]
# 编写一个函数，传递参数一conditions_list，参数二为分割数量n，如何根据conditions_list进行拆分，将列表内的dict字典进行遍历，然后根据遍历出来的value再次进行提取，计算数量，如果数量超过n则重新计算，并将结果插入到列表中
# 如果超过value的值第一个元素是n，第二个计数超过n则将第一个和第二个一组放到下次
# 如上：当n为1时，执行结果为[[{"A": [{"con": "xxx", 'sno':'A'}]}], [{"A or B": [{"con": "xxx", 'sno':'A'}, {"con": "xxx", 'sno':'B"}]}], [{"C or D": [{"con": "xxx", 'sno':'C'}, {"con": "xxx", 'sno':'D"}]}]]
# 当n为3时，执行结果为[[{"A": [{"con": "xxx", 'sno':'A'}]}, {"A or B": [{"con": "xxx", 'sno':'A'}, {"con": "xxx", 'sno':'B"}]}], [{"C or D": [{"con": "xxx", 'sno':'C'}, {"con": "xxx", 'sno':'D"}]}]]


def split_conditions(conditions_list, n):
    """
    根据条件列表和分割数量进行规则拆分
    
    参数：
        conditions_list (list): 包含条件字典的列表，每个字典的值为条件列表
        n (int): 分割数量，用于控制每个分组的条件总数上限
    
    返回：
        list: 嵌套列表，每个子列表包含一组条件字典
    
    异常：
        TypeError: 当输入参数类型不正确时
        ValueError: 当分割数量n小于等于0时
    """
    # 参数验证
    if not isinstance(conditions_list, list):
        raise TypeError("conditions_list必须是列表类型")
    if not isinstance(n, int):
        raise TypeError("分割数量n必须是整数类型")
    if n <= 0:
        raise ValueError("分割数量n必须大于0")
    
    # 初始化结果列表和当前组
    result = []
    current_group = []
    current_count = 0
    
    # 遍历条件列表中的每个字典
    for condition_dict in conditions_list:
        if not isinstance(condition_dict, dict) or not condition_dict:
            # 跳过空字典或非字典元素
            continue
        
        # 获取字典中的value（条件列表）
        # 假设每个字典只有一个键值对
        value_list = list(condition_dict.values())[0]
        
        # 计算当前条件字典的条件数量
        condition_count = len(value_list)
        
        # 判断是否需要创建新组
        # 如果当前组为空，或者当前组条件数加上当前条件数不超过n
        if not current_group or (current_count + condition_count <= n):
            # 添加到当前组
            current_group.append(condition_dict)
            current_count += condition_count
        else:
            # 将当前组添加到结果中，并创建新组
            result.append(current_group)
            current_group = [condition_dict]
            current_count = condition_count
    
    # 处理最后一个组
    if current_group:
        result.append(current_group)
    
    return result


# 测试代码
if __name__ == "__main__":
    # 测试样例
    test_conditions = [
        {"A": [{"con": "xxx", 'sno': 'A'}]},
        {"A or B": [{"con": "xxx", 'sno': 'A'}, {"con": "xxx", 'sno': 'B'}]},
        {"C or D": [{"con": "xxx", 'sno': 'C'}, {"con": "xxx", 'sno': 'D'}]},
        {"E or F": [{"con": "xxx", 'sno': 'E'}, {"con": "xxx", 'sno': 'F'}]},
        {"G or H": [{"con": "xxx", 'sno': 'G'}, {"con": "xxx", 'sno': 'H'}]},
        {"I or J": [{"con": "xxx", 'sno': 'I'}, {"con": "xxx", 'sno': 'J'}]},
        {"K or L": [{"con": "xxx", 'sno': 'K'}, {"con": "xxx", 'sno': 'L'}]},
        {"M or N": [{"con": "xxx", 'sno': 'M'}, {"con": "xxx", 'sno': 'N'}]},
        {"O or P": [{"con": "xxx", 'sno': 'O'}, {"con": "xxx", 'sno': 'P'}]},
        {"Q or R": [{"con": "xxx", 'sno': 'Q'}, {"con": "xxx", 'sno': 'R'}]},
        {"S or T": [{"con": "xxx", 'sno': 'S'}, {"con": "xxx", 'sno': 'T'}]},
        {"U or V": [{"con": "xxx", 'sno': 'U'}, {"con": "xxx", 'sno': 'V'}]},
        {"W or X": [{"con": "xxx", 'sno': 'W'}, {"con": "xxx", 'sno': 'X'}]},
        {"Y or Z": [{"con": "xxx", 'sno': 'Y'}, {"con": "xxx", 'sno': 'Z'}]},

    ]
    
    # 测试n=1的情况
    print("当n=1时的分割结果：")
    result_n1 = split_conditions(test_conditions, 1)
    print(result_n1)
    
    # 测试n=3的情况
    print("\n当n=3时的分割结果：")
    result_n3 = split_conditions(test_conditions, 3)
    print(result_n3)
    
    # 测试n=5的情况
    print("\n当n=5时的分割结果：")
    result_n5 = split_conditions(test_conditions, 25)
    print(result_n5)
    
    # 测试空列表
    print("\n当conditions_list为空时的分割结果：")
    result_empty = split_conditions([], 2)
    print(result_empty)
    
    # 测试异常情况
    try:
        split_conditions(test_conditions, 0)
    except ValueError as e:
        print(f"\n异常测试（n=0）: {e}")
    
    try:
        split_conditions("not a list", 2)
    except TypeError as e:
        print(f"异常测试（非列表输入）: {e}")


