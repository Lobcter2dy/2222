#!/usr/bin/env python3
"""
Механизм: Путь (Path)
Движение по произвольной траектории с несколькими точками
"""
import math
from .mechanism_base import MechanismBase


class PathMechanism(MechanismBase):
    """Механизм движения по произвольному пути"""

    MECHANISM_TYPE = "path"
    MECHANISM_SYMBOL = "⤳"
    MECHANISM_NAME = "Путь"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        self.width = 150
        self.height = 100
        
        self.properties.update({
            # Точки пути [(x, y), ...]
            'points': [
                (0, 0),
                (50, -30),
                (100, 0),
                (150, 30),
                (200, 0),
            ],
            
            # Тип пути
            'path_type': 'linear',       # linear, bezier, catmull_rom
            'closed': False,             # Замкнутый путь
            
            # Движение
            'speed': 100,                # Пикселей в секунду
            'constant_speed': True,      # Постоянная скорость
            
            # Поведение
            'loop': True,
            'reverse_on_end': False,
            'easing': 'linear',
            'orient_to_path': False,     # Поворачивать элемент по направлению
            
            # Визуализация
            'show_path': True,           # Показывать путь
            'show_points': True,         # Показывать точки
            'path_color': '#666666',
            'point_color': '#888888',
        })
        
        self.element_manager = None
        self._initial_positions = {}
        self._path_length = 0
        self._segment_lengths = []
        self._cumulative_lengths = []

    def set_element_manager(self, manager):
        self.element_manager = manager

    def _calculate_path(self):
        """Вычисляет длину пути и сегментов"""
        points = self.properties.get('points', [])
        if len(points) < 2:
            return
        
        self._segment_lengths = []
        self._cumulative_lengths = [0]
        total = 0
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx * dx + dy * dy)
            self._segment_lengths.append(length)
            total += length
            self._cumulative_lengths.append(total)
        
        if self.properties.get('closed') and len(points) > 2:
            p1 = points[-1]
            p2 = points[0]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx * dx + dy * dy)
            self._segment_lengths.append(length)
            total += length
            self._cumulative_lengths.append(total)
        
        self._path_length = total

    def draw(self):
        if not self.is_visible:
            return

        points = self.properties.get('points', [])
        if len(points) < 2:
            return
        
        # Цвет состояния
        if self.is_active and not self.is_paused:
            color = "#00ff00"
        elif self.is_paused:
            color = "#ffaa00"
        else:
            color = "#666666"
        
        # Преобразуем точки в экранные координаты
        screen_points = []
        for px, py in points:
            abs_x = self.x + px
            abs_y = self.y + py
            if self.zoom_system:
                sx, sy = self.zoom_system.real_to_screen(abs_x, abs_y)
            else:
                sx, sy = abs_x, abs_y
            screen_points.append((sx, sy))
        
        # 1. Линия пути
        if self.properties.get('show_path', True):
            flat_points = []
            for p in screen_points:
                flat_points.extend(p)
            
            if self.properties.get('closed'):
                flat_points.extend(screen_points[0])
            
            path_line = self.canvas.create_line(
                *flat_points,
                fill=color, width=2, dash=(6, 4),
                smooth=self.properties.get('path_type') != 'linear',
                tags=("mechanism", self.id, "path")
            )
            self.canvas_items.append(path_line)
        
        # 2. Точки пути
        if self.properties.get('show_points', True):
            for i, (sx, sy) in enumerate(screen_points):
                r = 6 if i in [0, len(screen_points) - 1] else 4
                
                if i == 0:
                    point_color = "#00aa00"  # Старт
                elif i == len(screen_points) - 1 and not self.properties.get('closed'):
                    point_color = "#aa0000"  # Финиш
                else:
                    point_color = "#888888"  # Промежуточная
                
                point = self.canvas.create_oval(
                    sx - r, sy - r, sx + r, sy + r,
                    fill=point_color, outline="#ffffff", width=1,
                    tags=("mechanism", self.id, f"point_{i}")
                )
                self.canvas_items.append(point)
                
                # Номер точки
                num = self.canvas.create_text(
                    sx, sy - r - 8,
                    text=str(i + 1),
                    fill="#aaaaaa",
                    font=("Arial", 8),
                    tags=("mechanism", self.id, f"num_{i}")
                )
                self.canvas_items.append(num)
        
        # 3. Текущая позиция (anchor)
        current_pos = self._get_position_at_progress(self._animation_progress)
        if current_pos:
            ax = self.x + current_pos[0]
            ay = self.y + current_pos[1]
            if self.zoom_system:
                ax, ay = self.zoom_system.real_to_screen(ax, ay)
            
            anchor = self.canvas.create_oval(
                ax - 8, ay - 8, ax + 8, ay + 8,
                fill="#ffff00", outline="#000000", width=2,
                tags=("mechanism", self.id, "anchor")
            )
            self.canvas_items.append(anchor)
        
        # 4. Название
        if screen_points:
            center_x = sum(p[0] for p in screen_points) / len(screen_points)
            center_y = sum(p[1] for p in screen_points) / len(screen_points)
            
            name = self.canvas.create_text(
                center_x, center_y,
                text=f"{self.MECHANISM_SYMBOL}",
                fill="#ffffff",
                font=("Arial", 14, "bold"),
                tags=("mechanism", self.id, "symbol")
            )
            self.canvas_items.append(name)
            
            label = self.canvas.create_text(
                center_x, center_y + 20,
                text=f"{self.MECHANISM_NAME} ({len(points)} точек)",
                fill="#666666",
                font=("Arial", 8),
                tags=("mechanism", self.id, "label")
            )
            self.canvas_items.append(label)
        
        # 5. Индикатор элементов
        if self.attached_elements and screen_points:
            attach = self.canvas.create_text(
                screen_points[0][0], screen_points[0][1] - 25,
                text=f"📎 {len(self.attached_elements)}",
                fill="#aaaaaa",
                font=("Arial", 9),
                tags=("mechanism", self.id, "attach")
            )
            self.canvas_items.append(attach)

    def _get_position_at_progress(self, progress):
        """Возвращает позицию на пути по прогрессу (0-1)"""
        points = self.properties.get('points', [])
        if len(points) < 2:
            return None
        
        if not self._segment_lengths:
            self._calculate_path()
        
        if self._path_length == 0:
            return points[0]
        
        # Целевое расстояние
        target_dist = progress * self._path_length
        
        # Находим сегмент
        for i, cum_len in enumerate(self._cumulative_lengths):
            if i == 0:
                continue
            if cum_len >= target_dist:
                # Интерполяция внутри сегмента
                seg_start = self._cumulative_lengths[i - 1]
                seg_len = self._segment_lengths[i - 1]
                
                if seg_len == 0:
                    t = 0
                else:
                    t = (target_dist - seg_start) / seg_len
                
                p1_idx = i - 1
                p2_idx = i if i < len(points) else 0
                
                if p2_idx >= len(points):
                    p2_idx = 0
                
                p1 = points[p1_idx]
                p2 = points[p2_idx]
                
                x = p1[0] + (p2[0] - p1[0]) * t
                y = p1[1] + (p2[1] - p1[1]) * t
                
                return (x, y)
        
        # По умолчанию - последняя точка
        return points[-1] if not self.properties.get('closed') else points[0]

    def attach_element(self, element_id):
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)
            
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    self._initial_positions[element_id] = (element.x, element.y)
            
            self.update()

    def detach_element(self, element_id):
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            if element_id in self._initial_positions:
                if self.element_manager:
                    element = self.element_manager.get_element_by_id(element_id)
                    if element:
                        x, y = self._initial_positions[element_id]
                        element.move_to(x, y)
                del self._initial_positions[element_id]
            
            self.update()

    def _run_animation(self):
        if not self.is_active or self.is_paused:
            return
        
        if self._path_length == 0:
            self._calculate_path()
        
        if self._path_length == 0:
            return
        
        speed = self.properties.get('speed', 100)
        frame_time = 1 / 60
        step = (speed * frame_time) / self._path_length
        
        self._animation_progress += step * self._animation_direction
        
        # Границы
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            
            if self.properties.get('loop'):
                if self.properties.get('closed'):
                    self._animation_progress = 0.0
                elif self.properties.get('reverse_on_end'):
                    self._animation_direction = -1
                else:
                    self._animation_progress = 0.0
            elif self.properties.get('reverse_on_end'):
                self._animation_direction = -1
            else:
                self.is_active = False
                self.update()
                return
        
        elif self._animation_progress <= 0.0:
            self._animation_progress = 0.0
            if self.properties.get('loop') or self.properties.get('reverse_on_end'):
                self._animation_direction = 1
            else:
                self.is_active = False
                self.update()
                return
        
        # Обновляем позиции
        self._update_attached_positions()
        
        self.update()
        self._animation_id = self.canvas.after(16, self._run_animation)

    def _update_attached_positions(self):
        if not self.element_manager:
            return
        
        current_pos = self._get_position_at_progress(self._animation_progress)
        if not current_pos:
            return
        
        for element_id in self.attached_elements:
            if element_id not in self._initial_positions:
                continue
            
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            # Смещение от начальной позиции
            init_x, init_y = self._initial_positions[element_id]
            points = self.properties.get('points', [])
            
            if points:
                start_x, start_y = points[0]
                offset_x = current_pos[0] - start_x
                offset_y = current_pos[1] - start_y
                
                element.move_to(init_x + offset_x, init_y + offset_y)

    def add_point(self, x, y, index=None):
        """Добавляет точку в путь"""
        points = self.properties.get('points', [])
        if index is None:
            points.append((x, y))
        else:
            points.insert(index, (x, y))
        self.properties['points'] = points
        self._calculate_path()
        self.update()

    def remove_point(self, index):
        """Удаляет точку из пути"""
        points = self.properties.get('points', [])
        if 0 <= index < len(points) and len(points) > 2:
            points.pop(index)
            self.properties['points'] = points
            self._calculate_path()
            self.update()

    def move_point(self, index, x, y):
        """Перемещает точку"""
        points = self.properties.get('points', [])
        if 0 <= index < len(points):
            points[index] = (x, y)
            self.properties['points'] = points
            self._calculate_path()
            self.update()

    def start(self):
        self._calculate_path()
        super().start()

