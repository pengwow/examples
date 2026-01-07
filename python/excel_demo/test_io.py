import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from export_excel_1231 import export_to_excel, import_from_excel
from io import BytesIO

# 测试IO流功能
def test_io_functionality():
    # 示例数据
    A = [
        {"hostname":"192.168.1.1","ip":"192.168.1.1","mac":"00:11:22:33:44:55"},
        {"hostname":"192.168.1.2","ip":"192.168.1.2","mac":"00:11:22:33:44:56"},
        {"hostname":"192.168.1.3","ip":"192.168.1.3","mac":"00:11:22:33:44:57","status":"active"}  # 包含额外字段
    ]
    
    print("=== IO流功能测试 ===")
    
    # 1. 导出到BytesIO
    print("\n1. 导出数据到BytesIO对象...")
    excel_buffer = export_to_excel(A)
    
    # 2. 验证BytesIO对象
    print(f"2. BytesIO对象大小: {excel_buffer.getbuffer().nbytes} 字节")
    
    # 3. 从BytesIO导入数据
    print("3. 从BytesIO对象导入数据...")
    imported_data = import_from_excel(excel_buffer)
    
    # 4. 验证数据完整性
    print("4. 验证数据完整性:")
    print(f"   原数据条数: {len(A)}")
    print(f"   导入数据条数: {len(imported_data)}")
    print(f"   数据格式是否一致: {all(isinstance(item, dict) for item in imported_data)}")
    
    # 5. 详细比较数据
    if len(A) == len(imported_data):
        all_match = True
        for i, (orig, imported) in enumerate(zip(A, imported_data)):
            # 获取所有可能的键
            all_keys = set(orig.keys()) | set(imported.keys())
            row_match = True
            for key in all_keys:
                if orig.get(key, "") != imported.get(key, ""):
                    row_match = False
                    break
            if not row_match:
                all_match = False
                print(f"   行 {i+1} 数据不匹配:")
                print(f"      原数据: {orig}")
                print(f"      导入数据: {imported}")
        
        if all_match:
            print("   所有数据完全匹配！")
    
    return len(A) == len(imported_data)

# 测试文件对象功能
def test_file_object():
    # 示例数据
    A = [
        {"hostname":"192.168.2.1","ip":"192.168.2.1","mac":"00:11:22:33:44:60"},
        {"hostname":"192.168.2.2","ip":"192.168.2.2","mac":"00:11:22:33:44:61"}
    ]
    
    print("\n=== 文件对象功能测试 ===")
    
    # 1. 创建BytesIO对象
    output_buffer = BytesIO()
    
    # 2. 导出到BytesIO对象
    print("1. 导出数据到BytesIO对象...")
    export_to_excel(A, output_buffer)
    
    # 3. 重置指针
    output_buffer.seek(0)
    
    # 4. 从BytesIO对象导入
    print("2. 从BytesIO对象导入数据...")
    imported_data = import_from_excel(output_buffer)
    
    # 5. 验证
    print(f"3. 原数据条数: {len(A)}")
    print(f"   导入数据条数: {len(imported_data)}")
    
    return len(A) == len(imported_data)

if __name__ == "__main__":
    # 运行测试
    test1_passed = test_io_functionality()
    test2_passed = test_file_object()
    
    print("\n=== 测试总结 ===")
    if test1_passed and test2_passed:
        print("✅ 所有IO流测试通过！")
        print("   - 导出到BytesIO功能正常")
        print("   - 从BytesIO导入功能正常")
        print("   - 文件对象作为参数功能正常")
    else:
        print("❌ 部分测试失败！")
        print(f"   - IO流功能测试: {'通过' if test1_passed else '失败'}")
        print(f"   - 文件对象测试: {'通过' if test2_passed else '失败'}")
