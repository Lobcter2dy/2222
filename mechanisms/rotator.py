#!/usr/bin/env python3
"""
Механизм: Вращатель (Rotator)
Вращает прикреплённые элементы вокруг центра
"""
import math
import tkinter as tk
from .mechanism_base import MechanismBase


class RotatorMechanism(MechanismBase):
    """Вращатель - механизм вращения элементов"""

    MECHANISM_TYPE = "rotator"
    MECHANISM_SYMBOL = "⟳"
    MECHANISM_NAME = "Вращатель"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Размеры по умолчанию
        self.width = 100
        self.height = 100
        
        # Дополнительные свойства для вращателя
        self.properties.update({
            'rotation_speed': 45,        # Градусов в секунду
            'direction': 'clockwise',    # clockwise, counterclockwise
            'angle_start': 0,            # Начальный угол
            'angle_end': 360,            # Конечный угол (0 = бесконечное вращение)
            'radius': 50,                # Радиус вращения
            'loop': True,                # Зацикливание
            'reverse_on_end': False,     # Обратное вращение в конце
            'easing': 'linear',          # linear, ease_in, ease_out, ease_in_out
            'pivot_offset_x': 0,         # Смещение центра вращения X
            'pivot_offset_y': 0,         # Смещение центра вращения Y
        })
        
        # Ссылка на element_manager
        self.element_manager = None
        
        # Начальные позиции и углы прикреплённых элементов
        self._initial_positions = {}  # element_id -> (x, y)
        self._initial_angles = {}     # element_id -> angle (relative to pivot)
        self._initial_distances = {}  # element_id -> distance from pivot
        
        # Текущий угол вращения
        self._current_angle = 0

    def set_element_manager(self, manager):
        """Устанавливает менеджер элементов"""
        self.element_manager = manager

    def draw(self):
        """Рисует вращатель на холсте"""
        if not self.is_visible:
            return

        # Центр вращения
        pivot_x = self.x + self.width / 2 + self.properties['pivot_offset_x']
        pivot_y = self.y + self.height / 2 + self.properties['pivot_offset_y']
        radius = self.properties['radius']
        
        # Преобразуем в экранные координаты
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(pivot_x, pivot_y)
            sr = self.zoom_system.scale_value(radius)
        else:
            sx, sy = pivot_x, pivot_y
            sr = radius
        
        # Цвет в зависимости от состояния
        if self.is_active and not self.is_paused:
            color = "#00ff00"  # Зелёный - активен
            pivot_color = "#00ff00"
        elif self.is_paused:
            color = "#ffaa00"  # Оранжевый - пауза
            pivot_color = "#ffaa00"
        else:
            color = "#666666"  # Серый - неактивен
            pivot_color = "#888888"
        
        # 1. Круг радиуса вращения (пунктир)
        orbit = self.canvas.create_oval(
            sx - sr, sy - sr, sx + sr, sy + sr,
            outline=color,
            width=2,
            dash=(6, 4),
            tags=("mechanism", self.id, "orbit")
        )
        self.canvas_items.append(orbit)
        
        # 2. Центр вращения (pivot)
        pivot_size = 8
        pivot_point = self.canvas.create_oval(
            sx - pivot_size, sy - pivot_size,
            sx + pivot_size, sy + pivot_size,
            fill=pivot_color,
            outline="#ffffff",
            width=2,
            tags=("mechanism", self.id, "pivot")
        )
        self.canvas_items.append(pivot_point)
        
        # 3. Стрелка направления
        arrow_angle = math.radians(self._current_angle)
        if self.properties['direction'] == 'counterclockwise':
            arrow_angle = -arrow_angle
        
        arrow_x = sx + sr * 0.7 * math.cos(arrow_angle)
        arrow_y = sy + sr * 0.7 * math.sin(arrow_angle)
        
        arrow = self.canvas.create_line(
            sx, sy, arrow_x, arrow_y,
            fill=color,
            width=3,
            arrow=tk.LAST,
            arrowshape=(10, 12, 5),
            tags=("mechanism", self.id, "arrow")
        )
        self.canvas_items.append(arrow)
        
        # 4. Символ направления в центре
        direction_symbol = "↻" if self.properties['direction'] == 'clockwise' else "↺"
        symbol = self.canvas.create_text(
            sx, sy,
            text=direction_symbol,
            fill="#ffffff",
            font=("Arial", 12, "bold"),
            tags=("mechanism", self.id, "symbol")
        )
        self.canvas_items.append(symbol)
        
        # 5. Индикатор прикреплённых элементов
        if self.attached_elements:
            attach_label = self.canvas.create_text(
                sx, sy - sr - 15,
                text=f"📎 {len(self.attached_elements)}",
                fill="#aaaaaa",
                font=("Arial", 9),
                anchor="center",
                tags=("mechanism", self.id, "attach_count")
            )
            self.canvas_items.append(attach_label)
        
        # 6. Угол вращения
        angle_label = self.canvas.create_text(
            sx, sy + sr + 15,
            text=f"{int(self._current_angle)}°",
            fill="#888888",
            font=("Arial", 9),
            anchor="center",
            tags=("mechanism", self.id, "angle")
        )
        self.canvas_items.append(angle_label)
        
        # 7. Метка типа механизма
        label = self.canvas.create_text(
            sx, sy + sr + 30,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#666666",
            font=("Arial", 8),
            anchor="center",
            tags=("mechanism", self.id, "label")
        )
        self.canvas_items.append(label)

    def attach_element(self, element_id):
        """Прикрепляет элемент и вычисляет его параметры относительно центра"""
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)
            
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    # Сохраняем начальную позицию
                    self._initial_positions[element_id] = (element.x, element.y)
                    
                    # Вычисляем позицию относительно центра вращения
                    pivot_x = self.x + self.width / 2 + self.properties['pivot_offset_x']
                    pivot_y = self.y + self.height / 2 + self.properties['pivot_offset_y']
                    
                    # Центр элемента
                    elem_cx = element.x + element.width / 2
                    elem_cy = element.y + element.height / 2
                    
                    # Расстояние от pivot до элемента
                    dx = elem_cx - pivot_x
                    dy = elem_cy - pivot_y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Начальный угол
                    angle = math.degrees(math.atan2(dy, dx))
                    
                    self._initial_distances[element_id] = distance
                    self._initial_angles[element_id] = angle
            
            self.update()

    def detach_element(self, element_id):
        """Открепляет элемент и возвращает его в начальную позицию"""
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            # Возвращаем в начальную позицию
            if element_id in self._initial_positions:
                if self.element_manager:
                    element = self.element_manager.get_element_by_id(element_id)
                    if element:
                        init_x, init_y = self._initial_positions[element_id]
                        element.move_to(init_x, init_y)
                
                del self._initial_positions[element_id]
            
            if element_id in self._initial_angles:
                del self._initial_angles[element_id]
            if element_id in self._initial_distances:
                del self._initial_distances[element_id]
            
            self.update()

    def _run_animation(self):
        """Основной цикл анимации вращения"""
        if not self.is_active or self.is_paused:
            return
        
        # Скорость вращения
        speed = self.properties.get('rotation_speed', 45)
        direction = 1 if self.properties['direction'] == 'clockwise' else -1
        
        # Шаг угла за кадр (60 FPS)
        frame_time = 1 / 60
        angle_step = speed * frame_time * direction
        
        # Обновляем текущий угол
        self._current_angle += angle_step
        
        # Проверяем границы
        angle_end = self.properties.get('angle_end', 360)
        
        if angle_end > 0:  # Есть ограничение
            if direction > 0 and self._current_angle >= angle_end:
                self._current_angle = angle_end
                if self.properties.get('reverse_on_end'):
                    self.properties['direction'] = 'counterclockwise'
                elif self.properties.get('loop'):
                    self._current_angle = self.properties.get('angle_start', 0)
                else:
                    self.is_active = False
                    self._update_attached_positions()
                    self.update()
                    return
            elif direction < 0 and self._current_angle <= self.properties.get('angle_start', 0):
                self._current_angle = self.properties.get('angle_start', 0)
                if self.properties.get('reverse_on_end'):
                    self.properties['direction'] = 'clockwise'
                elif self.properties.get('loop'):
                    self._current_angle = angle_end
                else:
                    self.is_active = False
                    self._update_attached_positions()
                    self.update()
                    return
        else:
            # Бесконечное вращение - нормализуем угол
            self._current_angle = self._current_angle % 360
        
        # Обновляем позиции элементов
        self._update_attached_positions()
        
        # Перерисовываем
        self.update()
        
        # Следующий кадр
        self._animation_id = self.canvas.after(16, self._run_animation)

    def _update_attached_positions(self):
        """Обновляет позиции прикреплённых элементов"""
        if not self.element_manager:
            return
        
        # Центр вращения
        pivot_x = self.x + self.width / 2 + self.properties['pivot_offset_x']
        pivot_y = self.y + self.height / 2 + self.properties['pivot_offset_y']
        
        for element_id in self.attached_elements:
            if element_id not in self._initial_angles or element_id not in self._initial_distances:
                continue
            
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            # Исходный угол и расстояние
            initial_angle = self._initial_angles[element_id]
            distance = self._initial_distances[element_id]
            
            # Новый угол
            new_angle = math.radians(initial_angle + self._current_angle)
            
            # Новая позиция центра элемента
            new_cx = pivot_x + distance * math.cos(new_angle)
            new_cy = pivot_y + distance * math.sin(new_angle)
            
            # Позиция элемента (от центра к углу)
            new_x = new_cx - element.width / 2
            new_y = new_cy - element.height / 2
            
            element.move_to(new_x, new_y)

    def get_pivot_point(self):
        """Возвращает координаты центра вращения"""
        pivot_x = self.x + self.width / 2 + self.properties['pivot_offset_x']
        pivot_y = self.y + self.height / 2 + self.properties['pivot_offset_y']
        return (pivot_x, pivot_y)

    def set_rotation_speed(self, speed):
        """Устанавливает скорость вращения"""
        self.properties['rotation_speed'] = max(1, speed)

    def set_direction(self, direction):
        """Устанавливает направление вращения"""
        if direction in ('clockwise', 'counterclockwise'):
            self.properties['direction'] = direction
            self.update()

    def set_radius(self, radius):
        """Устанавливает радиус вращения"""
        self.properties['radius'] = max(10, radius)
        self.update()

    def reset_angle(self):
        """Сбрасывает угол на начальный"""
        self._current_angle = self.properties.get('angle_start', 0)
        self._update_attached_positions()
        self.update()

