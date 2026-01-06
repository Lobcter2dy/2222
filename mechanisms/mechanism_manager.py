#!/usr/bin/env python3
"""
Менеджер механизмов
Управляет всеми механизмами на холсте
Поддерживает группировку, видимость, блокировку
"""
from .move_track import MoveTrackMechanism
from .rotator import RotatorMechanism
from .scale_mechanism import ScaleMechanism
from .fade_mechanism import FadeMechanism
from .shake_mechanism import ShakeMechanism
from .path_mechanism import PathMechanism
from .pulse_mechanism import PulseMechanism


class MechanismGroup:
    """Группа механизмов"""
    
    def __init__(self, name="Группа"):
        self.id = f"mech_group_{id(self)}"
        self.name = name
        self.mechanism_ids = []
        self.is_expanded = True  # Развёрнута в UI
        self.is_locked = False   # Заблокирована
        self.is_visible = True   # Видима
    
    def add(self, mech_id):
        if mech_id not in self.mechanism_ids:
            self.mechanism_ids.append(mech_id)
    
    def remove(self, mech_id):
        if mech_id in self.mechanism_ids:
            self.mechanism_ids.remove(mech_id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'mechanism_ids': self.mechanism_ids,
            'is_expanded': self.is_expanded,
            'is_locked': self.is_locked,
            'is_visible': self.is_visible,
        }
    
    @classmethod
    def from_dict(cls, data):
        group = cls(data.get('name', 'Группа'))
        group.id = data.get('id', group.id)
        group.mechanism_ids = data.get('mechanism_ids', [])
        group.is_expanded = data.get('is_expanded', True)
        group.is_locked = data.get('is_locked', False)
        group.is_visible = data.get('is_visible', True)
        return group


