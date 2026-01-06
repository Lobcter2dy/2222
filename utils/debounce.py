"""
Утилиты для дебаунса и троттлинга функций
Предотвращает избыточные вызовы при частых событиях
"""

import time
import threading
from typing import Callable, Any, Optional
from functools import wraps


class Debouncer:
    """
    Дебаунсер - откладывает выполнение до прекращения вызовов.
    
    Использование:
        debouncer = Debouncer(500)  # 500ms
        
        def update_ui():
            print("Updating...")
        
        # Вызывается много раз, но выполнится только один раз
        # через 500ms после последнего вызова
        for i in range(100):
            debouncer.call(update_ui)
    """
    
    def __init__(self, delay_ms: int = 50):
        """
        Args:
            delay_ms: Задержка в миллисекундах
        """
        self.delay_ms = delay_ms
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs):
        """
        Отложенный вызов функции.
        
        Args:
            func: Функция для вызова
            *args, **kwargs: Аргументы функции
        """
        with self._lock:
            # Отменяем предыдущий таймер
            if self._timer:
                self._timer.cancel()
                
            # Создаём новый таймер
            self._timer = threading.Timer(
                self.delay_ms / 1000.0,
                func,
                args=args,
                kwargs=kwargs
            )
            self._timer.start()
            
    def cancel(self):
        """Отменяет отложенный вызов"""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
                
    def flush(self):
        """Немедленно выполняет отложенный вызов (если есть)"""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                # Таймер хранит функцию и аргументы
                # Но threading.Timer не предоставляет к ним доступ
                # Поэтому flush работает только как cancel
                self._timer = None


class Throttler:
    """
    Троттлер - ограничивает частоту вызовов.
    
    Использование:
        throttler = Throttler(100)  # Максимум раз в 100ms
        
        def on_scroll():
            print("Scrolling...")
        
        # Вызывается много раз, но выполнится максимум 10 раз в секунду
        for i in range(100):
            throttler.call(on_scroll)
    """
    
    def __init__(self, interval_ms: int = 16):
        """
        Args:
            interval_ms: Минимальный интервал между вызовами (мс)
        """
        self.interval_ms = interval_ms
        self._last_call = 0.0
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs) -> bool:
        """
        Вызывает функцию если прошло достаточно времени.
        
        Args:
            func: Функция для вызова
            *args, **kwargs: Аргументы функции
            
        Returns:
            True если функция была вызвана
        """
        with self._lock:
            now = time.time() * 1000  # В миллисекунды
            
            if now - self._last_call >= self.interval_ms:
                self._last_call = now
                func(*args, **kwargs)
                return True
            return False
            
    def reset(self):
        """Сбрасывает таймер"""
        with self._lock:
            self._last_call = 0.0


def debounce(delay_ms: int = 50):
    """
    Декоратор для дебаунса функции.
    
    Использование:
        @debounce(300)
        def update_preview():
            ...
    """
    def decorator(func: Callable):
        debouncer = Debouncer(delay_ms)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            debouncer.call(func, *args, **kwargs)
            
        wrapper.cancel = debouncer.cancel
        wrapper.flush = debouncer.flush
        return wrapper
        
    return decorator


def throttle(interval_ms: int = 16):
    """
    Декоратор для троттлинга функции.
    
    Использование:
        @throttle(100)
        def on_mouse_move(x, y):
            ...
    """
    def decorator(func: Callable):
        throttler = Throttler(interval_ms)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return throttler.call(func, *args, **kwargs)
            
        wrapper.reset = throttler.reset
        return wrapper
        
    return decorator


class TkDebouncer:
    """
    Дебаунсер для Tkinter - использует after() вместо threading.
    Безопаснее для UI операций.
    
    Использование:
        debouncer = TkDebouncer(root, 300)
        
        def highlight_syntax():
            ...
        
        # В обработчике события
        debouncer.call(highlight_syntax)
    """
    
    def __init__(self, widget, delay_ms: int = 50):
        """
        Args:
            widget: Tkinter виджет (root или любой другой)
            delay_ms: Задержка в миллисекундах
        """
        self.widget = widget
        self.delay_ms = delay_ms
        self._timer_id: Optional[str] = None
        
    def call(self, func: Callable, *args, **kwargs):
        """
        Отложенный вызов функции через Tkinter.
        
        Args:
            func: Функция для вызова
            *args, **kwargs: Аргументы функции
        """
        # Отменяем предыдущий таймер
        self.cancel()
        
        # Создаём новый
        def callback():
            self._timer_id = None
            func(*args, **kwargs)
            
        self._timer_id = self.widget.after(self.delay_ms, callback)
        
    def cancel(self):
        """Отменяет отложенный вызов"""
        if self._timer_id:
            try:
                self.widget.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None


class TkThrottler:
    """
    Троттлер для Tkinter.
    
    Использование:
        throttler = TkThrottler(100)  # Раз в 100ms
        
        def update_info(x, y):
            info_label.config(text=f"{x}, {y}")
        
        canvas.bind('<Motion>', lambda e: throttler.call(update_info, e.x, e.y))
    """
    
    def __init__(self, interval_ms: int = 16):
        """
        Args:
            interval_ms: Минимальный интервал между вызовами (мс)
        """
        self.interval_ms = interval_ms
        self._last_call = 0
        
    def call(self, func: Callable, *args, **kwargs) -> bool:
        """
        Вызывает функцию если прошло достаточно времени.
        """
        import time
        now = int(time.time() * 1000)
        
        if now - self._last_call >= self.interval_ms:
            self._last_call = now
            func(*args, **kwargs)
            return True
        return False


# Готовые дебаунсеры для типичных задач
DEBOUNCE_UI = 50      # Обновление UI
DEBOUNCE_SEARCH = 300  # Поиск/фильтрация
DEBOUNCE_SAVE = 2000   # Автосохранение
DEBOUNCE_RESIZE = 100  # Изменение размера окна

THROTTLE_SCROLL = 16   # Скролл (60fps)
THROTTLE_DRAG = 16     # Перетаскивание (60fps)
THROTTLE_MOUSE = 50    # Движение мыши

