#!/usr/bin/env python3
"""测试HTML清理功能"""

import re

def test_html_cleanup():
    """测试HTML清理功能"""
    
    # 模拟HTML内容（包含标签和换行符）
    html_content = """<html>
 <head>
  <title>测试标题</title>
 </head>
 <body>
  <p>第一段内容</p>
  
  <p>第二段内容</p>
  
  
  <p>第三段内容</p>
  
  <div>  这里有很多空格    </div>
 </body>
</html>"""
    
    print("原始HTML内容:")
    print(repr(html_content))
    print("\n" + "="*50 + "\n")
    
    # 旧方法（只去除HTML标签）
    old_method = re.sub(r'<[^>]+>', '', html_content)
    print("旧方法结果（只去除HTML标签）:")
    print(repr(old_method))
    print("显示效果:")
    print(old_method)
    print("\n" + "="*50 + "\n")
    
    # 新方法（完整清理）
    # 去除HTML标签
    main_body = re.sub(r'<[^>]+>', '', html_content)
    # 清理多余换行符：替换多个连续换行符为单个换行符
    main_body = re.sub(r'\n{3,}', '\n\n', main_body)
    # 清理行首和行尾的空白字符
    main_body = re.sub(r'^\s+|\s+$', '', main_body, flags=re.MULTILINE)
    # 清理行内的多余空白字符
    main_body = re.sub(r'\s{2,}', ' ', main_body)
    
    print("新方法结果（完整清理）:")
    print(repr(main_body))
    print("显示效果:")
    print(main_body)
    print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    test_html_cleanup()