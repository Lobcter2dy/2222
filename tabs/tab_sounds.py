#!/usr/bin/env python3
"""
Вкладка звуков - управление звуковыми эффектами для UI
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from pathlib import Path

from .tab_base import TabBase


class SoundManager:
    """Менеджер звуков для воспроизведения и управления"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.sounds = {}  # id -> {path, name, volume, category}
        self.bindings = {}  # element_id -> {event: sound_id}
        self._pygame_available = False
        self._sounds_dir = None
        
        # Пытаемся импортировать pygame для воспроизведения звуков
        try:
            import pygame
            pygame.mixer.init()
            self._pygame_available = True
        except ImportError:
            print("[SoundManager] pygame не установлен - звуки недоступны")
        except Exception as e:
            print(f"[SoundManager] Ошибка инициализации pygame: {e}")
        
        # Создаём папку для звуков
        self._setup_sounds_dir()
        self._load_sounds_config()
    
    def _setup_sounds_dir(self):
        """Создаёт папку для звуков"""
        base_dir = Path(__file__).parent.parent.parent
        self._sounds_dir = base_dir / "sounds"
        self._sounds_dir.mkdir(exist_ok=True)
        
        # Создаём подпапки для категорий
        for cat in ["ui", "effects", "alerts", "custom"]:
            (self._sounds_dir / cat).mkdir(exist_ok=True)
    
    def _load_sounds_config(self):
        """Загружает конфигурацию звуков"""
        config_path = self._sounds_dir / "sounds_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sounds = data.get('sounds', {})
                    self.bindings = data.get('bindings', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"[SoundManager] Ошибка загрузки конфига: {e}")
    
    def _save_sounds_config(self):
        """Сохраняет конфигурацию звуков"""
        config_path = self._sounds_dir / "sounds_config.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'sounds': self.sounds,
                    'bindings': self.bindings
                }, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[SoundManager] Ошибка сохранения конфига: {e}")
    
    def add_sound(self, path, name=None, category="custom", volume=1.0):
        """Добавляет звук"""
        if not os.path.exists(path):
            return None
        
        # Копируем файл в папку проекта
        filename = os.path.basename(path)
        dest_dir = self._sounds_dir / category
        dest_path = dest_dir / filename
        
        # Уникальное имя если файл уже существует
        counter = 1
        base, ext = os.path.splitext(filename)
        while dest_path.exists():
            dest_path = dest_dir / f"{base}_{counter}{ext}"
            counter += 1
        
        # Копируем файл
        import shutil
        try:
            shutil.copy2(path, dest_path)
        except IOError as e:
            print(f"[SoundManager] Ошибка копирования: {e}")
            return None
        
        # Создаём ID
        sound_id = f"snd_{len(self.sounds)}_{base}"
        
        self.sounds[sound_id] = {
            'path': str(dest_path.relative_to(self._sounds_dir)),
            'name': name or base,
            'category': category,
            'volume': volume
        }
        
        self._save_sounds_config()
        return sound_id
    
    def remove_sound(self, sound_id):
        """Удаляет звук"""
        if sound_id not in self.sounds:
            return False
        
        # Удаляем файл
        sound = self.sounds[sound_id]
        file_path = self._sounds_dir / sound['path']
        try:
            if file_path.exists():
                file_path.unlink()
        except IOError:
            pass
        
        # Удаляем из конфига
        del self.sounds[sound_id]
        
        # Удаляем привязки
        for elem_id in list(self.bindings.keys()):
            for event in list(self.bindings.get(elem_id, {}).keys()):
                if self.bindings[elem_id].get(event) == sound_id:
                    del self.bindings[elem_id][event]
        
        self._save_sounds_config()
        return True
    
    def play(self, sound_id, volume=None):
        """Воспроизводит звук"""
        if not self._pygame_available:
            return False
        
        if sound_id not in self.sounds:
            return False
        
        sound = self.sounds[sound_id]
        file_path = self._sounds_dir / sound['path']
        
        if not file_path.exists():
            return False
        
        try:
            import pygame
            snd = pygame.mixer.Sound(str(file_path))
            vol = volume if volume is not None else sound.get('volume', 1.0)
            snd.set_volume(vol)
            snd.play()
            return True
        except Exception as e:
            print(f"[SoundManager] Ошибка воспроизведения: {e}")
            return False
    
    def bind_sound(self, element_id, event, sound_id):
        """Привязывает звук к событию элемента"""
        if element_id not in self.bindings:
            self.bindings[element_id] = {}
        self.bindings[element_id][event] = sound_id
        self._save_sounds_config()
    
    def unbind_sound(self, element_id, event=None):
        """Отвязывает звук от события"""
        if element_id not in self.bindings:
            return
        if event:
            if event in self.bindings[element_id]:
                del self.bindings[element_id][event]
        else:
            del self.bindings[element_id]
        self._save_sounds_config()
    
    def get_binding(self, element_id, event):
        """Получает привязанный звук"""
        return self.bindings.get(element_id, {}).get(event)
    
    def trigger_event(self, element_id, event):
        """Запускает звук по событию"""
        sound_id = self.get_binding(element_id, event)
        if sound_id:
            self.play(sound_id)
    
    def get_all_sounds(self):
        """Возвращает все звуки"""
        return self.sounds.copy()
    
    def get_sounds_by_category(self, category):
        """Возвращает звуки по категории"""
        return {k: v for k, v in self.sounds.items() 
                if v.get('category') == category}
    
    def is_available(self):
        """Проверяет доступность звуковой системы"""
        return self._pygame_available


