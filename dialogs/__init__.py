#!/usr/bin/env python3
"""
Модуль диалоговых окон
Диалоги настройки элементов и другие модальные окна
"""
from .button_config_dialog import ButtonConfigDialog, show_button_config
from .frame_config_dialog import FrameConfigDialog, show_frame_config
from .panel_config_dialog import PanelConfigDialog, show_panel_config
from .image_config_dialog import ImageConfigDialog, show_image_config
from .visibility_dialog import VisibilityDialog, show_visibility_dialog
from .scroll_area_config_dialog import ScrollAreaConfigDialog, show_scroll_area_config
from .artifact_dialog import SaveArtifactDialog, ArtifactBrowserDialog, show_save_artifact_dialog, show_artifact_browser
from .state_switcher_config_dialog import StateSwitcherConfigDialog, show_state_switcher_config
from .element_extended_dialog import ElementExtendedDialog, show_element_extended_dialog
from .action_config_dialog import ActionConfigDialog, show_action_config

