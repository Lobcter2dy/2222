#!/usr/bin/env python3
"""
Базовый класс для диалогов с автозакрытием и адаптивными размерами
"""
import tkinter as tk
from typing import Optional, Tuple, Callable


class DialogBase:
    """
    Базовый класс для диалогов настроек с улучшенным UX.
    
    Особенности:
    - Автозакрытие при клике вне диалога
    - Адаптивные размеры под содержимое
    - Корректное центрирование
    - Стандартные горячие клавиши
    """
    
    # Стандартные размеры для разных типов диалогов
    DIALOG_SIZES = {
        'simple': (350, 250),      # Простые настройки (visibility, etc)
        'medium': (450, 400),      # Средние настройки (button, panel, etc)
        'large': (650, 550),       # Расширенные настройки (extended dialog)
        'tall': (400, 600),        # Высокие диалоги (scroll area, state switcher)
        'wide': (700, 450),        # Широкие диалоги (с множеством вкладок)
    }
    
    def __init__(self, parent: tk.Widget, title: str, 
                 size_type: str = 'medium', 
                 resizable: bool = False,
                 auto_close: bool = True):
        """
        Args:
            parent: Родительское окно
            title: Заголовок диалога
            size_type: Тип размера из DIALOG_SIZES
            resizable: Можно ли изменять размер
            auto_close: Автозакрытие при клике вне
        """
        self.parent = parent
        self.auto_close = auto_close
        self.result = None
        
        # Создаём диалог
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        
        # Устанавливаем размеры
        width, height = self.DIALOG_SIZES.get(size_type, self.DIALOG_SIZES['medium'])
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(resizable, resizable)
        
        if resizable:
            self.dialog.minsize(int(width * 0.7), int(height * 0.7))
        
        # Делаем модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Стандартный стиль
        self.dialog.configure(bg="#2a2a2a")
        
        # Центрируем
        self._center_dialog(width, height)
        
        # Настраиваем события
        self._setup_events()
    
    def _center_dialog(self, width: int, height: int):
        """Центрирует диалог относительно родителя"""
        self.dialog.update_idletasks()
        
        # Получаем размеры и позицию родителя
        parent_x = self.parent.winfo_x() if hasattr(self.parent, 'winfo_x') else 0
        parent_y = self.parent.winfo_y() if hasattr(self.parent, 'winfo_y') else 0
        parent_width = self.parent.winfo_width() if hasattr(self.parent, 'winfo_width') else 800
        parent_height = self.parent.winfo_height() if hasattr(self.parent, 'winfo_height') else 600
        
        # Вычисляем центральную позицию
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Убеждаемся что диалог помещается на экран
        x = max(50, x)
        y = max(50, y)
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _setup_events(self):
        """Настраивает события диалога"""
        # Горячие клавиши
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        self.dialog.bind('<Return>', lambda e: self._on_apply_if_exists())
        
        # Автозакрытие при клике вне диалога
        if self.auto_close:
            # Отслеживаем фокус
            self.dialog.bind('<FocusOut>', self._on_focus_out)
            
            # Клик по родительскому окну
            def on_parent_click(event):
                # Проверяем что клик не по диалогу
                if self.dialog.winfo_exists():
                    dialog_x = self.dialog.winfo_x()
                    dialog_y = self.dialog.winfo_y()
                    dialog_width = self.dialog.winfo_width()
                    dialog_height = self.dialog.winfo_height()
                    
                    click_x = event.x_root
                    click_y = event.y_root
                    
                    # Если клик вне диалога - закрываем
                    if not (dialog_x <= click_x <= dialog_x + dialog_width and
                            dialog_y <= click_y <= dialog_y + dialog_height):
                        self._auto_close()
            
            # Привязываем к родительскому окну
            self.parent.bind('<Button-1>', on_parent_click, add=True)
    
    def _on_focus_out(self, event):
        """Обработчик потери фокуса"""
        # Небольшая задержка чтобы избежать ложных срабатываний
        self.dialog.after(100, self._check_focus)
    
    def _check_focus(self):
        """Проверяет фокус и закрывает диалог если фокус потерян"""
        if self.dialog.winfo_exists():
            focused = self.dialog.focus_get()
            if focused is None or not str(focused).startswith(str(self.dialog)):
                # Фокус не на диалоге - проверяем мышь
                pointer_x = self.dialog.winfo_pointerx()
                pointer_y = self.dialog.winfo_pointery()
                
                dialog_x = self.dialog.winfo_rootx()
                dialog_y = self.dialog.winfo_rooty()
                dialog_width = self.dialog.winfo_width()
                dialog_height = self.dialog.winfo_height()
                
                # Если мышь не над диалогом - закрываем
                if not (dialog_x <= pointer_x <= dialog_x + dialog_width and
                        dialog_y <= pointer_y <= dialog_y + dialog_height):
                    self._auto_close()
    
    def _auto_close(self):
        """Автозакрытие диалога"""
        if hasattr(self, '_auto_closing'):
            return  # Уже закрываем
        self._auto_closing = True
        
        try:
            self._on_cancel()
        except:
            self.dialog.destroy()
    
    def _on_apply_if_exists(self):
        """Применяет изменения если метод существует"""
        if hasattr(self, '_on_ok'):
            self._on_ok()
        elif hasattr(self, '_on_apply'):
            self._on_apply()
    
    def _on_cancel(self):
        """Отмена - переопределить в наследниках"""
        self.dialog.destroy()
    
    def show(self):
        """Показывает диалог и ждёт закрытия"""
        self.dialog.wait_window()
        return self.result
    
    def close(self):
        """Закрывает диалог"""
        self.dialog.destroy()


class AdaptiveDialog(DialogBase):
    """
    Диалог с адаптивными размерами под содержимое.
    Автоматически подстраивает размер под количество элементов.
    """
    
    def __init__(self, parent: tk.Widget, title: str, 
                 min_size: Optional[Tuple[int, int]] = None,
                 max_size: Optional[Tuple[int, int]] = None,
                 auto_close: bool = True):
        """
        Args:
            min_size: Минимальные размеры (width, height)
            max_size: Максимальные размеры (width, height)
        """
        self.min_size = min_size or (300, 200)
        self.max_size = max_size or (800, 700)
        
        # Начинаем с минимального размера
        super().__init__(parent, title, auto_close=auto_close)
        
        # Переопределяем геометрию
        self.dialog.geometry(f"{self.min_size[0]}x{self.min_size[1]}")
    
    def _auto_resize_to_content(self):
        """Автоматически подстраивает размер под содержимое"""
        self.dialog.update_idletasks()
        
        # Получаем требуемые размеры содержимого
        required_width = self.dialog.winfo_reqwidth()
        required_height = self.dialog.winfo_reqheight()
        
        # Применяем ограничения
        new_width = max(self.min_size[0], min(required_width, self.max_size[0]))
        new_height = max(self.min_size[1], min(required_height, self.max_size[1]))
        
        # Обновляем размеры
        current_width = self.dialog.winfo_width()
        current_height = self.dialog.winfo_height()
        
        if abs(new_width - current_width) > 20 or abs(new_height - current_height) > 20:
            self.dialog.geometry(f"{new_width}x{new_height}")
            self._center_dialog(new_width, new_height)
    
    def add_content_and_resize(self, content_builder: Callable):
        """Добавляет содержимое и автоматически подстраивает размер"""
        content_builder()
        self.dialog.after_idle(self._auto_resize_to_content)
