import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

# 默认日志目录
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

# 日志级别映射
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# 默认日志格式
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logger(name=None, log_level='info', log_file=None, log_format=None,
                max_file_size=10*1024*1024, backup_count=5, console_output=True):
    """
    设置并返回一个日志记录器
    
    参数:
        name: 日志记录器名称，默认为root
        log_level: 日志级别，可选值：debug, info, warning, error, critical
        log_file: 日志文件路径，如果为None则不记录到文件
        log_format: 日志格式，默认为时间-名称-级别-消息格式
        max_file_size: 单个日志文件最大大小，默认10MB
        backup_count: 备份日志文件数量，默认5个
        console_output: 是否输出到控制台，默认True
        
    返回:
        配置好的日志记录器实例
    """
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    level = LOG_LEVELS.get(log_level.lower(), logging.INFO)
    logger.setLevel(level)
    
    # 设置日志格式
    formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
    
    # 添加控制台处理器
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # 创建文件处理器，使用RotatingFileHandler支持日志轮转
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_logger(name=None, log_level='info'):
    """
    获取默认配置的日志记录器，输出到控制台和日期命名的日志文件
    
    参数:
        name: 日志记录器名称
        log_level: 日志级别
        
    返回:
        配置好的日志记录器实例
    """
    # 确保日志目录存在
    if not os.path.exists(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
    
    # 使用日期作为日志文件名
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(DEFAULT_LOG_DIR, f'{today}.log')
    
    return setup_logger(
        name=name,
        log_level=log_level,
        log_file=log_file
    )


# 创建默认日志记录器实例，可在其他模块中直接导入使用
logger = get_default_logger('root')


# 提供便捷的日志记录函数
def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


# 允许自定义日志记录器
def get_custom_logger(name, log_level='info', log_dir=None, log_file=None):
    """
    获取自定义配置的日志记录器
    
    参数:
        name: 日志记录器名称
        log_level: 日志级别
        log_dir: 日志目录，默认为DEFAULT_LOG_DIR
        log_file: 日志文件名，默认使用日期命名
        
    返回:
        配置好的日志记录器实例
    """
    # 设置日志目录
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    
    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志文件
    if log_file is None:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = f'{name}_{today}.log'
    
    log_file_path = os.path.join(log_dir, log_file)
    
    return setup_logger(
        name=name,
        log_level=log_level,
        log_file=log_file_path
    )