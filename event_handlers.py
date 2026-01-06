#!/usr/bin/env python3
"""
Модуль обработчиков событий мыши и клавиатуры
=============================================
Выносит логику обработки событий из main.py для лучшей модульности.
"""
import tkinter as tk


class EventHandlers:
    """Класс для обработки событий мыши и клавиатуры"""
    
    # Курсоры для маркеров resize
    RESIZE_CURSORS = {
        'nw': 'top_left_corner',
        'ne': 'top_right_corner',
        'sw': 'bottom_left_corner',
        'se': 'bottom_right_corner',
        'n': 'top_side',
        's': 'bottom_side',
        'w': 'left_side',
        'e': 'right_side',
    }
    
    def __init__(self, app):
        """
        Args:
            app: Ссылка на главное приложение PanelWithControl
        """
        self.app = app
        
        # Состояние перетаскивания
        self._drag_start = None
        self._drag_element_start = None
        self._drag_main_canvas_start = None
        self._dragging_main_canvas = False
        self._resize_handle = None
        self._resize_start_bounds = None
        self._pan_start = None
    
    def bind_events(self):
        """Привязывает все события к холсту и окну"""
        canvas = self.app.canvas
        root = self.app.root
        
        # Привязываем события canvas
        self.bind_canvas_events(canvas, root)
        
        # Горячие клавиши (привязываются один раз)
        root.bind("<Delete>", self._on_delete_key)
        root.bind("<BackSpace>", self._on_delete_key)
        root.bind("<Control-s>", self._on_save_project)
        root.bind("<Control-z>", lambda e: None)
        root.bind("<Control-Shift-s>", self._on_save_project_as)
        root.bind("<Control-n>", self._on_new_project)
        root.bind("<Control-a>", lambda e: None)
        
        # Стрелки для перемещения
        root.bind("<Up>", lambda e: self._move_selected(0, -1))
        root.bind("<Down>", lambda e: self._move_selected(0, 1))
        root.bind("<Left>", lambda e: self._move_selected(-1, 0))
        root.bind("<Right>", lambda e: self._move_selected(1, 0))
        root.bind("<Shift-Up>", lambda e: self._move_selected(0, -10))
        root.bind("<Shift-Down>", lambda e: self._move_selected(0, 10))
        root.bind("<Shift-Left>", lambda e: self._move_selected(-10, 0))
        root.bind("<Shift-Right>", lambda e: self._move_selected(10, 0))
        
        # Escape
        root.bind("<Escape>", self._on_escape_key)
        
        # Zoom
        root.bind("<Control-plus>", lambda e: self.app.zoom_in())
        root.bind("<Control-minus>", lambda e: self.app.zoom_out())
        
    def bind_canvas_events(self, canvas, root=None):
        """Привязывает события мыши к холсту (публичный метод для восстановления)"""
        # События мыши на холсте
        canvas.bind("<Button-1>", self._on_mouse_press)
        canvas.bind("<B1-Motion>", self._on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        canvas.bind("<Motion>", self._on_mouse_move)
        canvas.bind("<Double-Button-1>", self._on_double_click)
        canvas.bind("<Button-3>", self._on_right_click)
        
        # Средняя кнопка - панорамирование
        canvas.bind("<Button-2>", self._on_pan_start)
        canvas.bind("<B2-Motion>", self._on_pan_drag)
        canvas.bind("<ButtonRelease-2>", self._on_pan_end)
        
        # Колесо мыши - zoom
        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel_up)
        canvas.bind("<Button-5>", self._on_mouse_wheel_down)
        canvas.bind("<Control-MouseWheel>", self._on_mouse_wheel)
        root.bind("<Control-equal>", lambda e: self.app.zoom_in())
        root.bind("<Control-0>", lambda e: self.app.zoom_reset())
    
    def _on_mouse_press(self, event):
        """Обработчик нажатия мыши"""
        app = self.app
        
        # Режим создания механизма
        if app.mechanism_manager.is_creating():
            real_x, real_y = app.zoom_system.screen_to_real(event.x, event.y)
            app.mechanism_manager.on_create_start(real_x, real_y)
            return
        
        # Режим создания элемента
        if app.element_manager.is_creating():
            real_x, real_y = app.zoom_system.screen_to_real(event.x, event.y)
            app.element_manager.on_create_start(real_x, real_y)
            return
        
        # Проверяем клик по маркеру resize
        if app.selection_tool.is_active():
            element = app.element_manager.selected_element
            if element and not element.size_locked:
                handle = app.selection_tool.get_resize_handle(event.x, event.y)
                if handle:
                    self._resize_handle = handle
                    self._drag_start = (event.x, event.y)
                    self._resize_start_bounds = element.get_bounds()
                    return
        
        # Клик по элементу
        element = app.element_manager.select_at(event.x, event.y)
        if element:
            app.selection_tool.select(element)
            self._drag_start = (event.x, event.y)
            self._drag_element_start = (element.x, element.y)
            self._resize_handle = None
            app._update_size_fields()
            app._load_element_to_color_tab(element)
            app.ui.update_lock_button(element.size_locked)
            return
        
        # Клик по главной панели
        if app.main_canvas.contains_point(event.x, event.y):
            app.element_manager.deselect_all()
            app.selection_tool.deselect()
            app._load_main_canvas_to_color_tab()
            app._update_size_fields()
            app.ui.update_lock_button(False)
            self._drag_start = (event.x, event.y)
            self._drag_main_canvas_start = (app.main_canvas.x, app.main_canvas.y)
            self._dragging_main_canvas = True
            return
        
        # Клик по пустому месту
        self._reset_drag_state()
        app.element_manager.deselect_all()
        app.selection_tool.deselect()
        
        if app.grid_system.grid_enabled:
            app.selection_system.on_mouse_press(event)
    
    def _on_mouse_drag(self, event):
        """Обработчик перетаскивания"""
        app = self.app
        
        # Создание элемента
        if app.element_manager.is_creating() and app.element_manager.creation_start:
            real_x, real_y = app.zoom_system.screen_to_real(event.x, event.y)
            app.element_manager.on_create_drag(real_x, real_y)
            return
        
        # Resize элемента
        if self._resize_handle and self._drag_start and self._resize_start_bounds:
            self._do_resize(event.x, event.y)
            return
        
        # Перетаскивание главной панели
        if self._dragging_main_canvas and self._drag_start and self._drag_main_canvas_start:
            dx_screen = event.x - self._drag_start[0]
            dy_screen = event.y - self._drag_start[1]
            dx_real = app.zoom_system.unscale_value(dx_screen)
            dy_real = app.zoom_system.unscale_value(dy_screen)
            new_x = self._drag_main_canvas_start[0] + dx_real
            new_y = self._drag_main_canvas_start[1] + dy_real
            app.main_canvas.move_to(new_x, new_y)
            app._update_grids()
            return
        
        # Перетаскивание элемента
        if self._drag_start and self._drag_element_start:
            if app.element_manager.selected_element:
                dx_screen = event.x - self._drag_start[0]
                dy_screen = event.y - self._drag_start[1]
                dx_real = app.zoom_system.unscale_value(dx_screen)
                dy_real = app.zoom_system.unscale_value(dy_screen)
                new_x = self._drag_element_start[0] + dx_real
                new_y = self._drag_element_start[1] + dy_real
                app.element_manager.selected_element.move_to(new_x, new_y)
                app.selection_tool.update()
                return
        
        if app.grid_system.grid_enabled:
            app.selection_system.on_mouse_drag(event)
    
    def _do_resize(self, mx, my):
        """Выполняет resize элемента"""
        app = self.app
        element = app.element_manager.selected_element
        if not element:
            return
        
        x1, y1, x2, y2 = self._resize_start_bounds
        dx = app.zoom_system.unscale_value(mx - self._drag_start[0])
        dy = app.zoom_system.unscale_value(my - self._drag_start[1])
        
        new_x1, new_y1, new_x2, new_y2 = x1, y1, x2, y2
        handle = self._resize_handle
        
        app.selection_tool.show_size(True)
        
        if 'n' in handle:
            new_y1 = y1 + dy
        if 's' in handle:
            new_y2 = y2 + dy
        if 'w' in handle:
            new_x1 = x1 + dx
        if 'e' in handle:
            new_x2 = x2 + dx
        
        # Минимальный размер (10 для маленьких элементов)
        min_size = 10
        if new_x2 - new_x1 < min_size:
            if 'w' in handle:
                new_x1 = new_x2 - min_size
            else:
                new_x2 = new_x1 + min_size
        
        if new_y2 - new_y1 < min_size:
            if 'n' in handle:
                new_y1 = new_y2 - min_size
            else:
                new_y2 = new_y1 + min_size
        
        element.x = new_x1
        element.y = new_y1
        element.width = new_x2 - new_x1
        element.height = new_y2 - new_y1
        element.update()
        
        app.selection_tool.update(show_size=True)
        app._update_size_fields()
    
    def _on_mouse_release(self, event):
        """Обработчик отпускания мыши"""
        app = self.app
        
        # Завершение создания механизма
        if app.mechanism_manager.is_creating():
            real_x, real_y = app.zoom_system.screen_to_real(event.x, event.y)
            mechanism = app.mechanism_manager.on_create_end(real_x, real_y)
            if mechanism:
                app._update_mechanisms_tab()
                if hasattr(app, 'tab_layers') and app.tab_layers:
                    try:
                        app.tab_layers.update()
                    except (tk.TclError, AttributeError):
                        pass  # Tab not ready
            app.canvas.config(cursor="arrow")
            return
        
        # Завершение создания элемента
        if app.element_manager.is_creating():
            real_x, real_y = app.zoom_system.screen_to_real(event.x, event.y)
            element = app.element_manager.on_create_end(real_x, real_y)
            if element:
                app._update_elements_tab()
                app._update_size_fields()
                if hasattr(app, 'tab_layers') and app.tab_layers:
                    try:
                        app.tab_layers.update()
                    except (tk.TclError, AttributeError):
                        pass  # Tab not ready
            app.canvas.config(cursor="arrow")
            return
        
        # Скрываем размеры после resize
        if self._resize_handle:
            app.selection_tool.show_size(False)
        
        self._reset_drag_state()
        
        if app.grid_system.grid_enabled:
            app.selection_system.on_mouse_release(event)
    
    def _on_mouse_move(self, event):
        """Обработчик движения мыши"""
        app = self.app
        
        if app.element_manager.is_creating():
            app.canvas.config(cursor="crosshair")
            return
        
        if app.selection_tool.is_active():
            handle = app.selection_tool.get_resize_handle(event.x, event.y)
            if handle:
                cursor = self.RESIZE_CURSORS.get(handle, "arrow")
                app.canvas.config(cursor=cursor)
                return
        
        # Сначала проверяем артефакты
        if hasattr(app, 'artifact_manager_integrated') and app.artifact_manager_integrated:
            artifact = app.artifact_manager_integrated.get_artifact_at(event.x, event.y)
            if artifact:
                app.canvas.config(cursor="fleur")
                return
        
        # Затем обычные элементы
        element = app.element_manager.get_element_at(event.x, event.y)
        if element:
            app.canvas.config(cursor="fleur")
            return
        
        if app.grid_system.is_any_grid_enabled():
            app.canvas.config(cursor="crosshair")
            app.selection_system.on_mouse_move(event)
        else:
            app.canvas.config(cursor="arrow")
    
    def _on_double_click(self, event):
        """Обработчик двойного клика"""
        app = self.app
        # Сначала проверяем артефакты
        if hasattr(app, 'artifact_manager_integrated') and app.artifact_manager_integrated:
            artifact = app.artifact_manager_integrated.get_artifact_at(event.x, event.y)
            if artifact:
                # Двойной клик по артефакту - настройки
                artifact._show_settings()
                return
        
        # Затем обычные элементы
        element = app.element_manager.get_element_at(event.x, event.y)
        if element and hasattr(element, 'on_double_click'):
            element.on_double_click()
    
    def _on_right_click(self, event):
        """Обработчик правой кнопки - контекстное меню"""
        self.app._on_right_click(event)  # Делегируем в app
    
    def _on_pan_start(self, event):
        """Начало панорамирования"""
        self._pan_start = (event.x, event.y)
        self.app.canvas.config(cursor="fleur")
    
    def _on_pan_drag(self, event):
        """Панорамирование"""
        if self._pan_start:
            app = self.app
            dx = event.x - self._pan_start[0]
            dy = event.y - self._pan_start[1]
            app.zoom_system.pan(dx, dy)
            self._pan_start = (event.x, event.y)
            app.element_manager.redraw_all()
            app.mechanism_manager.redraw_all()
            app.selection_tool.update()
    
    def _on_pan_end(self, event):
        """Конец панорамирования"""
        self._pan_start = None
        self.app.canvas.config(cursor="arrow")
    
    def _on_mouse_wheel(self, event):
        """Zoom колесом мыши"""
        app = self.app
        if event.delta > 0:
            app.zoom_system.zoom_in(event.x, event.y)
        else:
            app.zoom_system.zoom_out(event.x, event.y)
        self._redraw_after_zoom()
    
    def _on_mouse_wheel_up(self, event):
        """Zoom in (Linux)"""
        self.app.zoom_system.zoom_in(event.x, event.y)
        self._redraw_after_zoom()
    
    def _on_mouse_wheel_down(self, event):
        """Zoom out (Linux)"""
        self.app.zoom_system.zoom_out(event.x, event.y)
        self._redraw_after_zoom()
    
    def _redraw_after_zoom(self):
        """Перерисовка после изменения масштаба"""
        app = self.app
        app.element_manager.redraw_all()
        app.mechanism_manager.redraw_all()
        app.selection_tool.update()
        app._update_zoom_label()
    
    def _on_delete_key(self, event):
        """Обработчик Delete"""
        self.app.delete_selected_element()
    
    def _on_escape_key(self, event):
        """Обработчик Escape"""
        self.app.element_manager.deselect_all()
        self.app.selection_tool.deselect()
    
    def _on_save_project(self, event):
        """Ctrl+S"""
        app = self.app
        if app.project_manager and app.project_manager.current_project:
            app.project_manager.save_project()
        return "break"
    
    def _on_save_project_as(self, event):
        """Ctrl+Shift+S"""
        tab_system = self.app.ui.get_tab_system()
        if tab_system:
            tab_menu = tab_system.get_tab('menu')
            if tab_menu:
                tab_menu._on_save_as()
        return "break"
    
    def _on_new_project(self, event):
        """Ctrl+N"""
        tab_system = self.app.ui.get_tab_system()
        if tab_system:
            tab_menu = tab_system.get_tab('menu')
            if tab_menu:
                tab_menu._on_new_project()
        return "break"
    
    def _move_selected(self, dx, dy):
        """Перемещает выбранный элемент"""
        element = self.app.element_manager.get_selected()
        if element:
            element.move_by(dx, dy)
            self.app._update_info_panel()
    
    def _reset_drag_state(self):
        """Сбрасывает состояние перетаскивания"""
        self._drag_start = None
        self._drag_element_start = None
        self._drag_main_canvas_start = None
        self._dragging_main_canvas = False
        self._resize_handle = None
        self._resize_start_bounds = None

