"""
Loading Overlay - полупрозрачный блокирующий слой загрузки
Стиль: Glassmorphism (тёмное стекло)
"""

import tkinter as tk
from typing import Optional, Callable
import math


class LoadingOverlay:
    """Полупрозрачный оверлей загрузки с анимацией"""
    
    # Цвета темы
    COLOR_OVERLAY = '#0d1117'      # Основной фон (полупрозрачный эффект)
    COLOR_GLASS = '#161b22'        # Стеклянная панель
    COLOR_BORDER = '#30363d'       # Граница
    COLOR_TEXT = '#e6edf3'         # Текст
    COLOR_ACCENT = '#58a6ff'       # Акцент (спиннер)
    COLOR_DIM = '#8b949e'          # Приглушённый текст
    
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.container: Optional[tk.Frame] = None
        self.spinner_canvas: Optional[tk.Canvas] = None
        self.progress_var = tk.DoubleVar(value=0)
        self.status_text = tk.StringVar(value="Загрузка...")
        self.detail_text = tk.StringVar(value="")
        
        self._animation_id: Optional[str] = None
        self._spinner_angle = 0
        self._is_visible = False
        self._on_cancel: Optional[Callable] = None
        
    def show(self, message: str = "Загрузка...", 
             detail: str = "", 
             progress: Optional[float] = None,
             cancellable: bool = False,
             on_cancel: Optional[Callable] = None):
        """
        Показывает оверлей загрузки
        
        Args:
            message: Основное сообщение
            detail: Детальное описание
            progress: Прогресс 0-100 (None = бесконечный спиннер)
            cancellable: Можно ли отменить
            on_cancel: Callback при отмене
        """
        if self._is_visible:
            # Обновляем текст если уже показан
            self.status_text.set(message)
            self.detail_text.set(detail)
            if progress is not None:
                self.progress_var.set(progress)
            return
            
        self._is_visible = True
        self._on_cancel = on_cancel
        
        # Создаём контейнер поверх всего
        self.container = tk.Frame(self.parent, bg=self.COLOR_OVERLAY)
        self.container.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.container.lift()  # Поверх всего
        
        # Блокируем все события мыши
        self.container.bind('<Button-1>', lambda e: 'break')
        self.container.bind('<Button-2>', lambda e: 'break')
        self.container.bind('<Button-3>', lambda e: 'break')
        self.container.bind('<Motion>', lambda e: 'break')
        
        # Полупрозрачный фон (имитация через несколько слоёв)
        self._create_glass_background()
        
        # Центральная панель
        self._create_loading_panel(message, detail, progress, cancellable)
        
        # Запускаем анимацию спиннера
        self._animate_spinner()
        
        # Обновляем UI
        self.parent.update_idletasks()
        
    def _create_glass_background(self):
        """Создаёт фон с эффектом стекла"""
        # Основной тёмный слой
        bg = tk.Frame(self.container, bg=self.COLOR_OVERLAY)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Лёгкие градиентные пятна для глубины
        canvas = tk.Canvas(bg, bg=self.COLOR_OVERLAY, highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Обновляем чтобы получить размеры
        self.parent.update_idletasks()
        w = self.parent.winfo_width() or 1200
        h = self.parent.winfo_height() or 800
        
        # Тонкие градиентные пятна
        canvas.create_oval(w*0.1, h*0.2, w*0.4, h*0.6, 
                          fill='#0a0f14', outline='')
        canvas.create_oval(w*0.6, h*0.3, w*0.9, h*0.8, 
                          fill='#0f0a14', outline='')
                          
    def _create_loading_panel(self, message: str, detail: str, 
                              progress: Optional[float], cancellable: bool):
        """Создаёт центральную панель загрузки"""
        # Внешняя тень
        shadow = tk.Frame(self.container, bg='#000000')
        shadow.place(relx=0.502, rely=0.503, anchor='center', 
                    width=284, height=184)
        
        # Граница
        border = tk.Frame(self.container, bg=self.COLOR_BORDER)
        border.place(relx=0.5, rely=0.5, anchor='center', 
                    width=280, height=180)
        
        # Стеклянная панель
        panel = tk.Frame(border, bg=self.COLOR_GLASS)
        panel.place(relx=0.5, rely=0.5, anchor='center', 
                   width=276, height=176)
        
        # Верхний блик
        highlight = tk.Frame(panel, bg='#1f2937', height=2)
        highlight.pack(fill=tk.X)
        
        # Контент
        content = tk.Frame(panel, bg=self.COLOR_GLASS)
        content.pack(expand=True, fill=tk.BOTH, padx=20, pady=15)
        
        # Спиннер
        self.spinner_canvas = tk.Canvas(content, width=48, height=48,
                                        bg=self.COLOR_GLASS, 
                                        highlightthickness=0)
        self.spinner_canvas.pack(pady=(10, 15))
        
        # Текст статуса
        self.status_text.set(message)
        status_label = tk.Label(content, textvariable=self.status_text,
                               font=('Segoe UI', 11, 'bold'),
                               fg=self.COLOR_TEXT, bg=self.COLOR_GLASS)
        status_label.pack()
        
        # Детальный текст
        self.detail_text.set(detail)
        detail_label = tk.Label(content, textvariable=self.detail_text,
                               font=('Segoe UI', 9),
                               fg=self.COLOR_DIM, bg=self.COLOR_GLASS)
        detail_label.pack(pady=(2, 0))
        
        # Прогресс-бар (если указан прогресс)
        if progress is not None:
            self.progress_var.set(progress)
            self._create_progress_bar(content)
            
        # Кнопка отмены
        if cancellable:
            cancel_btn = tk.Button(content, text="Отмена",
                                  font=('Segoe UI', 9),
                                  fg=self.COLOR_DIM, bg='#21262d',
                                  activeforeground=self.COLOR_TEXT,
                                  activebackground='#30363d',
                                  relief='flat', cursor='hand2',
                                  command=self._on_cancel_click)
            cancel_btn.pack(pady=(10, 0))
            
    def _create_progress_bar(self, parent: tk.Frame):
        """Создаёт прогресс-бар"""
        bar_frame = tk.Frame(parent, bg='#21262d', height=6)
        bar_frame.pack(fill=tk.X, pady=(10, 0))
        bar_frame.pack_propagate(False)
        
        self.progress_fill = tk.Frame(bar_frame, bg=self.COLOR_ACCENT)
        self.progress_fill.place(relx=0, rely=0, relheight=1, 
                                relwidth=self.progress_var.get()/100)
        
        # Трекинг изменений прогресса
        self.progress_var.trace_add('write', self._update_progress)
        
    def _update_progress(self, *args):
        """Обновляет прогресс-бар"""
        if hasattr(self, 'progress_fill') and self.progress_fill.winfo_exists():
            progress = max(0, min(100, self.progress_var.get()))
            self.progress_fill.place_configure(relwidth=progress/100)
            
    def _animate_spinner(self):
        """Анимация спиннера"""
        if not self._is_visible or not self.spinner_canvas:
            return
            
        try:
            if not self.spinner_canvas.winfo_exists():
                return
        except tk.TclError:
            return
            
        # Очищаем canvas
        self.spinner_canvas.delete('all')
        
        cx, cy = 24, 24  # Центр
        radius = 18
        
        # Рисуем дугу спиннера
        for i in range(12):
            angle = math.radians(self._spinner_angle + i * 30)
            x1 = cx + (radius - 4) * math.cos(angle)
            y1 = cy + (radius - 4) * math.sin(angle)
            x2 = cx + radius * math.cos(angle)
            y2 = cy + radius * math.sin(angle)
            
            # Градиент прозрачности
            alpha = int(255 * (i / 12))
            # Преобразуем в hex цвет
            intensity = int(88 + (166 - 88) * (i / 12))
            color = f'#{intensity:02x}{min(255, intensity+50):02x}ff'
            
            self.spinner_canvas.create_line(x1, y1, x2, y2, 
                                           fill=color, width=3,
                                           capstyle='round')
        
        self._spinner_angle = (self._spinner_angle + 30) % 360
        
        # Следующий кадр
        self._animation_id = self.parent.after(80, self._animate_spinner)
        
    def _on_cancel_click(self):
        """Обработчик отмены"""
        if self._on_cancel:
            self._on_cancel()
        self.hide()
        
    def update(self, message: Optional[str] = None, 
               detail: Optional[str] = None,
               progress: Optional[float] = None):
        """Обновляет состояние загрузки"""
        if message is not None:
            self.status_text.set(message)
        if detail is not None:
            self.detail_text.set(detail)
        if progress is not None:
            self.progress_var.set(progress)
        self.parent.update_idletasks()
        
    def hide(self):
        """Скрывает оверлей"""
        self._is_visible = False
        
        # Останавливаем анимацию
        if self._animation_id:
            try:
                self.parent.after_cancel(self._animation_id)
            except tk.TclError:
                pass  # Parent destroyed
            self._animation_id = None
            
        # Удаляем контейнер
        if self.container:
            try:
                self.container.destroy()
            except tk.TclError:
                pass  # Already destroyed
            self.container = None
            
        self.spinner_canvas = None
        
    @property
    def is_visible(self) -> bool:
        return self._is_visible


class LoadingContext:
    """Контекстный менеджер для загрузки"""
    
    def __init__(self, overlay: LoadingOverlay, 
                 message: str = "Загрузка...",
                 detail: str = ""):
        self.overlay = overlay
        self.message = message
        self.detail = detail
        
    def __enter__(self):
        self.overlay.show(self.message, self.detail)
        return self.overlay
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.overlay.hide()
        return False

