#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时备份脚本

功能：
1. 定时全量备份一个目录到SFTP指定目录
2. 按照每天、每月、每年的周期组织备份文件
3. 自动创建目录结构
4. 根据配置清理过期备份
5. 本地传输前进行压缩

用法：
python backup_script.py [配置文件路径]

依赖：
- paramiko: 用于SFTP连接
- pyyaml: 用于解析YAML配置文件
"""

import os
import sys
import time
import yaml
import logging
import argparse
import datetime
import shutil
import tarfile
import zipfile
from stat import S_ISDIR
import paramiko


class BackupManager:
    """备份管理类，负责执行备份操作"""
    
    def __init__(self, config_path):
        """
        初始化备份管理器
        
        参数:
            config_path: 配置文件路径
        
        异常:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML配置文件解析错误
        """
        # 读取配置文件
        self.config = self._read_config(config_path)
        
        # 初始化日志
        self._init_logging()
        
        # 获取当前日期
        self.now = datetime.datetime.now()
        
        # 源目录路径
        self.source_path = self.config['source']['path']
        
        # SFTP配置
        self.sftp_config = self.config['sftp']
        
        # 备份配置
        self.backup_config = self.config['backup']
        
        # 压缩配置
        self.compression_config = self.config['compression']
        
        # 创建临时目录
        if not os.path.exists(self.compression_config['temp_dir']):
            os.makedirs(self.compression_config['temp_dir'])
        
        # SFTP客户端
        self.sftp = None
        self.ssh = None
    
    def _read_config(self, config_path):
        """
        读取YAML配置文件
        
        参数:
            config_path: 配置文件路径
        
        返回:
            配置字典
        
        异常:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML配置文件解析错误
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件解析错误: {e}")
    
    def _init_logging(self):
        """\初始化日志系统"""
        log_config = self.config['logging']
        log_level = getattr(logging, log_config['level'].upper(), logging.INFO)
        
        # 创建日志器
        logger = logging.getLogger('backup_script')
        logger.setLevel(log_level)
        
        # 清空已有的处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 创建文件处理器
        if log_config['file']:
            if log_config['rotate']:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_config['file'],
                    maxBytes=log_config['max_size'] * 1024 * 1024,
                    backupCount=log_config['backup_count']
                )
            else:
                file_handler = logging.FileHandler(log_config['file'])
            
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        self.logger = logger
    
    def _connect_sftp(self):
        """
        连接SFTP服务器
        
        异常:
            paramiko.SSHException: SFTP连接失败
        """
        try:
            self.logger.info(f"连接到SFTP服务器: {self.sftp_config['host']}:{self.sftp_config['port']}")
            
            # 创建SSH客户端
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接服务器
            if self.sftp_config.get('key_file'):
                self.ssh.connect(
                    hostname=self.sftp_config['host'],
                    port=self.sftp_config['port'],
                    username=self.sftp_config['username'],
                    key_filename=self.sftp_config['key_file'],
                    timeout=self.sftp_config['timeout']
                )
            else:
                self.ssh.connect(
                    hostname=self.sftp_config['host'],
                    port=self.sftp_config['port'],
                    username=self.sftp_config['username'],
                    password=self.sftp_config.get('password'),
                    timeout=self.sftp_config['timeout']
                )
            
            # 创建SFTP客户端
            self.sftp = self.ssh.open_sftp()
            self.logger.info("SFTP连接成功")
        except Exception as e:
            self.logger.error(f"SFTP连接失败: {e}")
            raise paramiko.SSHException(f"SFTP连接失败: {e}")
    
    def _disconnect_sftp(self):
        """断开SFTP连接"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        self.logger.info("SFTP连接已断开")
    
    def _sftp_makedirs(self, path):
        """
        在SFTP服务器上创建多级目录
        
        参数:
            path: 要创建的目录路径
        """
        try:
            self.sftp.stat(path)
        except FileNotFoundError:
            # 递归创建父目录
            dirname = os.path.dirname(path)
            if dirname and dirname != '/':
                self._sftp_makedirs(dirname)
            # 创建当前目录
            self.sftp.mkdir(path)
            self.logger.info(f"在SFTP上创建目录: {path}")
    
    def _compress_directory(self, source_dir, output_path, compression_format):
        """
        压缩目录
        
        参数:
            source_dir: 源目录路径
            output_path: 输出文件路径
            compression_format: 压缩格式
        
        返回:
            压缩文件路径
        
        异常:
            Exception: 压缩过程失败
        """
        try:
            self.logger.info(f"开始压缩目录: {source_dir}")
            
            if compression_format == 'tar.gz':
                with tarfile.open(output_path, 'w:gz') as tar:
                    tar.add(source_dir, arcname=os.path.basename(source_dir))
            elif compression_format == 'zip':
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                            zipf.write(file_path, arcname)
            else:
                raise ValueError(f"不支持的压缩格式: {compression_format}")
            
            self.logger.info(f"目录压缩完成，输出文件: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"目录压缩失败: {e}")
            raise Exception(f"目录压缩失败: {e}")
    
    def _upload_file(self, local_path, remote_path):
        """
        上传文件到SFTP服务器
        
        参数:
            local_path: 本地文件路径
            remote_path: 远程文件路径
        
        异常:
            Exception: 文件上传失败
        """
        try:
            self.logger.info(f"开始上传文件: {local_path} -> {remote_path}")
            self.sftp.put(local_path, remote_path)
            self.logger.info(f"文件上传完成")
        except Exception as e:
            self.logger.error(f"文件上传失败: {e}")
            raise Exception(f"文件上传失败: {e}")
    
    def _clean_old_backups(self, backup_type):
        """
        清理过期备份
        
        参数:
            backup_type: 备份类型 (daily, monthly, yearly)
        """
        config = self.backup_config[backup_type]
        if not config['delete_old']:
            self.logger.info(f"备份类型 {backup_type} 的过期清理已禁用")
            return
        
        # 确定基础路径
        base_path = os.path.join(self.sftp_config['target_base_path'], backup_type)
        
        try:
            # 列出目录内容
            items = self.sftp.listdir_attr(base_path)
            
            # 根据备份类型确定保留策略
            if backup_type == 'daily':
                # 保留指定天数
                keep_days = config['keep_days']
                cutoff_date = self.now - datetime.timedelta(days=keep_days)
                
                for item in items:
                    if S_ISDIR(item.st_mode):
                        try:
                            # 解析目录名中的日期
                            dir_date = datetime.datetime.strptime(item.filename, '%Y%m%d')
                            if dir_date < cutoff_date:
                                self._sftp_rmtree(os.path.join(base_path, item.filename))
                                self.logger.info(f"已删除过期的每日备份: {item.filename}")
                        except ValueError:
                            # 目录名不是有效的日期格式，跳过
                            continue
            
            elif backup_type == 'monthly':
                # 保留指定月数
                keep_months = config['keep_months']
                cutoff_date = self.now - datetime.timedelta(days=keep_months * 30)
                
                for item in items:
                    if S_ISDIR(item.st_mode):
                        try:
                            # 解析目录名中的年月
                            dir_date = datetime.datetime.strptime(item.filename, '%Y%m')
                            if dir_date < cutoff_date:
                                self._sftp_rmtree(os.path.join(base_path, item.filename))
                                self.logger.info(f"已删除过期的每月备份: {item.filename}")
                        except ValueError:
                            # 目录名不是有效的年月格式，跳过
                            continue
            
            elif backup_type == 'yearly':
                # 如果设置了永久保留，则不删除
                if config['keep_forever']:
                    self.logger.info("年度备份已设置为永久保留")
                    return
                
                # 否则根据配置删除过期备份
                # 这里可以根据需要添加年度备份的保留策略
        except Exception as e:
            self.logger.error(f"清理过期备份时出错: {e}")
    
    def _sftp_rmtree(self, path):
        """
        递归删除SFTP服务器上的目录
        
        参数:
            path: 要删除的目录路径
        """
        try:
            # 列出目录内容
            items = self.sftp.listdir_attr(path)
            
            for item in items:
                item_path = os.path.join(path, item.filename)
                
                if S_ISDIR(item.st_mode):
                    # 递归删除子目录
                    self._sftp_rmtree(item_path)
                else:
                    # 删除文件
                    self.sftp.remove(item_path)
            
            # 删除空目录
            self.sftp.rmdir(path)
        except Exception as e:
            self.logger.error(f"删除SFTP目录时出错: {e}")
    
    def run_backup(self):
        """
        执行备份操作
        
        返回:
            bool: 备份是否成功
        """
        try:
            # 连接SFTP
            self._connect_sftp()
            
            # 获取日期信息
            current_date = self.now.strftime('%Y%m%d')
            current_month = self.now.strftime('%Y%m')
            current_year = self.now.strftime('%Y')
            
            # 压缩源目录
            if self.compression_config['enabled']:
                archive_name = f"backup_{current_date}"
                archive_ext = self.compression_config['format']
                temp_archive_path = os.path.join(
                    self.compression_config['temp_dir'],
                    f"{archive_name}.{archive_ext}"
                )
                
                # 压缩目录
                compressed_file = self._compress_directory(
                    self.source_path,
                    temp_archive_path,
                    archive_ext
                )
            else:
                # 不压缩，直接使用源目录（这种情况实际上无法直接上传整个目录，这里仅作为示例）
                compressed_file = self.source_path
                self.logger.warning("压缩已禁用，此模式可能无法正常工作")
            
            # 执行每日备份
            if self.backup_config['daily']['enabled']:
                daily_path = os.path.join(
                    self.sftp_config['target_base_path'],
                    'daily',
                    current_date
                )
                
                # 创建目录
                self._sftp_makedirs(daily_path)
                
                # 上传文件
                remote_file_path = os.path.join(daily_path, os.path.basename(compressed_file))
                self._upload_file(compressed_file, remote_file_path)
                
                # 清理过期备份
                self._clean_old_backups('daily')
            
            # 检查是否需要执行每月备份（每月第一天）
            if self.backup_config['monthly']['enabled'] and self.now.day == 1:
                monthly_path = os.path.join(
                    self.sftp_config['target_base_path'],
                    'monthly',
                    current_month
                )
                
                # 创建目录
                self._sftp_makedirs(monthly_path)
                
                # 上传文件
                remote_file_path = os.path.join(monthly_path, os.path.basename(compressed_file))
                self._upload_file(compressed_file, remote_file_path)
                
                # 清理过期备份
                self._clean_old_backups('monthly')
            
            # 检查是否需要执行年度备份（每年第一天）
            if self.backup_config['yearly']['enabled'] and self.now.day == 1 and self.now.month == 1:
                yearly_path = os.path.join(
                    self.sftp_config['target_base_path'],
                    'yearly',
                    current_year
                )
                
                # 创建目录
                self._sftp_makedirs(yearly_path)
                
                # 上传文件
                remote_file_path = os.path.join(yearly_path, os.path.basename(compressed_file))
                self._upload_file(compressed_file, remote_file_path)
                
                # 清理过期备份
                self._clean_old_backups('yearly')
            
            # 删除临时文件
            if self.compression_config['enabled'] and os.path.exists(temp_archive_path):
                os.remove(temp_archive_path)
                self.logger.info(f"已删除临时压缩文件: {temp_archive_path}")
            
            self.logger.info("备份任务完成")
            return True
        except Exception as e:
            self.logger.error(f"备份任务失败: {e}")
            return False
        finally:
            # 断开SFTP连接
            self._disconnect_sftp()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='定时备份脚本')
    parser.add_argument('config', nargs='?', default='backup_config.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    try:
        # 创建备份管理器
        backup_manager = BackupManager(args.config)
        
        # 执行备份
        success = backup_manager.run_backup()
        
        # 根据备份结果设置退出码
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()