class MechanismManager:
    """Менеджер механизмов"""

    # Реестр типов механизмов
    MECHANISM_TYPES = {
        'move_track': MoveTrackMechanism,
        'rotator': RotatorMechanism,
        'scale': ScaleMechanism,
        'fade': FadeMechanism,
        'shake': ShakeMechanism,
        'path': PathMechanism,
        'pulse': PulseMechanism,
    }

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Список всех механизмов
        self.mechanisms = []
        
        # Группы механизмов
        self.groups = []
        
        # Выбранный механизм
        self.selected_mechanism = None
        
        # Множественный выбор
        self.multi_selection = []
        
        # Ссылка на element_manager
        self.element_manager = None
        
        # Система масштабирования
        self.zoom_system = None
        
        # Callback при выборе механизма
        self._selection_callback = None
        
        # Режим создания
        self._creating_type = None
        self._creation_start = None

    def set_element_manager(self, manager):
        """Устанавливает менеджер элементов"""
        self.element_manager = manager
        # Обновляем ссылку во всех механизмах
        for mech in self.mechanisms:
            mech.set_element_manager(manager)

    def set_zoom_system(self, zoom_system):
        """Устанавливает систему масштабирования"""
        self.zoom_system = zoom_system
        for mech in self.mechanisms:
            mech.set_zoom_system(zoom_system)

    def set_selection_callback(self, callback):
        """Устанавливает callback при выборе механизма"""
        self._selection_callback = callback

    def create_mechanism(self, mech_type, x, y, width=200, height=10):
        """Создаёт новый механизм"""
        if mech_type not in self.MECHANISM_TYPES:
            print(f"[MechanismManager] Неизвестный тип: {mech_type}")
            return None
        
        mech_class = self.MECHANISM_TYPES[mech_type]
        mechanism = mech_class(self.canvas, self.config)
        mechanism.x = x
        mechanism.y = y
        mechanism.width = width
        mechanism.height = height
        
        if self.zoom_system:
            mechanism.set_zoom_system(self.zoom_system)
        
        if self.element_manager:
            mechanism.set_element_manager(self.element_manager)
        
        mechanism.draw()
        self.mechanisms.append(mechanism)
        
        return mechanism

    def get_mechanism_at(self, screen_x, screen_y):
        """Возвращает механизм под указанными координатами"""
        # Проверяем только видимые
        for mechanism in reversed(self.mechanisms):
            if mechanism.is_visible and mechanism.contains_point(screen_x, screen_y):
                return mechanism
        return None

    def select_mechanism(self, mechanism):
        """Выбирает механизм"""
        self.selected_mechanism = mechanism
        if self._selection_callback:
            self._selection_callback(mechanism)

    def select_at(self, screen_x, screen_y):
        """Выбирает механизм по координатам"""
        mechanism = self.get_mechanism_at(screen_x, screen_y)
        if mechanism:
            self.select_mechanism(mechanism)
        return mechanism

    def deselect_all(self):
        """Снимает выделение"""
        self.selected_mechanism = None
        self.multi_selection.clear()
        if self._selection_callback:
            self._selection_callback(None)

    # === Множественный выбор ===
    
    def add_to_selection(self, mechanism):
        """Добавляет механизм к выбранным"""
        if mechanism and mechanism.id not in self.multi_selection:
            self.multi_selection.append(mechanism.id)

    def remove_from_selection(self, mechanism):
        """Убирает механизм из выбранных"""
        if mechanism and mechanism.id in self.multi_selection:
            self.multi_selection.remove(mechanism.id)

    def get_selected_mechanisms(self):
        """Возвращает список выбранных механизмов"""
        result = []
        for mech_id in self.multi_selection:
            mech = self.get_mechanism_by_id(mech_id)
            if mech:
                result.append(mech)
        return result

    # === Удаление ===

    def delete_mechanism(self, mechanism):
        """Удаляет механизм"""
        if mechanism in self.mechanisms:
            mechanism.stop()
            mechanism.clear()
            self.mechanisms.remove(mechanism)
            
            # Удаляем из групп
            for group in self.groups:
                group.remove(mechanism.id)
            
            # Удаляем из выбора
            if mechanism.id in self.multi_selection:
                self.multi_selection.remove(mechanism.id)
            
            if self.selected_mechanism == mechanism:
                self.selected_mechanism = None

    def delete_selected(self):
        """Удаляет выбранный механизм"""
        if self.selected_mechanism:
            self.delete_mechanism(self.selected_mechanism)

    def delete(self, mechanism):
        """Алиас для delete_mechanism"""
        self.delete_mechanism(mechanism)

    # === Поиск ===

    def get_all_mechanisms(self):
        """Возвращает список всех механизмов"""
        return self.mechanisms.copy()

    def get_mechanism_by_id(self, mech_id):
        """Ищет механизм по ID"""
        for mechanism in self.mechanisms:
            if mechanism.id == mech_id:
                return mechanism
        return None

    def get_mechanisms_by_type(self, mech_type):
        """Возвращает механизмы определённого типа"""
        return [m for m in self.mechanisms if m.MECHANISM_TYPE == mech_type]

    def get_visible_mechanisms(self):
        """Возвращает только видимые механизмы"""
        return [m for m in self.mechanisms if m.is_visible]

    # === Видимость и блокировка ===
    
    def set_visible(self, mechanism, visible):
        """Устанавливает видимость механизма"""
        if mechanism:
            mechanism.is_visible = visible
            if visible:
                mechanism.update()
            else:
                mechanism.clear()

    def toggle_visible(self, mechanism):
        """Переключает видимость"""
        if mechanism:
            self.set_visible(mechanism, not mechanism.is_visible)

    def set_locked(self, mechanism, locked):
        """Устанавливает блокировку (нельзя запустить/остановить)"""
        if mechanism and hasattr(mechanism, 'is_locked'):
            mechanism.is_locked = locked

    def hide_all(self):
        """Скрывает все механизмы"""
        for mech in self.mechanisms:
            mech.is_visible = False
            mech.clear()

    def show_all(self):
        """Показывает все механизмы"""
        for mech in self.mechanisms:
            mech.is_visible = True
            mech.update()

    # === Группировка ===
    
    def create_group(self, name="Группа", mechanism_ids=None):
        """Создаёт новую группу механизмов"""
        group = MechanismGroup(name)
        if mechanism_ids:
            for mech_id in mechanism_ids:
                group.add(mech_id)
        self.groups.append(group)
        return group

    def delete_group(self, group):
        """Удаляет группу (механизмы остаются)"""
        if group in self.groups:
            self.groups.remove(group)

    def get_group_by_id(self, group_id):
        """Ищет группу по ID"""
        for group in self.groups:
            if group.id == group_id:
                return group
        return None

    def add_to_group(self, mechanism, group):
        """Добавляет механизм в группу"""
        if mechanism and group:
            group.add(mechanism.id)

    def remove_from_group(self, mechanism, group):
        """Удаляет механизм из группы"""
        if mechanism and group:
            group.remove(mechanism.id)

    def get_mechanism_group(self, mechanism):
        """Возвращает группу механизма (или None)"""
        if not mechanism:
            return None
        for group in self.groups:
            if mechanism.id in group.mechanism_ids:
                return group
        return None

    def group_selected(self, name="Группа"):
        """Группирует выбранные механизмы"""
        if len(self.multi_selection) < 2:
            return None
        return self.create_group(name, self.multi_selection.copy())

    def ungroup(self, group):
        """Расформировывает группу"""
        self.delete_group(group)

    # === Управление группой ===
    
    def start_group(self, group):
        """Запускает все механизмы группы"""
        if not group:
            return
        for mech_id in group.mechanism_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech and not getattr(mech, 'is_locked', False):
                mech.start()

    def stop_group(self, group):
        """Останавливает все механизмы группы"""
        if not group:
            return
        for mech_id in group.mechanism_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech:
                mech.stop()

    def toggle_group(self, group):
        """Переключает все механизмы группы"""
        if not group:
            return
        for mech_id in group.mechanism_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech and not getattr(mech, 'is_locked', False):
                mech.toggle()

    def set_group_visible(self, group, visible):
        """Устанавливает видимость всей группы"""
        if not group:
            return
        group.is_visible = visible
        for mech_id in group.mechanism_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech:
                self.set_visible(mech, visible)

    def set_group_locked(self, group, locked):
        """Блокирует/разблокирует всю группу"""
        if not group:
            return
        group.is_locked = locked
        for mech_id in group.mechanism_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech:
                self.set_locked(mech, locked)

    # === Объединение механизмов (цепочка) ===
    
    def chain_mechanisms(self, mech_ids, loop=False):
        """
        Создаёт цепочку механизмов (один запускает следующий)
        
        Args:
            mech_ids: список ID механизмов
            loop: зациклить цепочку
        """
        for i, mech_id in enumerate(mech_ids):
            mech = self.get_mechanism_by_id(mech_id)
            if not mech:
                continue
            
            # Следующий механизм
            next_idx = i + 1
            if next_idx >= len(mech_ids):
                if loop:
                    next_idx = 0
                else:
                    continue
            
            next_mech_id = mech_ids[next_idx]
            mech.properties['chain_next'] = next_mech_id

    def unchain_mechanisms(self, mech_ids):
        """Разрывает цепочку механизмов"""
        for mech_id in mech_ids:
            mech = self.get_mechanism_by_id(mech_id)
            if mech and 'chain_next' in mech.properties:
                del mech.properties['chain_next']

    # === Перерисовка ===

    def redraw_all(self):
        """Перерисовывает все механизмы"""
        for mechanism in self.mechanisms:
            if mechanism.is_visible:
                mechanism.update()

    # === Режим создания ===
    
    def start_creation(self, mech_type):
        """Начинает режим создания механизма"""
        if mech_type in self.MECHANISM_TYPES:
            self._creating_type = mech_type
            return True
        return False

    def is_creating(self):
        """Проверяет активен ли режим создания"""
        return self._creating_type is not None

    def on_create_start(self, x, y):
        """Начало создания (первый клик)"""
        self._creation_start = (x, y)

    def on_create_end(self, x, y):
        """Конец создания (отпускание)"""
        if not self._creating_type or not self._creation_start:
            return None
        
        start_x, start_y = self._creation_start
        
        # Минимальный размер
        width = abs(x - start_x)
        height = abs(y - start_y)
        
        if width < 50:
            width = 200
        if height < 10:
            height = 10
        
        # Создаём механизм
        mechanism = self.create_mechanism(
            self._creating_type,
            min(start_x, x),
            min(start_y, y),
            width,
            height
        )
        
        if mechanism:
            # Настраиваем точки трека
            if hasattr(mechanism, 'set_track_points'):
                mechanism.set_track_points(
                    0, 0,
                    x - start_x, y - start_y
                )
            
            self.select_mechanism(mechanism)
        
        # Сбрасываем режим создания
        self._creating_type = None
        self._creation_start = None
        
        return mechanism

    def cancel_creation(self):
        """Отменяет режим создания"""
        self._creating_type = None
        self._creation_start = None

    # === Привязка к кнопкам ===
    
    def trigger_by_function(self, function_id):
        """Запускает все механизмы привязанные к функции"""
        triggered = []
        for mechanism in self.mechanisms:
            if mechanism.trigger_function_id == function_id:
                if not getattr(mechanism, 'is_locked', False):
                    mechanism.toggle()
                    triggered.append(mechanism)
        return triggered

    # === Управление всеми ===
    
    def start_all(self):
        """Запускает все механизмы"""
        for mech in self.mechanisms:
            if not getattr(mech, 'is_locked', False):
                mech.start()

    def stop_all(self):
        """Останавливает все механизмы"""
        for mech in self.mechanisms:
            mech.stop()

    def pause_all(self):
        """Ставит на паузу все механизмы"""
        for mech in self.mechanisms:
            if hasattr(mech, 'pause'):
                mech.pause()

    def resume_all(self):
        """Возобновляет все механизмы"""
        for mech in self.mechanisms:
            if hasattr(mech, 'resume'):
                mech.resume()

    # === Сериализация ===
    
    def to_dict(self):
        """Сериализует все механизмы и группы"""
        return {
            'mechanisms': [mech.to_dict() for mech in self.mechanisms],
            'groups': [group.to_dict() for group in self.groups],
        }

    def from_dict(self, data):
        """Загружает механизмы и группы из словаря"""
        # Загружаем механизмы
        mechanisms_data = data if isinstance(data, list) else data.get('mechanisms', [])
        for mech_data in mechanisms_data:
            mech_type = mech_data.get('type')
            if mech_type not in self.MECHANISM_TYPES:
                continue
            
            mech_class = self.MECHANISM_TYPES[mech_type]
            mechanism = mech_class(self.canvas, self.config)
            mechanism.from_dict(mech_data)
            
            if self.zoom_system:
                mechanism.set_zoom_system(self.zoom_system)
            if self.element_manager:
                mechanism.set_element_manager(self.element_manager)
            
            mechanism.draw()
            self.mechanisms.append(mechanism)
        
        # Загружаем группы
        if isinstance(data, dict) and 'groups' in data:
            for group_data in data.get('groups', []):
                group = MechanismGroup.from_dict(group_data)
                self.groups.append(group)
