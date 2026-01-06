#!/usr/bin/env python3
"""
Механизм: Прозрачность (Fade)
Плавное появление и исчезновение элементов
"""
import math
from .mechanism_base import MechanismBase


class FadeMechanism(MechanismBase):
    """Механизм управления прозрачностью"""

    MECHANISM_TYPE = "fade"
    MECHANISM_SYMBOL = "◐"
    MECHANISM_NAME = "Прозрачность"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        self.width = 60
        self.height = 60
        
        self.properties.update({
            # Прозрачность (0-100)
            'opacity_start': 0,          # Начальная прозрачность
            'opacity_end': 100,          # Конечная прозрачность
            
            # Режим
            'mode': 'fade_in',           # fade_in, fade_out, fade_in_out, blink
            'blink_count': 0,            # Количество морганий (0 = бесконечно)
            
            # Скорость
            'duration': 1000,            # Длительность перехода (мс)
            'speed': 50,                 # Единиц в секунду
            
            # Поведение
            'loop': False,
            'reverse_on_end': False,
            'easing': 'linear',
            'start_delay': 0,
            
            # Специальные эффекты
            'flash_on_complete': False,  # Вспышка в конце
            'hide_on_zero': True,        # Скрывать элемент при 0%
        })
        
        self.element_manager = None
        self._initial_opacity = {}  # element_id -> opacity
        self._current_opacity = 100
        self._blink_counter = 0

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
            color = "#00ff00"
        elif self.is_paused:
            color = "#ffaa00"
        else:
            color = "#666666"
        
        # 1. Круг (градиент прозрачности)
        opacity_ratio = self._current_opacity / 100
        
        # Внешний круг (100%)
        outer = self.canvas.create_oval(
            sx - r, sy - r, sx + r, sy + r,
            outline=color, width=2,
            tags=("mechanism", self.id, "outer")
        )
        self.canvas_items.append(outer)
        
        # Заполнение (текущая прозрачность)
        inner_r = r * opacity_ratio
        if inner_r > 2:
            fill_color = f"#{int(0x66 * opacity_ratio):02x}{int(0x66 * opacity_ratio):02x}{int(0x66 * opacity_ratio):02x}"
            inner = self.canvas.create_oval(
                sx - inner_r, sy - inner_r,
                sx + inner_r, sy + inner_r,
                fill=fill_color, outline="",
                tags=("mechanism", self.id, "inner")
            )
            self.canvas_items.append(inner)
        
        # 2. Символ режима
        mode = self.properties.get('mode', 'fade_in')
        if mode == 'fade_in':
            symbol = "▲"  # Появление
        elif mode == 'fade_out':
            symbol = "▼"  # Исчезновение
        elif mode == 'fade_in_out':
            symbol = "◆"  # Туда-обратно
        else:  # blink
            symbol = "◉"  # Мигание
        
        sym = self.canvas.create_text(
            sx, sy,
            text=symbol,
            fill="#ffffff",
            font=("Arial", 14, "bold"),
            tags=("mechanism", self.id, "symbol")
        )
        self.canvas_items.append(sym)
        
        # 3. Процент
        percent = self.canvas.create_text(
            sx, sy + r + 15,
            text=f"{int(self._current_opacity)}%",
            fill="#888888",
            font=("Arial", 10, "bold"),
            tags=("mechanism", self.id, "percent")
        )
        self.canvas_items.append(percent)
        
        # 4. Название
        name = self.canvas.create_text(
            sx, sy + r + 30,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#666666",
            font=("Arial", 8),
            tags=("mechanism", self.id, "name")
        )
        self.canvas_items.append(name)
        
        # 5. Индикатор элементов
        if self.attached_elements:
            attach = self.canvas.create_text(
                sx, sy - r - 15,
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
                if element and hasattr(element, 'properties'):
                    self._initial_opacity[element_id] = element.properties.get('opacity', 100)
            
            self.update()

    def detach_element(self, element_id):
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            if element_id in self._initial_opacity:
                if self.element_manager:
                    element = self.element_manager.get_element_by_id(element_id)
                    if element and hasattr(element, 'properties'):
                        element.properties['opacity'] = self._initial_opacity[element_id]
                        element.show()
                        element.update()
                del self._initial_opacity[element_id]
            
            self.update()

    def _run_animation(self):
        if not self.is_active or self.is_paused:
            return
        
        duration = self.properties.get('duration', 1000)
        opacity_start = self.properties['opacity_start']
        opacity_end = self.properties['opacity_end']
        mode = self.properties.get('mode', 'fade_in')
        
        # Шаг за кадр (60 FPS)
        frame_time = 1000 / 60  # мс
        step = frame_time / duration if duration > 0 else 1
        
        self._animation_progress += step * self._animation_direction
        
        # Границы
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            
            if mode == 'blink':
                self._blink_counter += 1
                blink_count = self.properties.get('blink_count', 0)
                if blink_count > 0 and self._blink_counter >= blink_count * 2:
                    self.is_active = False
                    self.update()
                    return
                self._animation_direction = -1
            elif self.properties.get('reverse_on_end') or mode == 'fade_in_out':
                self._animation_direction = -1
            elif self.properties.get('loop'):
                self._animation_progress = 0.0
            else:
                self.is_active = False
                if self.properties.get('flash_on_complete'):
                    self._flash_effect()
                self.update()
                return
        
        elif self._animation_progress <= 0.0:
            self._animation_progress = 0.0
            
            if mode == 'blink':
                self._animation_direction = 1
            elif self.properties.get('loop') or mode == 'fade_in_out':
                self._animation_direction = 1
            else:
                self.is_active = False
                self.update()
                return
        
        # Easing
        eased = self._apply_easing(self._animation_progress)
        
        # Вычисляем прозрачность
        self._current_opacity = opacity_start + (opacity_end - opacity_start) * eased
        
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
        elif easing == 'smooth':
            return t * t * (3 - 2 * t)
        
        return t

    def _update_attached_positions(self):
        if not self.element_manager:
            return
        
        hide_on_zero = self.properties.get('hide_on_zero', True)
        
        for element_id in self.attached_elements:
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            if hasattr(element, 'properties'):
                element.properties['opacity'] = int(self._current_opacity)
            
            # Скрываем/показываем
            if hide_on_zero:
                if self._current_opacity <= 0:
                    element.hide()
                else:
                    element.show()
            
            element.update()

    def _flash_effect(self):
        """Эффект вспышки"""
        for element_id in self.attached_elements:
            element = self.element_manager.get_element_by_id(element_id)
            if element and hasattr(element, 'properties'):
                # Быстрая вспышка
                element.properties['opacity'] = 100
                element.update()
                self.canvas.after(50, lambda e=element: self._restore_opacity(e))

    def _restore_opacity(self, element):
        """Восстанавливает прозрачность после вспышки"""
        if hasattr(element, 'properties'):
            element.properties['opacity'] = int(self._current_opacity)
            element.update()

    def fade_in(self, duration=1000):
        """Быстрое появление"""
        self.properties['mode'] = 'fade_in'
        self.properties['opacity_start'] = 0
        self.properties['opacity_end'] = 100
        self.properties['duration'] = duration
        self.start()

    def fade_out(self, duration=1000):
        """Быстрое исчезновение"""
        self.properties['mode'] = 'fade_out'
        self.properties['opacity_start'] = 100
        self.properties['opacity_end'] = 0
        self.properties['duration'] = duration
        self.start()

