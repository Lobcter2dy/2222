#!/usr/bin/env python3
"""
Менеджер элементов
Управляет всеми элементами на холсте: создание, выбор, перемещение, удаление
Не содержит логику выделения - это делает SelectionTool
Главная панель - отдельный модуль (MainCanvas), не является элементом
"""
import tkinter as tk
from .frame import FrameElement
from .panel import PanelElement
from .button import ButtonElement
from .image import ImageElement
from .text import TextElement
from .scroll_area import ScrollAreaElement
from .state_switcher import StateSwitcherElement
from .artifact import ArtifactElement
from ..utils.event_bus import event_bus
from ..size_constraints import SizeConstraints


class ElementManager:
    """Менеджер элементов на холсте"""

    # Реестр типов элементов
    ELEMENT_TYPES = {
        'frame': FrameElement,
        'panel': PanelElement,
        'button': ButtonElement,
        'image': ImageElement,
        'text': TextElement,
        'scroll_area': ScrollAreaElement,
        'state_switcher': StateSwitcherElement,
        'artifact': ArtifactElement,
    }

    def __init__(self, canvas, config):
        """
        Args:
            canvas: холст для рисования
            config: конфигурация приложения
        """
        self.canvas = canvas
        self.config = config
        
        # Система масштабирования
        self.zoom_system = None
        
        # Ссылка на главную панель (отдельный модуль)
        self.main_canvas = None
        
        # Список всех элементов
        self.elements = []
        
        # Текущий выбранный элемент
        self.selected_element = None
        
        # Колбэки при выборе элемента (множественные)
        self._selection_callbacks = []
        self._notifying = False  # Защита от рекурсии
        
        # Режим создания элемента
        self.creation_mode = None
        self.creation_start = None
        self.creation_params = {}  # Дополнительные параметры (для артефактов и т.д.)
        
        # Превью создания
        self._preview_items = []
        self._size_label = None

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system

    def set_main_canvas(self, main_canvas):
        """Устанавливает ссылку на главную панель"""
        self.main_canvas = main_canvas

    def set_selection_callback(self, callback):
        """Добавляет колбэк при изменении выбора"""
        if callback and callback not in self._selection_callbacks:
            self._selection_callbacks.append(callback)

    def create_element(self, element_type, x, y, width=100, height=100, **kwargs):
        """Создаёт новый элемент указанного типа"""
        if element_type not in self.ELEMENT_TYPES:
            return None
        
        element_class = self.ELEMENT_TYPES[element_type]
        element = element_class(self.canvas, self.config)
        
        if self.zoom_system:
            element.set_zoom_system(self.zoom_system)
        
        element.x = x
        element.y = y
        element.width = width
        element.height = height
        
        # Дополнительные параметры для артефактов
        if element_type == 'artifact' and hasattr(element, 'set_artifact_type'):
            artifact_type = kwargs.get('artifact_type') or getattr(self, 'creation_params', {}).get('artifact_type')
            if artifact_type:
                element.set_artifact_type(artifact_type)
        
        self.elements.append(element)
        self.redraw_all()
        self.select_element(element)
        
        return element

    def delete_element(self, element):
        """Удаляет элемент"""
        if element in self.elements:
            element.clear()
            self.elements.remove(element)
            
            if self.selected_element == element:
                self.selected_element = None
                self._notify_selection_change()

    def delete_selected(self):
        """Удаляет выбранный элемент"""
        if self.selected_element:
            self.delete_element(self.selected_element)

    def clear_all(self):
        """Удаляет все элементы"""
        for element in self.elements[:]:  # Копия списка
            element.clear()
        self.elements = []
        self.selected_element = None
        self._notify_selection_change()

    def select_element(self, element):
        """Выбирает элемент"""
        self.selected_element = element
        self._notify_selection_change()

    def select_at(self, x, y):
        """Выбирает элемент по координатам (клик)"""
        # Перебираем элементы сверху вниз (последний - самый верхний)
        for element in reversed(self.elements):
            if element.is_visible and element.contains_point(x, y):
                self.select_element(element)
                return element
        
        # Ничего не найдено - снимаем выделение
        self.select_element(None)
        return None

    def deselect_all(self):
        """Снимает выделение со всех элементов"""
        self.select_element(None)

    def _notify_selection_change(self):
        """Уведомляет о изменении выбора"""
        if self._notifying:
            return
        
        self._notifying = True
        try:
            for callback in self._selection_callbacks:
                try:
                    callback(self.selected_element)
                except Exception as e:
                    print(f"Selection callback error: {e}")
        finally:
            self._notifying = False

    def get_element_at(self, x, y):
        """Возвращает элемент по координатам (без выбора)"""
        for element in reversed(self.elements):
            if element.is_visible and element.contains_point(x, y):
                return element
        return None

    def move_selected(self, dx, dy):
        """Перемещает выбранный элемент"""
        if self.selected_element:
            self.selected_element.move_by(dx, dy)
            event_bus.emit('element.moved', {'element': self.selected_element})

    def resize_selected(self, width, height):
        """Изменяет размер выбранного элемента с применением ограничений"""
        if self.selected_element:
            element_type = getattr(self.selected_element, 'ELEMENT_TYPE', 'default')
            
            # Применяем ограничения
            original_size = (width, height)
            width, height = SizeConstraints.constrain_size(element_type, width, height)
            
            # Логируем если размеры изменились
            if (width, height) != original_size:
                print(f"[ElementManager] Размеры {element_type} скорректированы при изменении: "
                      f"{original_size[0]}×{original_size[1]} → {width}×{height}")
            
            self.selected_element.resize(width, height)
            event_bus.emit('element.resized', {'element': self.selected_element})

    def set_selected_property(self, key, value):
        """Устанавливает свойство выбранного элемента"""
        if self.selected_element:
            self.selected_element.set_property(key, value)

    def set_selected_properties(self, props):
        """Устанавливает несколько свойств выбранного элемента"""
        if self.selected_element:
            self.selected_element.set_properties(props)
            event_bus.emit('element.updated', {'element': self.selected_element})

    def get_selected_properties(self):
        """Возвращает свойства выбранного элемента"""
        if self.selected_element:
            return self.selected_element.get_properties()
        return None

    def start_creation(self, element_type, **kwargs):
        """Начинает режим создания элемента"""
        self.creation_mode = element_type
        self.creation_params = kwargs  # Дополнительные параметры (например artifact_type)

    def cancel_creation(self):
        """Отменяет режим создания"""
        self.creation_mode = None
        self.creation_start = None
        self.creation_params = {}

    def is_creating(self):
        """Проверяет, активен ли режим создания"""
        return self.creation_mode is not None

    def on_create_start(self, x, y):
        """Начало создания элемента (mousedown)"""
        if self.creation_mode:
            self.creation_start = (x, y)
            self._preview_items = []
            self._size_label = None

    def on_create_drag(self, x, y):
        """Обновление превью во время создания (mousemove)"""
        if self.creation_mode and self.creation_start:
            self._draw_creation_preview(x, y)

    def _draw_creation_preview(self, current_x, current_y):
        """Рисует превью создаваемого элемента"""
        # Очищаем предыдущее превью
        self._clear_preview()
        
        x1, y1 = self.creation_start
        x2, y2 = current_x, current_y
        
        # Нормализуем координаты
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        width = right - left
        height = bottom - top
        
        # Преобразуем в экранные координаты если есть zoom
        if self.zoom_system:
            sx1, sy1 = self.zoom_system.real_to_screen(left, top)
            sx2, sy2 = self.zoom_system.real_to_screen(right, bottom)
        else:
            sx1, sy1, sx2, sy2 = left, top, right, bottom
        
        # Рисуем превью (пунктирный прямоугольник)
        preview = self.canvas.create_rectangle(
            sx1, sy1, sx2, sy2,
            outline="#00ffff",
            width=2,
            dash=(6, 4),
            tags=("creation_preview",)
        )
        self._preview_items.append(preview)
        
        # Заливка с прозрачностью (stipple)
        fill_preview = self.canvas.create_rectangle(
            sx1, sy1, sx2, sy2,
            fill="#00ffff",
            outline="",
            stipple="gray25",
            tags=("creation_preview",)
        )
        self._preview_items.append(fill_preview)
        self.canvas.tag_lower(fill_preview, preview)
        
        # Рисуем метку с размерами
        self._draw_size_label(sx1, sy1, int(width), int(height))

    def _draw_size_label(self, x, y, width, height):
        """Рисует метку с размерами"""
        if self._size_label:
            self.canvas.delete(self._size_label)
            self._size_label = None
        
        text = f"{width} × {height}"
        
        # Позиция над элементом
        label_x = x
        label_y = y - 25
        
        # Фон для метки
        bg = self.canvas.create_rectangle(
            label_x - 5, label_y - 12,
            label_x + len(text) * 8 + 5, label_y + 12,
            fill="#222222",
            outline="#00ffff",
            tags=("size_label",)
        )
        self._preview_items.append(bg)
        
        # Текст
        self._size_label = self.canvas.create_text(
            label_x + len(text) * 4, label_y,
            text=text,
            fill="#00ffff",
            font=("Arial", 11, "bold"),
            anchor="center",
            tags=("size_label",)
        )
        self._preview_items.append(self._size_label)

    def _clear_preview(self):
        """Очищает превью создания"""
        for item in self._preview_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Item already deleted
        self._preview_items = []
        
        if self._size_label:
            try:
                self.canvas.delete(self._size_label)
            except tk.TclError:
                pass  # Item already deleted
            self._size_label = None

    def on_create_end(self, x, y):
        """Завершение создания элемента (mouseup)"""
        # Очищаем превью
        self._clear_preview()
        
        if self.creation_mode and self.creation_start:
            x1, y1 = self.creation_start
            x2, y2 = x, y
            
            # Нормализуем координаты
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Минимальный размер - если слишком мало, ставим 30, не 100
            if width < 10:
                width = 30
            if height < 10:
                height = 30
            
            # Создаём элемент
            element = self.create_element(self.creation_mode, left, top, width, height)
            
            # Выходим из режима создания
            self.creation_mode = None
            self.creation_start = None
            
            return element
        return None

    def redraw_all(self):
        """Перерисовывает все элементы (главная панель рисуется отдельно)"""
        # Сначала рисуем главную панель (если она установлена)
        if self.main_canvas:
            self.main_canvas.draw()
        
        # Затем рисуем все элементы
        for element in self.elements:
            element.update()

    def clear_all(self):
        """Удаляет все элементы"""
        for element in self.elements:
            element.clear()
        self.elements = []
        self.selected_element = None
        self._notify_selection_change()

    def get_all_elements(self):
        """Возвращает список всех элементов"""
        return self.elements.copy()

    # === Управление порядком слоёв ===
    
    def bring_to_front(self, element):
        """Перемещает элемент на передний план"""
        if element in self.elements:
            self.elements.remove(element)
            self.elements.append(element)
            self._redraw_all()

    def send_to_back(self, element):
        """Перемещает элемент на задний план"""
        if element in self.elements:
            self.elements.remove(element)
            self.elements.insert(0, element)
            self._redraw_all()

    def move_up(self, element):
        """Перемещает элемент на один уровень выше"""
        if element in self.elements:
            index = self.elements.index(element)
            if index < len(self.elements) - 1:
                self.elements.remove(element)
                self.elements.insert(index + 1, element)
                self._redraw_all()

    def move_down(self, element):
        """Перемещает элемент на один уровень ниже"""
        if element in self.elements:
            index = self.elements.index(element)
            if index > 0:
                self.elements.remove(element)
                self.elements.insert(index - 1, element)
                self._redraw_all()

    def _redraw_all(self):
        """Перерисовывает все элементы в правильном порядке"""
        for element in self.elements:
            element.update()

    def get_elements_count(self):
        """Возвращает количество элементов"""
        return len(self.elements)

    def bring_to_front(self, element):
        """Перемещает элемент на передний план"""
        if element in self.elements:
            self.elements.remove(element)
            self.elements.append(element)
            self.redraw_all()

    def send_to_back(self, element):
        """Перемещает элемент на задний план"""
        if element in self.elements:
            self.elements.remove(element)
            self.elements.insert(0, element)
            self.redraw_all()

    def to_dict(self):
        """Сериализует все элементы"""
        return [el.to_dict() for el in self.elements]

    def from_dict(self, data):
        """Восстанавливает элементы из словаря"""
        self.clear_all()
        for item in data:
            element_type = item.get('type')
            if element_type in self.ELEMENT_TYPES:
                element_class = self.ELEMENT_TYPES[element_type]
                element = element_class(self.canvas, self.config)
                if self.zoom_system:
                    element.set_zoom_system(self.zoom_system)
                element.from_dict(item)
                self.elements.append(element)
