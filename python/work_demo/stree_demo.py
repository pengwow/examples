def parse_service_tree(stree_list):
    """
    解析服务树数据，实现部门层级的角色继承
    
    参数:
        stree_list: 服务树数据列表，每个元素是包含skey和角色信息的字典
        格式示例: [{'skey': '部门1.部门2.部门3', 'rd_domain_admin': 'zhangsan', 'op_group_admin': 'lisi'}]
    
    返回:
        dict: 部门及其继承后的角色信息字典
        格式示例: {'部门1': {'rd_domain_admin': 'zhangsan', 'op_group_admin': ''}, ...}
    """
    # 初始化结果字典
    result = {}
    
    # 角色类型列表
    role_types = ['rd_domain_admin', 'op_group_admin']
    
    # 父部门映射：{子部门: 父部门}
    parent_map = {}
    
    # 第一步：收集所有部门信息和层级关系
    for node in stree_list:
        skey = node.get('skey', '')
        # 按点分割得到部门层级
        departments = skey.split('.')
        
        if not departments or departments == ['']:
            continue
        
        # 记录部门层级关系
        for i in range(len(departments)):
            dept = departments[i]
            # 初始化部门的角色信息
            if dept not in result:
                result[dept] = {role: '' for role in role_types}
            
            # 记录父部门关系
            if i > 0:
                parent_dept = departments[i-1]
                if dept not in parent_map:
                    parent_map[dept] = parent_dept
        
        # 为叶子部门设置指定的角色信息
        leaf_dept = departments[-1]
        for role in role_types:
            role_value = node.get(role, '')
            if role_value:  # 只有当角色值非空时才更新
                result[leaf_dept][role] = role_value
    
    # 第二步：实现角色继承 - 从叶子部门向上传递
    # 首先找出所有叶子部门
    leaf_departments = set()
    for node in stree_list:
        skey = node.get('skey', '')
        departments = skey.split('.')
        if departments and departments != ['']:
            leaf_departments.add(departments[-1])
    
    # 从叶子部门向上传递角色信息
    for dept in leaf_departments:
        current_dept = dept
        # 向上遍历所有父部门
        while current_dept in parent_map:
            parent_dept = parent_map[current_dept]
            
            # 将当前部门的非空角色传递给父部门
            for role in role_types:
                if result[current_dept][role] and not result[parent_dept][role]:
                    result[parent_dept][role] = result[current_dept][role]
            
            current_dept = parent_dept
    
    # 第三步：确保子部门能够从父部门继承角色信息
    # 找出所有根部门（没有父部门的部门）
    root_departments = [dept for dept in result if dept not in parent_map]
    
    # 从根部门向下传递角色信息
    def propagate_down(dept):
        """从当前部门向下传播角色信息"""
        # 找出所有子部门
        children = [child for child, parent in parent_map.items() if parent == dept]
        
        for child in children:
            # 将当前部门的非空角色传递给子部门
            for role in role_types:
                if result[dept][role] and not result[child][role]:
                    result[child][role] = result[dept][role]
            
            # 递归处理子部门
            propagate_down(child)
    
    # 从每个根部门开始向下传播
    for root_dept in root_departments:
        propagate_down(root_dept)
    
    return result

# 测试函数
def test_parse_service_tree():
    # 测试数据
    stree_list = [
        {
            'skey': '部门1.部门2.部门3',
            'rd_domain_admin': 'zhangsan',
            'op_group_admin': 'lisi'
        },
        {
            'skey': '部门1.部门2.部门4',
            'rd_domain_admin': '',  # 空字符串，应该继承部门2或部门1的角色
            'op_group_admin': 'wangwu'
        }
    ]
    
    result = parse_service_tree(stree_list)
    print("解析结果:")
    for dept, roles in result.items():
        print(f"{dept}: {roles}")

if __name__ == "__main__":
    test_parse_service_tree()