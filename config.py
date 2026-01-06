#!/usr/bin/env python3
"""
Конфигурация панели управления
Стиль: GitHub Dark
"""
import tkinter as tk


class Config:
    """Константы интерфейса в стиле GitHub Dark"""

    # ============================================
    # ЦВЕТОВАЯ СХЕМА GITHUB DARK
    # ============================================
    # Фоны
    BG_CANVAS = "#0d1117"        # Основной фон (canvas-default)
    BG_SUBTLE = "#161b22"        # Вторичный фон (canvas-subtle)
    BG_INSET = "#010409"         # Углублённый фон (canvas-inset)
    BG_OVERLAY = "#1c2128"       # Оверлей (canvas-overlay)
    
    # Границы
    BORDER_DEFAULT = "#30363d"   # Стандартная граница
    BORDER_MUTED = "#21262d"     # Приглушённая граница
    BORDER_SUBTLE = "#6e768166"  # Тонкая граница
    
    # Текст
    FG_DEFAULT = "#e6edf3"       # Основной текст
    FG_MUTED = "#8d96a0"         # Приглушённый текст
    FG_SUBTLE = "#6e7681"        # Тонкий текст
    FG_ON_EMPHASIS = "#ffffff"   # Текст на акценте
    
    # Акценты
    ACCENT_FG = "#2f81f7"        # Синий акцент
    ACCENT_EMPHASIS = "#1f6feb"  # Сильный акцент
    ACCENT_MUTED = "#388bfd66"   # Приглушённый акцент
    ACCENT_SUBTLE = "#388bfd26"  # Тонкий акцент
    
    # Состояния
    SUCCESS_FG = "#3fb950"       # Успех
    SUCCESS_EMPHASIS = "#238636" # Успех сильный
    WARNING_FG = "#d29922"       # Предупреждение
    WARNING_EMPHASIS = "#9e6a03" # Предупреждение сильное
    DANGER_FG = "#f85149"        # Ошибка
    DANGER_EMPHASIS = "#da3633"  # Ошибка сильная
    
    # ============================================
    # ОКНО
    # ============================================
    WINDOW_TITLE = "Every Frame Dominator"
    WINDOW_BG = BG_INSET
    
    # Режимы окна  
    WINDOW_START_FULLSCREEN = False      # Запуск в оконном режиме
    WINDOW_AUTO_FULLSCREEN = True        # Автопереход в fullscreen после загрузки
    
    # Размеры загрузочного окна - ФИКСИРОВАННЫЕ КОМПАКТНЫЕ
    WINDOW_LOADING_WIDTH = 1200          # Фиксированная ширина загрузки
    WINDOW_LOADING_HEIGHT = 800          # Фиксированная высота загрузки  
    WINDOW_MIN_WIDTH = 800               # Минимальная ширина
    WINDOW_MIN_HEIGHT = 600              # Минимальная высота
    
    # Размеры оконного режима (если не fullscreen) 
    WINDOW_DEFAULT_WIDTH = 1400          # Размер в оконном режиме
    WINDOW_DEFAULT_HEIGHT = 900          # Размер в оконном режиме
    WINDOW_RESIZABLE = True              # Можно ли менять размер
    
    # Устаревшие (для совместимости)
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 900

    # ============================================
    # БОКОВАЯ ПАНЕЛЬ УПРАВЛЕНИЯ (слева)
    # ============================================
    CONTROL_PANEL_WIDTH = 480
    CONTROL_PANEL_HEIGHT = None
    CONTROL_PANEL_BG = BG_SUBTLE
    CONTROL_PANEL_BORDER = 1
    CONTROL_PANEL_RELIEF = tk.FLAT
    CONTROL_PANEL_PADX = 8
    CONTROL_PANEL_PADY = 8
    CONTROL_PANEL_SIDE = tk.LEFT
    CONTROL_PANEL_FILL = tk.Y
    CONTROL_PANEL_EXPAND = False

    # ============================================
    # ОСНОВНАЯ ПАНЕЛЬ (справа от боковой)
    # ============================================
    MAIN_PANEL_BG = BG_CANVAS
    MAIN_PANEL_BORDER = 1
    MAIN_PANEL_RELIEF = tk.FLAT
    MAIN_PANEL_PADX = 8
    MAIN_PANEL_PADY = 8
    MAIN_PANEL_FILL = tk.BOTH
    MAIN_PANEL_EXPAND = True

    # ============================================
    # СЕКЦИИ ВНУТРИ БОКОВОЙ ПАНЕЛИ
    # ============================================
    SECTION_WIDTH = None
    SECTION_HEIGHT = None
    SECTION3_HEIGHT = 60
    SECTION_PADX = 3
    SECTION_PADY = 3
    SECTION_BG = BG_OVERLAY
    SECTION_BORDER = 1
    SECTION_RELIEF = tk.FLAT
    SECTION_FILL = tk.X
    SECTION_EXPAND = False

    # ============================================
    # КНОПКИ
    # ============================================
    # Кнопка перезагрузки
    RELOAD_BTN_TEXT = "↻"
    RELOAD_BTN_FONT_FAMILY = "Arial"
    RELOAD_BTN_FONT_SIZE = 12
    RELOAD_BTN_WIDTH = 1
    RELOAD_BTN_HEIGHT = 1
    RELOAD_BTN_PADX = 3
    RELOAD_BTN_PADY = 3
    RELOAD_BTN_BORDER = 0
    RELOAD_BTN_RELIEF = tk.FLAT
    RELOAD_BTN_BG = BG_OVERLAY
    RELOAD_BTN_FG = FG_DEFAULT
    RELOAD_BTN_ACTIVE_BG = BORDER_DEFAULT
    RELOAD_BTN_ACTIVE_FG = FG_ON_EMPHASIS
    RELOAD_BTN_CURSOR = "hand2"

    # Кнопка сетки
    CONNECT_BTN_TEXT = "▦"
    CONNECT_BTN_FONT_FAMILY = "Arial"
    CONNECT_BTN_FONT_SIZE = 12
    CONNECT_BTN_WIDTH = 1
    CONNECT_BTN_HEIGHT = 1
    CONNECT_BTN_PADX = 3
    CONNECT_BTN_PADY = 3
    CONNECT_BTN_BORDER = 0
    CONNECT_BTN_RELIEF = tk.FLAT
    CONNECT_BTN_BG = BG_OVERLAY
    CONNECT_BTN_FG = FG_DEFAULT
    CONNECT_BTN_ACTIVE_BG = BORDER_DEFAULT
    CONNECT_BTN_ACTIVE_FG = FG_ON_EMPHASIS
    CONNECT_BTN_CURSOR = "hand2"

    # Кнопка второй сетки
    GRID2_BTN_TEXT = "▣"
    GRID2_BTN_FONT_FAMILY = "Arial"
    GRID2_BTN_FONT_SIZE = 12
    GRID2_BTN_WIDTH = 1
    GRID2_BTN_HEIGHT = 1
    GRID2_BTN_PADX = 3
    GRID2_BTN_PADY = 3
    GRID2_BTN_BORDER = 0
    GRID2_BTN_RELIEF = tk.FLAT
    GRID2_BTN_BG = BG_OVERLAY
    GRID2_BTN_FG = FG_DEFAULT
    GRID2_BTN_ACTIVE_BG = BORDER_DEFAULT
    GRID2_BTN_ACTIVE_FG = FG_ON_EMPHASIS
    GRID2_BTN_CURSOR = "hand2"

    # ============================================
    # НАСТРОЙКИ СЕТОК
    # ============================================
    GRID_SIZE = 10
    GRID_COLOR = BORDER_MUTED
    GRID2_SIZE = 50
    GRID2_COLOR = BORDER_DEFAULT

    # ============================================
    # НАСТРОЙКИ ВЫДЕЛЕНИЯ
    # ============================================
    SELECTION_COLOR = ACCENT_FG
    SELECTION_WIDTH = 2

    # ============================================
    # ИНФОРМАЦИОННАЯ ПАНЕЛЬ
    # ============================================
    INFO_FONT_SIZE = 10
    INFO_BG = BG_INSET
    INFO_FG = SUCCESS_FG
    INFO_FRAME_BG = BG_OVERLAY
    INFO_FRAME_BORDER = 1
    INFO_FRAME_RELIEF = tk.FLAT
    INFO_FRAME_PADX = 5
    INFO_FRAME_PADY = 5
    INFO_LABEL_FONT_SIZE = 8
    INFO_LABEL_FG = FG_MUTED
    INFO_LABEL_BG = BG_OVERLAY

    # ============================================
    # НИЖНЯЯ ПАНЕЛЬ
    # ============================================
    BOTTOM_PANEL_WIDTH = None
    BOTTOM_PANEL_HEIGHT = 36
    BOTTOM_PANEL_BG = BG_SUBTLE
    BOTTOM_PANEL_BORDER = 1
    BOTTOM_PANEL_RELIEF = tk.FLAT
    BOTTOM_PANEL_PADX = 0
    BOTTOM_PANEL_PADY = 4
    BOTTOM_PANEL_SIDE = tk.BOTTOM
    BOTTOM_PANEL_FILL = tk.X
    BOTTOM_PANEL_EXPAND = False

    # ============================================
    # РАБОЧАЯ ЗОНА (холст)
    # ============================================
    WORK_ZONE_DEFAULT_WIDTH = 800
    WORK_ZONE_DEFAULT_HEIGHT = 600
    WORK_ZONE_MIN_SIZE = 100
    WORK_ZONE_MAX_SIZE = 5000
    WORK_ZONE_COLOR = BG_INSET
    CANVAS_BG = BG_CANVAS
