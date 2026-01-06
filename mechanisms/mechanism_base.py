#!/usr/bin/env python3
"""
Базовый класс механизма
Все механизмы наследуются от этого класса
"""
import uuid
import tkinter as tk


class MechanismBase:
    """Базовый класс для всех механизмов"""

    MECHANISM_TYPE = "base"
    MECHANISM_SYMBOL = "⚙"
    MECHANISM_NAME = "Механизм"

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Уникальный ID
        self.id = f"mech_{self.MECHANISM_TYPE}_{uuid.uuid4().hex[:6]}"
        
        # Позиция и размеры
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 20
        
        # Состояние
        self.is_visible = True
        self.is_active = False       # Механизм запущен
        self.is_paused = False
        self.is_locked = False       # Заблокирован (нельзя запустить)
        
        # Прикреплённые элементы
        self.attached_elements = []  # Список ID элементов
        
        # Привязка к кнопке
        self.trigger_button_id = None   # ID кнопки которая запускает
        self.trigger_function_id = 0    # Номер функции
        
        # Свойства механизма
        self.properties = {
            'speed': 100,            # Скорость (px/сек)
            'duration': 0,           # Длительность (0 = бесконечно)
            'loop': False,           # Зацикливание
            'reverse_on_end': True,  # Обратное движение в конце
            'easing': 'linear',      # Функция плавности
            'start_delay': 0,        # Задержка перед стартом (мс)
        }
        
        # Canvas items
        self.canvas_items = []
        
        # Система масштабирования
        self.zoom_system = None
        
        # Анимация
        self._animation_id = None
        self._animation_progress = 0.0  # 0.0 - 1.0
        self._animation_direction = 1   # 1 = вперёд, -1 = назад

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system

    def _scale(self, value):
        """Масштабирует значение"""
        if self.zoom_system:
            return self.zoom_system.scale_value(value)
        return value

    def get_screen_bounds(self):
        """Возвращает экранные координаты"""
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(self.x, self.y)
            sw = self.zoom_system.scale_value(self.width)
            sh = self.zoom_system.scale_value(self.height)
            return (sx, sy, sx + sw, sy + sh)
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def draw(self):
        """Рисует механизм на холсте"""
        raise NotImplementedError

    def clear(self):
        """Удаляет графику с холста"""
        for item in self.canvas_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Элемент уже удалён
        self.canvas_items = []

    def update(self):
        """Перерисовывает механизм"""
        self.clear()
        self.draw()

    # === Управление прикреплёнными элементами ===
    
    def attach_element(self, element_id):
        """Прикрепляет элемент к механизму"""
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)

    def detach_element(self, element_id):
        """Открепляет элемент от механизма"""
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)

    def get_attached_elements(self):
        """Возвращает список прикреплённых элементов"""
        return self.attached_elements.copy()

    # === Управление анимацией ===
    
    def start(self):
        """Запускает механизм"""
        if self.is_active:
            return
        
        self.is_active = True
        self.is_paused = False
        self._animation_progress = 0.0
        self._animation_direction = 1
        
        # Задержка перед стартом
        delay = self.properties.get('start_delay', 0)
        if delay > 0:
            self.canvas.after(delay, self._run_animation)
        else:
            self._run_animation()

    def stop(self):
        """Останавливает механизм"""
        self.is_active = False
        self.is_paused = False
        
        self._cancel_animation()
        
        # Сбрасываем в начальное положение
        self._animation_progress = 0.0
        self._update_attached_positions()
        
    def _cancel_animation(self):
        """Отменяет текущую анимацию (таймер)"""
        if self._animation_id is not None:
            try:
                self.canvas.after_cancel(self._animation_id)
            except tk.TclError:
                pass  # Canvas уже уничтожен
            self._animation_id = None

    def pause(self):
        """Ставит на паузу"""
        if self.is_active and not self.is_paused:
            self.is_paused = True
            self._cancel_animation()

    def resume(self):
        """Возобновляет после паузы"""
        if self.is_active and self.is_paused:
            self.is_paused = False
            self._run_animation()

    def toggle(self):
        """Переключает состояние"""
        if self.is_active:
            if self.is_paused:
                self.resume()
            else:
                self.pause()
        else:
            self.start()

    def _run_animation(self):
        """Основной цикл анимации"""
        raise NotImplementedError

    def _update_attached_positions(self):
        """Обновляет позиции прикреплённых элементов"""
        raise NotImplementedError

    # === Привязка к кнопке ===
    
    def set_trigger_button(self, button_id, function_id=0):
        """Устанавливает кнопку-триггер"""
        self.trigger_button_id = button_id
        self.trigger_function_id = function_id

    def get_trigger_info(self):
        """Возвращает информацию о триггере"""
        return {
            'button_id': self.trigger_button_id,
            'function_id': self.trigger_function_id
        }

    # === Точка закрепа ===
    
    def get_anchor_point(self):
        """Возвращает координаты точки закрепа"""
        # По умолчанию - центр механизма
        return (self.x + self.width / 2, self.y + self.height / 2)

    def set_position(self, x, y):
        """Устанавливает позицию механизма"""
        self.x = x
        self.y = y
        self.update()

    def contains_point(self, screen_x, screen_y):
        """Проверяет содержит ли механизм точку"""
        x1, y1, x2, y2 = self.get_screen_bounds()
        return x1 <= screen_x <= x2 and y1 <= screen_y <= y2

    # === Сериализация ===
    
    def to_dict(self):
        """Сериализует механизм в словарь"""
        return {
            'id': self.id,
            'type': self.MECHANISM_TYPE,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'properties': self.properties.copy(),
            'attached_elements': self.attached_elements.copy(),
            'trigger_button_id': self.trigger_button_id,
            'trigger_function_id': self.trigger_function_id,
        }

    def from_dict(self, data):
        """Загружает механизм из словаря"""
        self.id = data.get('id', self.id)
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.width = data.get('width', 100)
        self.height = data.get('height', 20)
        self.properties.update(data.get('properties', {}))
        self.attached_elements = data.get('attached_elements', [])
        self.trigger_button_id = data.get('trigger_button_id')
        self.trigger_function_id = data.get('trigger_function_id', 0)
        
    def destroy(self):
        """
        Полностью уничтожает механизм.
        Вызывать перед удалением из менеджера.
        """
        self._cancel_animation()
        self.clear()
        self.attached_elements.clear()
        
    def __del__(self):
        """Деструктор - очищает таймеры"""
        try:
            self._cancel_animation()
        except Exception:
            pass  # Игнорируем ошибки при удалении

