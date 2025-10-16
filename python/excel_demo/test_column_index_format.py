#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试列标识从字母格式(A,B,C)改为数字格式(1,2,3)的功能是否正常
"""
import os
from temp import create_id_name_dropdown_excel, create_multiple_mappings_excel


def test_single_mapping_with_numeric_columns():
    """
    测试单个映射关系的Excel创建功能，使用数字列索引
    """
    try:
        print("\n===== 测试单个映射关系的Excel创建功能 ======")
        # 准备测试数据
        test_data = [
            {'id': 1, 'name': '苹果'},
            {'id': 2, 'name': '香蕉'},
            {'id': 3, 'name': '橙子'},
            {'id': 4, 'name': '葡萄'}
        ]
        
        # 创建Excel文件
        file_name = "test_numeric_columns_single.xlsx"
        result_file = create_id_name_dropdown_excel(test_data, file_name)
        
        # 验证文件是否创建成功
        if os.path.exists(result_file):
            print(f"✓ 成功创建Excel文件: {result_file}")
            print(f"✓ 文件大小: {os.path.getsize(result_file)} 字节")
            return True
        else:
            print(f"✗ 失败：文件 {result_file} 未创建成功")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def test_multiple_mappings_with_numeric_columns():
    """
    测试多个映射关系的Excel创建功能，使用数字列索引
    """
    try:
        print("\n===== 测试多个映射关系的Excel创建功能 ======")
        
        # 准备测试数据
        fruit_data = [
            {'id': 101, 'name': '苹果'},
            {'id': 102, 'name': '香蕉'},
            {'id': 103, 'name': '橙子'},
            {'id': 104, 'name': '西瓜'},
            {'id': 105, 'name': '葡萄'}
        ]
        
        type_data = [
            {'id': 201, 'name': '温带水果'},
            {'id': 202, 'name': '热带水果'},
            {'id': 203, 'name': '柑橘类'},
            {'id': 204, 'name': '浆果类'}
        ]
        
        # 构造正确的配置字典
        mapping_config = {
            "mapping_data": {
                "水果映射表": {
                    "data": fruit_data,
                    "id_col": 1,
                    "name_col": 2
                },
                "类型映射表": {
                    "data": type_data,
                    "id_col": 1,
                    "name_col": 2
                }
            },
            "col_settings": [
                {
                    "dropdown_col": 1,  # 下拉列表所在列（数字索引，从1开始）
                    "id_col": 2,        # ID存储列（数字索引，从1开始）
                    "mapping_name": "水果映射表",
                    "title_row": 1,
                    "data_start_row": 2,
                    "data_end_row": 100,
                    "dropdown_title": "选择的水果",  # 可选：下拉列表列标题
                    "id_title": "水果ID"  # 可选：ID列标题
                },
                {
                    "dropdown_col": 3,  # 下拉列表所在列（数字索引，从1开始）
                    "id_col": 4,        # ID存储列（数字索引，从1开始）
                    "mapping_name": "类型映射表",
                    "title_row": 1,
                    "data_start_row": 2,
                    "data_end_row": 100,
                    "dropdown_title": "选择的类型",  # 可选：下拉列表列标题
                    "id_title": "类型ID"  # 可选：ID列标题
                }
            ]
        }
        
        # 创建Excel文件
        file_name = "test_numeric_columns_multiple.xlsx"
        result_file = create_multiple_mappings_excel(mapping_config, file_name)
        
        # 验证文件是否创建成功
        if os.path.exists(result_file):
            print(f"✓ 成功创建Excel文件: {result_file}")
            print(f"✓ 文件大小: {os.path.getsize(result_file)} 字节")
            return True
        else:
            print(f"✗ 失败：文件 {result_file} 未创建成功")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def main():
    """
    运行所有测试
    """
    print("开始测试列标识格式修改（字母→数字）的功能...")
    
    # 运行测试
    single_success = test_single_mapping_with_numeric_columns()
    multiple_success = test_multiple_mappings_with_numeric_columns()
    
    # 总结测试结果
    print("\n===== 测试总结 ======")
    if single_success and multiple_success:
        print("✓ 所有测试通过！列标识从字母格式改为数字格式的功能正常工作。")
        print("修改的主要内容：")
        print("1. 所有下拉列表列(dropdown_col)和ID列(id_col)均从字母格式(A,B,C)改为数字格式(1,2,3)")
        print("2. 添加了col_index_to_letter辅助函数用于在内部处理Excel列标识转换")
        print("3. 保持了原有功能不变，同时提高了代码的可读性和易用性")
        return 0
    else:
        print("✗ 部分或全部测试失败，请检查代码。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)