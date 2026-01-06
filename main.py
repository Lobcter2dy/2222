#!/usr/bin/env python3
"""
Панель управления с сеткой
Главный модуль - собирает все компоненты вместе

Рефакторинг: добавлены контроллеры для улучшения модульности
"""
import tkinter as tk
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.config import Config
from modules.grid_system import GridSystem
from modules.selection_system import SelectionSystem
from modules.selection_tool import SelectionTool
from modules.ui_builder import UIBuilder
from modules.elements import ElementManager, ButtonElement
from modules.zoom_system import ZoomSystem
from modules.main_canvas import MainCanvas
from modules.code_generator import CodeGenerator
from modules.dialogs import show_button_config, show_frame_config, show_panel_config, show_image_config, show_visibility_dialog, show_scroll_area_config, show_save_artifact_dialog, show_artifact_browser, show_state_switcher_config, show_element_extended_dialog
from modules.elements.state_switcher import StateSwitcherElement
from modules.component_system import Component, ComponentManager
from modules.artifact_manager import ArtifactManager as NewArtifactManager
from modules.live_project_manager import get_live_project_manager
from modules.artifact_manager_integrated import get_artifact_manager_integrated
from modules.loading_overlay import LoadingOverlay, LoadingContext
from modules.button_functions import call_button_function, register_button_function, get_button_functions
from modules.window_manager import get_window_manager
from modules.dialogs import show_action_config
from modules.elements import FrameElement, PanelElement, ImageElement, TextElement, ScrollAreaElement
from modules.mechanisms import MechanismManager
from modules.project_manager import ProjectManager
from modules.event_handlers import EventHandlers
from modules.app_callbacks import AppCallbacks

# Контроллеры
from modules.controllers import AppController, CanvasController, ElementController, UIController
from modules.utils.logger import get_logger
from modules.utils.event_bus import event_bus, on as subscribe, emit
from modules.utils.hotkeys import HotkeyManager

log = get_logger('Main')


