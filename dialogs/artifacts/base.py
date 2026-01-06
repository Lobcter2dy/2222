"""
Базовый класс функциональных артефактов
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod


class FunctionalArtifact(ABC):
    """
    Базовый класс для функциональных артефактов.
    Артефакт - это панель с встроенным функционалом,
    которая размещается на холсте редактора.
    """
    
    # Метаданные артефакта (переопределить в наследниках)
    ARTIFACT_ID = "base"
    ARTIFACT_NAME = "Базовый артефакт"
    ARTIFACT_ICON = "◆"
    ARTIFACT_DESCRIPTION = "Базовый функциональный артефакт"
    
    # Цвета GitHub Dark
    COLOR_BG = '#161b22'
    COLOR_BG_DARK = '#0d1117'
    COLOR_BORDER = '#30363d'
    COLOR_TEXT = '#e6edf3'
    COLOR_TEXT_MUTED = '#8b949e'
    COLOR_ACCENT = '#2f81f7'
    COLOR_HOVER = '#21262d'
    COLOR_SELECTED = '#388bfd33'
    
    def __init__(self, parent_canvas: tk.Canvas, x: int, y: int, 
                 width: int = 300, height: int = 400,
                 config: Optional[Dict[str, Any]] = None):
        """
        Args:
            parent_canvas: Холст на котором размещается артефакт
            x, y: Позиция на холсте
            width, height: Размеры панели артефакта
            config: Дополнительная конфигурация
        """
        self.parent_canvas = parent_canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.config = config or {}
        
        # Внутренний Frame для контента
        self.frame: Optional[tk.Frame] = None
        self.window_id: Optional[int] = None
        
        # Состояние
        self._selected = False
        self._visible = True
        self._locked = False
        
        # Колбэки
        self._on_select: Optional[Callable] = None
        self._on_change: Optional[Callable] = None
        
        # Создаём виджет
        self._create_widget()
        
    def _create_widget(self):
        """Создаёт основной виджет артефакта"""
        # Основной фрейм
        self.frame = tk.Frame(
            self.parent_canvas,
            bg=self.COLOR_BG,
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1,
            width=self.width,
            height=self.height
        )
        self.frame.pack_propagate(False)
        
        # Заголовок
        self._create_header()
        
        # Контент (переопределяется в наследниках)
        self.content_frame = tk.Frame(self.frame, bg=self.COLOR_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
        
        self._build_content()
        
        # Размещаем на холсте
        self.window_id = self.parent_canvas.create_window(
            self.x, self.y,
            window=self.frame,
            anchor='nw',
            width=self.width,
            height=self.height,
            tags=('artifact', f'artifact_{id(self)}')
        )
        
        # Привязка событий
        self._bind_events()
        
    def _create_header(self):
        """Создаёт заголовок артефакта"""
        header = tk.Frame(self.frame, bg=self.COLOR_BG_DARK, height=28)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Иконка и название
        title_frame = tk.Frame(header, bg=self.COLOR_BG_DARK)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        icon_label = tk.Label(title_frame, text=self.ARTIFACT_ICON,
                             font=('Segoe UI', 11), fg=self.COLOR_ACCENT,
                             bg=self.COLOR_BG_DARK)
        icon_label.pack(side=tk.LEFT, pady=4)
        
        name_label = tk.Label(title_frame, text=self.ARTIFACT_NAME,
                             font=('Segoe UI', 10), fg=self.COLOR_TEXT,
                             bg=self.COLOR_BG_DARK)
        name_label.pack(side=tk.LEFT, padx=(6, 0), pady=4)
        
        # Кнопки управления
        btn_frame = tk.Frame(header, bg=self.COLOR_BG_DARK)
        btn_frame.pack(side=tk.RIGHT, padx=4)
        
        # Кнопка настроек
        settings_btn = tk.Label(btn_frame, text="⚙", font=('Segoe UI', 10),
                               fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                               cursor='hand2')
        settings_btn.pack(side=tk.LEFT, padx=2)
        settings_btn.bind('<Button-1>', lambda e: self._show_settings())
        settings_btn.bind('<Enter>', lambda e: settings_btn.config(fg=self.COLOR_TEXT))
        settings_btn.bind('<Leave>', lambda e: settings_btn.config(fg=self.COLOR_TEXT_MUTED))
        
        # Сохраняем ссылку на header для drag
        self.header = header
        header.bind('<Button-1>', self._on_header_click)
        header.bind('<B1-Motion>', self._on_header_drag)
        
    def _bind_events(self):
        """Привязывает события"""
        self.frame.bind('<Button-1>', self._on_click)
        self.frame.bind('<Button-3>', self._on_right_click)
        
    def _on_click(self, event):
        """Клик по артефакту"""
        self.select()
        
    def _on_right_click(self, event):
        """Правый клик - контекстное меню"""
        self._show_context_menu(event)
        
    def _on_header_click(self, event):
        """Клик по заголовку - начало перетаскивания"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.select()
        
    def _on_header_drag(self, event):
        """Перетаскивание артефакта"""
        if self._locked:
            return
            
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        
        self.x += dx
        self.y += dy
        
        self.parent_canvas.coords(self.window_id, self.x, self.y)
        
        if self._on_change:
            self._on_change(self)
            
    def _show_context_menu(self, event):
        """Показывает контекстное меню"""
        menu = tk.Menu(self.frame, tearoff=0, bg=self.COLOR_BG,
                      fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT,
                      activeforeground='white')
        
        menu.add_command(label="⚙ Настройки", command=self._show_settings)
        menu.add_separator()
        menu.add_command(label="📋 Дублировать", command=self._duplicate)
        menu.add_command(label="🔒 Заблокировать" if not self._locked else "🔓 Разблокировать",
                        command=self._toggle_lock)
        menu.add_separator()
        menu.add_command(label="🗑 Удалить", command=self._delete)
        
        menu.tk_popup(event.x_root, event.y_root)
        
    def _show_settings(self):
        """Показывает диалог настроек (переопределить в наследниках)"""
        pass
        
    def _duplicate(self):
        """Дублирует артефакт"""
        # Реализуется через ArtifactRegistry
        pass
        
    def _toggle_lock(self):
        """Переключает блокировку"""
        self._locked = not self._locked
        
    def _delete(self):
        """Удаляет артефакт"""
        if self.window_id:
            self.parent_canvas.delete(self.window_id)
        if self.frame:
            self.frame.destroy()
            
    def select(self):
        """Выделяет артефакт"""
        self._selected = True
        self.frame.config(highlightbackground=self.COLOR_ACCENT, highlightthickness=2)
        if self._on_select:
            self._on_select(self)
            
    def deselect(self):
        """Снимает выделение"""
        self._selected = False
        self.frame.config(highlightbackground=self.COLOR_BORDER, highlightthickness=1)
        
    def set_position(self, x: int, y: int):
        """Устанавливает позицию"""
        self.x = x
        self.y = y
        self.parent_canvas.coords(self.window_id, x, y)
        
    def set_size(self, width: int, height: int):
        """Устанавливает размер"""
        self.width = width
        self.height = height
        self.parent_canvas.itemconfig(self.window_id, width=width, height=height)
        self.frame.config(width=width, height=height)
        
    def set_select_callback(self, callback: Callable):
        """Устанавливает колбэк выделения"""
        self._on_select = callback
        
    def set_change_callback(self, callback: Callable):
        """Устанавливает колбэк изменения"""
        self._on_change = callback
        
    def get_bounds(self) -> tuple:
        """Возвращает границы (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
        
    def get_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию для сохранения"""
        return {
            'artifact_id': self.ARTIFACT_ID,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'config': self.config,
            'locked': self._locked
        }
        
    @abstractmethod
    def _build_content(self):
        """Строит контент артефакта (переопределить в наследниках)"""
        pass
        
    @abstractmethod
    def get_settings_fields(self) -> List[Dict[str, Any]]:
        """Возвращает список полей настроек для левой панели"""
        pass
        
    def apply_settings(self, settings: Dict[str, Any]):
        """Применяет настройки из левой панели"""
        self.config.update(settings)
        self._refresh_content()
        
    def _refresh_content(self):
        """Обновляет контент после изменения настроек"""
        # Очищаем контент
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Перестраиваем
        self._build_content()


