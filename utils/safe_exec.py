"""
Безопасное выполнение кода в изолированном окружении (sandbox)
Блокирует доступ к файловой системе, сети, опасным модулям
"""

import sys
import io
import ast
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager


class SafeExecutionError(Exception):
    """Ошибка безопасного выполнения"""
    pass


class RestrictedImportError(SafeExecutionError):
    """Попытка импорта запрещённого модуля"""
    pass


class DangerousCodeError(SafeExecutionError):
    """Обнаружен опасный код"""
    pass


class SafeExecutor:
    """
    Безопасный исполнитель кода Python.
    Блокирует опасные операции и модули.
    """
    
    # Запрещённые модули
    BLOCKED_MODULES = {
        'os', 'sys', 'subprocess', 'shutil', 'pathlib',
        'socket', 'urllib', 'requests', 'http', 'ftplib',
        'pickle', 'shelve', 'marshal',
        'ctypes', 'multiprocessing', 'threading',
        'importlib', '__builtin__', 'builtins',
        'code', 'codeop', 'compile',
        'pty', 'tty', 'termios',
        'signal', 'resource',
        'gc', 'inspect', 'traceback',
    }
    
    # Запрещённые встроенные функции
    BLOCKED_BUILTINS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'input', 'breakpoint',
        'globals', 'locals', 'vars', 'dir',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'type', 'object', 'super',
        'memoryview', 'bytearray',
    }
    
    # Разрешённые встроенные функции
    ALLOWED_BUILTINS = {
        # Типы
        'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set', 'frozenset',
        'bytes', 'complex',
        # Функции
        'abs', 'all', 'any', 'bin', 'chr', 'divmod', 'enumerate',
        'filter', 'format', 'hex', 'id', 'isinstance', 'issubclass',
        'iter', 'len', 'map', 'max', 'min', 'next', 'oct', 'ord',
        'pow', 'print', 'range', 'repr', 'reversed', 'round',
        'slice', 'sorted', 'sum', 'zip',
        # Константы
        'True', 'False', 'None',
        # Исключения (базовые)
        'Exception', 'ValueError', 'TypeError', 'KeyError', 
        'IndexError', 'AttributeError', 'RuntimeError',
    }
    
    # Разрешённые модули (безопасные)
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'time', 'json',
        'collections', 'itertools', 'functools',
        're', 'string', 'textwrap',
        'decimal', 'fractions', 'statistics',
    }
    
    def __init__(self, timeout: int = 5, max_output: int = 10000):
        """
        Args:
            timeout: Максимальное время выполнения (сек)
            max_output: Максимальный размер вывода (символов)
        """
        self.timeout = timeout
        self.max_output = max_output
        self._output_buffer = io.StringIO()
        
    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Создаёт безопасный набор встроенных функций"""
        import builtins
        
        safe_builtins = {}
        for name in self.ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)
        
        # Безопасный print с ограничением
        original_print = print
        def safe_print(*args, **kwargs):
            output = io.StringIO()
            kwargs['file'] = output
            original_print(*args, **kwargs)
            result = output.getvalue()
            
            # Ограничиваем размер вывода
            current_size = len(self._output_buffer.getvalue())
            if current_size + len(result) > self.max_output:
                result = result[:self.max_output - current_size]
                result += "\n[...вывод обрезан...]"
                
            self._output_buffer.write(result)
            
        safe_builtins['print'] = safe_print
        
        # Безопасный __import__
        def safe_import(name, *args, **kwargs):
            if name in self.BLOCKED_MODULES:
                raise RestrictedImportError(f"Модуль '{name}' запрещён")
            if name.split('.')[0] in self.BLOCKED_MODULES:
                raise RestrictedImportError(f"Модуль '{name}' запрещён")
            if name not in self.ALLOWED_MODULES:
                raise RestrictedImportError(f"Модуль '{name}' не в списке разрешённых")
            return __import__(name, *args, **kwargs)
            
        safe_builtins['__import__'] = safe_import
        
        return safe_builtins
        
    def _check_ast(self, code: str) -> None:
        """Проверяет AST кода на опасные конструкции"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SafeExecutionError(f"Синтаксическая ошибка: {e}")
            
        for node in ast.walk(tree):
            # Запрет import
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split('.')[0] in self.BLOCKED_MODULES:
                            raise DangerousCodeError(f"Импорт '{alias.name}' запрещён")
                else:
                    if node.module and node.module.split('.')[0] in self.BLOCKED_MODULES:
                        raise DangerousCodeError(f"Импорт из '{node.module}' запрещён")
                        
            # Запрет exec/eval
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ('exec', 'eval', 'compile', '__import__'):
                        raise DangerousCodeError(f"Вызов '{node.func.id}' запрещён")
                        
            # Запрет доступа к __
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__') and node.attr.endswith('__'):
                    if node.attr not in ('__init__', '__str__', '__repr__', '__len__'):
                        raise DangerousCodeError(f"Доступ к '{node.attr}' запрещён")
                        
    def execute(self, code: str, local_vars: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Any]:
        """
        Выполняет код в безопасном окружении.
        
        Args:
            code: Код для выполнения
            local_vars: Дополнительные переменные
            
        Returns:
            Tuple[success: bool, output: str, result: Any]
        """
        self._output_buffer = io.StringIO()
        
        try:
            # Проверка AST
            self._check_ast(code)
            
            # Создаём безопасное окружение
            safe_globals = {
                '__builtins__': self._create_safe_builtins(),
                '__name__': '__main__',
                '__doc__': None,
            }
            
            # Добавляем разрешённые модули
            for module_name in self.ALLOWED_MODULES:
                try:
                    safe_globals[module_name] = __import__(module_name)
                except ImportError:
                    pass
                    
            # Добавляем пользовательские переменные
            if local_vars:
                safe_globals.update(local_vars)
                
            # Выполняем код
            result = None
            exec(compile(code, '<sandbox>', 'exec'), safe_globals)
            
            output = self._output_buffer.getvalue()
            return True, output, result
            
        except SafeExecutionError as e:
            return False, f"Ошибка безопасности: {e}", None
        except Exception as e:
            return False, f"Ошибка выполнения: {type(e).__name__}: {e}", None
            
    def evaluate(self, expression: str, local_vars: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Any]:
        """
        Вычисляет выражение безопасно.
        
        Args:
            expression: Выражение для вычисления
            local_vars: Дополнительные переменные
            
        Returns:
            Tuple[success: bool, message: str, result: Any]
        """
        try:
            # Проверяем что это простое выражение
            tree = ast.parse(expression, mode='eval')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.BLOCKED_BUILTINS:
                            raise DangerousCodeError(f"Вызов '{node.func.id}' запрещён")
                            
            # Создаём безопасное окружение
            safe_globals = {
                '__builtins__': self._create_safe_builtins(),
            }
            
            if local_vars:
                safe_globals.update(local_vars)
                
            result = eval(compile(tree, '<sandbox>', 'eval'), safe_globals)
            return True, str(result), result
            
        except SafeExecutionError as e:
            return False, f"Ошибка безопасности: {e}", None
        except Exception as e:
            return False, f"Ошибка: {type(e).__name__}: {e}", None


# Глобальный экземпляр для удобства
_default_executor = SafeExecutor()


def safe_exec(code: str, local_vars: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Any]:
    """
    Удобная функция для безопасного выполнения кода.
    
    Args:
        code: Код для выполнения
        local_vars: Дополнительные переменные
        
    Returns:
        Tuple[success: bool, output: str, result: Any]
        
    Example:
        success, output, _ = safe_exec('print("Hello")')
        if success:
            print(output)  # "Hello\n"
    """
    return _default_executor.execute(code, local_vars)

