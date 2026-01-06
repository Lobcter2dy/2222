#!/usr/bin/env python3
"""
Вкладка механизмов - анимации и интерактивность
"""
import tkinter as tk
from tkinter import ttk
from .tab_base import TabBase


class TabMechanisms(TabBase):
    """Вкладка механизмов"""

    TAB_ID = "mechanisms"
    TAB_SYMBOL = "⚙"

    MECHANISMS = [
        ('move_track', '⟷', 'Движение'),
        ('rotator', '⟳', 'Вращение'),
        ('scale', '⤢', 'Масштаб'),
        ('fade', '◐', 'Затухание'),
        ('shake', '≋', 'Тряска'),
        ('path', '⤳', 'Путь'),
        ('pulse', '◉', 'Пульсация'),
    ]

    EASING = [
        ('linear', 'Линейно'),
        ('ease_in', 'Ускорение'),
        ('ease_out', 'Замедление'),
        ('ease_in_out', 'Плавно'),
        ('bounce', 'Отскок'),
        ('elastic', 'Упругость'),
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.mechanism_manager = None
        self.element_manager = None
        self.btns = {}
        self._updating = False  # Защита от рекурсии

    def set_mechanism_manager(self, manager):
        self.mechanism_manager = manager
        if manager:
            manager.set_selection_callback(self._on_selection)

    def set_element_manager(self, manager):
        self.element_manager = manager

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Создание ===
        sec = self._section(self.content, "Создать механизм")
        
        grid = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        grid.pack(fill=tk.X)
        
        for i, (mtype, sym, name) in enumerate(self.MECHANISMS):
            btn = tk.Button(grid, text=sym, font=("Arial", 12),
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                           activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                           relief=tk.FLAT, width=3, cursor="hand2",
                           command=lambda t=mtype: self._create(t))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="ew")
            self._tooltip(btn, name)
            self.btns[mtype] = btn
        
        for c in range(4):
            grid.columnconfigure(c, weight=1)
        
        self.status_lbl = tk.Label(sec, text="", font=("Arial", 9),
                                  bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_ACCENT)
        self.status_lbl.pack(anchor="w", pady=(4, 0))
        
        # === Список ===
        sec = self._section(self.content, "Активные механизмы")
        
        # Управление
        toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        
        for sym, tip, cmd, clr in [
            ('▶', 'Запуск', self._play, self.COLOR_SUCCESS),
            ('⏸', 'Пауза', self._pause, self.COLOR_WARNING),
            ('⏹', 'Стоп', self._stop, self.COLOR_DANGER),
            ('✕', 'Удалить', self._delete, self.COLOR_TEXT_MUTED),
        ]:
            b = self._icon_button(toolbar, sym, cmd, clr)
            b.pack(side=tk.LEFT, padx=1)
            self._tooltip(b, tip)
        
        self._icon_button(toolbar, '⟳', self._refresh).pack(side=tk.RIGHT)
        
        # Список
        cols = ('status', 'type', 'attached')
        self.tree = self._tree(sec, cols, 6)
        self.tree.heading('status', text='◉')
        self.tree.heading('type', text='Тип')
        self.tree.heading('attached', text='Привязка')
        self.tree.column('status', width=30)
        self.tree.column('type', width=80)
        self.tree.column('attached', width=60)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # НЕ используем <<TreeviewSelect>> - вызывает бесконечный цикл
        self.tree.bind('<ButtonRelease-1>', self._on_tree_click)
        
        # === Привязка ===
        sec = self._section(self.content, "Привязка элементов")
        
        row = self._row(sec)
        self.elem_combo = self._combo(row, [], width=14)
        self.elem_combo.pack(side=tk.LEFT)
        
        self._icon_button(row, '⊕', self._attach).pack(side=tk.LEFT, padx=4)
        self._icon_button(row, '⊖', self._detach).pack(side=tk.LEFT)
        
        self.attach_lbl = tk.Label(sec, text="Привязано: 0", font=("Arial", 8),
                                  bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE)
        self.attach_lbl.pack(anchor="w", pady=(4, 0))
        
        # === Общие настройки ===
        sec = self._section(self.content, "Общие параметры")
        
        # Скорость
        row = self._row(sec)
        self._label(row, "Скорость:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="100")
        self._entry(row, self.speed_var, 6).pack(side=tk.LEFT)
        self.speed_unit_lbl = tk.Label(row, text="px/s", font=("Arial", 8),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE)
        self.speed_unit_lbl.pack(side=tk.LEFT, padx=4)
        
        # Задержка
        row = self._row(sec)
        self._label(row, "Задержка:").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="0")
        self._entry(row, self.delay_var, 6).pack(side=tk.LEFT)
        tk.Label(row, text="мс", font=("Arial", 8),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=4)
        
        # Easing
        row = self._row(sec)
        self._label(row, "Смягчение:").pack(side=tk.LEFT)
        self.easing_var = tk.StringVar(value="linear")
        self._combo(row, [e[1] for e in self.EASING], self.easing_var, 12).pack(side=tk.LEFT)
        
        # Опции
        row = self._row(sec)
        self.loop_var = tk.BooleanVar(value=False)
        self._checkbox(row, "Цикл", self.loop_var).pack(side=tk.LEFT)
        
        self.reverse_var = tk.BooleanVar(value=True)
        self._checkbox(row, "Реверс", self.reverse_var).pack(side=tk.LEFT, padx=(8, 0))
        
        row = self._row(sec)
        self.autostart_var = tk.BooleanVar(value=False)
        self._checkbox(row, "Автозапуск", self.autostart_var).pack(side=tk.LEFT)
        
        # === Специфические настройки (динамически) ===
        self.specific_section = self._section(self.content, "Параметры механизма")
        self.specific_frame = tk.Frame(self.specific_section, bg=self.COLOR_BG_OVERLAY)
        self.specific_frame.pack(fill=tk.X)
        
        # Словарь для хранения переменных специфических настроек
        self.specific_vars = {}
        
        # Применить
        row = self._row(self.content)
        self._button(row, "Применить", self._apply, 'primary').pack(side=tk.LEFT)

    def _create(self, mtype):
        """Начать создание"""
        if not self.mechanism_manager:
            return
        
        name = next((n for t, s, n in self.MECHANISMS if t == mtype), mtype)
        self.status_lbl.config(text=f"⏵ {name}")
        
        for t, btn in self.btns.items():
            btn.config(bg=self.COLOR_ACCENT if t == mtype else self.COLOR_BG,
                      fg='#fff' if t == mtype else self.COLOR_TEXT)
        
        self.mechanism_manager.start_creation(mtype)

    def _on_tree_click(self, e=None):
        """Клик по списку"""
        if self._updating or not self.mechanism_manager:
            return
        self._updating = True
        try:
            sel = self.tree.selection()
            if sel:
                for mech in self.mechanism_manager.get_all_mechanisms():
                    if mech.id == sel[0]:
                        self.mechanism_manager.select_mechanism(mech)
                        self._load_settings(mech)
                        break
        finally:
            self._updating = False

    def _on_selection(self, mech):
        """Колбэк выбора механизма"""
        if self._updating:
            return
        self._updating = True
        try:
            self._refresh()
            self.status_lbl.config(text="")
            
            for btn in self.btns.values():
                btn.config(bg=self.COLOR_BG, fg=self.COLOR_TEXT)
            
            if mech:
                self._load_settings(mech)
                self._update_element_info(mech)
                try:
                    self.tree.selection_set(mech.id)
                    self.tree.see(mech.id)
                except tk.TclError:
                    pass  # Item not found in tree
        finally:
            self._updating = False
    
    def _update_element_info(self, mech):
        """Обновляет информацию о привязанных элементах"""
        if hasattr(mech, 'attached_elements') and mech.attached_elements:
            count = len(mech.attached_elements)
            if count == 1:
                elem_id = mech.attached_elements[0][:8]
                self.element_info_lbl.config(text=f"привязан к {elem_id}", fg=self.COLOR_SUCCESS)
            else:
                self.element_info_lbl.config(text=f"привязан к {count} элементам", fg=self.COLOR_SUCCESS)
        else:
            self.element_info_lbl.config(text="не привязан", fg=self.COLOR_TEXT_MUTED)
    
    def update_for_element(self, element):
        """Обновляет панель механизмов для выбранного элемента"""
        if not element or not hasattr(element, 'attached_mechanisms'):
            return
        
        attached_mechanisms = getattr(element, 'attached_mechanisms', [])
        
        # Показываем информацию о привязанных механизмах
        if attached_mechanisms:
            count = len(attached_mechanisms)
            info_text = f"К элементу привязано: {count} механизмов"
            
            # Подсвечиваем привязанные механизмы в списке
            for mech in self.mechanism_manager.get_all_mechanisms():
                if mech.id in attached_mechanisms:
                    try:
                        # Выделяем в дереве
                        item = self.tree.selection()
                        if not item or item[0] != mech.id:
                            # Только если ещё не выбран
                            pass
                    except:
                        pass
        else:
            info_text = "К элементу не привязано механизмов"
        
        # Обновляем статус
        self.status_lbl.config(text=info_text)

    def _load_settings(self, mech):
        # Общие настройки
        props = getattr(mech, 'properties', {})
        self.speed_var.set(str(props.get('speed', 100)))
        self.delay_var.set(str(props.get('start_delay', 0)))
        self.loop_var.set(props.get('loop', False))
        self.reverse_var.set(props.get('reverse_on_end', True))
        self.autostart_var.set(getattr(mech, 'autostart', False))
        
        # Обновить единицы измерения скорости
        mtype = getattr(mech, 'MECHANISM_TYPE', '')
        if mtype == 'rotator':
            self.speed_unit_lbl.config(text="°/s")
        else:
            self.speed_unit_lbl.config(text="px/s")
        
        count = len(getattr(mech, 'attached_elements', []))
        self.attach_lbl.config(text=f"Привязано: {count}")
        
        # Специфические настройки
        self._build_specific_settings(mech)

    def _build_specific_settings(self, mech):
        """Создаёт специфические настройки для типа механизма"""
        # Очищаем предыдущие настройки
        for w in self.specific_frame.winfo_children():
            w.destroy()
        self.specific_vars.clear()
        
        mtype = getattr(mech, 'MECHANISM_TYPE', '')
        props = getattr(mech, 'properties', {})
        
        if mtype == 'move_track':
            # Направление
            row = self._row(self.specific_frame)
            self._label(row, "Направление:").pack(side=tk.LEFT)
            self.specific_vars['direction'] = tk.StringVar(value=props.get('direction', 'horizontal'))
            for val, txt in [('horizontal', 'Гориз'), ('vertical', 'Верт'), ('custom', 'Своё')]:
                rb = tk.Radiobutton(row, text=txt, variable=self.specific_vars['direction'], value=val,
                                   font=("Arial", 8), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                                   selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY)
                rb.pack(side=tk.LEFT, padx=2)
            
            # Точки трека
            row = self._row(self.specific_frame)
            self._label(row, "Начало X:").pack(side=tk.LEFT)
            self.specific_vars['start_x'] = tk.StringVar(value=str(props.get('start_x', 0)))
            self._entry(row, self.specific_vars['start_x'], 5).pack(side=tk.LEFT)
            self._label(row, "Y:", 3).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['start_y'] = tk.StringVar(value=str(props.get('start_y', 0)))
            self._entry(row, self.specific_vars['start_y'], 5).pack(side=tk.LEFT)
            
            row = self._row(self.specific_frame)
            self._label(row, "Конец X:").pack(side=tk.LEFT)
            self.specific_vars['end_x'] = tk.StringVar(value=str(props.get('end_x', 200)))
            self._entry(row, self.specific_vars['end_x'], 5).pack(side=tk.LEFT)
            self._label(row, "Y:", 3).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['end_y'] = tk.StringVar(value=str(props.get('end_y', 0)))
            self._entry(row, self.specific_vars['end_y'], 5).pack(side=tk.LEFT)
            
        elif mtype == 'rotator':
            # Направление вращения
            row = self._row(self.specific_frame)
            self._label(row, "Вращение:").pack(side=tk.LEFT)
            self.specific_vars['direction'] = tk.StringVar(value=props.get('direction', 'clockwise'))
            for val, txt in [('clockwise', '↻ По часов.'), ('counterclockwise', '↺ Против')]:
                rb = tk.Radiobutton(row, text=txt, variable=self.specific_vars['direction'], value=val,
                                   font=("Arial", 8), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                                   selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY)
                rb.pack(side=tk.LEFT, padx=2)
            
            # Радиус
            row = self._row(self.specific_frame)
            self._label(row, "Радиус:").pack(side=tk.LEFT)
            self.specific_vars['radius'] = tk.StringVar(value=str(props.get('radius', 50)))
            self._entry(row, self.specific_vars['radius'], 5).pack(side=tk.LEFT)
            tk.Label(row, text="px", font=("Arial", 8),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=2)
            
            # Углы
            row = self._row(self.specific_frame)
            self._label(row, "От угла:").pack(side=tk.LEFT)
            self.specific_vars['angle_start'] = tk.StringVar(value=str(props.get('angle_start', 0)))
            self._entry(row, self.specific_vars['angle_start'], 4).pack(side=tk.LEFT)
            self._label(row, "до:", 3).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['angle_end'] = tk.StringVar(value=str(props.get('angle_end', 360)))
            self._entry(row, self.specific_vars['angle_end'], 4).pack(side=tk.LEFT)
            tk.Label(row, text="° (0=беск.)", font=("Arial", 7),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=2)
            
        elif mtype == 'scale':
            # Масштаб от-до
            row = self._row(self.specific_frame)
            self._label(row, "От:").pack(side=tk.LEFT)
            self.specific_vars['scale_from'] = tk.StringVar(value=str(props.get('scale_from', 1.0)))
            self._entry(row, self.specific_vars['scale_from'], 4).pack(side=tk.LEFT)
            self._label(row, "до:", 3).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['scale_to'] = tk.StringVar(value=str(props.get('scale_to', 1.5)))
            self._entry(row, self.specific_vars['scale_to'], 4).pack(side=tk.LEFT)
            
        elif mtype == 'fade':
            # Прозрачность от-до
            row = self._row(self.specific_frame)
            self._label(row, "От:").pack(side=tk.LEFT)
            self.specific_vars['opacity_from'] = tk.StringVar(value=str(props.get('opacity_from', 100)))
            self._entry(row, self.specific_vars['opacity_from'], 4).pack(side=tk.LEFT)
            self._label(row, "до:", 3).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['opacity_to'] = tk.StringVar(value=str(props.get('opacity_to', 0)))
            self._entry(row, self.specific_vars['opacity_to'], 4).pack(side=tk.LEFT)
            tk.Label(row, text="%", font=("Arial", 8),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=2)
            
        elif mtype == 'shake':
            # Интенсивность и частота
            row = self._row(self.specific_frame)
            self._label(row, "Сила:").pack(side=tk.LEFT)
            self.specific_vars['intensity'] = tk.StringVar(value=str(props.get('intensity', 10)))
            self._entry(row, self.specific_vars['intensity'], 4).pack(side=tk.LEFT)
            tk.Label(row, text="px", font=("Arial", 8),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=2)
            
            row = self._row(self.specific_frame)
            self._label(row, "Частота:").pack(side=tk.LEFT)
            self.specific_vars['frequency'] = tk.StringVar(value=str(props.get('frequency', 20)))
            self._entry(row, self.specific_vars['frequency'], 4).pack(side=tk.LEFT)
            tk.Label(row, text="Гц", font=("Arial", 8),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=2)
            
        elif mtype == 'pulse':
            # Масштаб и частота пульсации
            row = self._row(self.specific_frame)
            self._label(row, "Мин:").pack(side=tk.LEFT)
            self.specific_vars['scale_min'] = tk.StringVar(value=str(props.get('scale_min', 0.9)))
            self._entry(row, self.specific_vars['scale_min'], 4).pack(side=tk.LEFT)
            self._label(row, "Макс:", 5).pack(side=tk.LEFT, padx=(4,0))
            self.specific_vars['scale_max'] = tk.StringVar(value=str(props.get('scale_max', 1.1)))
            self._entry(row, self.specific_vars['scale_max'], 4).pack(side=tk.LEFT)
            
        elif mtype == 'path':
            # Количество точек и замкнутость
            row = self._row(self.specific_frame)
            self._label(row, "Точек:").pack(side=tk.LEFT)
            points = props.get('points', [])
            tk.Label(row, text=str(len(points)), font=("Arial", 9, "bold"),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_ACCENT).pack(side=tk.LEFT, padx=4)
            
            self.specific_vars['closed'] = tk.BooleanVar(value=props.get('closed', False))
            self._checkbox(row, "Замкнутый", self.specific_vars['closed']).pack(side=tk.LEFT, padx=(8,0))
        
        # Если нет специфических настроек
        if not self.specific_vars:
            tk.Label(self.specific_frame, text="Нет доп. настроек",
                    font=("Arial", 8), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED).pack(pady=4)

    def _apply(self):
        if not self.mechanism_manager or not self.mechanism_manager.selected_mechanism:
            return
        
        mech = self.mechanism_manager.selected_mechanism
        props = getattr(mech, 'properties', {})
        
        try:
            # Общие настройки
            props['speed'] = int(self.speed_var.get() or 100)
            props['start_delay'] = int(self.delay_var.get() or 0)
            props['loop'] = self.loop_var.get()
            props['reverse_on_end'] = self.reverse_var.get()
            mech.autostart = self.autostart_var.get()
            
            # Для rotator скорость - это rotation_speed
            if getattr(mech, 'MECHANISM_TYPE', '') == 'rotator':
                props['rotation_speed'] = props['speed']
            
            easing_text = self.easing_var.get()
            for key, text in self.EASING:
                if text == easing_text:
                    props['easing'] = key
                    break
            
            # Специфические настройки
            for key, var in self.specific_vars.items():
                val = var.get()
                # Преобразуем типы
                if key in ('start_x', 'start_y', 'end_x', 'end_y', 'radius', 
                          'angle_start', 'angle_end', 'intensity', 'frequency',
                          'opacity_from', 'opacity_to'):
                    val = int(float(val))
                elif key in ('scale_from', 'scale_to', 'scale_min', 'scale_max'):
                    val = float(val)
                elif key == 'closed':
                    val = bool(val)
                props[key] = val
            
            # Обновляем механизм
            mech.update()
            
        except (ValueError, AttributeError) as e:
            print(f"[TabMechanisms] Ошибка применения настроек: {e}")
    
    def _attach_to_selected(self):
        """Привязывает выбранный механизм к выбранному элементу"""
        if not self.mechanism_manager or not self.element_manager:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Предупреждение", "Менеджеры недоступны", parent=self.frame)
            return
        
        selected_mech = self.mechanism_manager.selected_mechanism
        selected_elem = self.element_manager.selected_element
        
        if not selected_mech:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Предупреждение", "Выберите механизм", parent=self.frame)
            return
        
        if not selected_elem:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Предупреждение", "Выберите элемент на холсте", parent=self.frame)
            return
        
        # Привязываем
        try:
            selected_mech.attach_element(selected_elem.id)
            selected_elem.attach_mechanism(selected_mech.id)
            
            import tkinter.messagebox as msgbox
            msgbox.showinfo("Успех", 
                           f"Механизм '{selected_mech.MECHANISM_NAME}' привязан к элементу", 
                           parent=self.frame)
            
            # Обновляем отображение
            self._refresh()
            
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Ошибка", f"Не удалось привязать механизм:\n{e}", parent=self.frame)
    
    def _start_mechanism(self):
        """Запускает выбранный механизм"""
        if not self.mechanism_manager:
            return
        
        selected_mech = self.mechanism_manager.selected_mechanism
        if not selected_mech:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Предупреждение", "Выберите механизм", parent=self.frame)
            return
        
        try:
            if hasattr(selected_mech, 'start'):
                selected_mech.start()
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Запуск", f"Механизм '{selected_mech.MECHANISM_NAME}' запущен", parent=self.frame)
            else:
                import tkinter.messagebox as msgbox
                msgbox.showwarning("Предупреждение", "Механизм не поддерживает запуск", parent=self.frame)
                
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Ошибка", f"Не удалось запустить механизм:\n{e}", parent=self.frame)
    
    def _stop_mechanism(self):
        """Останавливает выбранный механизм"""
        if not self.mechanism_manager:
            return
        
        selected_mech = self.mechanism_manager.selected_mechanism
        if not selected_mech:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Предупреждение", "Выберите механизм", parent=self.frame)
            return
        
        try:
            if hasattr(selected_mech, 'stop'):
                selected_mech.stop()
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Остановка", f"Механизм '{selected_mech.MECHANISM_NAME}' остановлен", parent=self.frame)
            else:
                import tkinter.messagebox as msgbox
                msgbox.showwarning("Предупреждение", "Механизм не поддерживает остановку", parent=self.frame)
                
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Ошибка", f"Не удалось остановить механизм:\n{e}", parent=self.frame)

    def _refresh(self):
        if not self.tree or not self.mechanism_manager:
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for mech in self.mechanism_manager.get_all_mechanisms():
            status = '▶' if mech.is_active else '○'
            name = next((n for t, s, n in self.MECHANISMS if t == mech.MECHANISM_TYPE), mech.MECHANISM_TYPE)
            attached = len(getattr(mech, 'attached_elements', []))
            self.tree.insert('', 'end', iid=mech.id, values=(status, name, attached))
        
        self._update_elem_combo()

    def _update_elem_combo(self):
        if not self.element_manager:
            return
        elements = self.element_manager.get_all_elements()
        values = [f"{e.ELEMENT_TYPE[:5]}:{e.id[:6]}" for e in elements]
        self.elem_combo['values'] = values
        if values:
            self.elem_combo.current(0)

    def _attach(self):
        if not self.mechanism_manager or not self.mechanism_manager.selected_mechanism:
            return
        if not self.element_manager:
            return
        
        sel = self.elem_combo.get()
        if not sel or ':' not in sel:
            return
        
        elem_id = sel.split(':')[1]
        for elem in self.element_manager.get_all_elements():
            if elem.id.startswith(elem_id):
                self.mechanism_manager.selected_mechanism.attach(elem)
                self._refresh()
                break

    def _detach(self):
        if not self.mechanism_manager or not self.mechanism_manager.selected_mechanism:
            return
        
        mech = self.mechanism_manager.selected_mechanism
        if hasattr(mech, 'attached_elements') and mech.attached_elements:
            mech.detach(mech.attached_elements[-1])
            self._refresh()

    def _play(self):
        if self.mechanism_manager and self.mechanism_manager.selected_mechanism:
            self.mechanism_manager.selected_mechanism.start()
            self._refresh()

    def _pause(self):
        if self.mechanism_manager and self.mechanism_manager.selected_mechanism:
            mech = self.mechanism_manager.selected_mechanism
            if mech.is_paused:
                mech.resume()
            else:
                mech.pause()
            self._refresh()

    def _stop(self):
        if self.mechanism_manager and self.mechanism_manager.selected_mechanism:
            self.mechanism_manager.selected_mechanism.stop()
            self._refresh()

    def _delete(self):
        if self.mechanism_manager:
            self.mechanism_manager.delete_selected()
            self._refresh()

    def refresh(self):
        """Публичный метод обновления"""
        self._refresh()

    def on_activate(self):
        self._refresh()