class ArtifactRegistry:
    """Реестр доступных артефактов"""
    
    _artifacts: Dict[str, type] = {}
    _instances: List[FunctionalArtifact] = []
    
    @classmethod
    def register(cls, artifact_class: type):
        """Регистрирует класс артефакта"""
        cls._artifacts[artifact_class.ARTIFACT_ID] = artifact_class
        
    @classmethod
    def get_available(cls) -> Dict[str, type]:
        """Возвращает все доступные артефакты"""
        return cls._artifacts.copy()
        
    @classmethod
    def create(cls, artifact_id: str, canvas: tk.Canvas, 
               x: int, y: int, **kwargs) -> Optional[FunctionalArtifact]:
        """Создаёт экземпляр артефакта"""
        if artifact_id not in cls._artifacts:
            return None
            
        artifact = cls._artifacts[artifact_id](canvas, x, y, **kwargs)
        cls._instances.append(artifact)
        return artifact
        
    @classmethod
    def get_instances(cls) -> List[FunctionalArtifact]:
        """Возвращает все созданные артефакты"""
        return cls._instances.copy()
        
    @classmethod  
    def remove(cls, artifact: FunctionalArtifact):
        """Удаляет артефакт из реестра"""
        if artifact in cls._instances:
            cls._instances.remove(artifact)
            artifact._delete()

