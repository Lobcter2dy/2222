"""
Менеджер горячих клавиш
Централизованное управление клавиатурными сокращениями
"""

import tkinter as tk
from typing import Dict, Callable, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class HotkeyBinding:
    """Информация о горячей клавише"""
    key: str              # Клавиша (например 'Control-s')
    callback: Callable    # Функция обработчик
    description: str      # Описание действия
    category: str         # Категория (Файл, Редактирование и т.д.)
    enabled: bool = True  # Активна ли клавиша


class HotkeyManager:
    """
    Менеджер горячих клавиш.
    
    Использование:
        hotkeys = HotkeyManager(root)
        
        # Регистрация
        hotkeys.register('Control-s', save_project, 'Сохранить проект', 'Файл')
        hotkeys.register('Control-z', undo, 'Отменить', 'Редактирование')
        
        # Отключение отдельных клавиш
        hotkeys.disable('Control-z')
        
        # Получение списка
        for binding in hotkeys.list_all():
            print(f"{binding.key}: {binding.description}")
    """
    
    # Стандартные категории
    CATEGORY_FILE = "Файл"
    CATEGORY_EDIT = "Редактирование"
    CATEGORY_VIEW = "Вид"
    CATEGORY_SELECTION = "Выделение"
    CATEGORY_TOOLS = "Инструменты"
    CATEGORY_NAVIGATION = "Навигация"
    CATEGORY_OTHER = "Другое"
    
    def __init__(self, root: tk.Tk):
        """
        Args:
            root: Главное окно Tkinter
        """
        self.root = root
        self._bindings: Dict[str, HotkeyBinding] = {}
        self._enabled = True
        
    def register(self, 
                 key: str, 
                 callback: Callable, 
                 description: str = "",
                 category: str = "Другое",
                 enabled: bool = True) -> bool:
        """
        Регистрирует горячую клавишу.
        
        Args:
            key: Комбинация клавиш (например 'Control-s', 'Control-Shift-z')
            callback: Функция обработчик
            description: Описание действия
            category: Категория
            enabled: Активна ли сразу
            
        Returns:
            True если успешно зарегистрировано
        """
        # Нормализуем ключ
        normalized_key = self._normalize_key(key)
        
        # Создаём запись
        binding = HotkeyBinding(
            key=normalized_key,
            callback=callback,
            description=description,
            category=category,
            enabled=enabled
        )
        
        self._bindings[normalized_key] = binding
        
        # Привязываем к root
        if enabled:
            self._bind(normalized_key, callback)
            
        return True
        
    def unregister(self, key: str) -> bool:
        """
        Удаляет регистрацию горячей клавиши.
        
        Args:
            key: Комбинация клавиш
            
        Returns:
            True если успешно удалено
        """
        normalized_key = self._normalize_key(key)
        
        if normalized_key in self._bindings:
            self._unbind(normalized_key)
            del self._bindings[normalized_key]
            return True
        return False
        
    def enable(self, key: str) -> bool:
        """Включает горячую клавишу"""
        normalized_key = self._normalize_key(key)
        
        if normalized_key in self._bindings:
            binding = self._bindings[normalized_key]
            if not binding.enabled:
                binding.enabled = True
                self._bind(normalized_key, binding.callback)
            return True
        return False
        
    def disable(self, key: str) -> bool:
        """Отключает горячую клавишу"""
        normalized_key = self._normalize_key(key)
        
        if normalized_key in self._bindings:
            binding = self._bindings[normalized_key]
            if binding.enabled:
                binding.enabled = False
                self._unbind(normalized_key)
            return True
        return False
        
    def enable_all(self):
        """Включает все горячие клавиши"""
        self._enabled = True
        for key, binding in self._bindings.items():
            if binding.enabled:
                self._bind(key, binding.callback)
                
    def disable_all(self):
        """Отключает все горячие клавиши"""
        self._enabled = False
        for key in self._bindings:
            self._unbind(key)
            
    def is_registered(self, key: str) -> bool:
        """Проверяет зарегистрирована ли клавиша"""
        return self._normalize_key(key) in self._bindings
        
    def get_binding(self, key: str) -> Optional[HotkeyBinding]:
        """Возвращает информацию о горячей клавише"""
        return self._bindings.get(self._normalize_key(key))
        
    def list_all(self) -> List[HotkeyBinding]:
        """Возвращает список всех горячих клавиш"""
        return list(self._bindings.values())
        
    def list_by_category(self, category: str) -> List[HotkeyBinding]:
        """Возвращает список горячих клавиш по категории"""
        return [b for b in self._bindings.values() if b.category == category]
        
    def get_categories(self) -> List[str]:
        """Возвращает список всех категорий"""
        return list(set(b.category for b in self._bindings.values()))
        
    def _normalize_key(self, key: str) -> str:
        """Нормализует формат клавиши"""
        # Control -> Control, Ctrl -> Control
        key = key.replace('Ctrl-', 'Control-')
        key = key.replace('ctrl-', 'Control-')
        key = key.replace('Alt-', 'Alt-')
        key = key.replace('alt-', 'Alt-')
        key = key.replace('Shift-', 'Shift-')
        key = key.replace('shift-', 'Shift-')
        
        # Для одиночных клавиш
        if '-' not in key:
            key = key.lower()
            
        return key
        
    def _bind(self, key: str, callback: Callable):
        """Привязывает клавишу к обработчику"""
        def handler(event):
            if self._enabled:
                callback()
            return "break"  # Предотвращаем дальнейшую обработку
            
        self.root.bind(f"<{key}>", handler)
        
    def _unbind(self, key: str):
        """Отвязывает клавишу"""
        try:
            self.root.unbind(f"<{key}>")
        except tk.TclError:
            pass
            

