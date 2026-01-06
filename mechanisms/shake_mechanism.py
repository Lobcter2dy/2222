#!/usr/bin/env python3
"""
Механизм: Тряска (Shake)
Встряхивание элементов с различными режимами
"""
import math
import random
from .mechanism_base import MechanismBase


class ShakeMechanism(MechanismBase):
    """Механизм тряски элементов"""

    MECHANISM_TYPE = "shake"
    MECHANISM_SYMBOL = "≋"
    MECHANISM_NAME = "Тряска"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        self.width = 70
        self.height = 70
        
        self.properties.update({
            # Амплитуда
            'amplitude_x': 10,           # Амплитуда по X (px)
            'amplitude_y': 10,           # Амплитуда по Y (px)
            
            # Режим
            'mode': 'random',            # random, horizontal, vertical, circular, wave
            
            # Скорость и частота
            'frequency': 20,             # Колебаний в секунду
            'decay': 0.0,                # Затухание (0-1, 0 = нет затухания)
            
            # Поведение
            'duration': 500,             # Длительность (мс, 0 = бесконечно)
            'loop': False,
            'intensity': 1.0,            # Интенсивность (множитель)
            
            # Случайность
            'randomness': 0.5,           # Доля случайности (0-1)
            'seed': None,                # Seed для случайных чисел
        })
        
        self.element_manager = None
        self._initial_positions = {}
        self._shake_offset_x = 0
        self._shake_offset_y = 0
        self._frame_count = 0
        self._start_time = 0

    def set_element_manager(self, manager):
        self.element_manager = manager

    def draw(self):
        if not self.is_visible:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(cx, cy)
            r = self.zoom_system.scale_value(self.width / 2)
        else:
            sx, sy = cx, cy
            r = self.width / 2
        
        # Цвет состояния
        if self.is_active and not self.is_paused:
            color = "#ff6600"
        elif self.is_paused:
            color = "#ffaa00"
        else:
            color = "#666666"
        
        # 1. Внешний квадрат с тряской
        shake_x = self._shake_offset_x * 0.3 if self.is_active else 0
        shake_y = self._shake_offset_y * 0.3 if self.is_active else 0
        
        outer = self.canvas.create_rectangle(
            sx - r + shake_x, sy - r + shake_y,
            sx + r + shake_x, sy + r + shake_y,
            outline=color, width=2, dash=(3, 3),
            tags=("mechanism", self.id, "outer")
        )
        self.canvas_items.append(outer)
        
        # 2. Линии вибрации
        mode = self.properties.get('mode', 'random')
        
        if mode in ['horizontal', 'random']:
            for i in range(-2, 3):
                line = self.canvas.create_line(
                    sx - r * 0.7 + shake_x, sy + i * 8 + shake_y,
                    sx + r * 0.7 + shake_x, sy + i * 8 + shake_y,
                    fill=color, width=1, dash=(2, 2),
                    tags=("mechanism", self.id, "h_line")
                )
                self.canvas_items.append(line)
        
        if mode in ['vertical', 'random']:
            for i in range(-2, 3):
                line = self.canvas.create_line(
                    sx + i * 8 + shake_x, sy - r * 0.7 + shake_y,
                    sx + i * 8 + shake_x, sy + r * 0.7 + shake_y,
                    fill=color, width=1, dash=(2, 2),
                    tags=("mechanism", self.id, "v_line")
                )
                self.canvas_items.append(line)
        
        # 3. Центральный символ
        symbol = self.canvas.create_text(
            sx + shake_x, sy + shake_y,
            text=self.MECHANISM_SYMBOL,
            fill="#ffffff",
            font=("Arial", 16, "bold"),
            tags=("mechanism", self.id, "symbol")
        )
        self.canvas_items.append(symbol)
        
        # 4. Название
        name = self.canvas.create_text(
            sx, sy + r + 15,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#666666",
            font=("Arial", 8),
            tags=("mechanism", self.id, "name")
        )
        self.canvas_items.append(name)
        
        # 5. Режим
        mode_text = {'random': 'хаос', 'horizontal': '↔', 'vertical': '↕', 
                     'circular': '◎', 'wave': '∿'}.get(mode, '')
        mode_label = self.canvas.create_text(
            sx, sy + r + 28,
            text=mode_text,
            fill="#888888",
            font=("Arial", 9),
            tags=("mechanism", self.id, "mode")
        )
        self.canvas_items.append(mode_label)
        
        # 6. Индикатор элементов
        if self.attached_elements:
            attach = self.canvas.create_text(
                sx, sy - r - 12,
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
        
        duration = self.properties.get('duration', 500)
        frequency = self.properties.get('frequency', 20)
        amplitude_x = self.properties.get('amplitude_x', 10)
        amplitude_y = self.properties.get('amplitude_y', 10)
        decay = self.properties.get('decay', 0.0)
        intensity = self.properties.get('intensity', 1.0)
        randomness = self.properties.get('randomness', 0.5)
        mode = self.properties.get('mode', 'random')
        
        self._frame_count += 1
        frame_time = 1 / 60  # 60 FPS
        current_time = self._frame_count * frame_time
        
        # Проверяем длительность
        if duration > 0 and current_time * 1000 >= duration:
            if self.properties.get('loop'):
                self._frame_count = 0
            else:
                self.stop()
                return
        
        # Вычисляем затухание
        if duration > 0 and decay > 0:
            progress = (current_time * 1000) / duration
            intensity *= (1 - progress * decay)
        
        # Вычисляем смещение в зависимости от режима
        t = current_time * frequency * 2 * math.pi
        
        if mode == 'horizontal':
            self._shake_offset_x = amplitude_x * math.sin(t) * intensity
            self._shake_offset_y = 0
        
        elif mode == 'vertical':
            self._shake_offset_x = 0
            self._shake_offset_y = amplitude_y * math.sin(t) * intensity
        
        elif mode == 'circular':
            self._shake_offset_x = amplitude_x * math.cos(t) * intensity
            self._shake_offset_y = amplitude_y * math.sin(t) * intensity
        
        elif mode == 'wave':
            # Волнообразное движение
            self._shake_offset_x = amplitude_x * math.sin(t) * intensity
            self._shake_offset_y = amplitude_y * math.sin(t * 1.5 + 0.5) * intensity
        
        else:  # random
            # Случайная тряска
            rand_x = (random.random() - 0.5) * 2
            rand_y = (random.random() - 0.5) * 2
            
            # Смешиваем синусоиду со случайностью
            base_x = math.sin(t)
            base_y = math.cos(t * 1.3)
            
            self._shake_offset_x = amplitude_x * ((1 - randomness) * base_x + randomness * rand_x) * intensity
            self._shake_offset_y = amplitude_y * ((1 - randomness) * base_y + randomness * rand_y) * intensity
        
        # Обновляем элементы
        self._update_attached_positions()
        
        self.update()
        self._animation_id = self.canvas.after(16, self._run_animation)

    def _update_attached_positions(self):
        if not self.element_manager:
            return
        
        for element_id in self.attached_elements:
            if element_id not in self._initial_positions:
                continue
            
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            init_x, init_y = self._initial_positions[element_id]
            element.move_to(init_x + self._shake_offset_x, init_y + self._shake_offset_y)

    def start(self):
        """Запускает тряску"""
        self._frame_count = 0
        self._shake_offset_x = 0
        self._shake_offset_y = 0
        super().start()

    def stop(self):
        """Останавливает и возвращает элементы"""
        self._shake_offset_x = 0
        self._shake_offset_y = 0
        super().stop()

    def pulse(self, duration=200, amplitude=15):
        """Короткая вибрация"""
        self.properties['duration'] = duration
        self.properties['amplitude_x'] = amplitude
        self.properties['amplitude_y'] = amplitude
        self.properties['decay'] = 1.0
        self.properties['mode'] = 'random'
        self.start()

