#!/usr/bin/env python3
"""
Интегрированный менеджер артефактов
Управляет функциональными артефактами на холсте
"""
from typing import Dict, List, Optional, Any
from .artifacts import FunctionalArtifact, ArtifactRegistry
from .artifacts.file_browser import FileBrowserArtifact
from .artifacts.code_editor import CodeEditorArtifact
from .utils.event_bus import event_bus
from .utils.logger import get_logger

log = get_logger('ArtifactManagerIntegrated')


class ArtifactManagerIntegrated:
    """
    Интегрированный менеджер артефактов.
    Управляет функциональными панелями с встроенным функционалом.
    """
    
    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Реестр артефактов
        self.artifacts: List[FunctionalArtifact] = []
        self.selected_artifact: Optional[FunctionalArtifact] = None
        
        # Режим создания
        self.creation_mode = None
        self.creation_config = {}
        
        # Callbacks
        self.selection_callback = None
        
        # Регистрируем доступные артефакты
        self._register_artifacts()
        
        log.info("Менеджер артефактов инициализирован")
    
    def _register_artifacts(self):
        """Регистрирует все доступные артефакты"""
        ArtifactRegistry.register(FileBrowserArtifact)
        ArtifactRegistry.register(CodeEditorArtifact)
        
        log.info(f"Зарегистрировано артефактов: {len(ArtifactRegistry.get_available())}")
    
    def get_available_artifacts(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает список доступных артефактов для UI.
        
        Returns:
            Dict с информацией об артефактах: {id: {name, icon, description, min_size}}
        """
        available = ArtifactRegistry.get_available()
        result = {}
        
        for artifact_id, artifact_class in available.items():
            result[artifact_id] = {
                'name': getattr(artifact_class, 'ARTIFACT_NAME', artifact_id),
                'icon': getattr(artifact_class, 'ARTIFACT_ICON', '◆'),
                'description': getattr(artifact_class, 'ARTIFACT_DESCRIPTION', 'Артефакт'),
                'min_size': self._get_min_size_for_artifact(artifact_id)
            }
        
        return result
    
    def _get_min_size_for_artifact(self, artifact_id: str) -> Dict[str, int]:
        """Возвращает минимальные размеры для артефакта"""
        constraints = {
            'file_browser': {'width': 250, 'height': 300},
            'code_editor': {'width': 400, 'height': 250},
            'default': {'width': 200, 'height': 150}
        }
        
        return constraints.get(artifact_id, constraints['default'])
    
    def start_creation(self, artifact_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Начинает режим создания артефакта.
        
        Args:
            artifact_id: ID типа артефакта
            config: Дополнительная конфигурация
        """
        if artifact_id not in ArtifactRegistry.get_available():
            log.error(f"Неизвестный тип артефакта: {artifact_id}")
            return False
        
        self.creation_mode = artifact_id
        self.creation_config = config or {}
        
        log.info(f"Начато создание артефакта: {artifact_id}")
        return True
    
    def cancel_creation(self):
        """Отменяет режим создания"""
        self.creation_mode = None
        self.creation_config = {}
    
    def is_creating(self) -> bool:
        """Проверяет активен ли режим создания"""
        return self.creation_mode is not None
    
    def create_artifact_at(self, x: int, y: int, width: int = None, height: int = None) -> Optional[FunctionalArtifact]:
        """
        Создаёт артефакт в указанной позиции.
        
        Args:
            x, y: Позиция на холсте
            width, height: Размеры (если не указаны - используются минимальные)
            
        Returns:
            Созданный артефакт или None при ошибке
        """
        if not self.creation_mode:
            log.error("Режим создания не активен")
            return None
        
        artifact_id = self.creation_mode
        min_size = self._get_min_size_for_artifact(artifact_id)
        
        # Используем размеры или минимальные
        if width is None:
            width = min_size['width']
        if height is None:
            height = min_size['height']
        
        # Применяем ограничения
        width = max(width, min_size['width'])
        height = max(height, min_size['height'])
        
        try:
            # Создаём артефакт
            artifact = ArtifactRegistry.create(
                artifact_id, self.canvas, x, y,
                width=width, height=height,
                config=self.creation_config
            )
            
            if artifact:
                # Добавляем в список
                self.artifacts.append(artifact)
                
                # Настраиваем callback
                artifact.set_change_callback(self._on_artifact_changed)
                
                # Сбрасываем режим создания
                self.cancel_creation()
                
                # Уведомляем о создании
                event_bus.emit('artifact.created', {'artifact': artifact})
                
                log.info(f"Артефакт создан: {artifact_id} в ({x}, {y})")
                return artifact
            
        except Exception as e:
            log.error(f"Ошибка создания артефакта {artifact_id}: {e}")
        
        return None
    
    def get_artifact_at(self, x: int, y: int) -> Optional[FunctionalArtifact]:
        """Находит артефакт в указанной точке"""
        for artifact in reversed(self.artifacts):  # Последние созданные сверху
            ax, ay, aw, ah = artifact.get_bounds()
            if ax <= x <= ax + aw and ay <= y <= ay + ah:
                return artifact
        return None
    
    def select_artifact(self, artifact: Optional[FunctionalArtifact]):
        """Выбирает артефакт"""
        if self.selected_artifact:
            self.selected_artifact.deselect()
        
        self.selected_artifact = artifact
        
        if artifact:
            artifact.select()
        
        # Уведомляем callback
        if self.selection_callback:
            self.selection_callback(artifact)
        
        # Уведомляем систему
        event_bus.emit('artifact.selected', {'artifact': artifact})
    
    def delete_artifact(self, artifact: FunctionalArtifact):
        """Удаляет артефакт"""
        if artifact in self.artifacts:
            self.artifacts.remove(artifact)
            
            if self.selected_artifact == artifact:
                self.selected_artifact = None
            
            # Удаляем из реестра
            ArtifactRegistry.remove(artifact)
            
            # Уведомляем
            event_bus.emit('artifact.deleted', {'artifact': artifact})
            
            log.info(f"Артефакт удалён: {artifact.ARTIFACT_ID}")
    
    def get_all_artifacts(self) -> List[FunctionalArtifact]:
        """Возвращает все артефакты"""
        return self.artifacts.copy()
    
    def clear_all(self):
        """Удаляет все артефакты"""
        for artifact in self.artifacts.copy():
            self.delete_artifact(artifact)
    
    def set_selection_callback(self, callback):
        """Устанавливает callback для выбора артефактов"""
        self.selection_callback = callback
    
    def _on_artifact_changed(self, artifact: FunctionalArtifact):
        """Обработчик изменения артефакта"""
        event_bus.emit('artifact.updated', {'artifact': artifact})
    
    def get_artifact_config(self, artifact: FunctionalArtifact) -> Dict[str, Any]:
        """Возвращает конфигурацию артефакта для сохранения"""
        return artifact.get_config()
    
    def restore_artifact_from_config(self, config: Dict[str, Any]) -> Optional[FunctionalArtifact]:
        """Восстанавливает артефакт из конфигурации"""
        try:
            artifact_id = config.get('artifact_id')
            if not artifact_id:
                return None
            
            artifact = ArtifactRegistry.create(
                artifact_id, self.canvas,
                config.get('x', 0), config.get('y', 0),
                width=config.get('width', 300),
                height=config.get('height', 400),
                config=config.get('config', {})
            )
            
            if artifact:
                # Восстанавливаем состояние
                if config.get('locked', False):
                    artifact._locked = True
                
                self.artifacts.append(artifact)
                artifact.set_change_callback(self._on_artifact_changed)
                
                log.info(f"Артефакт восстановлен: {artifact_id}")
                return artifact
                
        except Exception as e:
            log.error(f"Ошибка восстановления артефакта: {e}")
        
        return None


# Глобальный экземпляр
_artifact_manager = None

def get_artifact_manager_integrated(canvas=None, config=None):
    """Получить глобальный экземпляр ArtifactManagerIntegrated"""
    global _artifact_manager
    if _artifact_manager is None and canvas and config:
        _artifact_manager = ArtifactManagerIntegrated(canvas, config)
    return _artifact_manager
