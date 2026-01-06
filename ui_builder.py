#!/usr/bin/env python3
"""
Построитель интерфейса
Отвечает за создание всех UI компонентов
"""
import tkinter as tk
from tkinter import ttk

from .tab_system import TabSystem
from .toolbar_buttons import ToolbarManager


# Пресеты размеров
SIZE_PRESETS = {
    # Мониторы
    "— Мониторы —": None,
    "HD (1280×720)": (1280, 720),
    "Full HD (1920×1080)": (1920, 1080),
    "2K QHD (2560×1440)": (2560, 1440),
    "4K UHD (3840×2160)": (3840, 2160),
    
    # Мобильные
    "— Мобильные —": None,
    "iPhone SE (375×667)": (375, 667),
    "iPhone 14 (390×844)": (390, 844),
    "iPhone 14 Pro Max (430×932)": (430, 932),
    "Android (360×800)": (360, 800),
    "Android Large (412×915)": (412, 915),
    
    # Планшеты
    "— Планшеты —": None,
    "iPad Mini (768×1024)": (768, 1024),
    "iPad Pro 11\" (834×1194)": (834, 1194),
    "iPad Pro 12.9\" (1024×1366)": (1024, 1366),
    
    # Соцсети
    "— Соцсети —": None,
    "Instagram Post (1080×1080)": (1080, 1080),
    "Instagram Story (1080×1920)": (1080, 1920),
    "Facebook Cover (820×312)": (820, 312),
    "YouTube Thumbnail (1280×720)": (1280, 720),
    "Twitter Header (1500×500)": (1500, 500),
    
    # Веб
    "— Веб —": None,
    "Баннер (728×90)": (728, 90),
    "Sidebar (300×250)": (300, 250),
    "Leaderboard (970×90)": (970, 90),
    
    # Иконки
    "— Иконки —": None,
    "Favicon (32×32)": (32, 32),
    "App Icon (512×512)": (512, 512),
    "Icon Small (64×64)": (64, 64),
    "Icon Medium (128×128)": (128, 128),
    "Icon Large (256×256)": (256, 256),
}


