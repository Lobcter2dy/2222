# -*- coding: utf-8 -*-
"""
Экран авторизации с эффектом glassmorphism
"""
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import secrets
import json
import os
import uuid
from datetime import datetime


class AuthScreen:
    """Экран авторизации при запуске"""
    
    # Цвета GitHub Dark + Glassmorphism
    COLOR_BG = '#0d1117'
    COLOR_GLASS = '#161b22'
    COLOR_GLASS_BORDER = '#30363d'
    COLOR_TEXT = '#e6edf3'
    COLOR_TEXT_MUTED = '#8b949e'
    COLOR_ACCENT = '#238636'
    COLOR_ACCENT_HOVER = '#2ea043'
    COLOR_LINK = '#58a6ff'
    COLOR_ERROR = '#f85149'
    COLOR_GOOGLE = '#4285f4'
    COLOR_GITHUB = '#6e40c9'
    
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.json')
        self.current_user = None
        
        # Настройка окна перед авторизацией
        self._setup_window()
        
        # Загрузка пользователей
        self.users = self._load_users()
        
        # Создание интерфейса
        self._create_ui()
    
    def _setup_window(self):
        """Настраивает размер окна для экрана авторизации - ОКОННЫЙ РЕЖИМ"""
        # Минимальный размер
        self.root.minsize(1000, 700)
        
        # Фиксированный размер окна для авторизации (НЕ полноэкранный)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # ФИКСИРОВАННЫЙ компактный размер - НЕ зависит от размера экрана
        win_w = 1000  # Фиксированная ширина
        win_h = 700   # Фиксированная высота
        
        # НЕ масштабируем под экран - всегда одинаковый размер!
        
        # Центрирование
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        # Убираем полноэкранный режим если был
        try:
            self.root.state('normal')
            self.root.attributes('-fullscreen', False)
        except tk.TclError:
            pass
        
        # Обновляем чтобы получить размеры
        self.root.update_idletasks()
    
    def _load_users(self):
        """Загружает пользователей из файла"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"[Auth] Ошибка загрузки пользователей: {e}")
        return {}
    
    def _save_users(self):
        """Сохраняет пользователей в файл"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password, salt=None):
        """
        Хеширует пароль с использованием PBKDF2-HMAC-SHA256.
        
        Args:
            password: Пароль для хеширования
            salt: Соль (если None - генерируется новая)
            
        Returns:
            str: Хеш в формате "salt$hash"
        """
        if salt is None:
            salt = secrets.token_hex(32)  # 256-bit соль
            
        # PBKDF2 с 310000 итерациями (рекомендация OWASP 2023)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=310000,
            dklen=64
        )
        hash_hex = hash_bytes.hex()
        
        return f"{salt}${hash_hex}"
    
    def _verify_password(self, password, stored_hash):
        """
        Проверяет пароль по сохранённому хешу.
        
        Args:
            password: Проверяемый пароль
            stored_hash: Сохранённый хеш в формате "salt$hash"
            
        Returns:
            bool: True если пароль верный
        """
        try:
            # Проверка старого формата (SHA256 без соли)
            if '$' not in stored_hash:
                # Миграция: если старый хеш - проверяем SHA256
                old_hash = hashlib.sha256(password.encode()).hexdigest()
                return secrets.compare_digest(old_hash, stored_hash)
            
            # Новый формат с солью
            salt, expected_hash = stored_hash.split('$', 1)
            
            hash_bytes = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations=310000,
                dklen=64
            )
            actual_hash = hash_bytes.hex()
            
            # Используем compare_digest для защиты от timing attack
            return secrets.compare_digest(actual_hash, expected_hash)
            
        except (ValueError, AttributeError):
            return False
    
    def _migrate_password_hash(self, username, password):
        """
        Мигрирует старый хеш пароля на новый формат.
        Вызывается после успешной проверки старого хеша.
        """
        if username in self.users:
            stored = self.users[username].get('password', '')
            # Если старый формат - обновляем
            if '$' not in stored:
                new_hash = self._hash_password(password)
                self.users[username]['password'] = new_hash
                self._save_users()
    
    def _create_ui(self):
        """Создаёт интерфейс авторизации"""
        # Полноэкранный контейнер
        self.container = tk.Frame(self.root, bg=self.COLOR_BG)
        self.container.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Фоновый градиент (имитация)
        self._create_background()
        
        # Центральная стеклянная панель
        self._create_glass_panel()
    
    def _create_background(self):
        """Создаёт фон с градиентным эффектом"""
        # Canvas для фона
        self.bg_canvas = tk.Canvas(self.container, bg=self.COLOR_BG, 
                                   highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Получаем размеры окна
        self.root.update_idletasks()
        w = self.root.winfo_width() or 1200
        h = self.root.winfo_height() or 800
        
        # Градиентные пятна (имитация blur)
        # Синее пятно слева вверху
        self.bg_canvas.create_oval(w*0.0, h*-0.1, w*0.5, h*0.5, 
                                   fill='#0c2d48', outline='')
        self.bg_canvas.create_oval(w*0.05, h*0.0, w*0.45, h*0.4, 
                                   fill='#0f3d5c', outline='')
        
        # Фиолетовое пятно справа
        self.bg_canvas.create_oval(w*0.5, h*0.3, w*1.1, h*1.0, 
                                   fill='#1a0f2e', outline='')
        self.bg_canvas.create_oval(w*0.55, h*0.35, w*1.0, h*0.95, 
                                   fill='#2d1a4a', outline='')
        
        # Тёмно-синее пятно внизу
        self.bg_canvas.create_oval(w*0.1, h*0.5, w*0.6, h*1.2, 
                                   fill='#0a1929', outline='')
        
        # Зелёный акцент (маленький)
        self.bg_canvas.create_oval(w*0.7, h*0.1, w*0.9, h*0.25, 
                                   fill='#0d2818', outline='')
    
    def _create_glass_panel(self):
        """Создаёт стеклянную панель с эффектом glassmorphism"""
        # Внешняя тень (размытие) - мягче
        self.glass_shadow = tk.Frame(self.container, bg='#080a0e')
        self.glass_shadow.place(relx=0.503, rely=0.506, anchor='center', 
                                width=504, height=624)
        
        # Второй слой размытия
        self.glass_blur = tk.Frame(self.container, bg='#0c0f14')
        self.glass_blur.place(relx=0.502, rely=0.503, anchor='center', 
                              width=500, height=620)
        
        # Внешняя рамка - тонкая граница
        self.glass_outer = tk.Frame(self.container, bg='#21262d')
        self.glass_outer.place(relx=0.5, rely=0.5, anchor='center', 
                               width=496, height=616)
        
        # Внутренняя стеклянная панель - ПОЛУПРОЗРАЧНАЯ
        # Имитация прозрачности через смешанный цвет
        glass_bg = '#0d1117'  # Очень тёмный, почти прозрачный
        self.glass_panel = tk.Frame(self.glass_outer, bg=glass_bg)
        self.glass_panel.place(relx=0.5, rely=0.5, anchor='center',
                               width=492, height=612)
        
        # Внутренняя подсветка сверху (имитация стекла)
        highlight = tk.Frame(self.glass_panel, bg='#161b22', height=1)
        highlight.pack(fill=tk.X)
        
        # Заголовок - минималистичный
        header = tk.Frame(self.glass_panel, bg=glass_bg)
        header.pack(fill=tk.X, padx=40, pady=(35, 15))
        
        # Только иконка и подзаголовок
        tk.Label(header, text="◆ Every Frame Dominator", font=("Arial", 16, "bold"),
                bg=glass_bg, fg=self.COLOR_TEXT).pack()
        tk.Label(header, text="Войдите для продолжения",
                font=("Arial", 10), bg=glass_bg, 
                fg=self.COLOR_TEXT_MUTED).pack(pady=(8, 0))
        
        # Контейнер для форм
        self.form_container = tk.Frame(self.glass_panel, bg=glass_bg)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Показываем форму входа
        self._show_login_form()
    
    def _clear_form(self):
        """Очищает контейнер формы"""
        for widget in self.form_container.winfo_children():
            widget.destroy()
    
    def _show_login_form(self):
        """Показывает форму входа"""
        self._clear_form()
        
        glass_bg = '#0d1117'
        
        # Email/Username
        tk.Label(self.form_container, text="Email или имя пользователя",
                font=("Arial", 10), bg=glass_bg, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(15, 5))
        
        self.login_entry = tk.Entry(self.form_container, font=("Arial", 12),
                                    bg='#161b22', fg=self.COLOR_TEXT,
                                    insertbackground=self.COLOR_TEXT,
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground=self.COLOR_GLASS_BORDER,
                                    highlightcolor=self.COLOR_ACCENT)
        self.login_entry.pack(fill=tk.X, ipady=10)
        
        # Пароль
        tk.Label(self.form_container, text="Пароль",
                font=("Arial", 10), bg=glass_bg, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(18, 5))
        
        pass_frame = tk.Frame(self.form_container, bg=glass_bg)
        pass_frame.pack(fill=tk.X)
        
        self.password_entry = tk.Entry(pass_frame, font=("Arial", 12),
                                       bg='#161b22', fg=self.COLOR_TEXT,
                                       insertbackground=self.COLOR_TEXT,
                                       relief=tk.FLAT, highlightthickness=1,
                                       highlightbackground=self.COLOR_GLASS_BORDER,
                                       highlightcolor=self.COLOR_ACCENT,
                                       show='●')
        self.password_entry.pack(fill=tk.X, ipady=10, side=tk.LEFT, expand=True)
        
        # Кнопка показать/скрыть пароль
        self.show_pass = tk.BooleanVar(value=False)
        show_btn = tk.Button(pass_frame, text="👁", font=("Arial", 11),
                            bg='#161b22', fg=self.COLOR_TEXT_MUTED,
                            relief=tk.FLAT, cursor="hand2",
                            command=self._toggle_password)
        show_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Забыли пароль?
        forgot = tk.Label(self.form_container, text="Забыли пароль?",
                         font=("Arial", 9), bg=glass_bg,
                         fg=self.COLOR_LINK, cursor="hand2")
        forgot.pack(anchor='e', pady=(10, 0))
        forgot.bind('<Button-1>', lambda e: self._show_reset_form())
        
        # Сообщение об ошибке
        self.error_label = tk.Label(self.form_container, text="",
                                   font=("Arial", 9), bg=glass_bg,
                                   fg=self.COLOR_ERROR)
        self.error_label.pack(pady=(10, 0))
        
        # Кнопка входа
        login_btn = tk.Button(self.form_container, text="Войти",
                             font=("Arial", 12, "bold"),
                             bg=self.COLOR_ACCENT, fg='#ffffff',
                             activebackground=self.COLOR_ACCENT_HOVER,
                             relief=tk.FLAT, cursor="hand2",
                             command=self._do_login)
        login_btn.pack(fill=tk.X, ipady=12, pady=(18, 0))
        
        # Разделитель
        sep_frame = tk.Frame(self.form_container, bg=glass_bg)
        sep_frame.pack(fill=tk.X, pady=25)
        tk.Frame(sep_frame, bg=self.COLOR_GLASS_BORDER, height=1).pack(fill=tk.X, side=tk.LEFT, expand=True)
        tk.Label(sep_frame, text=" быстрый вход ", font=("Arial", 9),
                bg=glass_bg, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT, padx=10)
        tk.Frame(sep_frame, bg=self.COLOR_GLASS_BORDER, height=1).pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # OAuth кнопки - ВЕРТИКАЛЬНО для большего пространства
        oauth_frame = tk.Frame(self.form_container, bg=glass_bg)
        oauth_frame.pack(fill=tk.X)
        
        # Google - полная ширина
        google_btn = tk.Button(oauth_frame, text="🔵  Продолжить с Google",
                              font=("Arial", 11),
                              bg='#21262d', fg=self.COLOR_TEXT,
                              activebackground='#30363d',
                              relief=tk.FLAT, cursor="hand2",
                              command=self._login_google)
        google_btn.pack(fill=tk.X, ipady=10)
        
        # GitHub - полная ширина
        github_btn = tk.Button(oauth_frame, text="⚫  Продолжить с GitHub",
                              font=("Arial", 11),
                              bg='#21262d', fg=self.COLOR_TEXT,
                              activebackground='#30363d',
                              relief=tk.FLAT, cursor="hand2",
                              command=self._login_github)
        github_btn.pack(fill=tk.X, ipady=10, pady=(8, 0))
        
        # Ссылка на регистрацию
        reg_frame = tk.Frame(self.form_container, bg=glass_bg)
        reg_frame.pack(pady=(25, 0))
        tk.Label(reg_frame, text="Нет аккаунта?", font=("Arial", 10),
                bg=glass_bg, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT)
        reg_link = tk.Label(reg_frame, text=" Создать", font=("Arial", 10, "bold"),
                           bg=glass_bg, fg=self.COLOR_LINK, cursor="hand2")
        reg_link.pack(side=tk.LEFT)
        reg_link.bind('<Button-1>', lambda e: self._show_register_form())
        
        # Привязка Enter
        self.login_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self._do_login())
        
        self.login_entry.focus()
    
    def _show_register_form(self):
        """Показывает форму регистрации"""
        self._clear_form()
        
        # Имя пользователя
        tk.Label(self.form_container, text="Имя пользователя",
                font=("Arial", 10), bg=self.COLOR_GLASS, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(10, 5))
        
        self.reg_username = tk.Entry(self.form_container, font=("Arial", 11),
                                     bg='#0d1117', fg=self.COLOR_TEXT,
                                     insertbackground=self.COLOR_TEXT,
                                     relief=tk.FLAT, highlightthickness=1,
                                     highlightbackground=self.COLOR_GLASS_BORDER,
                                     highlightcolor=self.COLOR_ACCENT)
        self.reg_username.pack(fill=tk.X, ipady=8)
        
        # Email
        tk.Label(self.form_container, text="Email",
                font=("Arial", 10), bg=self.COLOR_GLASS, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(12, 5))
        
        self.reg_email = tk.Entry(self.form_container, font=("Arial", 11),
                                  bg='#0d1117', fg=self.COLOR_TEXT,
                                  insertbackground=self.COLOR_TEXT,
                                  relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground=self.COLOR_GLASS_BORDER,
                                  highlightcolor=self.COLOR_ACCENT)
        self.reg_email.pack(fill=tk.X, ipady=8)
        
        # Пароль
        tk.Label(self.form_container, text="Пароль",
                font=("Arial", 10), bg=self.COLOR_GLASS, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(12, 5))
        
        self.reg_password = tk.Entry(self.form_container, font=("Arial", 11),
                                     bg='#0d1117', fg=self.COLOR_TEXT,
                                     insertbackground=self.COLOR_TEXT,
                                     relief=tk.FLAT, highlightthickness=1,
                                     highlightbackground=self.COLOR_GLASS_BORDER,
                                     highlightcolor=self.COLOR_ACCENT,
                                     show='●')
        self.reg_password.pack(fill=tk.X, ipady=8)
        
        # Подтверждение пароля
        tk.Label(self.form_container, text="Подтвердите пароль",
                font=("Arial", 10), bg=self.COLOR_GLASS, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(12, 5))
        
        self.reg_confirm = tk.Entry(self.form_container, font=("Arial", 11),
                                    bg='#0d1117', fg=self.COLOR_TEXT,
                                    insertbackground=self.COLOR_TEXT,
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground=self.COLOR_GLASS_BORDER,
                                    highlightcolor=self.COLOR_ACCENT,
                                    show='●')
        self.reg_confirm.pack(fill=tk.X, ipady=8)
        
        # Сообщение об ошибке
        self.error_label = tk.Label(self.form_container, text="",
                                   font=("Arial", 9), bg=self.COLOR_GLASS,
                                   fg=self.COLOR_ERROR)
        self.error_label.pack(pady=(10, 0))
        
        # Кнопка регистрации
        reg_btn = tk.Button(self.form_container, text="Создать аккаунт",
                           font=("Arial", 11, "bold"),
                           bg=self.COLOR_ACCENT, fg='#ffffff',
                           activebackground=self.COLOR_ACCENT_HOVER,
                           relief=tk.FLAT, cursor="hand2",
                           command=self._do_register)
        reg_btn.pack(fill=tk.X, ipady=10, pady=(15, 0))
        
        # Разделитель
        sep_frame = tk.Frame(self.form_container, bg=self.COLOR_GLASS)
        sep_frame.pack(fill=tk.X, pady=15)
        tk.Frame(sep_frame, bg=self.COLOR_GLASS_BORDER, height=1).pack(fill=tk.X, side=tk.LEFT, expand=True)
        tk.Label(sep_frame, text=" или ", font=("Arial", 9),
                bg=self.COLOR_GLASS, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT)
        tk.Frame(sep_frame, bg=self.COLOR_GLASS_BORDER, height=1).pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # OAuth кнопки
        oauth_frame = tk.Frame(self.form_container, bg=self.COLOR_GLASS)
        oauth_frame.pack(fill=tk.X)
        
        google_btn = tk.Button(oauth_frame, text="⬡ Google",
                              font=("Arial", 10),
                              bg='#21262d', fg=self.COLOR_TEXT,
                              activebackground='#30363d',
                              relief=tk.FLAT, cursor="hand2",
                              command=self._login_google)
        google_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
        
        github_btn = tk.Button(oauth_frame, text="⬢ GitHub",
                              font=("Arial", 10),
                              bg='#21262d', fg=self.COLOR_TEXT,
                              activebackground='#30363d',
                              relief=tk.FLAT, cursor="hand2",
                              command=self._login_github)
        github_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(5, 0))
        
        # Ссылка на вход
        login_frame = tk.Frame(self.form_container, bg=self.COLOR_GLASS)
        login_frame.pack(pady=(15, 0))
        tk.Label(login_frame, text="Уже есть аккаунт?", font=("Arial", 9),
                bg=self.COLOR_GLASS, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT)
        login_link = tk.Label(login_frame, text=" Войти", font=("Arial", 9, "bold"),
                             bg=self.COLOR_GLASS, fg=self.COLOR_LINK, cursor="hand2")
        login_link.pack(side=tk.LEFT)
        login_link.bind('<Button-1>', lambda e: self._show_login_form())
        
        self.reg_username.focus()
    
    def _show_reset_form(self):
        """Показывает форму сброса пароля"""
        self._clear_form()
        
        tk.Label(self.form_container, text="Сброс пароля",
                font=("Arial", 14, "bold"), bg=self.COLOR_GLASS,
                fg=self.COLOR_TEXT).pack(pady=(20, 10))
        
        tk.Label(self.form_container, text="Введите email для получения\nинструкций по сбросу пароля",
                font=("Arial", 10), bg=self.COLOR_GLASS,
                fg=self.COLOR_TEXT_MUTED).pack(pady=(0, 20))
        
        # Email
        tk.Label(self.form_container, text="Email",
                font=("Arial", 10), bg=self.COLOR_GLASS, 
                fg=self.COLOR_TEXT).pack(anchor='w', pady=(10, 5))
        
        self.reset_email = tk.Entry(self.form_container, font=("Arial", 11),
                                    bg='#0d1117', fg=self.COLOR_TEXT,
                                    insertbackground=self.COLOR_TEXT,
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground=self.COLOR_GLASS_BORDER,
                                    highlightcolor=self.COLOR_ACCENT)
        self.reset_email.pack(fill=tk.X, ipady=8)
        
        # Сообщение
        self.error_label = tk.Label(self.form_container, text="",
                                   font=("Arial", 9), bg=self.COLOR_GLASS,
                                   fg=self.COLOR_ERROR)
        self.error_label.pack(pady=(10, 0))
        
        # Кнопка сброса
        reset_btn = tk.Button(self.form_container, text="Отправить",
                             font=("Arial", 11, "bold"),
                             bg=self.COLOR_ACCENT, fg='#ffffff',
                             activebackground=self.COLOR_ACCENT_HOVER,
                             relief=tk.FLAT, cursor="hand2",
                             command=self._do_reset)
        reset_btn.pack(fill=tk.X, ipady=10, pady=(20, 0))
        
        # Назад
        back_link = tk.Label(self.form_container, text="← Вернуться к входу",
                            font=("Arial", 9), bg=self.COLOR_GLASS,
                            fg=self.COLOR_LINK, cursor="hand2")
        back_link.pack(pady=(20, 0))
        back_link.bind('<Button-1>', lambda e: self._show_login_form())
        
        self.reset_email.focus()
    
    def _toggle_password(self):
        """Переключает видимость пароля"""
        current = self.password_entry.cget('show')
        self.password_entry.config(show='' if current else '●')
    
    def _do_login(self):
        """Выполняет вход - ПОКА ПРОПУСКАЕТ ВСЕГДА"""
        login = self.login_entry.get().strip() or 'User'
        
        # Режим разработки - сразу пропускаем
        self.current_user = {'username': login, 'id': 'dev_user', 'email': ''}
        self._login_success()
    
    def _do_register(self):
        """Выполняет регистрацию"""
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        # Валидация
        if not username or not email or not password:
            self.error_label.config(text="Заполните все поля")
            return
        
        if len(username) < 3:
            self.error_label.config(text="Имя пользователя минимум 3 символа")
            return
        
        if '@' not in email or '.' not in email:
            self.error_label.config(text="Некорректный email")
            return
        
        if len(password) < 6:
            self.error_label.config(text="Пароль минимум 6 символов")
            return
        
        if password != confirm:
            self.error_label.config(text="Пароли не совпадают")
            return
        
        # Проверка уникальности
        for user_data in self.users.values():
            if user_data.get('username') == username:
                self.error_label.config(text="Имя пользователя занято")
                return
            if user_data.get('email') == email:
                self.error_label.config(text="Email уже зарегистрирован")
                return
        
        # Создание пользователя
        user_id = str(uuid.uuid4())[:8]
        self.users[user_id] = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'oauth_provider': None
        }
        
        self._save_users()
        
        # Автовход после регистрации
        self.current_user = self.users[user_id]
        self._login_success()
    
    def _do_reset(self):
        """Отправляет запрос на сброс пароля"""
        email = self.reset_email.get().strip()
        
        if not email or '@' not in email:
            self.error_label.config(text="Введите корректный email")
            return
        
        # Имитация отправки
        self.error_label.config(text="", fg=self.COLOR_ACCENT)
        messagebox.showinfo("Сброс пароля", 
                           f"Инструкции отправлены на {email}\n(в демо-режиме не работает)")
        self._show_login_form()
    
    def _login_google(self):
        """Быстрый вход через Google - сразу пропускает"""
        user_id = f"google_{uuid.uuid4().hex[:6]}"
        self.current_user = {
            'id': user_id,
            'username': 'Google User',
            'email': f'{user_id}@gmail.com',
            'oauth_provider': 'google'
        }
        self._login_success()
    
    def _login_github(self):
        """Быстрый вход через GitHub - сразу пропускает"""
        user_id = f"github_{uuid.uuid4().hex[:6]}"
        self.current_user = {
            'id': user_id,
            'username': 'GitHub User',
            'email': f'{user_id}@github.com',
            'oauth_provider': 'github'
        }
        self._login_success()
    
    def _login_success(self):
        """Успешный вход - сразу переходим к загрузке без анимации"""
        # Сразу уничтожаем экран авторизации
        self.container.destroy()
        # Вызываем callback
        if self.on_success:
            self.on_success(self.current_user)
    
    def show(self):
        """Показывает экран авторизации"""
        self.container.lift()
    
    def get_current_user(self):
        """Возвращает текущего пользователя"""
        return self.current_user

