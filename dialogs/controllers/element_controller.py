"""
Контроллер элементов
Управляет операциями с элементами: создание, выделение, перемещение
"""

import tkinter as tk
from typing import Optional, List, Tuple
from ..utils.logger import get_logger
from ..utils.event_bus import emit

log = get_logger('ElementController')


class ElementController:
    """
    Контроллер элементов.
    Отвечает за:
    - Создание элементов
    - Выделение и снятие выделения
    - Перемещение и изменение размера
    - Копирование, вставка, дублирование
    - Удаление
    """
    
    def __init__(self, app_controller):
        """
        Args:
            app_controller: Главный контроллер приложения
        """
        self.app = app_controller
        
        # Буфер обмена
        self._clipboard = None
        
        # Состояние перетаскивания
        self._drag_start = None
        self._drag_offset = (0, 0)
        
    @property
    def element_manager(self):
        return self.app.element_manager
        
    @property
    def selection_tool(self):
        return getattr(self.app, 'selection_tool', None)
        
    # === Выделение ===
    
    def select(self, element):
        """
        Выделяет элемент.
        
        Args:
            element: Элемент для выделения
        """
        if self.element_manager:
            self.element_manager.select(element)
            emit('element:selected', element)
            log.debug(f"Selected: {element.id}")
            
    def deselect(self):
        """Снимает выделение с текущего элемента"""
        if self.element_manager:
            old = self.element_manager.selected_element
            self.element_manager.deselect()
            if old:
                emit('element:deselected', old)
                
    def deselect_all(self):
        """Снимает выделение со всех элементов"""
        self.deselect()
        
    def select_all(self):
        """Выделяет все элементы (для будущего мульти-выделения)"""
        # TODO: реализовать мульти-выделение
        if self.element_manager:
            elements = self.element_manager.get_all_elements()
            if elements:
                self.select(elements[-1])  # Пока выделяем последний
                
    def get_selected(self):
        """Возвращает выделенный элемент"""
        if self.element_manager:
            return self.element_manager.selected_element
        return None
        
    # === Создание ===
    
    def start_create(self, element_type: str, x: int, y: int):
        """
        Начинает создание элемента.
        
        Args:
            element_type: Тип элемента
            x, y: Начальные координаты
        """
        if self.element_manager:
            self.element_manager.start_create(element_type, x, y)
            
    def update_create(self, x: int, y: int):
        """
        Обновляет создаваемый элемент.
        
        Args:
            x, y: Текущие координаты
        """
        if self.element_manager:
            self.element_manager.on_create_move(x, y)
            
    def end_create(self, x: int, y: int):
        """
        Завершает создание элемента.
        
        Args:
            x, y: Конечные координаты
            
        Returns:
            Созданный элемент или None
        """
        if self.element_manager:
            element = self.element_manager.on_create_end(x, y)
            if element:
                emit('element:created', element)
                log.info(f"Created: {element.ELEMENT_TYPE} ({element.id})")
            return element
        return None
        
    # === Перемещение ===
    
    def start_drag(self, x: int, y: int):
        """
        Начинает перетаскивание выделенного элемента.
        
        Args:
            x, y: Начальные координаты
        """
        element = self.get_selected()
        if element:
            self._drag_start = (x, y)
            self._drag_offset = (x - element.x, y - element.y)
            
    def update_drag(self, x: int, y: int):
        """
        Обновляет позицию при перетаскивании.
        
        Args:
            x, y: Текущие координаты
        """
        element = self.get_selected()
        if element and self._drag_start:
            new_x = x - self._drag_offset[0]
            new_y = y - self._drag_offset[1]
            
            # Привязка к сетке
            if self.app.canvas_controller:
                new_x, new_y = self.app.canvas_controller.snap_to_grid(new_x, new_y)
                
            element.move_to(new_x, new_y)
            
    def end_drag(self):
        """Завершает перетаскивание"""
        element = self.get_selected()
        if element and self._drag_start:
            emit('element:moved', element)
            log.debug(f"Moved: {element.id} to ({element.x}, {element.y})")
        self._drag_start = None
        
    # === Изменение размера ===
    
    def resize(self, width: int, height: int):
        """
        Изменяет размер выделенного элемента.
        
        Args:
            width, height: Новые размеры
        """
        element = self.get_selected()
        if element:
            element.width = max(10, width)
            element.height = max(10, height)
            element.update()
            emit('element:resized', element)
            
    # === Буфер обмена ===
    
    def copy(self):
        """Копирует выделенный элемент в буфер"""
        element = self.get_selected()
        if element:
            self._clipboard = element.to_dict()
            log.debug(f"Copied: {element.id}")
            
    def paste(self):
        """Вставляет элемент из буфера"""
        if not self._clipboard or not self.element_manager:
            return None
            
        data = self._clipboard.copy()
        
        # Смещаем позицию
        data['x'] = data.get('x', 0) + 20
        data['y'] = data.get('y', 0) + 20
        
        # Создаём новый элемент
        element = self.element_manager.create_from_dict(data)
        if element:
            self.select(element)
            emit('element:created', element)
            log.debug(f"Pasted: {element.id}")
            
        return element
        
    def duplicate(self):
        """Дублирует выделенный элемент"""
        self.copy()
        return self.paste()
        
    # === Удаление ===
    
    def delete_selected(self):
        """Удаляет выделенный элемент"""
        element = self.get_selected()
        if element and self.element_manager:
            element_id = element.id
            self.element_manager.delete(element)
            emit('element:deleted', element_id)
            log.info(f"Deleted: {element_id}")
            
    def delete(self, element):
        """
        Удаляет конкретный элемент.
        
        Args:
            element: Элемент для удаления
        """
        if element and self.element_manager:
            element_id = element.id
            self.element_manager.delete(element)
            emit('element:deleted', element_id)
            
    # === Слои ===
    
    def bring_to_front(self):
        """Поднимает выделенный элемент на передний план"""
        element = self.get_selected()
        if element and self.element_manager:
            self.element_manager.bring_to_front(element)
            
    def send_to_back(self):
        """Отправляет выделенный элемент на задний план"""
        element = self.get_selected()
        if element and self.element_manager:
            self.element_manager.send_to_back(element)
            
    # === Поиск ===
    
    def find_at(self, x: float, y: float):
        """
        Находит элемент по координатам.
        
        Args:
            x, y: Координаты
            
        Returns:
            Элемент или None
        """
        if self.element_manager:
            return self.element_manager.find_at(x, y)
        return None
        
    def find_by_id(self, element_id: str):
        """
        Находит элемент по ID.
        
        Args:
            element_id: ID элемента
            
        Returns:
            Элемент или None
        """
        if self.element_manager:
            return self.element_manager.get_element_by_id(element_id)
        return None

