"""
Главный контроллер приложения
Координирует инициализацию и связь модулей
"""

import tkinter as tk
from typing import Optional
from ..utils.logger import get_logger
from ..utils.event_bus import event_bus, emit

log = get_logger('AppController')


class AppController:
    """
    Главный контроллер приложения.
    Отвечает за:
    - Инициализацию приложения
    - Координацию между контроллерами
    - Управление жизненным циклом
    """
    
    def __init__(self, root: tk.Tk, config):
        """
        Args:
            root: Главное окно Tkinter
            config: Конфигурация приложения
        """
        self.root = root
        self.config = config
        
        # Состояние
        self.is_initialized = False
        self.is_running = False
        
        # Ссылки на другие контроллеры (устанавливаются позже)
        self.canvas_controller: Optional['CanvasController'] = None
        self.element_controller: Optional['ElementController'] = None
        self.ui_controller: Optional['UIController'] = None
        
        # Ссылки на менеджеры
        self.element_manager = None
        self.mechanism_manager = None
        self.project_manager = None
        self.zoom_system = None
        self.grid_system = None
        
        # UI компоненты
        self.main_canvas = None
        self.canvas = None  # Tkinter canvas
        
        log.info("AppController создан")
        
    def set_controllers(self, canvas_ctrl, element_ctrl, ui_ctrl):
        """
        Устанавливает ссылки на другие контроллеры.
        
        Args:
            canvas_ctrl: CanvasController
            element_ctrl: ElementController
            ui_ctrl: UIController
        """
        self.canvas_controller = canvas_ctrl
        self.element_controller = element_ctrl
        self.ui_controller = ui_ctrl
        
    def set_managers(self, element_mgr, mechanism_mgr, project_mgr, zoom_sys, grid_sys):
        """
        Устанавливает ссылки на менеджеры.
        
        Args:
            element_mgr: ElementManager
            mechanism_mgr: MechanismManager  
            project_mgr: ProjectManager
            zoom_sys: ZoomSystem
            grid_sys: GridSystem
        """
        self.element_manager = element_mgr
        self.mechanism_manager = mechanism_mgr
        self.project_manager = project_mgr
        self.zoom_system = zoom_sys
        self.grid_system = grid_sys
        
    def set_canvas(self, main_canvas, tk_canvas):
        """
        Устанавливает ссылки на холст.
        
        Args:
            main_canvas: MainCanvas объект
            tk_canvas: Tkinter Canvas виджет
        """
        self.main_canvas = main_canvas
        self.canvas = tk_canvas
        
    def initialize(self):
        """Инициализирует приложение после создания всех компонентов"""
        if self.is_initialized:
            return
            
        log.info("Инициализация приложения...")
        
        # Настраиваем связи между менеджерами
        if self.element_manager and self.mechanism_manager:
            self.mechanism_manager.set_element_manager(self.element_manager)
            
        # Устанавливаем систему масштабирования
        if self.element_manager and self.zoom_system:
            # Элементы получают zoom_system через менеджер
            pass
            
        self.is_initialized = True
        emit('app:ready')
        log.info("Приложение инициализировано")
        
    def start(self):
        """Запускает главный цикл приложения"""
        if not self.is_initialized:
            self.initialize()
            
        self.is_running = True
        log.info("Приложение запущено")
        
    def stop(self):
        """Останавливает приложение"""
        if not self.is_running:
            return
            
        log.info("Остановка приложения...")
        emit('app:closing')
        
        # Очистка ресурсов
        self._cleanup()
        
        self.is_running = False
        log.info("Приложение остановлено")
        
    def _cleanup(self):
        """Очищает ресурсы перед закрытием"""
        # Останавливаем все механизмы
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                try:
                    mech.stop()
                except Exception as e:
                    log.error(f"Ошибка остановки механизма: {e}")
                    
        # Очищаем event bus
        event_bus.clear()
        
    # === Действия приложения ===
    
    def new_project(self):
        """Создаёт новый проект"""
        log.info("Создание нового проекта")
        
        if self.element_manager:
            self.element_manager.clear_all()
            
        if self.mechanism_manager:
            self.mechanism_manager.clear_all()
            
        if self.main_canvas:
            self.main_canvas.reset()
            
        emit('project:new')
        
    def save_project(self):
        """Сохраняет текущий проект"""
        if self.project_manager:
            success = self.project_manager.save()
            if success:
                log.info("Проект сохранён")
                emit('project:saved')
            return success
        return False
        
    def save_project_as(self):
        """Сохраняет проект как новый"""
        if self.project_manager:
            success = self.project_manager.save_as()
            if success:
                log.info("Проект сохранён как новый")
                emit('project:saved')
            return success
        return False
        
    def open_project(self):
        """Открывает проект"""
        if self.project_manager:
            success = self.project_manager.open_dialog()
            if success:
                log.info("Проект открыт")
                emit('project:opened')
            return success
        return False
        
    def undo(self):
        """Отменяет последнее действие"""
        # TODO: реализовать систему undo/redo
        log.debug("Undo не реализован")
        
    def redo(self):
        """Повторяет отменённое действие"""
        # TODO: реализовать систему undo/redo
        log.debug("Redo не реализован")
        
    def delete_selected(self):
        """Удаляет выбранный элемент"""
        if self.element_controller:
            self.element_controller.delete_selected()
            
    def select_all(self):
        """Выделяет все элементы"""
        if self.element_controller:
            self.element_controller.select_all()
            
    def deselect_all(self):
        """Снимает выделение"""
        if self.element_controller:
            self.element_controller.deselect_all()
            
    def copy_element(self):
        """Копирует выбранный элемент"""
        if self.element_controller:
            self.element_controller.copy()
            
    def paste_element(self):
        """Вставляет скопированный элемент"""
        if self.element_controller:
            self.element_controller.paste()
            
    def duplicate_element(self):
        """Дублирует выбранный элемент"""
        if self.element_controller:
            self.element_controller.duplicate()
            
    def zoom_in(self):
        """Увеличивает масштаб"""
        if self.canvas_controller:
            self.canvas_controller.zoom_in()
            
    def zoom_out(self):
        """Уменьшает масштаб"""
        if self.canvas_controller:
            self.canvas_controller.zoom_out()
            
    def zoom_reset(self):
        """Сбрасывает масштаб"""
        if self.canvas_controller:
            self.canvas_controller.zoom_reset()
            
    def toggle_grid(self):
        """Переключает отображение сетки"""
        if self.grid_system:
            self.grid_system.grid_enabled = not self.grid_system.grid_enabled
            if self.canvas_controller:
                self.canvas_controller.refresh()
            emit('ui:grid_toggled', self.grid_system.grid_enabled)
            
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        if self.ui_controller:
            self.ui_controller.toggle_fullscreen()
            
    def start_preview(self):
        """Запускает режим просмотра"""
        if hasattr(self, 'preview_mode') and self.preview_mode:
            self.preview_mode.toggle()
            
    def set_tool(self, tool: str):
        """Устанавливает текущий инструмент"""
        if self.canvas_controller:
            self.canvas_controller.set_tool(tool)