def setup_default_hotkeys(hotkeys: HotkeyManager, app) -> HotkeyManager:
    """
    Настраивает стандартные горячие клавиши для приложения.
    
    Args:
        hotkeys: Менеджер горячих клавиш
        app: Ссылка на главное приложение
        
    Returns:
        Настроенный менеджер
    """
    # === Файл ===
    hotkeys.register(
        'Control-n', 
        lambda: app.new_project() if hasattr(app, 'new_project') else None,
        'Новый проект',
        HotkeyManager.CATEGORY_FILE
    )
    
    hotkeys.register(
        'Control-o', 
        lambda: app.open_project() if hasattr(app, 'open_project') else None,
        'Открыть проект',
        HotkeyManager.CATEGORY_FILE
    )
    
    hotkeys.register(
        'Control-s', 
        lambda: app.save_project() if hasattr(app, 'save_project') else None,
        'Сохранить',
        HotkeyManager.CATEGORY_FILE
    )
    
    hotkeys.register(
        'Control-Shift-s', 
        lambda: app.save_project_as() if hasattr(app, 'save_project_as') else None,
        'Сохранить как...',
        HotkeyManager.CATEGORY_FILE
    )
    
    # === Редактирование ===
    hotkeys.register(
        'Control-z', 
        lambda: app.undo() if hasattr(app, 'undo') else None,
        'Отменить',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Control-y', 
        lambda: app.redo() if hasattr(app, 'redo') else None,
        'Повторить',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Control-Shift-z', 
        lambda: app.redo() if hasattr(app, 'redo') else None,
        'Повторить (альт.)',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Control-c', 
        lambda: app.copy_element() if hasattr(app, 'copy_element') else None,
        'Копировать',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Control-v', 
        lambda: app.paste_element() if hasattr(app, 'paste_element') else None,
        'Вставить',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Control-d', 
        lambda: app.duplicate_element() if hasattr(app, 'duplicate_element') else None,
        'Дублировать',
        HotkeyManager.CATEGORY_EDIT
    )
    
    hotkeys.register(
        'Delete', 
        lambda: app.delete_selected() if hasattr(app, 'delete_selected') else None,
        'Удалить',
        HotkeyManager.CATEGORY_EDIT
    )
    
    # === Выделение ===
    hotkeys.register(
        'Control-a', 
        lambda: app.select_all() if hasattr(app, 'select_all') else None,
        'Выделить всё',
        HotkeyManager.CATEGORY_SELECTION
    )
    
    hotkeys.register(
        'Escape', 
        lambda: app.deselect_all() if hasattr(app, 'deselect_all') else None,
        'Снять выделение',
        HotkeyManager.CATEGORY_SELECTION
    )
    
    # === Вид ===
    hotkeys.register(
        'Control-plus', 
        lambda: app.zoom_in() if hasattr(app, 'zoom_in') else None,
        'Увеличить',
        HotkeyManager.CATEGORY_VIEW
    )
    
    hotkeys.register(
        'Control-minus', 
        lambda: app.zoom_out() if hasattr(app, 'zoom_out') else None,
        'Уменьшить',
        HotkeyManager.CATEGORY_VIEW
    )
    
    hotkeys.register(
        'Control-0', 
        lambda: app.zoom_reset() if hasattr(app, 'zoom_reset') else None,
        'Сбросить масштаб',
        HotkeyManager.CATEGORY_VIEW
    )
    
    hotkeys.register(
        'Control-g', 
        lambda: app.toggle_grid() if hasattr(app, 'toggle_grid') else None,
        'Переключить сетку',
        HotkeyManager.CATEGORY_VIEW
    )
    
    hotkeys.register(
        'F11', 
        lambda: app.toggle_fullscreen() if hasattr(app, 'toggle_fullscreen') else None,
        'Полноэкранный режим',
        HotkeyManager.CATEGORY_VIEW
    )
    
    # === Навигация ===
    hotkeys.register(
        'F5', 
        lambda: app.start_preview() if hasattr(app, 'start_preview') else None,
        'Режим просмотра',
        HotkeyManager.CATEGORY_NAVIGATION
    )
    
    # === Инструменты ===
    hotkeys.register(
        'v', 
        lambda: app.set_tool('select') if hasattr(app, 'set_tool') else None,
        'Инструмент выделения',
        HotkeyManager.CATEGORY_TOOLS
    )
    
    hotkeys.register(
        'h', 
        lambda: app.set_tool('hand') if hasattr(app, 'set_tool') else None,
        'Инструмент руки',
        HotkeyManager.CATEGORY_TOOLS
    )
    
    return hotkeys


# Глобальный экземпляр (инициализируется позже)
_hotkey_manager: Optional[HotkeyManager] = None


def init_hotkeys(root: tk.Tk, app=None) -> HotkeyManager:
    """
    Инициализирует глобальный менеджер горячих клавиш.
    
    Args:
        root: Главное окно Tkinter
        app: Ссылка на приложение (для стандартных клавиш)
        
    Returns:
        Инициализированный менеджер
    """
    global _hotkey_manager
    _hotkey_manager = HotkeyManager(root)
    
    if app:
        setup_default_hotkeys(_hotkey_manager, app)
        
    return _hotkey_manager


def get_hotkey_manager() -> Optional[HotkeyManager]:
    """Возвращает глобальный менеджер горячих клавиш"""
    return _hotkey_manager

