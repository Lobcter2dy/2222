#!/usr/bin/env python3
"""
Механизм: Масштабирование (Scale)
Плавно изменяет размер прикреплённых элементов
"""
import math
from .mechanism_base import MechanismBase


class ScaleMechanism(MechanismBase):
    """Механизм масштабирования элементов"""

    MECHANISM_TYPE = "scale"
    MECHANISM_SYMBOL = "⤢"
    MECHANISM_NAME = "Масштаб"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        self.width = 80
        self.height = 80
        
        self.properties.update({
            # Масштаб
            'scale_start': 1.0,          # Начальный масштаб
            'scale_end': 1.5,            # Конечный масштаб
            'scale_x': True,             # Масштабировать по X
            'scale_y': True,             # Масштабировать по Y
            'uniform': True,             # Одинаковый масштаб
            
            # Центр масштабирования
            'origin': 'center',          # center, top_left, top_right, bottom_left, bottom_right
            
            # Анимация
            'speed': 1.0,                # Скорость (масштаб в секунду)
            'loop': True,
            'reverse_on_end': True,
            'easing': 'ease_in_out',
            
            # Дополнительно
            'auto_start': False,
            'pulse_mode': False,         # Режим пульсации
            'pulse_count': 0,            # Количество пульсаций (0 = бесконечно)
        })
        
        self.element_manager = None
        self._initial_sizes = {}       # element_id -> (width, height)
        self._initial_positions = {}   # element_id -> (x, y)
        self._current_scale = 1.0
        self._pulse_counter = 0

    def set_element_manager(self, manager):
        self.element_manager = manager

    def draw(self):
        if not self.is_visible:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(cx, cy)
            size = self.zoom_system.scale_value(self.width / 2)
        else:
            sx, sy = cx, cy
            size = self.width / 2
        
        # Цвет состояния
        if self.is_active and not self.is_paused:
            color = "#00ff00"
        elif self.is_paused:
            color = "#ffaa00"
        else:
            color = "#666666"
        
        # 1. Внешний квадрат
        outer = self.canvas.create_rectangle(
            sx - size, sy - size, sx + size, sy + size,
            outline=color, width=2, dash=(4, 4),
            tags=("mechanism", self.id, "outer")
        )
        self.canvas_items.append(outer)
        
        # 2. Внутренний квадрат (текущий масштаб)
        inner_size = size * (self._current_scale / self.properties['scale_end'])
        inner = self.canvas.create_rectangle(
            sx - inner_size, sy - inner_size,
            sx + inner_size, sy + inner_size,
            outline=color, fill="", width=2,
            tags=("mechanism", self.id, "inner")
        )
        self.canvas_items.append(inner)
        
        # 3. Стрелки масштабирования
        arrow_offset = size * 0.7
        arrows = [
            (sx - arrow_offset, sy, sx - size, sy, "◀"),
            (sx + arrow_offset, sy, sx + size, sy, "▶"),
            (sx, sy - arrow_offset, sx, sy - size, "▲"),
            (sx, sy + arrow_offset, sx, sy + size, "▼"),
        ]
        
        for ax1, ay1, ax2, ay2, symbol in arrows:
            arrow = self.canvas.create_line(
                ax1, ay1, ax2, ay2,
                fill=color, width=2,
                tags=("mechanism", self.id, "arrow")
            )
            self.canvas_items.append(arrow)
        
        # 4. Центр
        pivot = self.canvas.create_oval(
            sx - 5, sy - 5, sx + 5, sy + 5,
            fill=color, outline="#ffffff", width=1,
            tags=("mechanism", self.id, "pivot")
        )
        self.canvas_items.append(pivot)
        
        # 5. Метка масштаба
        scale_text = f"{self._current_scale:.2f}x"
        label = self.canvas.create_text(
            sx, sy + size + 15,
            text=scale_text,
            fill="#888888",
            font=("Arial", 9),
            tags=("mechanism", self.id, "scale_label")
        )
        self.canvas_items.append(label)
        
        # 6. Название
        name = self.canvas.create_text(
            sx, sy + size + 30,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#666666",
            font=("Arial", 8),
            tags=("mechanism", self.id, "name")
        )
        self.canvas_items.append(name)
        
        # 7. Индикатор элементов
        if self.attached_elements:
            attach = self.canvas.create_text(
                sx, sy - size - 15,
                text=f"📎 {len(self.attached_elements)}",
                fill="#aaaaaa",
                font=("Arial", 9),
                tags=("mechanism", self.id, "attach")
            )
            self.canvas_items.append(attach)

    def attach_element(self, element_id):
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)
            
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    self._initial_sizes[element_id] = (element.width, element.height)
                    self._initial_positions[element_id] = (element.x, element.y)
            
            self.update()

    def detach_element(self, element_id):
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            # Восстанавливаем размер
            if element_id in self._initial_sizes:
                if self.element_manager:
                    element = self.element_manager.get_element_by_id(element_id)
                    if element:
                        w, h = self._initial_sizes[element_id]
                        element.width = w
                        element.height = h
                        if element_id in self._initial_positions:
                            x, y = self._initial_positions[element_id]
                            element.move_to(x, y)
                        element.update()
                del self._initial_sizes[element_id]
            
            if element_id in self._initial_positions:
                del self._initial_positions[element_id]
            
            self.update()

    def _run_animation(self):
        if not self.is_active or self.is_paused:
            return
        
        speed = self.properties.get('speed', 1.0)
        scale_start = self.properties['scale_start']
        scale_end = self.properties['scale_end']
        scale_range = abs(scale_end - scale_start)
        
        if scale_range == 0:
            return
        
        # Шаг за кадр
        frame_time = 1 / 60
        step = (speed * frame_time) / scale_range
        
        self._animation_progress += step * self._animation_direction
        
        # Границы
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            if self.properties.get('pulse_mode'):
                self._pulse_counter += 1
                pulse_count = self.properties.get('pulse_count', 0)
                if pulse_count > 0 and self._pulse_counter >= pulse_count:
                    self.is_active = False
                    self.update()
                    return
            
            if self.properties.get('reverse_on_end'):
                self._animation_direction = -1
            elif self.properties.get('loop'):
                self._animation_progress = 0.0
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
        
        # Применяем easing
        eased = self._apply_easing(self._animation_progress)
        
        # Вычисляем текущий масштаб
        self._current_scale = scale_start + (scale_end - scale_start) * eased
        
        # Обновляем элементы
        self._update_attached_positions()
        
        self.update()
        self._animation_id = self.canvas.after(16, self._run_animation)

    def _apply_easing(self, t):
        easing = self.properties.get('easing', 'linear')
        
        if easing == 'linear':
            return t
        elif easing == 'ease_in':
            return t * t
        elif easing == 'ease_out':
            return 1 - (1 - t) * (1 - t)
        elif easing == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            return 1 - 2 * (1 - t) * (1 - t)
        elif easing == 'bounce':
            if t < 0.5:
                return 8 * t * t * t * t
            return 1 - 8 * (1 - t) ** 4
        elif easing == 'elastic':
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
        
        return t

    def _update_attached_positions(self):
        if not self.element_manager:
            return
        
        origin = self.properties.get('origin', 'center')
        scale_x = self.properties.get('scale_x', True)
        scale_y = self.properties.get('scale_y', True)
        
        for element_id in self.attached_elements:
            if element_id not in self._initial_sizes:
                continue
            
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            init_w, init_h = self._initial_sizes[element_id]
            init_x, init_y = self._initial_positions.get(element_id, (element.x, element.y))
            
            # Новые размеры
            new_w = init_w * self._current_scale if scale_x else init_w
            new_h = init_h * self._current_scale if scale_y else init_h
            
            # Смещение для сохранения origin
            if origin == 'center':
                new_x = init_x - (new_w - init_w) / 2
                new_y = init_y - (new_h - init_h) / 2
            elif origin == 'top_left':
                new_x = init_x
                new_y = init_y
            elif origin == 'top_right':
                new_x = init_x - (new_w - init_w)
                new_y = init_y
            elif origin == 'bottom_left':
                new_x = init_x
                new_y = init_y - (new_h - init_h)
            elif origin == 'bottom_right':
                new_x = init_x - (new_w - init_w)
                new_y = init_y - (new_h - init_h)
            else:
                new_x = init_x
                new_y = init_y
            
            element.width = new_w
            element.height = new_h
            element.move_to(new_x, new_y)