# Глобальный экземпляр
_sound_manager = None

def get_sound_manager():
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


class TabSounds(TabBase):
    """Вкладка управления звуками"""
    
    TAB_ID = "sounds"
    TAB_SYMBOL = "🔊"
    
    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.sound_manager = get_sound_manager()
        self.element_manager = None
        self.selected_sound_id = None
        self.vars = {}
    
    def set_element_manager(self, manager):
        """Устанавливает менеджер элементов"""
        self.element_manager = manager
    
    def _build_content(self):
        """Строит содержимое вкладки"""
        content = self._scroll_container(self.frame)
        
        # Статус pygame
        if not self.sound_manager.is_available():
            warn = tk.Frame(content, bg='#3d2a1f')
            warn.pack(fill=tk.X, padx=4, pady=4)
            tk.Label(warn, text="⚠️ pygame не установлен",
                    font=("Arial", 9), bg='#3d2a1f', fg='#f0ad4e'
                    ).pack(padx=6, pady=4)
            tk.Label(warn, text="pip install pygame",
                    font=("Consolas", 8), bg='#3d2a1f', fg='#8d96a0'
                    ).pack(padx=6, pady=(0, 4))
        
        # === Секция: Библиотека звуков ===
        sec = self._section(content, "📁 Библиотека звуков")
        
        # Кнопки управления
        btn_row = self._row(sec)
        self._button(btn_row, "+ Добавить", self._add_sound, 'primary').pack(side=tk.LEFT)
        self._button(btn_row, "▶ Играть", self._play_selected).pack(side=tk.LEFT, padx=(4, 0))
        self._button(btn_row, "✕ Удалить", self._delete_sound, 'danger').pack(side=tk.LEFT, padx=(4, 0))
        
        # Список звуков
        list_frame = tk.Frame(sec, bg=self.COLOR_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        
        self.sounds_tree = ttk.Treeview(list_frame, columns=('name', 'category'),
                                        show='headings', height=8,
                                        selectmode='browse')
        self.sounds_tree.heading('name', text='Название')
        self.sounds_tree.heading('category', text='Категория')
        self.sounds_tree.column('name', width=140)
        self.sounds_tree.column('category', width=70)
        self.sounds_tree.pack(fill=tk.BOTH, expand=True)
        self.sounds_tree.bind('<<TreeviewSelect>>', self._on_sound_select)
        self.sounds_tree.bind('<Double-1>', lambda e: self._play_selected())
        
        # === Секция: Свойства звука ===
        sec = self._section(content, "⚙️ Свойства")
        
        row = self._row(sec)
        self._label(row, "Название:").pack(side=tk.LEFT)
        self.vars['name'] = tk.StringVar()
        self._entry(row, self.vars['name'], 18).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        row = self._row(sec)
        self._label(row, "Громкость:").pack(side=tk.LEFT)
        self.vars['volume'] = tk.DoubleVar(value=1.0)
        vol_scale = ttk.Scale(row, from_=0.0, to=1.0, variable=self.vars['volume'],
                              orient=tk.HORIZONTAL, length=120)
        vol_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        row = self._row(sec)
        self._label(row, "Категория:").pack(side=tk.LEFT)
        self.vars['category'] = tk.StringVar()
        self._combo(row, ['ui', 'effects', 'alerts', 'custom'], 
                   self.vars['category'], 12).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._button(row, "💾 Сохранить", self._save_sound_props).pack(side=tk.LEFT)
        
        # === Секция: Привязка к элементам ===
        sec = self._section(content, "🔗 Привязка к элементам")
        
        row = self._row(sec)
        self._label(row, "Элемент:").pack(side=tk.LEFT)
        self.vars['bind_element'] = tk.StringVar()
        self.element_combo = ttk.Combobox(row, textvariable=self.vars['bind_element'],
                                          width=18, state='readonly')
        self.element_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._button(row, "↻", self._refresh_elements).pack(side=tk.LEFT, padx=(4, 0))
        
        row = self._row(sec)
        self._label(row, "Событие:").pack(side=tk.LEFT)
        self.vars['bind_event'] = tk.StringVar()
        self._combo(row, ['click', 'hover', 'press', 'release', 'focus', 'blur'],
                   self.vars['bind_event'], 10).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._button(row, "🔗 Привязать", self._bind_sound, 'primary').pack(side=tk.LEFT)
        self._button(row, "⛓️‍💥 Отвязать", self._unbind_sound).pack(side=tk.LEFT, padx=(4, 0))
        
        # Список привязок
        bind_frame = tk.Frame(sec, bg=self.COLOR_BG)
        bind_frame.pack(fill=tk.X, pady=(6, 0))
        
        self.bindings_tree = ttk.Treeview(bind_frame, columns=('element', 'event', 'sound'),
                                          show='headings', height=5,
                                          selectmode='browse')
        self.bindings_tree.heading('element', text='Элемент')
        self.bindings_tree.heading('event', text='Событие')
        self.bindings_tree.heading('sound', text='Звук')
        self.bindings_tree.column('element', width=80)
        self.bindings_tree.column('event', width=60)
        self.bindings_tree.column('sound', width=80)
        self.bindings_tree.pack(fill=tk.X)
        
        # === Секция: Быстрые звуки ===
        sec = self._section(content, "⚡ Быстрые звуки")
        
        row = self._row(sec)
        self._button(row, "🔔 Уведомление", lambda: self._play_quick('notification')).pack(side=tk.LEFT)
        self._button(row, "✓ Успех", lambda: self._play_quick('success')).pack(side=tk.LEFT, padx=(4, 0))
        
        row = self._row(sec)
        self._button(row, "⚠️ Ошибка", lambda: self._play_quick('error')).pack(side=tk.LEFT)
        self._button(row, "👆 Клик", lambda: self._play_quick('click')).pack(side=tk.LEFT, padx=(4, 0))
        
        # Обновляем списки
        self._refresh_sounds()
        self._refresh_elements()
        self._refresh_bindings()
    
    def _refresh_sounds(self):
        """Обновляет список звуков"""
        self.sounds_tree.delete(*self.sounds_tree.get_children())
        
        for sound_id, sound in self.sound_manager.get_all_sounds().items():
            self.sounds_tree.insert('', 'end', iid=sound_id,
                                    values=(sound['name'], sound['category']))
    
    def _refresh_elements(self):
        """Обновляет список элементов"""
        elements = []
        if self.element_manager:
            for elem in self.element_manager.get_all_elements():
                elem_id = getattr(elem, 'id', str(id(elem)))
                elem_type = getattr(elem, 'element_type', 'unknown')
                elements.append(f"{elem_type}_{elem_id[-6:]}")
        
        self.element_combo['values'] = elements
    
    def _refresh_bindings(self):
        """Обновляет список привязок"""
        self.bindings_tree.delete(*self.bindings_tree.get_children())
        
        for elem_id, events in self.sound_manager.bindings.items():
            for event, sound_id in events.items():
                sound = self.sound_manager.sounds.get(sound_id, {})
                self.bindings_tree.insert('', 'end',
                                          values=(elem_id[:12], event, sound.get('name', '?')))
    
    def _on_sound_select(self, event=None):
        """Обработчик выбора звука"""
        sel = self.sounds_tree.selection()
        if not sel:
            self.selected_sound_id = None
            return
        
        self.selected_sound_id = sel[0]
        sound = self.sound_manager.sounds.get(self.selected_sound_id, {})
        
        self.vars['name'].set(sound.get('name', ''))
        self.vars['volume'].set(sound.get('volume', 1.0))
        self.vars['category'].set(sound.get('category', 'custom'))
    
    def _add_sound(self):
        """Добавляет звук из файла"""
        filetypes = [
            ("Звуковые файлы", "*.mp3 *.wav *.ogg *.flac"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("OGG", "*.ogg"),
            ("Все файлы", "*.*")
        ]
        
        path = filedialog.askopenfilename(filetypes=filetypes)
        if not path:
            return
        
        category = self.vars['category'].get() or 'custom'
        sound_id = self.sound_manager.add_sound(path, category=category)
        
        if sound_id:
            self._refresh_sounds()
            # Выбираем добавленный
            self.sounds_tree.selection_set(sound_id)
            self._on_sound_select()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить звук")
    
    def _delete_sound(self):
        """Удаляет выбранный звук"""
        if not self.selected_sound_id:
            return
        
        if messagebox.askyesno("Удаление", "Удалить звук?"):
            self.sound_manager.remove_sound(self.selected_sound_id)
            self.selected_sound_id = None
            self._refresh_sounds()
            self._refresh_bindings()
    
    def _play_selected(self):
        """Воспроизводит выбранный звук"""
        if self.selected_sound_id:
            volume = self.vars['volume'].get()
            self.sound_manager.play(self.selected_sound_id, volume)
    
    def _save_sound_props(self):
        """Сохраняет свойства звука"""
        if not self.selected_sound_id:
            return
        
        sound = self.sound_manager.sounds.get(self.selected_sound_id)
        if sound:
            sound['name'] = self.vars['name'].get()
            sound['volume'] = self.vars['volume'].get()
            sound['category'] = self.vars['category'].get()
            self.sound_manager._save_sounds_config()
            self._refresh_sounds()
    
    def _bind_sound(self):
        """Привязывает звук к элементу"""
        if not self.selected_sound_id:
            messagebox.showwarning("Внимание", "Выберите звук")
            return
        
        element = self.vars['bind_element'].get()
        event = self.vars['bind_event'].get()
        
        if not element or not event:
            messagebox.showwarning("Внимание", "Выберите элемент и событие")
            return
        
        self.sound_manager.bind_sound(element, event, self.selected_sound_id)
        self._refresh_bindings()
    
    def _unbind_sound(self):
        """Отвязывает звук"""
        sel = self.bindings_tree.selection()
        if not sel:
            return
        
        item = self.bindings_tree.item(sel[0])
        values = item.get('values', [])
        if len(values) >= 2:
            elem_id = values[0]
            event = values[1]
            self.sound_manager.unbind_sound(elem_id, event)
            self._refresh_bindings()
    
    def _play_quick(self, sound_type):
        """Воспроизводит системный звук"""
        # Эти звуки можно добавить по умолчанию или использовать системные
        print(f"[Sounds] Quick sound: {sound_type}")
        # TODO: Добавить встроенные звуки
    
    def on_activate(self):
        """При активации вкладки"""
        self._refresh_sounds()
        self._refresh_elements()
        self._refresh_bindings()


