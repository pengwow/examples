# 请求数据：
data = {"op":"GET", "type": "ALL", "size": 100, "timeFrom": 1763433220000, "timeTill": 1763443220000, "hasChildren": False, "page": 1, "level": [20, 10, 5], "status": ["CLOSE"]}
# data中size和page两个参数为分页查找涉及的关联变量，其余字段可忽略
# 1.根据requests.post请求返回结果格式，如res={"datas": {"hits":{"total": 476, "hits": [{"id":123, "data":"xxxx"},]}}}
# 2.返回数据中res['datas']['hits']['total']为结果总数， 实际数据为res_data=res['datas']['hits']['hits']
# 如何结合请求数据中的size和page，循环递归调用接口返回数据合并到结果集列表中

import requests
from math import ceil
from typing import Dict, List, Any

def get_all_paginated_data(url: str, request_data: Dict[str, Any], headers: Dict[str, str] = None, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    分页获取所有数据的函数
    
    参数:
        url (str): API接口地址
        request_data (dict): 请求数据字典，必须包含size字段，建议包含page字段
        headers (dict, optional): 请求头信息，默认为None
        max_retries (int, optional): 单次请求的最大重试次数，默认为3
    
    返回:
        list: 所有页面数据合并后的列表
    
    异常:
        requests.RequestException: 网络请求异常
        KeyError: 返回数据格式不符合预期
        ValueError: 参数验证失败
    """
    # 参数验证
    if not isinstance(request_data, dict):
        raise ValueError("request_data必须是字典类型")
    
    if "size" not in request_data:
        raise ValueError("request_data必须包含size字段")
    
    # 确保size为正数
    size = request_data.get("size", 100)
    if size <= 0:
        raise ValueError("size必须为正整数")
    
    # 初始化结果列表
    all_results = []
    
    # 第一次请求获取总数
    first_request_data = request_data.copy()
    first_request_data["page"] = 1  # 确保从第一页开始
    
    # 获取总数和第一页数据
    try:
        response = requests.post(url, json=first_request_data, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        res = response.json()
        
        # 提取总数
        total_count = res["datas"]["hits"]["total"]
        
        # 添加第一页数据
        first_page_data = res["datas"]["hits"]["hits"]
        all_results.extend(first_page_data)
        
        # 计算总页数
        total_pages = ceil(total_count / size)
        
        print(f"找到{total_count}条数据，每页{size}条，共{total_pages}页")
        print(f"已获取第1页数据，共{len(first_page_data)}条")
        
        # 如果只有一页数据，直接返回
        if total_pages <= 1:
            print("已是最后一页，返回数据")
            return all_results
        
        # 循环获取剩余页面数据
        for page in range(2, total_pages + 1):
            # 复制请求数据并更新页码
            page_request_data = request_data.copy()
            page_request_data["page"] = page
            
            # 获取当前页数据
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    page_response = requests.post(url, json=page_request_data, headers=headers)
                    page_response.raise_for_status()
                    
                    page_res = page_response.json()
                    page_data = page_res["datas"]["hits"]["hits"]
                    
                    all_results.extend(page_data)
                    print(f"已获取第{page}页数据，共{len(page_data)}条")
                    success = True
                    
                except requests.RequestException as e:
                    retry_count += 1
                    print(f"获取第{page}页数据失败，第{retry_count}次重试... 错误: {str(e)}")
                    
                    if retry_count >= max_retries:
                        raise requests.RequestException(f"获取第{page}页数据失败，已达到最大重试次数")
            
    except KeyError as e:
        raise KeyError(f"返回数据格式不符合预期，缺少必要的字段: {str(e)}")
    except requests.RequestException as e:
        raise requests.RequestException(f"网络请求失败: {str(e)}")
    
    print(f"数据获取完成，共获取{len(all_results)}条数据")
    return all_results


def get_all_paginated_data_recursive(url: str, request_data: Dict[str, Any], headers: Dict[str, str] = None, 
                                    current_page: int = 1, all_results: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    递归方式分页获取所有数据的函数
    
    参数:
        url (str): API接口地址
        request_data (dict): 请求数据字典，必须包含size字段
        headers (dict, optional): 请求头信息，默认为None
        current_page (int, optional): 当前页码，默认为1
        all_results (list, optional): 已收集的结果列表，默认为None
    
    返回:
        list: 所有页面数据合并后的列表
    
    异常:
        requests.RequestException: 网络请求异常
        KeyError: 返回数据格式不符合预期
        ValueError: 参数验证失败
    """
    # 参数验证
    if not isinstance(request_data, dict):
        raise ValueError("request_data必须是字典类型")
    
    if "size" not in request_data:
        raise ValueError("request_data必须包含size字段")
    
    # 初始化结果列表
    if all_results is None:
        all_results = []
    
    # 准备当前页的请求数据
    page_request_data = request_data.copy()
    page_request_data["page"] = current_page
    size = page_request_data["size"]
    
    # 发送请求
    response = requests.post(url, json=page_request_data, headers=headers)
    response.raise_for_status()
    
    res = response.json()
    
    # 对于第一页，获取总数信息
    if current_page == 1:
        total_count = res["datas"]["hits"]["total"]
        total_pages = ceil(total_count / size)
        print(f"[递归方式] 找到{total_count}条数据，每页{size}条，共{total_pages}页")
    
    # 添加当前页数据
    current_page_data = res["datas"]["hits"]["hits"]
    all_results.extend(current_page_data)
    print(f"[递归方式] 已获取第{current_page}页数据，共{len(current_page_data)}条")
    
    # 判断是否还有下一页
    if len(current_page_data) == size:  # 如果当前页数据量等于size，可能还有下一页
        # 递归获取下一页
        return get_all_paginated_data_recursive(url, request_data, headers, current_page + 1, all_results)
    else:
        # 已经是最后一页
        print(f"[递归方式] 数据获取完成，共获取{len(all_results)}条数据")
        return all_results


# 示例使用（模拟环境）
if __name__ == "__main__":
    # 模拟API URL
    mock_api_url = "http://example.com/api/events"
    
    # 模拟请求数据
    request_data = data.copy()  # 使用文件开头定义的data
    
    print("=== 分页获取数据示例 ===")
    print(f"请求数据: {request_data}")
    print("注意: 以下代码为示例，在实际环境中需要替换为真实的API地址")
    print()
    
    # 示例代码不会实际发送请求，只会打印调用方式
    print("# 非递归方式调用示例:")
    print("# try:")
    print("#     all_data = get_all_paginated_data(mock_api_url, request_data)")
    print("#     print(f'获取到的数据总数: {len(all_data)}')")
    print("# except Exception as e:")
    print("#     print(f'发生错误: {str(e)}')")
    print()
    
    print("# 递归方式调用示例:")
    print("# try:")
    print("#     all_data_recursive = get_all_paginated_data_recursive(mock_api_url, request_data)")
    print("#     print(f'获取到的数据总数: {len(all_data_recursive)}')")
    print("# except Exception as e:")
    print("#     print(f'发生错误: {str(e)}')")
    print()
    
    print("# 提示:")
    print("# 1. 实际使用时，替换mock_api_url为真实的API地址")
    print("# 2. 如果API需要认证，请在headers参数中提供认证信息")
    print("# 3. 根据实际情况调整size参数以优化请求性能")
    print("# 4. 对于大量数据，非递归方式可能更稳定")