class UIBuilder:
    """Построитель пользовательского интерфейса"""

    def __init__(self, root, config):
        self.root = root
        self.config = config

        # Ссылки на виджеты
        self.control_panel = None
        self.main_panel = None
        self.canvas = None
        self.grid_coords_label = None
        self.canvas_width_entry = None
        self.canvas_height_entry = None

        # Система вкладок
        self.tab_system = None
        
        # Менеджер кнопок панели инструментов
        self.toolbar_manager = None
        
        # Ссылка на приложение (для функций кнопок)
        self.app_ref = None

        # Колбэки
        self.on_toggle_grid = None
        self.on_grid_increase = None
        self.on_grid_decrease = None
        self.on_apply_size = None
        self.on_reload = None
        self.on_delete = None
        self.on_save = None
        self.on_lock_size = None

    def set_callbacks(self, toggle_grid=None, grid_increase=None, grid_decrease=None,
                      apply_size=None, reload_app=None, delete_element=None, 
                      save=None, lock_size=None):
        """Устанавливает колбэки для кнопок"""
        self.on_toggle_grid = toggle_grid
        self.on_grid_increase = grid_increase
        self.on_grid_decrease = grid_decrease
        self.on_apply_size = apply_size
        self.on_reload = reload_app
        self.on_delete = delete_element
        self.on_save = save
        self.on_lock_size = lock_size

    def set_app_reference(self, app):
        """Устанавливает ссылку на приложение"""
        self.app_ref = app
        if self.toolbar_manager:
            self.toolbar_manager.app = app

    def build(self):
        """Строит весь интерфейс"""
        self._setup_window()
        self._create_bottom_panel()  # Сначала низ
        self._create_control_panel()  # Потом боковая
        self._create_main_panel()  # Потом основная

        return self.canvas

    def _setup_window(self):
        """Настройка главного окна"""
        cfg = self.config
        
        self.root.title(cfg.WINDOW_TITLE)
        self.root.configure(bg=cfg.WINDOW_BG)
        
        # Минимальный размер окна
        self.root.minsize(cfg.WINDOW_MIN_WIDTH, cfg.WINDOW_MIN_HEIGHT)
        
        # Определяем платформу
        import sys
        self._is_linux = sys.platform.startswith('linux')
        
        # Сохраняем геометрию для оконного режима
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - cfg.WINDOW_DEFAULT_WIDTH) // 2
        y = (screen_h - cfg.WINDOW_DEFAULT_HEIGHT) // 2
        self._windowed_geometry = f"{cfg.WINDOW_DEFAULT_WIDTH}x{cfg.WINDOW_DEFAULT_HEIGHT}+{x}+{y}"
        
        # Запуск в полноэкранном или оконном режиме
        if cfg.WINDOW_START_FULLSCREEN:
            # Полноэкранный режим (кроссплатформенный)
            self._set_fullscreen(True)
            self._is_fullscreen = True
        else:
            # КОМПАКТНЫЙ оконный режим - ФИКСИРОВАННЫЕ размеры
            load_w = cfg.WINDOW_LOADING_WIDTH   # 1200px
            load_h = cfg.WINDOW_LOADING_HEIGHT  # 800px
            
            # НЕ привязываемся к размерам экрана!
            # Всегда один и тот же компактный размер
            
            # ЖЕСТКАЯ ФИКСАЦИЯ НА ГЛАВНОМ МОНИТОРЕ
            # Всегда центрируем на первичном экране (0,0)
            load_x = (screen_w - load_w) // 2
            load_y = (screen_h - load_h) // 2
            
            # ПРИНУДИТЕЛЬНО устанавливаем позицию
            geometry = f"{load_w}x{load_h}+{load_x}+{load_y}"
            self.root.geometry(geometry)
            
            # БЛОКИРУЕМ изменения во время загрузки
            self.root.resizable(False, False)
            self.root.wm_attributes('-topmost', True)  # Всегда сверху во время загрузки
            
            self._is_fullscreen = False
            
            print(f"[Window] КОМПАКТНЫЙ режим: {load_w}×{load_h} ФИКСИРОВАННО на {load_x},{load_y}")
            
            # Сохраняем для восстановления
            self._loading_geometry = geometry
        
        # Привязываем F11 для переключения режимов
        self.root.bind('<F11>', self._toggle_fullscreen)
        self.root.bind('<Escape>', self._exit_fullscreen)
        
        # Отслеживание изменения размера
        self.root.bind('<Configure>', self._on_window_resize)
    
    def _set_fullscreen(self, enable: bool):
        """Устанавливает полноэкранный режим кроссплатформенно"""
        if enable:
            if self._is_linux:
                # На Linux используем -fullscreen для настоящего полноэкранного режима
                self.root.attributes('-fullscreen', True)
            else:
                # Windows - используем zoomed
                try:
                    self.root.state('zoomed')
                except tk.TclError:
                    self.root.attributes('-fullscreen', True)
        else:
            if self._is_linux:
                self.root.attributes('-fullscreen', False)
            else:
                try:
                    self.root.state('normal')
                except tk.TclError:
                    self.root.attributes('-fullscreen', False)
    
    def _toggle_fullscreen(self, event=None):
        """Переключает полноэкранный/оконный режим (F11)"""
        if self._is_fullscreen:
            # Выход из полноэкранного
            self._set_fullscreen(False)
            self.root.geometry(self._windowed_geometry)
            self._is_fullscreen = False
        else:
            # Сохраняем текущий размер
            self._windowed_geometry = self.root.geometry()
            # Переход в полноэкранный
            self._set_fullscreen(True)
            self._is_fullscreen = True
        return 'break'
    
    def _exit_fullscreen(self, event=None):
        """Выход из полноэкранного режима (Escape)"""
        if self._is_fullscreen:
            self._set_fullscreen(False)
            self.root.geometry(self._windowed_geometry)
            self._is_fullscreen = False
    
    def _on_window_resize(self, event=None):
        """Обработка изменения размера окна"""
        # Вызывается при любом изменении геометрии
        # Можно использовать для адаптации интерфейса
        pass

    def _create_control_panel(self):
        """Создает боковую панель управления"""
        self.control_panel = tk.Frame(
            self.root,
            bg=self.config.CONTROL_PANEL_BG,
            width=self.config.CONTROL_PANEL_WIDTH,
            height=self.config.CONTROL_PANEL_HEIGHT,
            relief=self.config.CONTROL_PANEL_RELIEF,
            borderwidth=self.config.CONTROL_PANEL_BORDER
        )
        self.control_panel.pack(
            side=self.config.CONTROL_PANEL_SIDE,
            fill=self.config.CONTROL_PANEL_FILL,
            expand=self.config.CONTROL_PANEL_EXPAND,
            padx=self.config.CONTROL_PANEL_PADX,
            pady=self.config.CONTROL_PANEL_PADY
        )
        self.control_panel.pack_propagate(False)

        # Создаём систему вкладок внутри боковой панели
        self._create_tab_system()

        # Нижняя часть боковой панели (координаты и кнопки)
        self._create_bottom_controls()

    def _create_tab_system(self):
        """Создаёт систему вкладок"""
        self.tab_system = TabSystem(self.control_panel, self.config)
        self.tab_system.build()

    def _create_bottom_controls(self):
        """Создаёт нижнюю часть боковой панели (координаты и кнопки)"""
        cfg = self.config

        # Контейнер для нижних элементов
        bottom_frame = tk.Frame(
            self.control_panel,
            bg=cfg.SECTION_BG
        )
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Секция кнопок
        section_buttons = tk.Frame(
            bottom_frame,
            bg=cfg.SECTION_BG,
            relief=cfg.SECTION_RELIEF,
            borderwidth=cfg.SECTION_BORDER
        )
        section_buttons.pack(
            fill=tk.X,
            padx=cfg.SECTION_PADX,
            pady=cfg.SECTION_PADY,
            side=tk.BOTTOM
        )
        self._create_buttons_section(section_buttons)

        # Секция координат
        section_coords = tk.Frame(
            bottom_frame,
            bg=cfg.SECTION_BG,
            height=cfg.SECTION3_HEIGHT,
            relief=cfg.SECTION_RELIEF,
            borderwidth=cfg.SECTION_BORDER
        )
        section_coords.pack(
            fill=tk.X,
            padx=cfg.SECTION_PADX,
            pady=cfg.SECTION_PADY,
            side=tk.BOTTOM
        )
        section_coords.pack_propagate(False)
        self._create_coordinates_section(section_coords)

    def _create_main_panel(self):
        """Создает основную панель с холстом и панелью артефактов"""
        self.main_panel = tk.Frame(
            self.root,
            bg=self.config.MAIN_PANEL_BG,
            relief=self.config.MAIN_PANEL_RELIEF,
            borderwidth=self.config.MAIN_PANEL_BORDER
        )
        self.main_panel.pack(
            side=tk.LEFT,
            fill=self.config.MAIN_PANEL_FILL,
            expand=self.config.MAIN_PANEL_EXPAND,
            padx=self.config.MAIN_PANEL_PADX,
            pady=self.config.MAIN_PANEL_PADY
        )

        # Canvas для рисования
        self.canvas = tk.Canvas(
            self.main_panel,
            bg=self.config.CANVAS_BG,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _create_coordinates_section(self, parent):
        """Создает секцию размеров - стиль GitHub"""
        BG = '#161b22'
        BG_INPUT = '#0d1117'
        BORDER = '#30363d'
        TEXT = '#e6edf3'
        TEXT_MUTED = '#8d96a0'
        ACCENT = '#238636'

        # Пресеты (компактнее)
        preset_frame = tk.Frame(parent, bg=BG)
        preset_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        
        self.size_preset_var = tk.StringVar()
        self.size_preset_combo = ttk.Combobox(
            preset_frame, textvariable=self.size_preset_var,
            values=list(SIZE_PRESETS.keys()), state="readonly",
            width=18, font=("Arial", 8)
        )
        self.size_preset_combo.pack(side=tk.LEFT)
        self.size_preset_combo.set("Full HD (1920×1080)")
        self.size_preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        # Разделитель
        tk.Frame(parent, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Ручной ввод (компактнее)
        manual_frame = tk.Frame(parent, bg=BG)
        manual_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)

        self.canvas_width_entry = tk.Entry(
            manual_frame, width=5, font=("Arial", 8),
            bg=BG_INPUT, fg=TEXT, justify=tk.CENTER,
            insertbackground=TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.canvas_width_entry.pack(side=tk.LEFT)
        self.canvas_width_entry.insert(0, str(self.config.WORK_ZONE_DEFAULT_WIDTH))

        tk.Label(manual_frame, text="×", bg=BG, fg=TEXT_MUTED, font=("Arial", 8)).pack(side=tk.LEFT)

        self.canvas_height_entry = tk.Entry(
            manual_frame, width=5, font=("Arial", 8),
            bg=BG_INPUT, fg=TEXT, justify=tk.CENTER,
            insertbackground=TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER
        )
        self.canvas_height_entry.pack(side=tk.LEFT)
        self.canvas_height_entry.insert(0, str(self.config.WORK_ZONE_DEFAULT_HEIGHT))

        # Кнопка OK
        tk.Button(
            manual_frame, text="OK", font=("Arial", 8),
            bg=ACCENT, fg='#ffffff', relief=tk.FLAT,
            activebackground='#2ea043', cursor="hand2",
            padx=4, command=self._on_apply_size_click
        ).pack(side=tk.LEFT, padx=2)

        # Разделитель
        tk.Frame(parent, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Zoom (расширен)
        zoom_frame = tk.Frame(parent, bg=BG)
        zoom_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=4, pady=2)

        self.grid_coords_label = tk.Label(
            zoom_frame, text="100%", bg=BG, fg=TEXT,
            font=("Consolas", 10), anchor="e"
        )
        self.grid_coords_label.pack(side=tk.RIGHT, padx=2)

    def _on_preset_selected(self, event=None):
        """Обработчик выбора пресета размера"""
        preset_name = self.size_preset_var.get()
        size = SIZE_PRESETS.get(preset_name)
        
        if size is None:
            # Это заголовок секции, игнорируем
            return
        
        width, height = size
        
        # Обновляем поля ввода
        self.canvas_width_entry.delete(0, tk.END)
        self.canvas_width_entry.insert(0, str(width))
        self.canvas_height_entry.delete(0, tk.END)
        self.canvas_height_entry.insert(0, str(height))
        
        # Применяем размер
        if self.on_apply_size:
            self.on_apply_size(width, height)

    def _create_tooltip(self, widget, text):
        """Создаёт всплывающую подсказку для виджета"""
        tooltip_window = None
        
        def show_tooltip(event):
            nonlocal tooltip_window
            if tooltip_window:
                return
            x = event.x_root + 15
            y = event.y_root - 30
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            tooltip_window.configure(bg="#1a1a1a")
            
            label = tk.Label(
                tooltip_window,
                text=text,
                bg="#1a1a1a",
                fg="#ffffff",
                font=("Arial", 9),
                padx=8,
                pady=4,
                relief=tk.SOLID,
                borderwidth=1
            )
            label.pack()
        
        def hide_tooltip(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def _create_buttons_section(self, parent):
        """Создает секцию с кнопками - стиль GitHub"""
        # GitHub Dark цвета
        BG = '#161b22'
        BG_BTN = '#21262d'
        BORDER = '#30363d'
        TEXT = '#e6edf3'
        TEXT_MUTED = '#8d96a0'

        buttons_frame = tk.Frame(parent, bg=BG)
        buttons_frame.pack(side=tk.RIGHT, padx=4, pady=3)

        # Группа: Сетка
        grid_group = tk.Frame(buttons_frame, bg=BG)
        grid_group.pack(side=tk.LEFT, padx=2)
        
        for sym, tip, cmd in [
            ('#', 'Сетка вкл/выкл', self._on_toggle_grid1_click),
            ('−', 'Сетка меньше', self._on_grid_decrease),
            ('+', 'Сетка больше', self._on_grid_increase),
        ]:
            btn = tk.Button(
                grid_group, text=sym, font=("Arial", 10),
                bg=BG_BTN, fg=TEXT_MUTED,
                activebackground=BORDER, activeforeground=TEXT,
                relief=tk.FLAT, width=2, pady=2, cursor="hand2", command=cmd
            )
            btn.pack(side=tk.LEFT, padx=1)
            self._create_tooltip(btn, tip)
        
        # Разделитель
        tk.Frame(buttons_frame, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Группа: Действия
        actions_group = tk.Frame(buttons_frame, bg=BG)
        actions_group.pack(side=tk.LEFT, padx=2)
        
        # Удалить
        del_btn = tk.Button(
            actions_group, text="×", font=("Arial", 11),
            bg=BG_BTN, fg=TEXT_MUTED,
            activebackground=BORDER, activeforeground=TEXT,
            relief=tk.FLAT, width=2, pady=2, cursor="hand2", command=self._on_delete_click
        )
        del_btn.pack(side=tk.LEFT, padx=1)
        self._create_tooltip(del_btn, "Удалить элемент")
        
        # Блокировка
        self.lock_btn = tk.Button(
            actions_group, text="◎", font=("Arial", 10),
            bg=BG_BTN, fg=TEXT_MUTED,
            activebackground=BORDER, activeforeground=TEXT,
            relief=tk.FLAT, width=2, pady=2, cursor="hand2", command=self._on_lock_size_click
        )
        self.lock_btn.pack(side=tk.LEFT, padx=1)
        self._create_tooltip(self.lock_btn, "Блокировка размера")
        
        # Разделитель
        tk.Frame(buttons_frame, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Сохранить
        save_btn = tk.Button(
            buttons_frame, text="↓", font=("Arial", 10),
            bg='#238636', fg='#ffffff',
            activebackground='#2ea043', activeforeground='#ffffff',
            relief=tk.FLAT, width=2, pady=2, cursor="hand2", command=self._on_save_click
        )
        save_btn.pack(side=tk.LEFT, padx=1)
        self._create_tooltip(save_btn, "Сохранить")
        
        # Перезагрузить
        reload_btn = tk.Button(
            buttons_frame, text="↻", font=("Arial", 10),
            bg=BG_BTN, fg=TEXT_MUTED,
            activebackground=BORDER, activeforeground=TEXT,
            relief=tk.FLAT, width=2, pady=2, cursor="hand2", command=self._on_reload_click
        )
        reload_btn.pack(side=tk.LEFT, padx=1)
        self._create_tooltip(reload_btn, "Перезагрузить")

    def _create_button(self, parent, text, font_family, font_size, bg, fg, active_bg, active_fg, padx, pady, command):
        """Создает кнопку"""
        btn = tk.Button(
            parent, text=text, bg=bg, fg=fg,
            font=(font_family, font_size), width=1, height=1,
            command=command, relief=tk.FLAT, borderwidth=0,
            activebackground=active_bg, activeforeground=active_fg, cursor="hand2"
        )
        btn.pack(side=tk.LEFT, padx=padx, pady=pady)
        return btn

    def _create_bottom_panel(self):
        """Создает нижнюю панель - стиль GitHub"""
        BG = '#161b22'
        
        # Сохраняем ссылку на панель для полноэкранного режима
        self.bottom_panel = tk.Frame(
            self.root, bg=BG, height=56  # Увеличена высота с 42 до 56
        )
        self.bottom_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)
        self.bottom_panel.pack_propagate(False)
        
        # Контейнер для кнопок
        toolbar_frame = tk.Frame(self.bottom_panel, bg=BG)
        toolbar_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        
        # Создаём менеджер кнопок
        self.toolbar_manager = ToolbarManager(toolbar_frame, self.config, self.app_ref)
        self.toolbar_manager.create_all_buttons(toolbar_frame)

    # Обработчики кнопок
    def _on_toggle_grid1_click(self):
        if self.on_toggle_grid:
            self.on_toggle_grid()

    def _on_grid_increase(self):
        if self.on_grid_increase:
            self.on_grid_increase()

    def _on_grid_decrease(self):
        if self.on_grid_decrease:
            self.on_grid_decrease()

    def _on_apply_size_click(self):
        if self.on_apply_size:
            try:
                width = int(self.canvas_width_entry.get())
                height = int(self.canvas_height_entry.get())
                self.on_apply_size(width, height)
            except ValueError:
                print("Ошибка: введите корректные числа")

    def _on_reload_click(self):
        if self.on_reload:
            self.on_reload()

    def _on_delete_click(self):
        if self.on_delete:
            self.on_delete()

    def _on_save_click(self):
        if self.on_save:
            self.on_save()

    def _on_lock_size_click(self):
        if self.on_lock_size:
            self.on_lock_size()

    def update_lock_button(self, is_locked):
        """Обновляет вид кнопки блокировки размера"""
        if hasattr(self, 'lock_btn'):
            if is_locked:
                self.lock_btn.config(text="●", fg="#9e6a03")
            else:
                self.lock_btn.config(text="◎", fg="#8d96a0")

    def update_coords_label(self, text):
        """Обновляет метку координат"""
        if self.grid_coords_label:
            self.grid_coords_label.config(text=text)

    def get_tab_system(self):
        """Возвращает систему вкладок"""
        return self.tab_system

