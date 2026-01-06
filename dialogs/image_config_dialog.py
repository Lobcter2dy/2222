#!/usr/bin/env python3
"""
Диалоговое окно настройки изображения
Позволяет загрузить изображение и настроить отображение
"""
import tkinter as tk
from tkinter import ttk, filedialog
import os


class ImageConfigDialog:
    """Диалог настройки изображения"""

    def __init__(self, parent, image_element):
        """
        Args:
            parent: родительское окно
            image_element: элемент изображения для настройки
        """
        self.image_element = image_element
        self.result = None
        
        # КОМПАКТНЫЙ диалог с НОРМАЛЬНЫМИ размерами
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка изображения")
        self.dialog.geometry("400x300")  # КОМПАКТНЫЙ размер
        self.dialog.resizable(False, False)  # ФИКСИРОВАННЫЙ размер
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.configure(bg="#2a2a2a")
        
        # АВТОЗАКРЫТИЕ при клике вне
        self._setup_auto_close(parent)
        
        self._build_ui()
        
        # Ждём закрытия
        self.dialog.wait_window()

    def _setup_auto_close(self, parent):
        """Настраивает автозакрытие при клике вне диалога"""
        def on_click_outside(event):
            # Получаем координаты диалога
            dialog_x = self.dialog.winfo_x()
            dialog_y = self.dialog.winfo_y()
            dialog_w = self.dialog.winfo_width()
            dialog_h = self.dialog.winfo_height()
            
            # Координаты клика
            click_x = event.x_root
            click_y = event.y_root
            
            # Если клик вне диалога - закрываем
            if not (dialog_x <= click_x <= dialog_x + dialog_w and
                    dialog_y <= click_y <= dialog_y + dialog_h):
                self._on_cancel()
        
        # Привязываем к родительскому окну
        parent.bind('<Button-1>', on_click_outside, add=True)
        
        # ESC для закрытия
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        self.dialog.focus_set()

    def _build_ui(self):
        """Создаёт КОМПАКТНЫЙ интерфейс диалога"""
        main_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title = tk.Label(
            main_frame,
            text="🖼 Изображение",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        )
        title.pack(pady=(0, 15))
        
        # === Секция: Загрузка файла ===
        file_frame = tk.LabelFrame(
            main_frame,
            text="  Изображение  ",
            font=("Arial", 11, "bold"),
            bg="#2a2a2a",
            fg="#ffffff",
            relief=tk.FLAT,
            borderwidth=1
        )
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Контейнер для загрузки
        load_frame = tk.Frame(file_frame, bg="#2a2a2a")
        load_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # НОРМАЛЬНАЯ кнопка загрузки
        browse_btn = tk.Button(
            load_frame,
            text="📁 Выбрать файл",
            font=("Arial", 10),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#106ebe",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self._browse_file
        )
        browse_btn.pack(pady=5)
        
        # Путь к файлу
        path_frame = tk.Frame(load_frame, bg="#2a2a2a")
        path_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(path_frame, text="Файл:", font=("Arial", 10), 
                bg="#2a2a2a", fg="#cccccc").pack(anchor=tk.W)
        
        self.path_var = tk.StringVar(
            value=self.image_element.properties.get('image_path', 'Файл не выбран')
        )
        self.path_entry = tk.Entry(
            path_frame,
            textvariable=self.path_var,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            state=tk.DISABLED  # Только для отображения
        )
        self.path_entry.pack(fill=tk.X, ipady=6, pady=2)
        
        # Кнопка очистки
        clear_btn = tk.Button(
            load_frame,
            text="✕ Убрать",
            font=("Arial", 9),
            bg="#da3633",
            fg="#ffffff",
            activebackground="#e14845",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._clear_path
        )
        clear_btn.pack(pady=3)
        
        # Информация о файле
        self.info_label = tk.Label(
            file_frame,
            text="",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#888888",
            wraplength=400
        )
        self.info_label.pack(fill=tk.X, pady=10)
        self._update_file_info()
        
        # === Режим отображения ===
        fit_frame = tk.LabelFrame(
            main_frame,
            text="  Режим отображения  ",
            font=("Arial", 11, "bold"),
            bg="#2a2a2a",
            fg="#ffffff",
            relief=tk.FLAT,
            borderwidth=1
        )
        fit_frame.pack(fill=tk.X, pady=(0, 15))
        
        fit_options_frame = tk.Frame(fit_frame, bg="#2a2a2a")
        fit_options_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.fit_var = tk.StringVar(
            value=self.image_element.properties.get('image_fit', 'contain')
        )
        
        fit_modes = [
            ('contain', 'Вписать'),
            ('cover', 'Покрыть'),
            ('stretch', 'Растянуть'),
            ('original', 'Оригинал'),
        ]
        
        for mode, label in fit_modes:
            rb = tk.Radiobutton(
                fit_frame,
                text=label,
                variable=self.fit_var,
                value=mode,
                font=("Arial", 10),
                bg="#2a2a2a",
                fg="#cccccc",
                activebackground="#2a2a2a",
                activeforeground="#ffffff",
                selectcolor="#4a4a4a",
                highlightthickness=0
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Описание режимов
        fit_desc = tk.Label(
            fit_section,
            text="Вписать — сохранить пропорции внутри области\n"
                 "Покрыть — заполнить всю область (с обрезкой)\n"
                 "Растянуть — заполнить без сохранения пропорций\n"
                 "Оригинал — без масштабирования",
            font=("Arial", 8),
            bg="#2a2a2a",
            fg="#666666",
            justify=tk.LEFT
        )
        fit_desc.pack(pady=(0, 10), padx=10, anchor="w")
        
        # Кнопки OK/Отмена
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(pady=15)
        
        ok_btn = tk.Button(
            btn_frame,
            text="Применить",
            font=("Arial", 11),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_ok
        )
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Привязка клавиш
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())

    def _browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [
            ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("GIF", "*.gif"),
            ("BMP", "*.bmp"),
            ("WebP", "*.webp"),
            ("Все файлы", "*.*")
        ]
        
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=filetypes
        )
        
        if path:
            self.path_var.set(path)
            self._update_file_info()

    def _clear_path(self):
        """Очищает путь к файлу"""
        self.path_var.set('')
        self._update_file_info()

    def _update_file_info(self):
        """Обновляет информацию о файле"""
        path = self.path_var.get()
        
        if not path:
            self.info_label.config(text="Файл не выбран")
            return
        
        if not os.path.exists(path):
            self.info_label.config(text="⚠ Файл не найден", fg="#ff6666")
            return
        
        try:
            # Получаем размер файла
            size = os.path.getsize(path)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            # Пробуем получить размеры изображения
            try:
                from PIL import Image
                with Image.open(path) as img:
                    w, h = img.size
                    self.info_label.config(
                        text=f"✓ {w}×{h} px | {size_str}",
                        fg="#88ff88"
                    )
            except (IOError, OSError, ImportError):
                self.info_label.config(
                    text=f"✓ {size_str}",
                    fg="#88ff88"
                )
        except Exception as e:
            self.info_label.config(text=f"Ошибка: {e}", fg="#ff6666")

    def _on_ok(self):
        """Применяет настройки"""
        path = self.path_var.get()
        fit_mode = self.fit_var.get()
        
        # Применяем к элементу
        self.image_element.properties['image_path'] = path
        self.image_element.properties['image_fit'] = fit_mode
        self.image_element._original_image = None  # Сбросить кеш
        self.image_element._display_image = None
        self.image_element.update()
        
        # Уведомляем систему о изменении
        from ..utils.event_bus import event_bus
        event_bus.emit('element.updated', {'element': self.image_element})
        
        self.result = {
            'path': path,
            'fit_mode': fit_mode
        }
        
        self.dialog.destroy()

    def _on_cancel(self):
        """Отменяет изменения"""
        self.dialog.destroy()


def show_image_config(parent, image_element):
    """Показывает диалог настройки изображения"""
    dialog = ImageConfigDialog(parent, image_element)
    return dialog.result