class PanelWithControl:
    """Главный класс панели управления"""

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

    def __init__(self):
        log.info("Инициализация приложения...")
        
        # Создание окна
        self.root = tk.Tk()
        self.config = Config()
        
        # Настройка тёмных стилей для ttk виджетов
        self._setup_dark_styles()
        
        # Оверлей загрузки (глобальный)
        self.loading = LoadingOverlay(self.root)
        
        # Текущий пользователь
        self.current_user = None
        
        # === Контроллеры ===
        self.app_controller = AppController(self.root, self.config)
        self.canvas_controller = CanvasController(self.app_controller)
        self.element_controller = ElementController(self.app_controller)
        self.ui_controller = UIController(self.app_controller)
        
        # Связываем контроллеры
        self.app_controller.set_controllers(
            self.canvas_controller,
            self.element_controller,
            self.ui_controller
        )
        
        # Менеджер горячих клавиш
        self.hotkey_manager = HotkeyManager(self.root)
        
        # Показываем экран авторизации
        from modules.auth_screen import AuthScreen
        self.auth_screen = AuthScreen(self.root, self._on_auth_success)
        
        # Интерфейс будет создан после авторизации
        self.ui = None
        self.canvas = None
        
        # Live Project Manager
        self.live_project_manager = get_live_project_manager(self.config)
        
        # Интегрированный менеджер артефактов (создается позже когда canvas готов)
        self.artifact_manager_integrated = None
    
    def _on_auth_success(self, user):
        """Колбэк успешной авторизации"""
        self.current_user = user
        # Показываем загрузку интерфейса с прогрессом
        self.loading.show("Подготовка интерфейса", "Инициализация...", progress=0)
        self.root.after(100, self._init_main_interface)
    
    def _init_main_interface(self):
        """Инициализирует основной интерфейс после авторизации"""
        try:
            # Строим интерфейс - 10%
            self.loading.update("Создание интерфейса", "UI компоненты...", progress=10)
            self.root.update_idletasks()
            
            self.ui = UIBuilder(self.root, self.config)
            self.ui.set_app_reference(self)
            self.ui.set_callbacks(
                toggle_grid=self.toggle_grid,
                grid_increase=self.grid_increase,
                grid_decrease=self.grid_decrease,
                apply_size=self.apply_element_size,
                reload_app=self.reload_app,
                delete_element=self.delete_selected_element,
                save=self.save_project,
                lock_size=self.toggle_size_lock
            )
            self.canvas = self.ui.build()
            self.root.update_idletasks()
        except Exception as e:
            print(f"[Init] UI Error: {e}")
            import traceback
            traceback.print_exc()

        # Инициализируем системы - 25%
        self.loading.update("Системы", "Zoom и сетка...", progress=25)
        self.root.update_idletasks()
        
        self.zoom_system = ZoomSystem(self.canvas, self.config)
        self.zoom_system.set_zoom_callback(self._on_zoom_changed)
        
        self.grid_system = GridSystem(self.canvas, self.config)
        self.selection_system = SelectionSystem(self.canvas, self.config)
        
        # Инструмент выделения
        self.selection_tool = SelectionTool(self.canvas, self.config)
        self.selection_tool.set_zoom_system(self.zoom_system)
        
        # Главная панель - 35%
        self.loading.update("Системы", "Главная панель...", progress=35)
        self.root.update_idletasks()
        
        self.main_canvas = MainCanvas(self.canvas, self.config)
        self.main_canvas.set_zoom_system(self.zoom_system)
        
        # Инициализируем главную панель ОДИН РАЗ после создания
        self.root.after(150, self._init_main_canvas)
        
        # Менеджер элементов - 45%
        self.loading.update("Менеджеры", "Элементы...", progress=45)
        self.root.update_idletasks()
        
        self.element_manager = ElementManager(self.canvas, self.config)
        self.element_manager.set_selection_callback(self._on_element_selected)
        self.element_manager.set_zoom_system(self.zoom_system)
        
        # Создаём интегрированный менеджер артефактов
        self.artifact_manager_integrated = get_artifact_manager_integrated(self.canvas, self.config)
        self.element_manager.set_main_canvas(self.main_canvas)

        # Менеджер механизмов - 55%
        self.loading.update("Менеджеры", "Механизмы...", progress=55)
        self.root.update_idletasks()
        
        self.mechanism_manager = MechanismManager(self.canvas, self.config)
        self.mechanism_manager.set_element_manager(self.element_manager)
        self.mechanism_manager.set_zoom_system(self.zoom_system)

        # Менеджер окон
        self.window_manager = get_window_manager()
        self.window_manager.set_element_manager(self.element_manager)
        self.window_manager.set_mechanism_manager(self.mechanism_manager)

        # Система функций - 65%
        self.loading.update("Менеджеры", "Функции...", progress=65)
        self.root.update_idletasks()
        
        self.button_functions = get_button_functions()
        self.button_functions.set_app(self)
        self.button_functions.set_element_manager(self.element_manager)
        self.button_functions.set_mechanism_manager(self.mechanism_manager)
        self.button_functions.set_window_manager(self.window_manager)

        # Менеджер проектов
        self.project_manager = ProjectManager(self)

        # Режим просмотра
        from modules.preview_mode import PreviewMode
        self.preview_mode = PreviewMode(self)

        # Система компонентов - 75%
        self.loading.update("Компоненты", "Артефакты...", progress=75)
        self.root.update_idletasks()
        
        self.component_manager = ComponentManager(self.element_manager, self.mechanism_manager, self.config)
        self.artifact_manager = NewArtifactManager()

        # Генератор кода
        self.code_generator = CodeGenerator()

        # События - 85%
        self.loading.update("Финализация", "События...", progress=85)
        self.root.update_idletasks()
        
        self.event_handlers = EventHandlers(self)
        self.callbacks = AppCallbacks(self)
        
        # === Обновляем контроллеры ссылками на менеджеры ===
        self.app_controller.set_managers(
            self.element_manager,
            self.mechanism_manager,
            self.project_manager,
            self.zoom_system,
            self.grid_system
        )
        self.app_controller.set_canvas(self.main_canvas, self.canvas)
        self.app_controller.preview_mode = self.preview_mode
        
        # Состояние для совместимости (делегируется в EventHandlers)
        self._drag_start = None
        self._drag_element_start = None
        self._drag_main_canvas_start = None
        self._dragging_main_canvas = False
        self._resize_handle = None
        self._resize_start_bounds = None
        self._pan_start = None

        # Связываем системы
        self.selection_system.set_info_callback(self.ui.update_coords_label)
        
        # Связываем вкладки с системами
        self._setup_tabs()
        
        # Связываем UI контроллер
        self.ui_controller.set_ui_builder(self.ui)
        self.ui_controller.set_tab_system(self.ui.get_tab_system())

        # Привязка событий мыши (через модуль EventHandlers)
        self.event_handlers.bind_events()
        
        # Регистрируем горячие клавиши через менеджер
        self._setup_hotkeys()
        
        # Инициализируем главный контроллер
        self.app_controller.initialize()

        # Создаём главную панель по центру
        self.loading.update("Загрузка интерфейса...", "Финализация")
        self.root.after(200, self._create_main_panel)

    def _setup_hotkeys(self):
        """Настраивает горячие клавиши через менеджер"""
        # Delete - удаление элемента
        self.hotkey_manager.register('Delete', self.delete_selected_element)
        self.hotkey_manager.register('BackSpace', self.delete_selected_element)
        
        # Ctrl+S - сохранить
        self.hotkey_manager.register('Control-s', lambda: self.save_project() or 'break')
        
        # Ctrl+Shift+S - сохранить как
        self.hotkey_manager.register('Control-Shift-s', self._on_save_project_as)
        
        # Ctrl+N - новый проект
        self.hotkey_manager.register('Control-n', self._on_new_project)
        
        # Escape - сбросить выделение
        self.hotkey_manager.register('Escape', self._on_escape_key)
        
        # Zoom
        self.hotkey_manager.register('Control-plus', self.zoom_in)
        self.hotkey_manager.register('Control-minus', self.zoom_out)
        self.hotkey_manager.register('Control-equal', self.zoom_in)
        self.hotkey_manager.register('Control-0', self.zoom_reset)
        
        # Стрелки для перемещения
        self.hotkey_manager.register('Up', lambda: self._move_selected(0, -1))
        self.hotkey_manager.register('Down', lambda: self._move_selected(0, 1))
        self.hotkey_manager.register('Left', lambda: self._move_selected(-1, 0))
        self.hotkey_manager.register('Right', lambda: self._move_selected(1, 0))
        self.hotkey_manager.register('Shift-Up', lambda: self._move_selected(0, -10))
        self.hotkey_manager.register('Shift-Down', lambda: self._move_selected(0, 10))
        self.hotkey_manager.register('Shift-Left', lambda: self._move_selected(-10, 0))
        self.hotkey_manager.register('Shift-Right', lambda: self._move_selected(10, 0))
        
        log.debug("Горячие клавиши настроены")

    def _setup_dark_styles(self):
        """Настраивает тёмные стили для ttk виджетов"""
        from tkinter import ttk
        style = ttk.Style()
        
        # Цвета
        BG = '#161b22'
        BG_DARK = '#0d1117'
        FG = '#e6edf3'
        FG_MUTED = '#8d96a0'
        BORDER = '#30363d'
        ACCENT = '#2f81f7'
        
        # Notebook (вкладки)
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', 
            background='#21262d', foreground=FG, padding=[8, 4], font=('Arial', 9))
        style.map('TNotebook.Tab',
            background=[('selected', ACCENT)], foreground=[('selected', '#ffffff')])
        
        # Combobox
        style.configure('TCombobox',
            fieldbackground=BG_DARK, background=BG, foreground=FG,
            arrowcolor=FG_MUTED, bordercolor=BORDER, lightcolor=BG, darkcolor=BG)
        style.map('TCombobox',
            fieldbackground=[('readonly', BG_DARK)],
            selectbackground=[('readonly', ACCENT)],
            selectforeground=[('readonly', '#ffffff')])
        
        # Scrollbar (скрытый)
        style.configure('TScrollbar', 
            background=BG, troughcolor=BG, bordercolor=BG, arrowcolor=BG)
        style.map('TScrollbar', background=[('active', BG), ('disabled', BG)])
        
        # Entry
        style.configure('TEntry',
            fieldbackground=BG_DARK, foreground=FG, insertcolor=FG, bordercolor=BORDER)
        
        # Treeview
        style.configure('Treeview',
            background=BG_DARK, fieldbackground=BG_DARK, foreground=FG,
            rowheight=22, borderwidth=0)
        style.configure('Treeview.Heading',
            background=BG, foreground=FG_MUTED, font=('Arial', 9))
        style.map('Treeview',
            background=[('selected', ACCENT)], foreground=[('selected', '#ffffff')])

    def _create_main_panel(self):
        """Создаёт главную панель по центру холста"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self._create_main_panel)
            return
        
        # Центрируем главную панель
        self.main_canvas.center_on_canvas()
        self.main_canvas.draw()
        
        # НЕ ДЕЛАЕМ принудительную перерисовку - это создаёт цикл!
        
        # Устанавливаем главную панель для сетки
        self.grid_system.set_main_panel(self.main_canvas)
        self.grid_system.set_zoom_system(self.zoom_system)
        
        # Обновляем поля размера (размеры главной панели)
        self._update_size_fields_from_main_canvas()
        
        # Обновляем zoom label
        self._update_zoom_label()
        
        # Финальная инициализация - запускаем с задержкой
        self.root.after(300, self._finalize_startup)
        
        # Принудительная отрисовка главной панели
        # НЕ вызываем _force_main_canvas_draw - это создавало цикл!
    
    def _finalize_startup(self):
        """Завершает загрузку и переключает в полноэкранный режим"""
        # Обновляем UI - 95%
        self.loading.update("Завершение", "Подготовка...", progress=95)
        self.root.update_idletasks()
        
        # Ждём для полной отрисовки
        self.root.after(300, self._complete_startup)
    
    def _complete_startup(self):
        """Полностью завершает запуск приложения"""
        # Финал - 100%
        self.loading.update("Готово!", "Запуск...", progress=100)
        self.root.update_idletasks()
        
        # УВЕЛИЧИВАЕМ паузу чтобы ВСЁ загрузилось
        self.root.after(1000, self._enter_fullscreen_after_load)
    
    def _enter_fullscreen_after_load(self):
        """Переход в полноэкранный режим после загрузки"""
        # Скрываем загрузку
        self.loading.hide()
        self.root.update_idletasks()
        
        # Переключаем в полноэкранный режим
        self.root.after(150, self._do_fullscreen)
    
    def _do_fullscreen(self):
        """Включает полноэкранный режим после загрузки"""
        print("[Main] Переключение в полноэкранный режим")
        
        # Сначала разрешаем изменение размера
        self.root.resizable(True, True)
        
        # Затем переключаем fullscreen через UIBuilder
        if self.ui and hasattr(self.ui, '_toggle_fullscreen'):
            if not self.ui._is_fullscreen:  # Переключаем только если не в fullscreen
                self.ui._toggle_fullscreen()
        
        log.info("Переход в полноэкранный режим завершён")
        print("[Main] Интерфейс полностью загружен и готов к работе")

    def _setup_tabs(self):
        """Настраивает связи вкладок с системами"""
        tab_system = self.ui.get_tab_system()
        if not tab_system:
            return
        
        # Связываем вкладку элементов с менеджером
        # Связываем вкладку меню с менеджером проектов и артефактов
        tab_menu = tab_system.get_tab('menu')
        if tab_menu:
            tab_menu.set_project_manager(self.project_manager)
            tab_menu.set_artifact_manager(self.artifact_manager)
            tab_menu.set_app(self)
        
        tab_elements = tab_system.get_tab('elements')
        if tab_elements:
            tab_elements.set_element_manager(self.element_manager)
            tab_elements.set_artifact_manager(self.artifact_manager)
            tab_elements.set_artifact_manager_integrated(self.artifact_manager_integrated)
            tab_elements.set_app(self)  # Для восстановления обработчиков после создания артефактов
        
        # Связываем вкладку механизмов
        tab_mechanisms = tab_system.get_tab('mechanisms')
        if tab_mechanisms:
            tab_mechanisms.set_mechanism_manager(self.mechanism_manager)
            tab_mechanisms.set_element_manager(self.element_manager)
        
        # Связываем вкладку цвета - при изменении применять к выбранному элементу
        tab_color = tab_system.get_tab('color')
        if tab_color:
            tab_color.set_change_callback(self._on_color_settings_changed)
        
        # Связываем вкладку текста - при изменении применять к текстовому элементу
        tab_text = tab_system.get_tab('text')
        if tab_text:
            tab_text.set_change_callback(self._on_text_settings_changed)
        
        # Связываем вкладку кода с генератором и данными
        tab_code = tab_system.get_tab('code')
        if tab_code:
            tab_code.set_code_generator(self.code_generator)
            tab_code.set_managers_extended(self.element_manager, self.main_canvas)
            
            # Настраиваем Live Project Manager
            if self.live_project_manager:
                self.live_project_manager.set_managers(self.element_manager, self.main_canvas)
        
        # Связываем вкладку фильтров
        tab_filters = tab_system.get_tab('filters')
        if tab_filters:
            tab_filters.set_element_manager(self.element_manager)
            tab_filters.set_main_canvas(self.main_canvas)
            tab_filters.set_app(self)
        
        # Связываем вкладку звуков
        tab_sounds = tab_system.get_tab('sounds')
        if tab_sounds:
            tab_sounds.set_element_manager(self.element_manager)
        
        # Инициализируем AI Assistant
        from modules.ai_assistant import get_ai_assistant
        self.ai_assistant = get_ai_assistant()
        
        # Связываем вкладку AI
        tab_ai = tab_system.get_tab('ai')
        if tab_ai:
            tab_ai.set_element_manager(self.element_manager)
            tab_ai.set_main_canvas(self.main_canvas)
            tab_ai.set_settings_tab(tab_system.get_tab('settings'))
            tab_ai.set_app(self)
        
        # Связываем вкладку слоёв
        self.tab_layers = tab_system.get_tab('layers')
        if self.tab_layers:
            self.tab_layers.set_element_manager(self.element_manager)
            self.tab_layers.set_mechanism_manager(self.mechanism_manager)

    def _bind_mouse_events(self):
        """Привязывает события мыши к холсту"""
        self.canvas.bind("<Button-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        
        # Двойной клик - активация кнопки
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        
        # ПКМ - контекстное меню для элементов
        self.canvas.bind("<Button-3>", self._on_right_click)
        
        # Средняя кнопка - панорамирование
        self.canvas.bind("<Button-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_drag)
        self.canvas.bind("<ButtonRelease-2>", self._on_pan_end)
        
        # Колесо мыши - zoom
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows/Mac
        self.canvas.bind("<Button-4>", self._on_mouse_wheel_up)  # Linux
        self.canvas.bind("<Button-5>", self._on_mouse_wheel_down)  # Linux
        
        # Ctrl + колесо для zoom на всех платформах
        self.canvas.bind("<Control-MouseWheel>", self._on_mouse_wheel)
        
        # Горячие клавиши
        self.root.bind("<Delete>", self._on_delete_key)
        self.root.bind("<BackSpace>", self._on_delete_key)
        
        # Ctrl+S - сохранить проект
        self.root.bind("<Control-s>", self._on_save_project)
        
        # Ctrl+Z - отмена (заглушка)
        self.root.bind("<Control-z>", lambda e: None)
        
        # Ctrl+Shift+S - сохранить как
        self.root.bind("<Control-Shift-s>", self._on_save_project_as)
        
        # Ctrl+N - новый проект
        self.root.bind("<Control-n>", self._on_new_project)
        
        # Ctrl+A - выбрать всё (заглушка)
        self.root.bind("<Control-a>", lambda e: None)
        
        # Стрелки для перемещения элемента
        self.root.bind("<Up>", lambda e: self._move_selected(0, -1))
        self.root.bind("<Down>", lambda e: self._move_selected(0, 1))
        self.root.bind("<Left>", lambda e: self._move_selected(-1, 0))
        self.root.bind("<Right>", lambda e: self._move_selected(1, 0))
        self.root.bind("<Shift-Up>", lambda e: self._move_selected(0, -10))
        self.root.bind("<Shift-Down>", lambda e: self._move_selected(0, 10))
        self.root.bind("<Shift-Left>", lambda e: self._move_selected(-10, 0))
        self.root.bind("<Shift-Right>", lambda e: self._move_selected(10, 0))
        self.root.bind("<BackSpace>", self._on_delete_key)
        
        # Escape - сбросить выделение
        self.root.bind("<Escape>", self._on_escape_key)
        
        # Горячие клавиши для zoom
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())  # = без Shift это +
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())

    def _on_mouse_press(self, event):
        """Обработчик нажатия мыши"""
        # Если режим создания механизма
        if self.mechanism_manager.is_creating():
            real_x, real_y = self.zoom_system.screen_to_real(event.x, event.y)
            self.mechanism_manager.on_create_start(real_x, real_y)
            return
        
        # Если режим создания элемента
        if self.element_manager.is_creating():
            # Преобразуем в реальные координаты
            real_x, real_y = self.zoom_system.screen_to_real(event.x, event.y)
            self.element_manager.on_create_start(real_x, real_y)
            return
        
        # Проверяем клик по маркеру resize (через SelectionTool)
        if self.selection_tool.is_active():
            element = self.element_manager.selected_element
            # Не разрешаем resize если размер заблокирован
            if element and not element.size_locked:
                handle = self.selection_tool.get_resize_handle(event.x, event.y)
                if handle:
                    self._resize_handle = handle
                    self._drag_start = (event.x, event.y)
                    self._resize_start_bounds = element.get_bounds()
                    return
        
        # Проверяем клик по элементу
        element = self.element_manager.select_at(event.x, event.y)
        if element:
            # Активируем рамку выделения
            self.selection_tool.select(element)
            # Запоминаем начальную позицию для перетаскивания
            self._drag_start = (event.x, event.y)
            self._drag_element_start = (element.x, element.y)
            self._resize_handle = None
            # Обновляем поля размера
            self._update_size_fields()
            # Загружаем свойства в панель цвета
            self._load_element_to_color_tab(element)
            # Обновляем кнопку блокировки
            self.ui.update_lock_button(element.size_locked)
            return
        
        # Проверяем клик по главной панели (main_canvas)
        if self.main_canvas.contains_point(event.x, event.y):
            # Снимаем выделение с элементов
            self.element_manager.deselect_all()
            self.selection_tool.deselect()
            # Загружаем свойства главной панели
            self._load_main_canvas_to_color_tab()
            # Обновляем поля размера
            self._update_size_fields()
            self.ui.update_lock_button(False)
            
            # Запоминаем позицию для перетаскивания главной панели
            self._drag_start = (event.x, event.y)
            self._drag_main_canvas_start = (self.main_canvas.x, self.main_canvas.y)
            self._dragging_main_canvas = True
            return
        
        # Клик по пустому месту - сбрасываем выделение
        self._drag_start = None
        self._drag_main_canvas_start = None
        self._dragging_main_canvas = False
        self._resize_handle = None
        self.element_manager.deselect_all()
        self.selection_tool.deselect()
        
        # Режим выделения сеткой
        if self.grid_system.grid_enabled:
            self.selection_system.on_mouse_press(event)

    def _on_mouse_drag(self, event):
        """Обработчик перетаскивания мыши"""
        # Создание элемента - показываем превью
        if self.element_manager.is_creating() and self.element_manager.creation_start:
            real_x, real_y = self.zoom_system.screen_to_real(event.x, event.y)
            self.element_manager.on_create_drag(real_x, real_y)
            return
        
        # Resize элемента
        if self._resize_handle and self._drag_start and self._resize_start_bounds:
            self._do_resize(event.x, event.y)
            return
        
        # Перетаскивание главной панели
        if self._dragging_main_canvas and self._drag_start and self._drag_main_canvas_start:
            # Вычисляем смещение в экранных координатах
            dx_screen = event.x - self._drag_start[0]
            dy_screen = event.y - self._drag_start[1]
            
            # Преобразуем в реальные координаты
            dx_real = self.zoom_system.unscale_value(dx_screen)
            dy_real = self.zoom_system.unscale_value(dy_screen)
            
            new_x = self._drag_main_canvas_start[0] + dx_real
            new_y = self._drag_main_canvas_start[1] + dy_real
            
            # Перемещаем главную панель
            self.main_canvas.move_to(new_x, new_y)
            
            # Обновляем сетку
            self._update_grids()
            return
        
        # Перетаскивание элемента
        if self._drag_start and self._drag_element_start:
            if self.element_manager.selected_element:
                # Вычисляем смещение в экранных координатах
                dx_screen = event.x - self._drag_start[0]
                dy_screen = event.y - self._drag_start[1]
                
                # Преобразуем в реальные координаты
                dx_real = self.zoom_system.unscale_value(dx_screen)
                dy_real = self.zoom_system.unscale_value(dy_screen)
                
                new_x = self._drag_element_start[0] + dx_real
                new_y = self._drag_element_start[1] + dy_real
                self.element_manager.selected_element.move_to(new_x, new_y)
                
                # Обновляем рамку выделения
                self.selection_tool.update()
                return
        
        # Режим выделения сеткой
        if self.grid_system.grid_enabled:
            self.selection_system.on_mouse_drag(event)

    def _do_resize(self, mx, my):
        """Выполняет resize элемента"""
        if not self.element_manager.selected_element:
            return
        
        x1, y1, x2, y2 = self._resize_start_bounds
        
        # Вычисляем смещение и преобразуем в реальные координаты
        dx_screen = mx - self._drag_start[0]
        dy_screen = my - self._drag_start[1]
        dx = self.zoom_system.unscale_value(dx_screen)
        dy = self.zoom_system.unscale_value(dy_screen)
        
        new_x1, new_y1, new_x2, new_y2 = x1, y1, x2, y2
        
        # Изменяем границы в зависимости от маркера
        handle = self._resize_handle
        
        # Показываем размеры во время resize
        self.selection_tool.show_size(True)
        
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
        
        # Применяем новые размеры
        element = self.element_manager.selected_element
        element.x = new_x1
        element.y = new_y1
        element.width = new_x2 - new_x1
        element.height = new_y2 - new_y1
        element.update()
        
        # Обновляем рамку выделения с размерами
        self.selection_tool.update(show_size=True)
        
        # Обновляем поля размера
        self._update_size_fields()

    def _on_mouse_release(self, event):
        """Обработчик отпускания мыши"""
        # Завершение создания механизма
        if self.mechanism_manager.is_creating():
            real_x, real_y = self.zoom_system.screen_to_real(event.x, event.y)
            mechanism = self.mechanism_manager.on_create_end(real_x, real_y)
            if mechanism:
                self._update_mechanisms_tab()
                # Обновляем вкладку слоёв
                if hasattr(self, 'tab_layers') and self.tab_layers:
                    self.tab_layers.update()
            self.canvas.config(cursor="arrow")
            return
        
        # Завершение создания элемента
        if self.element_manager.is_creating():
            real_x, real_y = self.zoom_system.screen_to_real(event.x, event.y)
            element = self.element_manager.on_create_end(real_x, real_y)
            if element:
                self._update_elements_tab()
                self._update_size_fields()
                # Обновляем вкладку слоёв
                if hasattr(self, 'tab_layers') and self.tab_layers:
                    self.tab_layers.update()
            self.canvas.config(cursor="arrow")
            return
        
        # Скрываем метку размеров после окончания resize
        if self._resize_handle:
            self.selection_tool.show_size(False)
        
        # Сброс состояния
        self._drag_start = None
        self._drag_element_start = None
        self._drag_main_canvas_start = None
        self._dragging_main_canvas = False
        self._resize_handle = None
        self._resize_start_bounds = None
        
        # Режим выделения сеткой
        if self.grid_system.grid_enabled:
            self.selection_system.on_mouse_release(event)

    def _on_mouse_move(self, event):
        """Обработчик движения мыши"""
        # Режим создания
        if self.element_manager.is_creating():
            self.canvas.config(cursor="crosshair")
            return
        
        # Проверяем наведение на маркер resize (через SelectionTool)
        if self.selection_tool.is_active():
            handle = self.selection_tool.get_resize_handle(event.x, event.y)
            if handle:
                cursor = self.RESIZE_CURSORS.get(handle, "arrow")
                self.canvas.config(cursor=cursor)
                return
        
        # Проверяем наведение на элемент
        element = self.element_manager.get_element_at(event.x, event.y)
        if element:
            self.canvas.config(cursor="fleur")  # Курсор перемещения
            return
        
        # Обычный курсор или сетка
        if self.grid_system.is_any_grid_enabled():
            self.canvas.config(cursor="crosshair")
            self.selection_system.on_mouse_move(event)
        else:
            self.canvas.config(cursor="arrow")

    def _on_pan_start(self, event):
        """Начало панорамирования"""
        self._pan_start = (event.x, event.y)
        self.canvas.config(cursor="fleur")

    def _on_pan_drag(self, event):
        """Панорамирование"""
        if self._pan_start:
            dx = event.x - self._pan_start[0]
            dy = event.y - self._pan_start[1]
            self.zoom_system.pan(dx, dy)
            self._pan_start = (event.x, event.y)
            self.element_manager.redraw_all()
            self.mechanism_manager.redraw_all()
            self.selection_tool.update()

    def _on_pan_end(self, event):
        """Конец панорамирования"""
        self._pan_start = None
        self.canvas.config(cursor="arrow")

    def _on_mouse_wheel(self, event):
        """Обработчик колеса мыши (zoom)"""
        # Windows/Mac
        if event.delta > 0:
            self.zoom_system.zoom_in(event.x, event.y)
        else:
            self.zoom_system.zoom_out(event.x, event.y)
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def _on_mouse_wheel_up(self, event):
        """Zoom in (Linux)"""
        self.zoom_system.zoom_in(event.x, event.y)
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def _on_mouse_wheel_down(self, event):
        """Zoom out (Linux)"""
        self.zoom_system.zoom_out(event.x, event.y)
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def zoom_in(self):
        """Увеличить масштаб"""
        self.zoom_system.zoom_in()
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def zoom_out(self):
        """Уменьшить масштаб"""
        self.zoom_system.zoom_out()
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def zoom_reset(self):
        """Сбросить масштаб на 100%"""
        self.zoom_system.reset_zoom()
        self.element_manager.redraw_all()
        self.mechanism_manager.redraw_all()
        self.selection_tool.update()
        self._update_zoom_label()

    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        if self.ui:
            self.ui._toggle_fullscreen()
    
    def toggle_preview_mode(self):
        """Переключает режим предпросмотра (полноэкранный просмотр без интерфейса)"""
        if self.preview_mode:
            self.preview_mode.toggle()

    def _on_zoom_changed(self, scale):
        """Вызывается при изменении масштаба"""
        self._update_zoom_label()
        self._update_grids()

    def _update_zoom_label(self):
        """Обновляет отображение текущего масштаба и размера сетки"""
        percent = self.zoom_system.get_zoom_percent()
        grid_size = self.grid_system.get_size()
        grid_status = "●" if self.grid_system.is_enabled() else "○"
        self.ui.update_coords_label(f"{percent}% | {grid_status}{grid_size}px")

    def _on_delete_key(self, event):
        """Обработчик клавиши Delete"""
        self.delete_selected_element()

    def delete_selected_element(self):
        """Удаляет выделенный элемент"""
        self.element_manager.delete_selected()
        self.selection_tool.deselect()
        self._update_elements_tab()

    def save_project(self):
        """Сохраняет проект"""
        if self.project_manager:
            self.project_manager.save_project()

    def _on_save_project(self, event):
        """Ctrl+S - сохранить проект"""
        if self.project_manager and self.project_manager.current_project:
            self.project_manager.save_project()
        return "break"

    def _on_save_project_as(self, event):
        """Ctrl+Shift+S - сохранить как"""
        tab_menu = self.tab_system.get_tab('menu')
        if tab_menu:
            tab_menu._on_save_as()
        return "break"

    def _on_new_project(self, event):
        """Ctrl+N - новый проект"""
        tab_menu = self.tab_system.get_tab('menu')
        if tab_menu:
            tab_menu._on_new_project()
        return "break"

    def _move_selected(self, dx, dy):
        """Перемещает выбранный элемент"""
        element = self.element_manager.get_selected()
        if element:
            element.move_by(dx, dy)
            self._update_info_panel()

    def toggle_size_lock(self):
        """Переключает блокировку размера для выбранного элемента"""
        element = self.element_manager.selected_element
        if element:
            element.size_locked = not element.size_locked
            self.ui.update_lock_button(element.size_locked)
            status = "заблокирован" if element.size_locked else "разблокирован"
            print(f"Размер элемента {status}")

    def _on_escape_key(self, event):
        """Обработчик клавиши Escape - сбросить выделение"""
        self.element_manager.deselect_all()
        self.selection_tool.deselect()

    def _on_right_click(self, event):
        """Обработчик правой кнопки мыши - контекстное меню"""
        # Проверяем, есть ли выбранный элемент
        element = self.element_manager.selected_element
        if not element:
            # Пробуем выбрать элемент под курсором
            element = self.element_manager.get_element_at(event.x, event.y)
            if element:
                self.element_manager.select_element(element)
                self.selection_tool.select(element)
        
        if not element:
            return
        
        # Создаём контекстное меню
        menu = tk.Menu(self.root, tearoff=0, bg="#2a2a2a", fg="#ffffff",
                      activebackground="#0078d4", activeforeground="#ffffff")
        
        # Определяем тип элемента для специфичных настроек
        if isinstance(element, ButtonElement):
            menu.add_command(label="⚙ Настройка кнопки", command=lambda: self._show_button_config(element))
            menu.add_command(label="⚡ Настройка действий", command=lambda: self._show_action_config(element))
        elif isinstance(element, FrameElement):
            menu.add_command(label="⚙ Настройка рамки", command=lambda: self._show_frame_config(element))
        elif isinstance(element, PanelElement):
            menu.add_command(label="⚙ Настройка панели", command=lambda: self._show_panel_config(element))
        elif isinstance(element, ImageElement):
            menu.add_command(label="🖼 Загрузить изображение", command=lambda: self._show_image_config(element))
        elif isinstance(element, ScrollAreaElement):
            menu.add_command(label="⊞ Настройка прокрутки", command=lambda: self._show_scroll_area_config(element))
        elif isinstance(element, StateSwitcherElement):
            menu.add_command(label="⟐ Настройка переключателя", command=lambda: self._show_state_switcher_config(element))
            menu.add_command(label="▶ Следующее состояние", command=lambda: self._switch_state_next(element))
            menu.add_command(label="◀ Предыдущее состояние", command=lambda: self._switch_state_prev(element))
            menu.add_command(label="📸 Захватить состояние", command=lambda: self._capture_state(element))
        
        menu.add_separator()
        
        # Общие настройки для всех элементов
        menu.add_command(label="👁 Настройки видимости...", command=lambda: self._show_visibility_dialog(element))
        menu.add_command(label="🔧 Расширенные настройки...", command=lambda: self._show_extended_settings(element))
        
        menu.add_separator()
        
        # Управление слоями
        menu.add_command(label="⬆ На передний план", command=lambda: self._bring_element_to_front(element))
        menu.add_command(label="⬇ На задний план", command=lambda: self._send_element_to_back(element))
        
        menu.add_separator()
        
        # Видимость
        vis_label = "◌ Скрыть" if element.is_visible else "👁 Показать"
        menu.add_command(label=vis_label, command=lambda: self._toggle_element_visibility(element))
        
        menu.add_separator()
        
        # Артефакты
        menu.add_command(label="📦 Сохранить как заготовку...", command=self.save_selection_as_artifact)
        menu.add_command(label="📚 Библиотека заготовок...", command=self.show_artifact_library)
        
        menu.add_separator()
        
        # Удаление
        menu.add_command(label="🗑 Удалить", command=lambda: self._delete_element(element))
        
        # Показываем меню
        menu.post(event.x_root, event.y_root)

    def _show_button_config(self, button_element):
        """Показывает диалог настройки кнопки"""
        result = show_button_config(self.root, button_element)
        if result:
            print(f"Кнопка настроена: функция #{result['function_id']}, текст: '{result['text']}'")
            # Обновляем отображение
            self.selection_tool.update()

    def _show_action_config(self, button_element):
        """Показывает диалог настройки действий кнопки"""
        result = show_action_config(
            self.root, 
            button_element, 
            self.element_manager, 
            self.mechanism_manager,
            self.button_functions
        )
        if result:
            print(f"Действия кнопки настроены")
            self.selection_tool.update()

    def _show_frame_config(self, frame_element):
        """Показывает диалог настройки рамки"""
        result = show_frame_config(self.root, frame_element)
        if result:
            points_count = len(result['spawn_points'])
            print(f"Рамка настроена: функция #{result['function_id']}, точек: {points_count}")
            # Обновляем отображение
            self.selection_tool.update()

    def _show_panel_config(self, panel_element):
        """Показывает диалог настройки панели"""
        result = show_panel_config(self.root, panel_element)
        if result:
            points_count = len(result['spawn_points'])
            print(f"Панель настроена: функция #{result['function_id']}, точек: {points_count}")
            # Обновляем отображение
            self.selection_tool.update()

    def _show_image_config(self, image_element):
        """Показывает диалог настройки изображения"""
        result = show_image_config(self.root, image_element)
        if result:
            self.selection_tool.update()

    def _show_scroll_area_config(self, scroll_area_element):
        """Показывает диалог настройки области прокрутки"""
        result = show_scroll_area_config(self.root, scroll_area_element)
        if result:
            self.selection_tool.update()

    def _show_state_switcher_config(self, state_switcher_element):
        """Показывает диалог настройки переключателя состояний"""
        result = show_state_switcher_config(
            self.root, 
            state_switcher_element, 
            self.element_manager, 
            self.mechanism_manager
        )
        if result:
            self.selection_tool.update()

    def _switch_state_next(self, state_switcher_element):
        """Переключает на следующее состояние"""
        state_switcher_element.switch_next(self.element_manager, self.mechanism_manager)
        self.selection_tool.update()

    def _switch_state_prev(self, state_switcher_element):
        """Переключает на предыдущее состояние"""
        state_switcher_element.switch_previous(self.element_manager, self.mechanism_manager)
        self.selection_tool.update()

    def _capture_state(self, state_switcher_element):
        """Захватывает текущее состояние элементов"""
        state_switcher_element.capture_current_state(self.element_manager, self.mechanism_manager)
        from tkinter import messagebox
        messagebox.showinfo("Захват", "Текущее состояние захвачено!")

    def _show_extended_settings(self, element):
        """Показывает расширенные настройки элемента"""
        # Устанавливаем менеджеры для элемента
        element.set_element_manager(self.element_manager)
        element.set_mechanism_manager(self.mechanism_manager)
        
        result = show_element_extended_dialog(
            self.root,
            element,
            self.element_manager,
            self.mechanism_manager
        )
        if result:
            self.selection_tool.update()
            if hasattr(self, 'tab_layers') and self.tab_layers:
                self.tab_layers.update()

    def _show_visibility_dialog(self, element):
        """Показывает диалог настройки видимости"""
        result = show_visibility_dialog(self.root, element, self.element_manager)
        if result:
            self.selection_tool.update()
            if hasattr(self, 'tab_layers') and self.tab_layers:
                self.tab_layers.update()

    # === Методы для работы с артефактами ===
    
    def save_selection_as_artifact(self):
        """Сохраняет выбранные элементы как артефакт"""
        # Собираем выбранные элементы
        selected_elements = []
        if self.element_manager.selected_element:
            selected_elements = [self.element_manager.selected_element]
        
        # Собираем механизмы (если выбран)
        selected_mechanisms = []
        if self.mechanism_manager and self.mechanism_manager.selected_mechanism:
            selected_mechanisms = [self.mechanism_manager.selected_mechanism]
        
        if not selected_elements and not selected_mechanisms:
            from tkinter import messagebox
            messagebox.showinfo("Информация", "Выберите элементы для сохранения")
            return
        
        # Показываем диалог сохранения
        result = show_save_artifact_dialog(
            self.root,
            element_count=len(selected_elements),
            mechanism_count=len(selected_mechanisms)
        )
        
        if result:
            # Создаём компонент
            element_ids = [e.id for e in selected_elements]
            mechanism_ids = [m.id for m in selected_mechanisms]
            
            component = self.component_manager.create_component_from_elements(
                element_ids, mechanism_ids, result['name']
            )
            
            # Применяем метаданные
            component.icon = result.get('icon', '📦')
            component.category = result.get('category', 'Пользовательские')
            component.tags = result.get('tags', [])
            component.description = result.get('description', '')
            
            # Сохраняем артефакт
            if self.artifact_manager.save_artifact(component):
                from tkinter import messagebox
                messagebox.showinfo("Успех", f"Заготовка '{result['name']}' сохранена!")

    def show_artifact_library(self):
        """Показывает библиотеку артефактов"""
        result = show_artifact_browser(self.root, self.artifact_manager)
        
        if result:
            # Размещаем выбранный артефакт
            self._place_artifact(result)

    def _place_artifact(self, artifact):
        """Размещает артефакт на холсте"""
        # Размещаем в центре видимой области
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Переводим в реальные координаты
        if self.zoom_system:
            cx, cy = self.zoom_system.screen_to_real(canvas_width / 2, canvas_height / 2)
        else:
            cx, cy = canvas_width / 2, canvas_height / 2
        
        # Смещаем на половину размера артефакта
        x = cx - artifact.width / 2
        y = cy - artifact.height / 2
        
        # Размещаем
        placed = self.component_manager.place_component(artifact, x, y)
        
        # Обновляем
        self.selection_tool.update()
        if hasattr(self, 'tab_layers') and self.tab_layers:
            self.tab_layers.update()
        
        # Сообщаем
        elem_count = len(placed.get('elements', []))
        mech_count = len(placed.get('mechanisms', []))
        print(f"[App] Размещена заготовка: {elem_count} элементов, {mech_count} механизмов")

    def _bring_element_to_front(self, element):
        """Перемещает элемент на передний план"""
        self.element_manager.bring_to_front(element)
        self.selection_tool.update()
        if hasattr(self, 'tab_layers') and self.tab_layers:
            self.tab_layers.update()

    def _send_element_to_back(self, element):
        """Перемещает элемент на задний план"""
        self.element_manager.send_to_back(element)
        self.selection_tool.update()
        if hasattr(self, 'tab_layers') and self.tab_layers:
            self.tab_layers.update()

    def _toggle_element_visibility(self, element):
        """Переключает видимость элемента"""
        if element.is_visible:
            element.hide()
        else:
            element.show()
        self.selection_tool.update()
        if hasattr(self, 'tab_layers') and self.tab_layers:
            self.tab_layers.update()

    def _delete_element(self, element):
        """Удаляет элемент"""
        self.element_manager.delete_element(element)
        self.selection_tool.clear()
        self._on_element_selected(None)
        
        # Обновляем вкладку слоёв
        if hasattr(self, 'tab_layers') and self.tab_layers:
            self.tab_layers.update()

    def _on_double_click(self, event):
        """Обработчик двойного клика - активация кнопки"""
        # Проверяем клик по элементу
        element = self.element_manager.get_element_at(event.x, event.y)
        
        if element and isinstance(element, ButtonElement):
            # Получаем номер функции
            func_id = element.get_function_id()
            if func_id > 0:
                # Вызываем функцию
                call_button_function(func_id)
                # Также запускаем механизмы привязанные к этой функции
                self.mechanism_manager.trigger_by_function(func_id)
            else:
                print(f"Кнопка не настроена (ПКМ для настройки)")

    def _on_element_selected(self, element):
        """Вызывается при выборе элемента"""
        try:
            # Обновляем инструмент выделения
            self.selection_tool.select(element)
            
            # Загружаем свойства элемента в панель цвета
            self._load_element_to_color_tab(element)
            
            # Обновляем поля размера
            self._update_size_fields()
            
            # Обновляем кнопку блокировки размера
            if element:
                self.ui.update_lock_button(element.size_locked)
            else:
                self.ui.update_lock_button(False)
        except Exception as e:
            print(f"Error in _on_element_selected: {e}")

    def _on_layer_panel_select(self, element):
        """Вызывается при выборе элемента через панель слоёв"""
        if element:
            self.element_manager.select_element(element)
            self._on_element_selected(element)
        
        # Обновляем сетки на выбранном элементе
        self._update_grids()

    def _on_layer_panel_mechanism_select(self, mechanism):
        """Вызывается при выборе механизма через панель слоёв"""
        if mechanism and self.mechanism_manager:
            self.mechanism_manager.select_mechanism(mechanism)
            # Переключаемся на вкладку механизмов
            if self.tab_system:
                self.tab_system.switch_to_tab('mechanisms')

    def _load_element_to_color_tab(self, element):
        """Загружает свойства элемента во вкладку цвета и текста"""
        tab_system = self.ui.get_tab_system()
        if not tab_system:
            return
        
        tab_color = tab_system.get_tab('color')
        tab_text = tab_system.get_tab('text')
        
        if element:
            # Определяем тип элемента
            element_type = element.ELEMENT_TYPE if hasattr(element, 'ELEMENT_TYPE') else None
            
            # Обновляем вкладку цвета
            if tab_color:
                tab_color.set_element_type(element_type, is_main_canvas=False)
                props = element.get_properties()
                tab_color.set_values(props)
            
            # Если это текст - обновляем вкладку текста
            if tab_text:
                if element_type == 'text':
                    tab_text.set_element(element)
                else:
                    tab_text.clear_element()
        else:
            # Нет выбранного элемента - блокируем настройки
            if tab_color:
                tab_color.clear_element()
            if tab_text:
                tab_text.clear_element()

    def _load_main_canvas_to_color_tab(self):
        """Загружает свойства главной панели во вкладку цвета"""
        tab_system = self.ui.get_tab_system()
        if not tab_system:
            return
        
        tab_color = tab_system.get_tab('color')
        if not tab_color:
            return
        
        # Устанавливаем режим главной панели
        tab_color.set_element_type(None, is_main_canvas=True)
        
        # Загружаем свойства главной панели
        props = self.main_canvas.get_properties()
        tab_color.set_values(props)

    def _on_color_settings_changed(self, values):
        """Вызывается при изменении настроек цвета"""
        # Проверяем режим главной панели
        tab_system = self.ui.get_tab_system()
        if tab_system:
            tab_color = tab_system.get_tab('color')
            if tab_color and tab_color.is_main_canvas_mode:
                # Применяем к главной панели
                self.main_canvas.set_properties(values)
                return
        
        # Применяем к выбранному элементу (без сброса выделения)
        if self.element_manager.selected_element:
            self.element_manager.set_selected_properties(values)
            # Обновляем рамку выделения (она должна остаться)
            self.selection_tool.update()

    def _on_text_settings_changed(self, values):
        """Вызывается при изменении настроек текста"""
        element = self.element_manager.selected_element
        if element and hasattr(element, 'ELEMENT_TYPE') and element.ELEMENT_TYPE == 'text':
            element.set_properties(values)
            self.selection_tool.update()

    def _update_elements_tab(self):
        """Обновляет вкладку элементов"""
        tab_system = self.ui.get_tab_system()
        if tab_system:
            tab_elements = tab_system.get_tab('elements')
            if tab_elements:
                tab_elements.refresh()

    def _update_mechanisms_tab(self):
        """Обновляет вкладку механизмов"""
        tab_system = self.ui.get_tab_system()
        if tab_system:
            tab_mechanisms = tab_system.get_tab('mechanisms')
            if tab_mechanisms:
                tab_mechanisms.refresh()

    def _update_size_fields(self):
        """Обновляет поля ввода размера из выбранного элемента или главной панели"""
        element = self.element_manager.selected_element
        if element:
            self.ui.canvas_width_entry.delete(0, tk.END)
            self.ui.canvas_width_entry.insert(0, str(int(element.width)))
            self.ui.canvas_height_entry.delete(0, tk.END)
            self.ui.canvas_height_entry.insert(0, str(int(element.height)))
        else:
            # Показываем размеры главной панели
            self._update_size_fields_from_main_canvas()

    def _update_size_fields_from_main_canvas(self):
        """Обновляет поля размера из главной панели"""
        self.ui.canvas_width_entry.delete(0, tk.END)
        self.ui.canvas_width_entry.insert(0, str(int(self.main_canvas.width)))
        self.ui.canvas_height_entry.delete(0, tk.END)
        self.ui.canvas_height_entry.insert(0, str(int(self.main_canvas.height)))

    def _update_grids(self):
        """Обновляет сетку на главной панели"""
        if self.grid_system.is_enabled():
            self.grid_system.draw_grid()
        else:
            self.grid_system.clear_grids()

    def toggle_grid(self):
        """Переключает сетку"""
        self.grid_system.toggle_grid()
        self._update_cursor()

        if not self.grid_system.is_enabled():
            self.selection_system.clear_selection()

    def grid_increase(self):
        """Увеличивает размер сетки"""
        new_size = self.grid_system.increase_size()
        self._update_zoom_label()

    def grid_decrease(self):
        """Уменьшает размер сетки"""
        new_size = self.grid_system.decrease_size()
        self._update_zoom_label()

    def _update_cursor(self):
        """Обновляет курсор в зависимости от состояния"""
        if self.element_manager.is_creating():
            self.canvas.config(cursor="crosshair")
        elif self.grid_system.is_any_grid_enabled():
            self.canvas.config(cursor="crosshair")
        else:
            self.canvas.config(cursor="arrow")

    def apply_element_size(self, width, height):
        """Применяет размер к выбранному элементу или главной панели"""
        # Ограничиваем размеры
        width = max(100, min(5000, width))
        height = max(100, min(5000, height))
        
        element = self.element_manager.selected_element
        if element:
            # Применяем к выбранному элементу
            element.width = width
            element.height = height
            element.update()
            
            # Обновляем рамку выделения
            self.selection_tool.update()
        else:
            # Применяем к главной панели
            self.main_canvas.resize(width, height)
            # Перерисовываем все элементы
            self.element_manager.redraw_all()
        
        # Обновляем сетки
        self._update_grids()

    def reload_app(self):
        """Перезагружает приложение"""
        self.root.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def run(self):
        """Запуск приложения"""
        log.info("Запуск главного цикла...")
        self.app_controller.start()
        self.root.mainloop()

    def _force_main_canvas_draw(self):
        """Принудительно отрисовывает главную панель"""
        if self.main_canvas and self.canvas:
            print("[Main] Принудительная отрисовка главной панели")
            self.main_canvas.is_visible = True
            self.main_canvas.draw()
            
            # Повторяем через интервалы для надёжности
            self.root.after(100, self._ensure_main_canvas_visible)
    
    def _ensure_main_canvas_visible(self):
        """Обеспечивает видимость главной панели"""
        if self.main_canvas and self.canvas:
            # Проверяем есть ли главная панель на холсте
            items = self.canvas.find_withtag("main_canvas")
            if not items:
                print("[Main] Главная панель отсутствует - перерисовываем")
                self.main_canvas.draw()
                
                # Центрируем если нужно
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                if canvas_width > 100 and canvas_height > 100:
                    self.main_canvas.center_on_canvas()
            else:
                print(f"[Main] Главная панель найдена: {len(items)} items")
    
    def _init_main_canvas(self):
        """Инициализирует и отрисовывает главную панель"""
        if self.main_canvas and self.canvas:
            print("[Main] Инициализация главной панели")
            
            # Центрируем на холсте
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            print(f"[Main] Размеры холста: {canvas_width}×{canvas_height}")
            
            if canvas_width > 1 and canvas_height > 1:
                self.main_canvas.center_on_canvas()
            else:
                # Если размеры холста ещё не готовы, повторяем позже
                self.root.after(100, self._init_main_canvas)
                return
            
            # Принудительная отрисовка
            self.main_canvas.draw()
            
            print("[Main] Главная панель инициализирована")

    def shutdown(self):
        """Корректное завершение приложения"""
        log.info("Завершение приложения...")
        self.app_controller.stop()
        self.hotkey_manager.unregister_all()


def main():
    """Точка входа"""
    log.info("=" * 50)
    log.info("Every Frame Dominator - Запуск")
    log.info("=" * 50)
    
    app = PanelWithControl()
    try:
        app.run()
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()

