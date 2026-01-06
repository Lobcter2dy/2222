"""
Контроллер холста
Управляет отображением, масштабированием, навигацией
"""

import tkinter as tk
from typing import Optional, Tuple
from ..utils.logger import get_logger
from ..utils.event_bus import emit

log = get_logger('CanvasController')


class CanvasController:
    """
    Контроллер холста.
    Отвечает за:
    - Управление масштабом (zoom)
    - Панорамирование (pan)
    - Отрисовку сетки
    - Курсор и инструменты
    """
    
    def __init__(self, app_controller):
        """
        Args:
            app_controller: Главный контроллер приложения
        """
        self.app = app_controller
        
        # Состояние
        self.current_tool = 'select'  # select, hand, create
        self._is_panning = False
        self._pan_start = (0, 0)
        
    @property
    def canvas(self):
        return self.app.canvas
        
    @property
    def zoom_system(self):
        return self.app.zoom_system
        
    @property
    def grid_system(self):
        return self.app.grid_system
        
    @property
    def main_canvas(self):
        return self.app.main_canvas
        
    def refresh(self):
        """Перерисовывает холст"""
        if self.canvas:
            # Очищаем и перерисовываем
            if self.main_canvas:
                self.main_canvas.draw()
                
            if self.grid_system and self.grid_system.grid_enabled:
                self.grid_system.draw(self.canvas)
                
            # Перерисовываем элементы
            if self.app.element_manager:
                for elem in self.app.element_manager.get_all_elements():
                    elem.update()
                    
            # Перерисовываем механизмы
            if self.app.mechanism_manager:
                for mech in self.app.mechanism_manager.get_all_mechanisms():
                    mech.update()
                    
    # === Масштабирование ===
    
    def zoom_in(self, center: Optional[Tuple[int, int]] = None):
        """
        Увеличивает масштаб.
        
        Args:
            center: Центр масштабирования (если None - центр холста)
        """
        if self.zoom_system:
            self.zoom_system.zoom_in(center)
            self.refresh()
            emit('ui:zoom_changed', self.zoom_system.zoom)
            log.debug(f"Zoom in: {self.zoom_system.zoom}")
            
    def zoom_out(self, center: Optional[Tuple[int, int]] = None):
        """
        Уменьшает масштаб.
        
        Args:
            center: Центр масштабирования
        """
        if self.zoom_system:
            self.zoom_system.zoom_out(center)
            self.refresh()
            emit('ui:zoom_changed', self.zoom_system.zoom)
            log.debug(f"Zoom out: {self.zoom_system.zoom}")
            
    def zoom_reset(self):
        """Сбрасывает масштаб на 100%"""
        if self.zoom_system:
            self.zoom_system.zoom = 1.0
            self.zoom_system.offset_x = 0
            self.zoom_system.offset_y = 0
            self.refresh()
            emit('ui:zoom_changed', 1.0)
            log.debug("Zoom reset")
            
    def zoom_fit(self):
        """Масштабирует чтобы всё поместилось"""
        if self.zoom_system and self.main_canvas:
            # Вычисляем масштаб
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            
            content_w = self.main_canvas.width
            content_h = self.main_canvas.height
            
            if content_w > 0 and content_h > 0:
                zoom_x = canvas_w / content_w * 0.9
                zoom_y = canvas_h / content_h * 0.9
                self.zoom_system.zoom = min(zoom_x, zoom_y, 1.0)
                
                # Центрируем
                self.zoom_system.offset_x = (canvas_w - content_w * self.zoom_system.zoom) / 2
                self.zoom_system.offset_y = (canvas_h - content_h * self.zoom_system.zoom) / 2
                
                self.refresh()
                emit('ui:zoom_changed', self.zoom_system.zoom)
                
    def get_zoom(self) -> float:
        """Возвращает текущий масштаб"""
        if self.zoom_system:
            return self.zoom_system.zoom
        return 1.0
        
    # === Панорамирование ===
    
    def start_pan(self, x: int, y: int):
        """
        Начинает панорамирование.
        
        Args:
            x, y: Начальные координаты
        """
        self._is_panning = True
        self._pan_start = (x, y)
        if self.canvas:
            self.canvas.config(cursor='fleur')
            
    def update_pan(self, x: int, y: int):
        """
        Обновляет панорамирование.
        
        Args:
            x, y: Текущие координаты
        """
        if not self._is_panning or not self.zoom_system:
            return
            
        dx = x - self._pan_start[0]
        dy = y - self._pan_start[1]
        
        self.zoom_system.offset_x += dx
        self.zoom_system.offset_y += dy
        
        self._pan_start = (x, y)
        self.refresh()
        
    def end_pan(self):
        """Завершает панорамирование"""
        self._is_panning = False
        if self.canvas:
            self.canvas.config(cursor='arrow')
            
    def is_panning(self) -> bool:
        """Проверяет идёт ли панорамирование"""
        return self._is_panning
        
    # === Инструменты ===
    
    def set_tool(self, tool: str):
        """
        Устанавливает текущий инструмент.
        
        Args:
            tool: Название инструмента (select, hand, create)
        """
        self.current_tool = tool
        
        # Обновляем курсор
        if self.canvas:
            cursors = {
                'select': 'arrow',
                'hand': 'fleur',
                'create': 'crosshair',
            }
            self.canvas.config(cursor=cursors.get(tool, 'arrow'))
            
        log.debug(f"Tool: {tool}")
        
    def get_tool(self) -> str:
        """Возвращает текущий инструмент"""
        return self.current_tool
        
    # === Координаты ===
    
    def screen_to_real(self, x: int, y: int) -> Tuple[float, float]:
        """
        Преобразует экранные координаты в реальные.
        
        Args:
            x, y: Экранные координаты
            
        Returns:
            (real_x, real_y): Реальные координаты
        """
        if self.zoom_system:
            return self.zoom_system.screen_to_real(x, y)
        return (float(x), float(y))
        
    def real_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """
        Преобразует реальные координаты в экранные.
        
        Args:
            x, y: Реальные координаты
            
        Returns:
            (screen_x, screen_y): Экранные координаты
        """
        if self.zoom_system:
            return self.zoom_system.real_to_screen(x, y)
        return (int(x), int(y))
        
    # === Сетка ===
    
    def toggle_grid(self):
        """Переключает отображение сетки"""
        if self.grid_system:
            self.grid_system.grid_enabled = not self.grid_system.grid_enabled
            self.refresh()
            emit('ui:grid_toggled', self.grid_system.grid_enabled)
            
    def set_grid_size(self, size: int):
        """Устанавливает размер ячейки сетки"""
        if self.grid_system:
            self.grid_system.cell_size = size
            self.refresh()
            
    def snap_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """
        Привязывает координаты к сетке.
        
        Args:
            x, y: Координаты
            
        Returns:
            (snapped_x, snapped_y): Привязанные координаты
        """
        if self.grid_system and self.grid_system.snap_enabled:
            return self.grid_system.snap(x, y)
        return (x, y)

