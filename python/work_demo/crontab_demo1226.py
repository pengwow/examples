# log_config.py - 日志配置模块
import logging
import logging.handlers
import os

def setup_logging(script_name, log_file='/var/log/aio/crontab/combined.log', level=logging.INFO):
    """
    设置日志格式，确保不同脚本的日志可区分
    :param script_name: 脚本标识名
    :param log_file: 日志文件路径
    :param level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 创建 logger
    logger = logging.getLogger(script_name)
    logger.setLevel(level)
    
    # 防止重复添加 handler（防止重载时重复日志）
    if not logger.handlers:
        # 创建文件 handler，并设置按时间轮转（例如每天）
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when='midnight', interval=1, backupCount=7
        )
        # 创建格式器，格式为：[时间] [脚本名] [日志级别] - 消息
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 可选：同时输出到控制台（crontab 会将其捕获到文件）
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger