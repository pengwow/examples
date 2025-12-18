# python如何查找字符串文本中"dfdfdf\n级别: 主要\n"级别:后面到回车换行之前的字符串,分为:主要,次要,严重,灾难,通知,信息等级别,不能超出这个范围
import re


def extract_levels(text: str) -> list:
    """
    从文本中提取所有"级别:"后面到换行符之前的字符串，并验证是否在预定义范围内
    
    参数:
        text: 要搜索的文本内容
        
    返回:
        list: 包含所有有效级别的列表，如果没有找到或所有匹配都无效则返回空列表
        
    预定义允许的级别: ['主要', '次要', '严重', '灾难', '通知', '信息']
    """
    # 预定义允许的级别列表
    allowed_levels = ['主要', '次要', '严重', '灾难', '通知', '信息']
    
    # 定义正则表达式模式：匹配"级别:"后面到换行符之前的内容，支持中英文冒号和0个或多个空格
    pattern = r'级别[：:]\s*([^\n]+)'
    
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, text)
    
    # 过滤出有效级别
    valid_levels = [level.strip() for level in matches if level.strip() in allowed_levels]
    
    return valid_levels


def extract_first_valid_level(text: str) -> str or None:
    """
    从文本中提取第一个有效级别
    
    参数:
        text: 要搜索的文本内容
        
    返回:
        str or None: 找到的第一个有效级别，如果没有找到则返回None
        
    预定义允许的级别: ['主要', '次要', '严重', '灾难', '通知', '信息']
    """
    # 预定义允许的级别列表
    allowed_levels = ['主要', '次要', '严重', '灾难', '通知', '信息']
    
    # 定义正则表达式模式：匹配"级别:"后面到换行符之前的内容，支持中英文冒号和0个或多个空格
    pattern = r'级别[：:]\s*([^\n]+)'
    
    # 使用正则表达式查找第一个匹配项
    match = re.search(pattern, text)
    
    if match:
        level = match.group(1).strip()
        # 验证级别是否在允许范围内
        if level in allowed_levels:
            return level
    
    return None


# 示例用法
if __name__ == "__main__":
    # 测试文本 - 包含中英文冒号和不同数量的空格
    test_text = """
    dfdfdf
    级别: 主要
    其他内容
    级别：次要
    更多内容
    级别:无效级别
    级别： 严重
    级别:灾难
    级别： 通知
    级别: 信息
    级别：   多个空格
    级别:    四个空格
    级别：	制表符
    最后一行
    """
    
    print("测试文本:")
    print(test_text)
    print("\n=== 提取所有有效级别 ===")
    all_levels = extract_levels(test_text)
    print(f"所有有效级别: {all_levels}")
    
    print("\n=== 提取第一个有效级别 ===")
    first_level = extract_first_valid_level(test_text)
    print(f"第一个有效级别: {first_level}")
    
    # 测试另一个文本
    test_text2 = "这是一个没有级别的文本"
    print("\n=== 测试没有级别的文本 ===")
    print(f"文本: {test_text2}")
    print(f"提取结果: {extract_levels(test_text2)}")
    print(f"第一个有效级别: {extract_first_valid_level(test_text2)}")
