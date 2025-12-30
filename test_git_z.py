#!/usr/bin/env python3
import subprocess
import re

# 测试脚本：分析带-z参数的Git log输出格式和处理逻辑
def test_git_z_output():
    # 使用-z参数的完整命令
    cmd = "git log --author='pengwow' --pretty=format:'COMMIT_START%H%n%ad%n%an%nCOMMIT_END' --date=short --numstat -z"
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    
    print(f"Total output length with -z: {len(output)}")
    print(f"Number of null characters: {output.count('\0')}")
    
    # 使用null字符分割
    all_parts = output.split('\0')
    print(f"Number of parts after split: {len(all_parts)}")
    
    # 分析前几个部分
    print(f"\n\nAnalyzing first 3 parts:")
    for i, part in enumerate(all_parts[:3]):
        if part.strip():
            print(f"\nPart {i} (length: {len(part)}):")
            print(repr(part))
    
    # 重新构建提交块
    commits = []
    current_commit = ""
    
    for part in all_parts:
        if part.startswith("COMMIT_START"):
            # 如果已有当前提交，先处理它
            if current_commit:
                commits.append(current_commit)
            # 开始新提交
            current_commit = part
        else:
            # 添加到当前提交
            current_commit += "\0" + part
    
    # 处理最后一个提交
    if current_commit:
        commits.append(current_commit)
    
    print(f"\n\nFound {len(commits)} complete commits.")
    
    # 分析第一个完整提交
    if commits:
        first_commit = commits[0]
        print(f"\nFirst commit block (length: {len(first_commit)}):")
        print(repr(first_commit[:500]) + "...")
        
        # 测试正则表达式
        commit_pattern = re.compile(r'COMMIT_START(.*?)\n(.*?)\n(.*?)\nCOMMIT_END(.*)', re.DOTALL)
        match = commit_pattern.search(first_commit)
        if match:
            commit_hash, date, author, file_changes_str = match.groups()
            print(f"\nPattern matched!")
            print(f"Commit hash: {commit_hash}")
            print(f"Date: {date}")
            print(f"Author: {author}")
            print(f"File changes (length: {len(file_changes_str)}):")
            print(repr(file_changes_str[:300]) + "...")
            
            # 处理文件变更（带-z参数，用null分隔）
            print(f"\nProcessing file changes with -z:")
            file_changes = file_changes_str.split('\0')
            print(f"Number of file changes: {len(file_changes)}")
            
            additions, deletions = 0, 0
            valid_changes = 0
            invalid_changes = 0
            
            for change in file_changes:
                if not change.strip():
                    continue
                
                print(f"Change line: {repr(change)}")
                parts = change.split()
                
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    add = int(parts[0])
                    delete = int(parts[1])
                    additions += add
                    deletions += delete
                    valid_changes += 1
                    print(f"  ✓ Valid: +{add}, -{delete}")
                else:
                    invalid_changes += 1
                    print(f"  ✗ Invalid: {parts}")
            
            print(f"\nSummary:")
            print(f"Valid file changes: {valid_changes}")
            print(f"Invalid file changes: {invalid_changes}")
            print(f"Total additions: {additions}")
            print(f"Total deletions: {deletions}")
            print(f"Total changes: {additions + deletions}")

if __name__ == "__main__":
    test_git_z_output()