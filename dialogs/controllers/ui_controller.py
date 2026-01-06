"""
Контроллер UI
Управляет интерфейсом, вкладками, обновлениями
"""

import tkinter as tk
from typing import Optional
from ..utils.logger import get_logger
from ..utils.event_bus import emit
from ..utils.debounce import TkDebouncer, DEBOUNCE_UI

log = get_logger('UIController')


class UIController:
    """
    Контроллер пользовательского интерфейса.
    Отвечает за:
    - Обновление вкладок
    - Обновление информационных панелей
    - Управление полноэкранным режимом
    - Уведомления и диалоги
    """
    
    def __init__(self, app_controller):
        """
        Args:
            app_controller: Главный контроллер приложения
        """
        self.app = app_controller
        
        # UI компоненты (устанавливаются позже)
        self.ui_builder = None
        self.tab_system = None
        
        # Состояние
        self._is_fullscreen = False
        self._windowed_geometry = None
        
        # Дебаунсеры для обновлений
        self._update_debouncer = None
        
    def set_ui_builder(self, ui_builder):
        """Устанавливает UI builder"""
        self.ui_builder = ui_builder
        if ui_builder and hasattr(ui_builder, 'root'):
            self._update_debouncer = TkDebouncer(ui_builder.root, DEBOUNCE_UI)
            
    def set_tab_system(self, tab_system):
        """Устанавливает систему вкладок"""
        self.tab_system = tab_system
        
    # === Обновление вкладок ===
    
    def refresh_elements_tab(self):
        """Обновляет вкладку элементов"""
        if self.tab_system:
            tab = self.tab_system.get_tab('elements')
            if tab and hasattr(tab, '_refresh'):
                try:
                    tab._refresh()
                except tk.TclError as e:
                    log.warning(f"Ошибка обновления elements tab: {e}")
                    
    def refresh_mechanisms_tab(self):
        """Обновляет вкладку механизмов"""
        if self.tab_system:
            tab = self.tab_system.get_tab('mechanisms')
            if tab and hasattr(tab, 'refresh'):
                try:
                    tab.refresh()
                except tk.TclError as e:
                    log.warning(f"Ошибка обновления mechanisms tab: {e}")
                    
    def refresh_layers_tab(self):
        """Обновляет вкладку слоёв"""
        if self.tab_system:
            tab = self.tab_system.get_tab('layers')
            if tab and hasattr(tab, 'update'):
                try:
                    tab.update()
                except tk.TclError as e:
                    log.warning(f"Ошибка обновления layers tab: {e}")
                    
    def refresh_all_tabs(self):
        """Обновляет все вкладки"""
        self.refresh_elements_tab()
        self.refresh_mechanisms_tab()
        self.refresh_layers_tab()
        
    def refresh_all_tabs_debounced(self):
        """Обновляет все вкладки с дебаунсом"""
        if self._update_debouncer:
            self._update_debouncer.call(self.refresh_all_tabs)
        else:
            self.refresh_all_tabs()
            
    # === Цветовая панель ===
    
    def load_element_to_color_tab(self, element):
        """
        Загружает свойства элемента в панель цвета.
        
        Args:
            element: Элемент
        """
        if not self.tab_system:
            return
            
        tab_color = self.tab_system.get_tab('color')
        if tab_color and hasattr(tab_color, 'set_element'):
            try:
                tab_color.set_element(element)
            except Exception as e:
                log.warning(f"Ошибка загрузки в color tab: {e}")
                
        # Для текстовых элементов
        if hasattr(element, 'ELEMENT_TYPE') and element.ELEMENT_TYPE == 'text':
            tab_text = self.tab_system.get_tab('text')
            if tab_text and hasattr(tab_text, 'set_element'):
                try:
                    tab_text.set_element(element)
                except Exception as e:
                    log.warning(f"Ошибка загрузки в text tab: {e}")
                    
    def load_canvas_to_color_tab(self):
        """Загружает свойства холста в панель цвета"""
        if not self.tab_system or not self.app.main_canvas:
            return
            
        tab_color = self.tab_system.get_tab('color')
        if tab_color:
            try:
                if hasattr(tab_color, 'set_element_type'):
                    tab_color.set_element_type('main_canvas')
                if hasattr(tab_color, 'load_from_canvas'):
                    tab_color.load_from_canvas(self.app.main_canvas)
            except Exception as e:
                log.warning(f"Ошибка загрузки холста в color tab: {e}")
                
    # === Информационная панель ===
    
    def update_size_fields(self, element=None):
        """
        Обновляет поля размера.
        
        Args:
            element: Элемент (если None - из выделенного)
        """
        if not self.ui_builder:
            return
            
        if element is None:
            element = self.app.element_manager.selected_element if self.app.element_manager else None
            
        if element:
            try:
                if hasattr(self.ui_builder, 'size_x_var'):
                    self.ui_builder.size_x_var.set(str(int(element.x)))
                if hasattr(self.ui_builder, 'size_y_var'):
                    self.ui_builder.size_y_var.set(str(int(element.y)))
                if hasattr(self.ui_builder, 'size_w_var'):
                    self.ui_builder.size_w_var.set(str(int(element.width)))
                if hasattr(self.ui_builder, 'size_h_var'):
                    self.ui_builder.size_h_var.set(str(int(element.height)))
            except tk.TclError:
                pass
                
    def update_zoom_display(self, zoom: float):
        """
        Обновляет отображение масштаба.
        
        Args:
            zoom: Текущий масштаб (1.0 = 100%)
        """
        if self.ui_builder and hasattr(self.ui_builder, 'zoom_var'):
            try:
                self.ui_builder.zoom_var.set(f"{int(zoom * 100)}%")
            except tk.TclError:
                pass
                
    # === Полноэкранный режим ===
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        # Делегируем в UIBuilder если доступен
        if self.ui_builder and hasattr(self.ui_builder, '_toggle_fullscreen'):
            self.ui_builder._toggle_fullscreen()
            self._is_fullscreen = self.ui_builder._is_fullscreen
            return self._is_fullscreen
            
        # Fallback реализация
        import sys
        is_linux = sys.platform.startswith('linux')
        root = self.app.root
        
        if self._is_fullscreen:
            # Выход из полноэкранного
            if is_linux:
                root.attributes('-fullscreen', False)
            else:
                try:
                    root.state('normal')
                except tk.TclError:
                    root.attributes('-fullscreen', False)
                
            if self._windowed_geometry:
                root.geometry(self._windowed_geometry)
                
            self._is_fullscreen = False
        else:
            # Сохраняем текущий размер
            self._windowed_geometry = root.geometry()
            
            # Переход в полноэкранный
            if is_linux:
                root.attributes('-fullscreen', True)
            else:
                try:
                    root.state('zoomed')
                except tk.TclError:
                    root.attributes('-fullscreen', True)
                
            self._is_fullscreen = True
            
        return self._is_fullscreen
        
    def is_fullscreen(self) -> bool:
        """Проверяет в полноэкранном ли режиме"""
        # Синхронизируем с UIBuilder
        if self.ui_builder and hasattr(self.ui_builder, '_is_fullscreen'):
            self._is_fullscreen = self.ui_builder._is_fullscreen
        return self._is_fullscreen
        
    # === Уведомления ===
    
    def show_status(self, message: str, duration_ms: int = 3000):
        """
        Показывает статусное сообщение.
        
        Args:
            message: Сообщение
            duration_ms: Длительность отображения
        """
        if self.ui_builder and hasattr(self.ui_builder, 'status_label'):
            try:
                self.ui_builder.status_label.config(text=message)
                
                # Очистка через указанное время
                if duration_ms > 0:
                    self.app.root.after(duration_ms, lambda: self._clear_status(message))
            except tk.TclError:
                pass
                
    def _clear_status(self, original_message: str):
        """Очищает статус если он не изменился"""
        if self.ui_builder and hasattr(self.ui_builder, 'status_label'):
            try:
                current = self.ui_builder.status_label.cget('text')
                if current == original_message:
                    self.ui_builder.status_label.config(text="")
            except tk.TclError:
                pass
                
    def show_toast(self, message: str, duration_ms: int = 2000):
        """
        Показывает всплывающее уведомление.
        
        Args:
            message: Сообщение
            duration_ms: Длительность отображения
        """
        # TODO: реализовать красивые toast уведомления
        self.show_status(message, duration_ms)
        
    def show_error(self, message: str):
        """
        Показывает сообщение об ошибке.
        
        Args:
            message: Текст ошибки
        """
        from tkinter import messagebox
        messagebox.showerror("Ошибка", message)
        log.error(message)
        
    def show_warning(self, message: str):
        """
        Показывает предупреждение.
        
        Args:
            message: Текст предупреждения
        """
        from tkinter import messagebox
        messagebox.showwarning("Предупреждение", message)
        log.warning(message)
        
    def ask_yes_no(self, title: str, message: str) -> bool:
        """
        Показывает диалог да/нет.
        
        Args:
            title: Заголовок
            message: Сообщение
            
        Returns:
            True если пользователь нажал Да
        """
        from tkinter import messagebox
        return messagebox.askyesno(title, message)

