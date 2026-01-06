#!/usr/bin/env python3
"""
Модуль callback-функций приложения
==================================
Содержит методы для обработки событий UI и взаимодействия между компонентами.
"""
import tkinter as tk


class AppCallbacks:
    """Класс для callback-функций приложения"""
    
    def __init__(self, app):
        """
        Args:
            app: Ссылка на главное приложение PanelWithControl
        """
        self.app = app
    
    # === Методы обновления UI ===
    
    def update_size_fields(self):
        """Обновляет поля размера в UI"""
        app = self.app
        element = app.element_manager.selected_element
        
        if element:
            width, height = int(element.width), int(element.height)
        else:
            width = app.main_canvas.width
            height = app.main_canvas.height
        
        app.ui.set_size_fields(width, height)
    
    def update_size_fields_from_main_canvas(self):
        """Обновляет поля размера из главной панели"""
        app = self.app
        app.ui.set_size_fields(app.main_canvas.width, app.main_canvas.height)
    
    def update_zoom_label(self):
        """Обновляет отображение масштаба и сетки"""
        app = self.app
        percent = app.zoom_system.get_zoom_percent()
        grid_size = app.grid_system.get_size()
        grid_status = "●" if app.grid_system.is_enabled() else "○"
        app.ui.update_coords_label(f"{percent}% | {grid_status}{grid_size}px")
    
    def update_grids(self):
        """Обновляет отрисовку сетки"""
        app = self.app
        if app.grid_system.is_enabled():
            app.grid_system.draw()
        app.main_canvas.draw()
        app.element_manager.redraw_all()
        app.mechanism_manager.redraw_all()
        app.selection_tool.update()
    
    def update_elements_tab(self):
        """Обновляет вкладку элементов"""
        tab_system = self.app.ui.get_tab_system()
        if tab_system:
            tab_elements = tab_system.get_tab('elements')
            if tab_elements and hasattr(tab_elements, '_refresh'):
                try:
                    tab_elements._refresh()
                except (tk.TclError, AttributeError) as e:
                    print(f"[AppCallbacks] Error refreshing elements tab: {e}")
    
    def update_mechanisms_tab(self):
        """Обновляет вкладку механизмов"""
        tab_system = self.app.ui.get_tab_system()
        if tab_system:
            tab_mechanisms = tab_system.get_tab('mechanisms')
            if tab_mechanisms and hasattr(tab_mechanisms, 'refresh'):
                try:
                    tab_mechanisms.refresh()
                except (tk.TclError, AttributeError) as e:
                    print(f"[AppCallbacks] Error refreshing mechanisms tab: {e}")
    
    def update_info_panel(self):
        """Обновляет информационную панель"""
        pass  # Заглушка
    
    # === Загрузка настроек в таб цвета ===
    
    def load_element_to_color_tab(self, element):
        """Загружает свойства элемента в панель цвета"""
        tab_system = self.app.ui.get_tab_system()
        if not tab_system:
            return
        
        tab_color = tab_system.get_tab('color')
        if tab_color:
            try:
                if hasattr(tab_color, 'set_element'):
                    tab_color.set_element(element)
            except Exception as e:
                print(f"Error loading element to color tab: {e}")
        
        # Для текстового элемента
        if hasattr(element, 'ELEMENT_TYPE') and element.ELEMENT_TYPE == 'text':
            tab_text = tab_system.get_tab('text')
            if tab_text and hasattr(tab_text, 'set_element'):
                try:
                    tab_text.set_element(element)
                except (tk.TclError, AttributeError) as e:
                    print(f"[AppCallbacks] Error loading text element: {e}")
    
    def load_main_canvas_to_color_tab(self):
        """Загружает свойства главной панели в панель цвета"""
        tab_system = self.app.ui.get_tab_system()
        if not tab_system:
            return
        
        tab_color = tab_system.get_tab('color')
        if tab_color:
            try:
                if hasattr(tab_color, 'set_element_type'):
                    tab_color.set_element_type(None, is_main_canvas=True)
            except Exception as e:
                print(f"Error loading main canvas to color tab: {e}")
    
    # === Колбэки изменения настроек ===
    
    def on_color_settings_changed(self, values):
        """Применяет изменения цвета к выбранному элементу или главной панели"""
        app = self.app
        element = app.element_manager.selected_element
        
        if element:
            self._apply_color_to_element(element, values)
        else:
            self._apply_color_to_main_canvas(values)
    
    def _apply_color_to_element(self, element, values):
        """Применяет цвет к элементу"""
        props = {}
        
        if 'fill_color' in values:
            props['fill_color'] = values['fill_color']
        if 'stroke_color' in values:
            props['stroke_color'] = values['stroke_color']
        if 'stroke_width' in values:
            props['stroke_width'] = values['stroke_width']
        if 'opacity' in values:
            props['opacity'] = values['opacity']
        if 'corner_radius' in values:
            props['corner_radius'] = values['corner_radius']
        if 'border_radius' in values:
            props['border_radius'] = values['border_radius']
        
        # Shadow
        if 'shadow_enabled' in values:
            props['shadow_enabled'] = values['shadow_enabled']
        if 'shadow_color' in values:
            props['shadow_color'] = values['shadow_color']
        if 'shadow_blur' in values:
            props['shadow_blur'] = values['shadow_blur']
        if 'shadow_offset_x' in values:
            props['shadow_offset_x'] = values['shadow_offset_x']
        if 'shadow_offset_y' in values:
            props['shadow_offset_y'] = values['shadow_offset_y']
        
        # Glow
        if 'glow_enabled' in values:
            props['glow_enabled'] = values['glow_enabled']
        if 'glow_color' in values:
            props['glow_color'] = values['glow_color']
        if 'glow_size' in values:
            props['glow_size'] = values['glow_size']
        
        if props:
            element.set_properties(props)
            element.update()
    
    def _apply_color_to_main_canvas(self, values):
        """Применяет цвет к главной панели"""
        app = self.app
        
        if 'fill_color' in values:
            app.main_canvas.set_property('fill_color', values['fill_color'])
        if 'stroke_color' in values:
            app.main_canvas.set_property('stroke_color', values['stroke_color'])
        if 'stroke_width' in values:
            app.main_canvas.set_property('stroke_width', values['stroke_width'])
        if 'corner_radius' in values:
            app.main_canvas.set_property('corner_radius', values['corner_radius'])
        
        app.main_canvas.update()
    
    def on_text_settings_changed(self, values):
        """Применяет изменения текста к текстовому элементу"""
        app = self.app
        element = app.element_manager.selected_element
        
        if not element or not hasattr(element, 'ELEMENT_TYPE'):
            return
        
        if element.ELEMENT_TYPE != 'text':
            return
        
        props = {}
        text_props = ['text', 'font_family', 'font_size', 'font_weight', 'font_style',
                      'text_color', 'text_align', 'line_height', 'letter_spacing',
                      'text_transform', 'text_decoration', 'text_shadow']
        
        for prop in text_props:
            if prop in values:
                props[prop] = values[prop]
        
        if props:
            element.set_properties(props)
            element.update()
    
    def on_element_selected(self, element):
        """Вызывается при выборе элемента"""
        app = self.app
        
        if element:
            self.load_element_to_color_tab(element)
            app.selection_tool.select(element)
        else:
            self.load_main_canvas_to_color_tab()
            app.selection_tool.deselect()
    
    # === Управление сеткой ===
    
    def toggle_grid(self):
        """Переключает отображение сетки"""
        app = self.app
        app.grid_system.toggle()
        self.update_grids()
        self.update_zoom_label()
    
    def grid_increase(self):
        """Увеличивает размер сетки"""
        app = self.app
        app.grid_system.increase_size()
        if app.grid_system.is_enabled():
            app.grid_system.draw()
        self.update_zoom_label()
    
    def grid_decrease(self):
        """Уменьшает размер сетки"""
        app = self.app
        app.grid_system.decrease_size()
        if app.grid_system.is_enabled():
            app.grid_system.draw()
        self.update_zoom_label()
    
    # === Управление размером ===
    
    def apply_element_size(self, width, height):
        """Применяет размер к выбранному элементу или главной панели"""
        app = self.app
        element = app.element_manager.selected_element
        
        if element:
            element.width = width
            element.height = height
            element.update()
            app.selection_tool.update()
        else:
            app.main_canvas.width = width
            app.main_canvas.height = height
            app.main_canvas.update()
            self.update_grids()
    
    def toggle_size_lock(self):
        """Переключает блокировку размера"""
        app = self.app
        element = app.element_manager.selected_element
        
        if element:
            element.size_locked = not element.size_locked
            app.ui.update_lock_button(element.size_locked)
    
    # === Zoom ===
    
    def zoom_in(self):
        """Увеличить масштаб"""
        app = self.app
        app.zoom_system.zoom_in()
        app.element_manager.redraw_all()
        app.mechanism_manager.redraw_all()
        app.selection_tool.update()
        self.update_zoom_label()
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        app = self.app
        app.zoom_system.zoom_out()
        app.element_manager.redraw_all()
        app.mechanism_manager.redraw_all()
        app.selection_tool.update()
        self.update_zoom_label()
    
    def zoom_reset(self):
        """Сбросить масштаб"""
        app = self.app
        app.zoom_system.reset_zoom()
        app.element_manager.redraw_all()
        app.mechanism_manager.redraw_all()
        app.selection_tool.update()
        self.update_zoom_label()
    
    def on_zoom_changed(self, scale):
        """Вызывается при изменении масштаба"""
        self.update_zoom_label()
        self.update_grids()
    
    # === Прочее ===
    
    def delete_selected_element(self):
        """Удаляет выделенный элемент"""
        app = self.app
        app.element_manager.delete_selected()
        app.selection_tool.deselect()
        self.update_elements_tab()
    
    def save_project(self):
        """Сохраняет проект"""
        if self.app.project_manager:
            self.app.project_manager.save_project()
    
    def reload_app(self):
        """Перезагружает приложение"""
        pass  # Заглушка

