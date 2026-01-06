#!/usr/bin/env python3
"""
Вкладка слоёв - управление порядком и видимостью элементов
"""
import tkinter as tk
from tkinter import ttk
from .tab_base import TabBase


class TabLayers(TabBase):
    """Вкладка слоёв"""

    TAB_ID = "layers"
    TAB_SYMBOL = "☰"

    ICONS = {
        'frame': '□', 'panel': '▢', 'button': '⬚', 'image': '▣',
        'text': 'T', 'scroll_area': '⊞', 'state_switcher': '◇',
        'move_track': '⟷', 'rotator': '⟳', 'scale': '⤢', 'fade': '◐',
        'shake': '≋', 'path': '⤳', 'pulse': '◉',
    }

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.element_manager = None
        self.mechanism_manager = None
        self._updating = False

    def set_element_manager(self, manager):
        self.element_manager = manager
        if manager:
            manager.set_selection_callback(self._on_selection)

    def set_mechanism_manager(self, manager):
        self.mechanism_manager = manager

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Элементы ===
        sec = self._section(self.content, "Элементы")
        
        # Тулбар
        toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        
        for sym, tip, cmd in [
            ('▲', 'Вверх', self._elem_up),
            ('▼', 'Вниз', self._elem_down),
            ('⊤', 'На передний план', self._elem_top),
            ('⊥', 'На задний план', self._elem_bottom),
        ]:
            b = self._icon_button(toolbar, sym, cmd)
            b.pack(side=tk.LEFT, padx=1)
            self._tooltip(b, tip)
        
        # Видимость/блокировка
        for sym, tip, cmd in [('◉', 'Видимость', self._toggle_visible), ('🔒', 'Блокировка', self._toggle_lock)]:
            b = self._icon_button(toolbar, sym, cmd)
            b.pack(side=tk.RIGHT, padx=1)
            self._tooltip(b, tip)
        
        # Список элементов
        cols = ('icon', 'name', 'vis', 'lock')
        self.elem_tree = self._tree(sec, cols, 10)
        self.elem_tree.heading('icon', text='')
        self.elem_tree.heading('name', text='Элемент')
        self.elem_tree.heading('vis', text='◉')
        self.elem_tree.heading('lock', text='🔒')
        self.elem_tree.column('icon', width=25)
        self.elem_tree.column('name', width=100)
        self.elem_tree.column('vis', width=25)
        self.elem_tree.column('lock', width=25)
        self.elem_tree.pack(fill=tk.BOTH, expand=True)
        # НЕ используем <<TreeviewSelect>> - вызывает бесконечный цикл
        self.elem_tree.bind('<ButtonRelease-1>', self._on_elem_click)
        self.elem_tree.bind('<Double-Button-1>', self._on_elem_double_click)
        
        # === Механизмы ===
        sec = self._section(self.content, "Механизмы")
        
        # Тулбар механизмов
        toolbar = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        
        for sym, tip, cmd, clr in [
            ('▶', 'Запустить все', self._mech_play_all, self.COLOR_SUCCESS),
            ('⏹', 'Остановить все', self._mech_stop_all, self.COLOR_DANGER),
        ]:
            b = self._icon_button(toolbar, sym, cmd, clr)
            b.pack(side=tk.LEFT, padx=1)
            self._tooltip(b, tip)
        
        # Список механизмов
        cols = ('icon', 'name', 'status')
        self.mech_tree = self._tree(sec, cols, 6)
        self.mech_tree.heading('icon', text='')
        self.mech_tree.heading('name', text='Механизм')
        self.mech_tree.heading('status', text='◉')
        self.mech_tree.column('icon', width=25)
        self.mech_tree.column('name', width=100)
        self.mech_tree.column('status', width=30)
        self.mech_tree.pack(fill=tk.BOTH, expand=True)
        self.mech_tree.bind('<<TreeviewSelect>>', self._on_mech_select)
        
        # === Информация ===
        sec = self._section(self.content, "Выбранный слой")
        
        self.info_lbl = tk.Label(sec, text="Ничего не выбрано", font=("Arial", 9),
                                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED, anchor="w")
        self.info_lbl.pack(fill=tk.X)
        
        row = self._row(sec)
        self._label(row, "Позиция:").pack(side=tk.LEFT)
        self.pos_lbl = tk.Label(row, text="—", font=("Arial", 9),
                               bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT)
        self.pos_lbl.pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Размер:").pack(side=tk.LEFT)
        self.size_lbl = tk.Label(row, text="—", font=("Arial", 9),
                                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT)
        self.size_lbl.pack(side=tk.LEFT)

    def _on_selection(self, elem):
        if self._updating:
            return
        self._updating = True
        try:
            self._refresh()
            if elem:
                self._update_info(elem)
        finally:
            self._updating = False

    def _on_elem_click(self, e=None):
        """Клик по списку элементов"""
        if self._updating or not self.element_manager:
            return
        self._updating = True
        try:
            sel = self.elem_tree.selection()
            if sel:
                for elem in self.element_manager.get_all_elements():
                    if elem.id == sel[0]:
                        self.element_manager.select_element(elem)
                        self._update_info(elem)
                        break
        finally:
            self._updating = False

    def _on_elem_double_click(self, e=None):
        """Двойной клик - переключить видимость"""
        self._toggle_visible()

    def _on_mech_select(self, e=None):
        if not self.mechanism_manager:
            return
        sel = self.mech_tree.selection()
        if sel:
            for mech in self.mechanism_manager.get_all_mechanisms():
                if mech.id == sel[0]:
                    self.mechanism_manager.select_mechanism(mech)
                    break

    def _update_info(self, elem):
        sym = self.ICONS.get(getattr(elem, 'ELEMENT_TYPE', ''), '?')
        self.info_lbl.config(text=f"{sym} {elem.id[:16]}", fg=self.COLOR_TEXT)
        self.pos_lbl.config(text=f"{int(elem.x)}, {int(elem.y)}")
        self.size_lbl.config(text=f"{int(elem.width)} × {int(elem.height)}")

    def _refresh(self):
        # Элементы
        if self.elem_tree and self.element_manager:
            sel = self.elem_tree.selection()
            for item in self.elem_tree.get_children():
                self.elem_tree.delete(item)
            
            for elem in reversed(self.element_manager.get_all_elements()):
                icon = self.ICONS.get(getattr(elem, 'ELEMENT_TYPE', ''), '?')
                name = elem.id[:10]
                vis = '◉' if getattr(elem, 'visible', True) else '○'
                lock = '🔒' if getattr(elem, 'size_locked', False) else '🔓'
                self.elem_tree.insert('', 'end', iid=elem.id, values=(icon, name, vis, lock))
            
            if sel:
                try:
                    self.elem_tree.selection_set(sel)
                except tk.TclError:
                    pass  # Item not found
        
        # Механизмы
        if self.mech_tree and self.mechanism_manager:
            for item in self.mech_tree.get_children():
                self.mech_tree.delete(item)
            
            for mech in self.mechanism_manager.get_all_mechanisms():
                icon = self.ICONS.get(mech.MECHANISM_TYPE, '⚙')
                name = mech.id[:10]
                status = '▶' if mech.is_active else '○'
                self.mech_tree.insert('', 'end', iid=mech.id, values=(icon, name, status))

    def _elem_up(self):
        if self.element_manager and self.element_manager.selected_element:
            # Переместить вверх в списке (ближе к наблюдателю)
            elems = self.element_manager.get_all_elements()
            elem = self.element_manager.selected_element
            idx = elems.index(elem) if elem in elems else -1
            if idx < len(elems) - 1:
                elems[idx], elems[idx + 1] = elems[idx + 1], elems[idx]
                self.element_manager.redraw_all()
                self._refresh()

    def _elem_down(self):
        if self.element_manager and self.element_manager.selected_element:
            elems = self.element_manager.get_all_elements()
            elem = self.element_manager.selected_element
            idx = elems.index(elem) if elem in elems else -1
            if idx > 0:
                elems[idx], elems[idx - 1] = elems[idx - 1], elems[idx]
                self.element_manager.redraw_all()
                self._refresh()

    def _elem_top(self):
        if self.element_manager and self.element_manager.selected_element:
            self.element_manager.bring_to_front(self.element_manager.selected_element)
            self._refresh()

    def _elem_bottom(self):
        if self.element_manager and self.element_manager.selected_element:
            self.element_manager.send_to_back(self.element_manager.selected_element)
            self._refresh()

    def _toggle_visible(self):
        if self.element_manager and self.element_manager.selected_element:
            elem = self.element_manager.selected_element
            elem.visible = not getattr(elem, 'visible', True)
            elem.update()
            self._refresh()

    def _toggle_lock(self):
        if self.element_manager and self.element_manager.selected_element:
            elem = self.element_manager.selected_element
            elem.size_locked = not getattr(elem, 'size_locked', False)
            self._refresh()

    def _mech_play_all(self):
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                mech.start()
            self._refresh()

    def _mech_stop_all(self):
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                mech.stop()
            self._refresh()

    def update(self):
        """Обновить список слоёв"""
        if not self._updating:
            self._refresh()

    def on_activate(self):
        self._refresh()
