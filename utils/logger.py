"""
Централизованная система логирования для проекта.
Поддерживает уровни логирования, форматирование, ротацию файлов.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


# Цвета для консоли (ANSI)
COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green  
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[35m', # Magenta
    'RESET': '\033[0m'
}


class ColoredFormatter(logging.Formatter):
    """Форматтер с цветным выводом для консоли"""
    
    def format(self, record):
        # Добавляем цвет
        color = COLORS.get(record.levelname, '')
        reset = COLORS['RESET']
        
        # Форматируем сообщение
        record.colored_levelname = f"{color}{record.levelname:8}{reset}"
        
        return super().format(record)


class Logger:
    """
    Менеджер логирования для проекта.
    
    Использование:
        from modules.utils.logger import Logger, get_logger
        
        # Способ 1: Получение логгера напрямую
        log = get_logger('MyModule')
        log.info('Сообщение')
        
        # Способ 2: Создание логгера для класса
        log = Logger.create('[ElementManager]')
        log.debug('Debug сообщение')
        log.info('Info сообщение')
        log.warning('Warning сообщение')
        log.error('Error сообщение')
    """
    
    # Глобальные настройки
    _log_dir: str = None
    _log_level: int = logging.INFO
    _file_logging: bool = True
    _console_logging: bool = True
    _initialized: bool = False
    _loggers: dict = {}
    
    # Константы
    MAX_LOG_SIZE = 50 * 1024 * 1024  # 50MB
    BACKUP_COUNT = 5
    
    @classmethod
    def initialize(cls, 
                   log_dir: Optional[str] = None,
                   level: int = logging.INFO,
                   file_logging: bool = True,
                   console_logging: bool = True):
        """
        Инициализирует систему логирования.
        
        Args:
            log_dir: Директория для лог-файлов
            level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            file_logging: Включить запись в файл
            console_logging: Включить вывод в консоль
        """
        if cls._initialized:
            return
            
        cls._log_level = level
        cls._file_logging = file_logging
        cls._console_logging = console_logging
        
        # Определяем директорию для логов
        if log_dir:
            cls._log_dir = log_dir
        else:
            # По умолчанию - рядом с проектом
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cls._log_dir = os.path.join(project_dir, 'logs')
            
        # Создаём директорию если нужно
        if cls._file_logging:
            os.makedirs(cls._log_dir, exist_ok=True)
            
        cls._initialized = True
        
    @classmethod
    def create(cls, name: str) -> logging.Logger:
        """
        Создаёт или возвращает существующий логгер.
        
        Args:
            name: Имя модуля (например '[ElementManager]' или 'MyModule')
            
        Returns:
            logging.Logger: Настроенный логгер
        """
        # Очищаем имя от скобок для имени файла
        clean_name = name.strip('[]')
        
        # Проверяем кэш
        if clean_name in cls._loggers:
            return cls._loggers[clean_name]
            
        # Инициализируем если нужно
        if not cls._initialized:
            cls.initialize()
            
        # Создаём логгер
        logger = logging.getLogger(clean_name)
        logger.setLevel(cls._log_level)
        
        # Предотвращаем дублирование обработчиков
        if logger.handlers:
            return logger
            
        # Формат сообщений
        format_str = '%(asctime)s | %(colored_levelname)s | %(name)s | %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Консольный обработчик
        if cls._console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(cls._log_level)
            console_formatter = ColoredFormatter(format_str, date_format)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
        # Файловый обработчик
        if cls._file_logging and cls._log_dir:
            log_file = os.path.join(cls._log_dir, f'{clean_name}.log')
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=cls.MAX_LOG_SIZE,
                backupCount=cls.BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(cls._log_level)
            
            # Без цветов для файла
            file_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
            file_formatter = logging.Formatter(file_format, date_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        # Кэшируем
        cls._loggers[clean_name] = logger
        
        return logger
        
    @classmethod
    def set_level(cls, level: int):
        """Устанавливает уровень логирования для всех логгеров"""
        cls._log_level = level
        for logger in cls._loggers.values():
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
                
    @classmethod
    def get_log_file(cls, name: str) -> Optional[str]:
        """Возвращает путь к лог-файлу"""
        if cls._log_dir:
            return os.path.join(cls._log_dir, f'{name}.log')
        return None


def get_logger(name: str) -> logging.Logger:
    """
    Удобная функция для получения логгера.
    
    Args:
        name: Имя модуля
        
    Returns:
        logging.Logger: Настроенный логгер
        
    Example:
        log = get_logger('MyModule')
        log.info('Работает!')
    """
    return Logger.create(name)


# Уровни для удобства
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

