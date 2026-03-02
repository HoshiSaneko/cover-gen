import logging
import sys

# 定义日志级别颜色
class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColoredFormatter(logging.Formatter):
    """自定义带颜色的日志格式化器"""
    
    FORMATS = {
        logging.DEBUG: LogColors.OKBLUE + "🐛 DEBUG: %(message)s" + LogColors.ENDC,
        logging.INFO: LogColors.OKGREEN + "ℹ️ INFO: %(message)s" + LogColors.ENDC,
        logging.WARNING: LogColors.WARNING + "⚠️ WARNING: %(message)s" + LogColors.ENDC,
        logging.ERROR: LogColors.FAIL + "❌ ERROR: %(message)s" + LogColors.ENDC,
        logging.CRITICAL: LogColors.FAIL + LogColors.BOLD + "💀 CRITICAL: %(message)s" + LogColors.ENDC,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name="cover-gen", level=logging.INFO):
    """配置并返回日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 防止重复添加处理器
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
