# 自动备份脚本使用说明

## 功能介绍

这是一个用于定时全量备份目录到SFTP服务器的Python脚本，主要功能包括：

1. 定时备份指定目录到SFTP服务器
2. 按每天、每月、每年三个周期组织备份文件
3. 自动创建所需的目录结构
4. 根据配置策略自动清理过期备份
5. 在传输前自动压缩文件

## 安装依赖

脚本依赖以下Python库：

- paramiko: 用于SFTP连接
- pyyaml: 用于解析YAML配置文件

可以使用pip安装这些依赖：

```bash
pip install paramiko pyyaml
```

## 配置说明

在使用脚本前，需要先配置`backup_config.yaml`文件。主要配置项如下：

### 源目录配置
```yaml
source:
  path: "/path/to/source/directory"  # 需要备份的源目录
```

### SFTP配置
```yaml
sftp:
  host: "sftp.example.com"           # SFTP服务器地址
  port: 22                           # SFTP服务器端口
  username: "username"               # SFTP用户名
  password: "password"               # SFTP密码（可选，如果使用密钥认证则不需要）
  key_file: ""                       # SSH私钥文件路径（可选，如果使用密码认证则不需要）
  timeout: 30                        # SFTP连接超时时间（秒）
  target_base_path: "/backup"        # SFTP上的基础备份路径
```

### 备份策略配置
```yaml
backup:
  daily:
    enabled: true                    # 是否启用每日备份
    keep_days: 30                    # 保留天数
    delete_old: true                 # 是否删除过期备份
  monthly:
    enabled: true                    # 是否启用每月备份
    keep_months: 3                   # 保留月数
    delete_old: true                 # 是否删除过期备份
  yearly:
    enabled: true                    # 是否启用每年备份
    keep_forever: true               # 是否永久保留
    delete_old: false                # 是否删除过期备份（如果keep_forever为true则忽略）
```

### 压缩配置
```yaml
compression:
  enabled: true                      # 是否启用压缩
  format: "tar.gz"                   # 压缩格式 (tar.gz, zip等)
  temp_dir: "/tmp/backup_temp"       # 临时压缩文件存放目录
```

### 日志配置
```yaml
logging:
  level: "INFO"                      # 日志级别 (DEBUG, INFO, WARNING, ERROR)
  file: "/var/log/backup_script.log" # 日志文件路径
  rotate: true                       # 是否启用日志轮转
  max_size: 10                       # 单个日志文件最大大小（MB）
  backup_count: 5                    # 保留的日志文件数量
```

## 使用方法

### 手动运行

可以通过以下命令手动运行备份脚本：

```bash
python backup_script.py [配置文件路径]
```

如果不指定配置文件路径，默认使用当前目录下的`backup_config.yaml`文件。

### 设置定时任务

要设置每天自动执行备份任务，可以使用crontab。执行以下命令编辑crontab配置：

```bash
crontab -e
```

在打开的编辑器中添加以下行（假设脚本位于`/Users/liupeng/workspace/examples/python/`目录下）：

```
# 每天凌晨2点执行备份任务
0 2 * * * cd /Users/liupeng/workspace/examples/python && python3 backup_script.py >> /var/log/backup_cron.log 2>&1
```

这会在每天凌晨2点执行备份脚本，并将输出重定向到日志文件。

## 目录结构

在SFTP服务器上，备份文件会按照以下目录结构组织：

```
/target_base_path/
├── daily/
│   ├── 20231001/
│   │   └── backup_20231001.tar.gz
│   ├── 20231002/
│   │   └── backup_20231002.tar.gz
│   └── ...
├── monthly/
│   ├── 202310/
│   │   └── backup_20231001.tar.gz
│   ├── 202311/
│   │   └── backup_20231101.tar.gz
│   └── ...
└── yearly/
    ├── 2023/
    │   └── backup_20230101.tar.gz
    ├── 2024/
    │   └── backup_20240101.tar.gz
    └── ...
```

## 注意事项

1. 请确保SFTP服务器有足够的磁盘空间存储备份文件
2. 请定期检查备份日志，确保备份任务正常执行
3. 首次运行前，请确认配置文件中的路径和认证信息正确无误
4. 对于重要数据，建议定期验证备份的完整性
5. 如果使用密钥认证，请确保私钥文件权限设置正确（chmod 600）

## 故障排除

- 如果备份失败，首先检查日志文件以获取详细错误信息
- 常见问题包括：SFTP连接问题、权限问题、磁盘空间不足等
- 确保源目录存在并且有足够的读取权限
- 确保临时目录可写，并有足够的空间存储压缩文件

## 示例配置

以下是一个完整的示例配置（仅供参考）：

```yaml
# 备份配置文件

source:
  path: "/Users/username/Documents/important_data"

sftp:
  host: "backup.example.com"
  port: 22
  username: "backup_user"
  key_file: "/Users/username/.ssh/id_rsa"
  timeout: 30
  target_base_path: "/backups/my_data"

backup:
  daily:
    enabled: true
    keep_days: 30
    delete_old: true
  monthly:
    enabled: true
    keep_months: 3
    delete_old: true
  yearly:
    enabled: true
    keep_forever: true
    delete_old: false

compression:
  enabled: true
  format: "tar.gz"
  temp_dir: "/tmp/backup_temp"

logging:
  level: "INFO"
  file: "/var/log/backup_script.log"
  rotate: true
  max_size: 10
  backup_count: 5
```