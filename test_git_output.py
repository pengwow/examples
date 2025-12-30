#!/usr/bin/env python3
import subprocess
import re

# 测试脚本：分析Git log输出格式
def test_git_output():
    # 去掉-z参数，更容易查看输出
    cmd = "git log --author='pengwow' --pretty=format:'COMMIT_START%H%n%ad%n%an%nCOMMIT_END' --date=short --numstat"
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    
    print(f"Total output length: {len(output)}")
    print(f"\nFirst 500 characters:")
    print(repr(output[:500]))
    
    # 测试带-z参数的输出
    print(f"\n\n=== Testing with -z parameter ===")
    cmd_z = "git log --author='pengwow' --pretty=format:'COMMIT_START%H%n%ad%n%an%nCOMMIT_END' --date=short --numstat -z"
    output_z = subprocess.run(cmd_z, shell=True, capture_output=True, text=True).stdout
    
    print(f"Total output length with -z: {len(output_z)}")
    print(f"Number of null characters: {output_z.count('\0')}")
    
    # 分析第一个提交块
    if '\0' in output_z:
        first_block = output_z.split('\0')[0]
        print(f"\nFirst block (without -z):")
        print(repr(first_block[:500]))
        
        # 测试正则表达式
        commit_pattern = re.compile(r'COMMIT_START(.*?)\n(.*?)\n(.*?)\nCOMMIT_END(.*)', re.DOTALL)
        match = commit_pattern.search(first_block)
        if match:
            commit_hash, date, author, file_changes_str = match.groups()
            print(f"\nPattern matched!")
            print(f"Commit hash: {commit_hash}")
            print(f"Date: {date}")
            print(f"Author: {author}")
            print(f"File changes (first 300 chars): {repr(file_changes_str[:300])}")
            
            # 测试文件变更处理
            print(f"\nFile changes processing:")
            # 注意：带-z参数时，文件变更也用null分隔
            # 但我们这里没有-z参数，所以用换行分隔
            file_changes = file_changes_str.strip().split('\n')
            for change in file_changes[:10]:
                if change.strip():
                    print(f"Change: {repr(change)}")
                    parts = change.split()
                    print(f"Parts: {parts}")
                    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                        print(f"Valid: additions={parts[0]}, deletions={parts[1]}")
                    else:
                        print(f"Invalid: not enough parts or not digits")

if __name__ == "__main__":
    test_git_output()