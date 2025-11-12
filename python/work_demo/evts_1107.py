# 编写一个正则表达式，用于匹配主机名中第三位的字母是h的
import re

pattern = r'^[a-zA-Z0-9]{2}h[a-zA-Z0-9]*$'

# 测试正则表达式
test_cases = [
    'abch',
    'abch123',
    'achch',
    'acch123',
    'a123',
    'ah123'
]

for case in test_cases:
    if re.match(pattern, case):
        print(f'{case} 匹配成功')
    else:
        print(f'{case} 匹配失败')