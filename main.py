import helpers
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from typing import Union
import numpy as np
import os
import re
import math
import appdirs
from pathvalidate import sanitize_filename, sanitize_filepath
from pathlib import Path
from collections import deque

BOARDADJUSTBUTTON = pygame.event.custom_type()

class SettingsWindow(pygame_gui.elements.UIWindow):
    def on_close_window_button_pressed(self):
        self.hide()

    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class WrappedScrollContainer(pygame_gui.elements.ui_scrolling_container.UIScrollingContainer):
    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class PNGFilePicker(pygame_gui.windows.ui_file_dialog.UIFileDialog):
    def update_current_file_list(self):
        """
        Updates the currently displayed list of files and directories. Usually called when the
        directory path has changed.
        """
        try:
            directories_on_path = [f.name for f in Path(self.current_directory_path).iterdir()
                                   if not f.is_file()]
            directories_on_path = sorted(directories_on_path, key=str.casefold)
            directories_on_path_tuples = [(f, '#directory_list_item') for f in directories_on_path]

            files_on_path = [f.name for f in Path(self.current_directory_path).iterdir()
                             if f.is_file() and f.name.lower().endswith('.png')]
            files_on_path = sorted(files_on_path, key=str.casefold)
            files_on_path_tuples = [(f, '#file_list_item') for f in files_on_path]

            self.current_file_list = directories_on_path_tuples + files_on_path_tuples
        except (PermissionError, FileNotFoundError):
            self.current_directory_path = self.last_valid_directory_path
            self.update_current_file_list()
        else:
            self.last_valid_directory_path = self.current_directory_path

class ChooseFileNameWindow(pygame_gui.elements.UIWindow):
    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'Choose file name',
                 object_id: Union[ObjectID, str] = ObjectID('#file_name_dialog', None),
                 visible: int = 1,
                 width: int = 500,
                 height: int = 500,
                 save_path: str = None):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        self.save_path = save_path
        starting_w = self.get_abs_rect().width
        self.set_dimensions((width, height))

        self.message = pygame_gui.elements.ui_label.UILabel(text='Enter file name:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'})
        self.file_name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 10), (self.get_real_width() - 20, 30)), manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.message})
        self.ok_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='OK', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.file_name_entry, 'top_target': self.message})
        self.cancel_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='Cancel', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.ok_button, 'top_target': self.message})

        self.file_name_entry.set_dimensions((self.get_real_width() - self.ok_button.get_abs_rect().width - self.cancel_button.get_abs_rect().width - 40, 30))
        self.ok_button.rebuild()
        self.cancel_button.rebuild()

        min_h = helpers.getHeightOfElements([self.message, self.file_name_entry]) + 65
        self.set_dimensions((starting_w, min_h))
        self.set_minimum_dimensions((250, min_h))

        if self.save_path.lower().endswith('.png') is True:
            default_filename = self.save_path.lower().removesuffix('.png').split('\\')[-1]
            number_end = re.search(r'\d+$', default_filename)
            if number_end is not None:
                default_filename = default_filename.removesuffix(number_end.group())
                number_end = int(number_end.group()) + 1
                default_filename = default_filename + str(number_end) + '.png'

            self.file_name_entry.set_text(default_filename)

            self.save_path = save_path.split('\\')[:-1]
            self.save_path = '\\'.join(self.save_path)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. There are a lot of buttons in the
        file dialog.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        handled = super().process_event(event)

        if ((event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.ok_button) or (event.type == pygame.KEYUP and event.key == pygame.K_RETURN)) and self.file_name_entry.text != '':
            filename = sanitize_filename(self.file_name_entry.get_text())
            if filename.lower().endswith('.png') is not True:
                filename = filename + '.png'

            self.save_path = self.save_path + '\\' + filename
            self.save_path = sanitize_filepath(self.save_path, platform='auto')

            event_data = {'text': self.save_path,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame_gui.UI_FILE_DIALOG_PATH_PICKED, event_data))

            self.kill()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.cancel_button:
            self.kill()

        return handled

    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class ActionWindow(pygame_gui.elements.UIWindow):
    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'Board selection actions',
                 object_id: Union[ObjectID, str] = ObjectID('#actions_dialog', None),
                 visible: int = 1,
                 width: int = 500,
                 height: int = 500,
                 ):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        starting_w = self.get_abs_rect().width
        self.set_dimensions((width, height))

        self.message = pygame_gui.elements.ui_label.UILabel(text='Choose an action:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'})
        self.zoom_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='Zoom', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.message})
        self.set_custom_board_size_entries_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='#', tool_tip_text='Set the custom board size settings to the board\'s current size', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.zoom_button, 'top_target': self.message})

        self.plus_top_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ top row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.zoom_button})
        self.plus_bottom_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ bottom row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_top_row_button, 'top_target': self.zoom_button})
        self.plus_left_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ left column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_bottom_row_button, 'top_target': self.zoom_button})
        self.plus_right_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ right column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_left_column_button, 'top_target': self.zoom_button})

        self.minus_top_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- top row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.plus_top_row_button})
        self.minus_bottom_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- bottom row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_top_row_button, 'top_target': self.plus_top_row_button})
        self.minus_left_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- left column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_bottom_row_button, 'top_target': self.plus_top_row_button})
        self.minus_right_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- right column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_left_column_button, 'top_target': self.plus_top_row_button})

        min_h = helpers.getHeightOfElements([self.message, self.zoom_button, self.plus_top_row_button, self.minus_top_row_button]) + 65
        self.set_dimensions((starting_w, min_h))
        self.set_minimum_dimensions((250, min_h))

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. There are a lot of buttons in the
        file dialog.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        handled = super().process_event(event)

        side = None
        plus = None

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.plus_top_row_button:
            side = 'Top'
            plus = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.plus_bottom_row_button:
            side = 'Bottom'
            plus = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.plus_left_column_button:
            side = 'Left'
            plus = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.plus_right_column_button:
            side = 'Right'
            plus = True

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.minus_top_row_button:
            side = 'Top'
            plus = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.minus_bottom_row_button:
            side = 'Bottom'
            plus = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.minus_left_column_button:
            side = 'Left'
            plus = False

        elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.minus_right_column_button:
            side = 'Right'
            plus = False

        if side is not None and plus is not None:
            event_data = {'side': side,
                          'plus': plus,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(BOARDADJUSTBUTTON, event_data))

        return handled

    def get_width(self):
        return self.get_relative_rect().width - 30

    def get_height(self):
        return self.get_relative_rect().height - 58

def main():
    # Set up pygame
    pygame.init()
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Personal Game Of Life")
    surf = pygame.display.set_mode((0, 0))
    infoObject = pygame.display.Info()
    w = infoObject.current_w
    h = infoObject.current_h
    manager = pygame_gui.UIManager((w, h))

    clock = pygame.time.Clock()
    time_delta_stack = deque([])
    step_stack = deque([])
    running = True

    Continuous = True
    WasContinuous = True
    Update = True
    Step = False
    StepBack = False
    NewBoard = False
    EditMode = False
    MenuOpen = False
    ClearBoard = False
    ClearHistory = False
    QuickSave = False
    QuickLoad = False
    CurrentBoardSurf = None
    LeftClickHeldDown = [False, 0]
    SelectionBoxPresent = False
    ActionWindowAlive = False
    AdjustBoard = False
    AdjustBoardTuple = None
    Zoom = False
    time_delta_added = 0

    save_location = None
    file_name_window = None
    action_window = None

    config_file_dir = appdirs.user_data_dir("PersonalGOL", "jsyocum")
    config_file_path = config_file_dir + '\\config.ini'
    print('Config file path:', config_file_path)

    quick_save_path = config_file_dir + '\\quick_save.png'
    DefaultSavePath = os.path.expanduser("~/Desktop")
    if os.path.exists(DefaultSavePath) is not True:
        DefaultSavePath = DefaultSavePath.removesuffix("/Desktop") + "\OneDrive\Desktop"

    DefaultScale = 20
    DefaultMaxFps = 18
    DefaultLikelihood = 5

    DefaultColorR = 255
    DefaultColorG = 255
    DefaultColorB = 255
    DefaultRandomColorByPixel = False

    DefaultCustomBoardSizeWidth = int(w / DefaultScale)
    DefaultCustomBoardSizeHeight = int(h / DefaultScale)

    DefaultEditCheckerboardBrightness = 15
    MaxEditCheckerboardBrightness = 200

    config_dict = {
        "Scale": [DefaultScale, 80],
        "MaxFps": [DefaultMaxFps, 50],
        "Likelihood": [DefaultLikelihood, 30],
        "R": [DefaultColorR, 255],
        "G": [DefaultColorG, 255],
        "B": [DefaultColorB, 255],
        "RandomColorByPixel": [DefaultRandomColorByPixel, False],
        "CustomBoardSizeWidth": [DefaultCustomBoardSizeWidth, w],
        "CustomBoardSizeHeight": [DefaultCustomBoardSizeHeight, h],
        "CustomBoardSizeEnabled": [False, False],
        "EditCheckerboardBrightness": [DefaultEditCheckerboardBrightness, 200]
    }

    helpers.initialConfigCheck(config_file_dir, config_file_path, config_dict)


    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show settings', manager=manager, visible=0)
    edit_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Enable edit mode (E)', manager=manager, visible=0)
    save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 200), (400, 50)), text='Save board', manager=manager, visible=0)
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 250), (400, 50)), text='Load board', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 300), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, edit_mode_button, save_button, load_button, quit_game_button]


    settings_window_actual = SettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, resizable=True, window_display_title='Settings', visible=0)
    settings_window_actual.set_minimum_dimensions((330, 200))
    settings_window_actual.set_dimensions((w, h))
    settings_window = WrappedScrollContainer(relative_rect=pygame.Rect((0, 0), (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())), manager=manager, container=settings_window_actual, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

    parameters_warning_text = pygame_gui.elements.ui_text_box.UITextBox('<font face=arial color=regular_text><font color=#989898 size=2>'
                                                                        '<b>Changing scale, likelihood, or board size will reset the board</b></font></font>',
                                                                        pygame.Rect((10, 10), (settings_window.get_real_width() - 10, -1)), manager=manager, container=settings_window)

    parameters_scale_text = pygame_gui.elements.ui_label.UILabel(text='Scale:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_warning_text})
    parameters_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["Scale"][0], value_range=(1, 80), manager=manager, container=settings_window, click_increment=5, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_text})
    parameters_scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 200', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultScale), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_scale_text})

    parameters_max_fps_text = pygame_gui.elements.ui_label.UILabel(text='Max fps:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_slider})
    parameters_max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["MaxFps"][0], value_range=(1, 50), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_text})
    parameters_max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 1000', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultMaxFps), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_max_fps_text})

    parameters_likelihood_text = pygame_gui.elements.ui_label.UILabel(text='Likelihood:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_slider})
    parameters_likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["Likelihood"][0], value_range=(1, 30), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_text})
    parameters_likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 100', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultLikelihood), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_text})

    parameters_color_text = pygame_gui.elements.ui_label.UILabel(text='Color:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_slider})
    parameters_color_picker_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-110, 10), (50, 25)), text='...', manager=manager, container=settings_window, tool_tip_text='Use a color picker to choose a color.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_random_cell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to randomize the color of each cell.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default: White', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_picker_dialog = None
    color = pygame.Color(config_dict["R"][0], config_dict["G"][0], config_dict["B"][0])

    parameters_custom_board_size_text = pygame_gui.elements.ui_label.UILabel(text='Set custom board size:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_color_text})
    parameters_custom_board_size_enable_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to enter a custom board size. Disables scale option.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_color_text})
    parameters_custom_board_size_width_text = pygame_gui.elements.ui_label.UILabel(text='Width:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_height_text = pygame_gui.elements.ui_label.UILabel(text='Height:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeHeight"][0], value_range=(1, h), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                                               'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                                               'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_height_slider, 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeWidth"][0], value_range=(1, w), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                                             'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                                             'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_width_slider, 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry.set_text(str(config_dict["CustomBoardSizeWidth"][0]))
    parameters_custom_board_size_height_entry.set_text(str(config_dict["CustomBoardSizeHeight"][0]))
    for element in [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry]: element.disable()

    settings_window_actual.set_dimensions(settings_window_actual.minimum_dimensions)
    parameters_warning_text.set_dimensions((settings_window.get_real_width() - 10, -1))
    parameters_warning_text.rebuild()

    all_parameters_height_references = [parameters_warning_text, parameters_scale_text, parameters_scale_slider, parameters_max_fps_text, parameters_max_fps_slider,
                                        parameters_likelihood_text, parameters_likelihood_slider, parameters_color_text,
                                        parameters_custom_board_size_text, parameters_custom_board_size_width_text, parameters_custom_board_size_height_text]
    parameters_height_total = helpers.getHeightOfElements(all_parameters_height_references) + 10
    settings_window_actual.set_dimensions((settings_window_actual.minimum_dimensions[0], parameters_height_total))
    settings_window.set_scrollable_area_dimensions((settings_window_actual.minimum_dimensions[0], parameters_height_total))

    previousSettingsWindowDimensions = None
    previousScaleSliderValue = None
    previousScaleEntryValue = None
    previousMaxFpsSliderValue = None
    previousMaxFpsEntryValue = None
    previousLikelihoodSliderValue = None
    previousLikelihoodEntryValue = None
    previousCustomBoardSizeWidthSliderValue = None
    previousCustomBoardSizeWidthEntryValue = None
    previousCustomBoardSizeHeightSliderValue = None
    previousCustomBoardSizeHeightEntryValue = None

    HeldDownCells = []

    previousWidth = int(w / config_dict["Scale"][0])
    previousHeight = int(h / config_dict["Scale"][0])

    pausedLikelihoodSliderValue = DefaultLikelihood

    all_parameters_color_elements = [parameters_color_random_cell_button, parameters_color_default_button, parameters_color_picker_button]

    all_parameters_entries = [[parameters_scale_entry, 1, 80], [parameters_max_fps_entry, 1, 50], [parameters_likelihood_entry, 1, 30],
                              [parameters_custom_board_size_width_entry, 1, w], [parameters_custom_board_size_height_entry, 1, h]]

    all_parameters_elements_matched = [[parameters_scale_slider, parameters_scale_entry, previousScaleSliderValue, previousScaleEntryValue],
                                       [parameters_max_fps_slider, parameters_max_fps_entry, previousMaxFpsSliderValue, previousMaxFpsEntryValue],
                                       [parameters_likelihood_slider, parameters_likelihood_entry, previousLikelihoodSliderValue, previousLikelihoodEntryValue],
                                       [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, previousCustomBoardSizeWidthSliderValue, previousCustomBoardSizeWidthEntryValue],
                                       [parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry, previousCustomBoardSizeHeightSliderValue, previousCustomBoardSizeHeightEntryValue]]

    all_buttons_with_tool_tips = {parameters_scale_slider_size_button, parameters_scale_default_button, parameters_max_fps_default_button,
                                  parameters_likelihood_default_button, parameters_max_fps_slider_size_button, parameters_likelihood_slider_size_button,
                                  parameters_custom_board_size_enable_button,
                                  parameters_color_random_cell_button, parameters_color_default_button, parameters_color_picker_button}

    for entry in all_parameters_entries: entry[0].set_allowed_characters('numbers')


    sidebar_header_font = pygame.font.SysFont('arial', size=30, bold=True)
    sidebar_font = pygame.font.SysFont('arial', size=18)

    controls_header_text = sidebar_header_font.render("Controls", True, (190, 190, 190))
    controls_pause_text = sidebar_font.render("Pause: SPACEBAR", True, (152, 152, 152))
    controls_step_forward_text = sidebar_font.render("Step forward: W", True, (152, 152, 152))
    controls_step_backward_text = sidebar_font.render("Step backwards: S", True, (152, 152, 152))
    controls_reset_text = sidebar_font.render("Reset: R", True, (152, 152, 152))
    controls_increase_max_fps_text = sidebar_font.render("+ max fps: MWHEELUP", True, (152, 152, 152))
    controls_decrease_max_fps_text = sidebar_font.render("-  max fps: MWHEELDOWN", True, (152, 152, 152))
    controls_edit_mode_text = sidebar_font.render("Toggle edit mode: E", True, (152, 152, 152))
    controls_clear_board_text = sidebar_font.render("Clear board: C", True, (152, 152, 152))
    controls_clear_history_text = sidebar_font.render("Clear history: V", True, (152, 152, 152))
    controls_quick_save_text = sidebar_font.render("Quick save: F5", True, (152, 152, 152))
    controls_quick_load_text = sidebar_font.render("Quick load: F6", True, (152, 152, 152))
    controls_rect = pygame.Rect((w / 2 - 510, h / 4 + 2), (300, 400))

    controls_text_array = [controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text, controls_increase_max_fps_text,
                           controls_decrease_max_fps_text, controls_edit_mode_text, controls_clear_board_text, controls_clear_history_text,
                           controls_quick_save_text, controls_quick_load_text]

    CustomBoardSizeEnabledDict = False
    RandomColorByPixelDict = False

    if config_dict["CustomBoardSizeEnabled"][0] is True:
        CustomBoardSizeEnabledDict = True
        parameters_scale_entry.set_text(str(config_dict["Scale"][0]))
        previousWidth = config_dict["CustomBoardSizeWidth"][0]
        previousHeight = config_dict["CustomBoardSizeHeight"][0]

    if config_dict["RandomColorByPixel"][0] is True:
        RandomColorByPixelDict = True

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    if config_dict["CustomBoardSizeEnabled"][0] is False:
        Board = helpers.generateArray(int(h / config_dict["Scale"][0]), int(w / config_dict["Scale"][0]), config_dict["Likelihood"][0])
    else:
        Board = helpers.generateArray(config_dict["CustomBoardSizeHeight"][0], config_dict["CustomBoardSizeWidth"][0], config_dict["Likelihood"][0])

    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)
    step_stack.append(Board.copy())

    while running:
        time_delta = clock.tick(120) / 1000.0
        time_delta_stack.append(time_delta)
        if len(time_delta_stack) > 2000:
            time_delta_stack.popleft()

        time_delta_added = time_delta_added + time_delta
        if time_delta_added >= (1 / parameters_max_fps_slider.get_current_value()):
            Update = True
            time_delta_added = 0

        save_load_windows = [save_location, file_name_window]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if MenuOpen is False:
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    Continuous = not Continuous
                    EditMode = False
                    edit_mode_button.set_text('Enable edit mode (E)')
                elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                    Step = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_s:
                    StepBack = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_r:
                    NewBoard = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_c:
                    if EditMode is True:
                        ClearBoard = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_v:
                    ClearHistory = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_F5:
                    QuickSave = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_F6:
                    QuickLoad = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                    if Continuous is True and EditMode is False:
                        WasContinuous = True
                        Continuous = False
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                    elif Continuous is False and EditMode is False:
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                        print(WasContinuous)
                    elif EditMode is True:
                        Continuous = WasContinuous
                        WasContinuous = False
                        EditMode = False
                        HeldDownCells = []
                        edit_mode_button.set_text('Enable edit mode (E)')

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    LeftClickHeldDown = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    LeftClickHeldDown = False

            if len(HeldDownCells) < 2:
                SelectionBoxPresent = False

            if helpers.anyAliveElements([action_window]) is True:
                ActionWindowAlive = True

            if (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_to_game_button):
                if MenuOpen is False:
                    if EditMode is False:
                        WasContinuous = Continuous
                        Continuous = False

                    LeftClickHeldDown = False
                    if len(HeldDownCells) == 2:
                        SelectionBoxPresent = True

                    pausedLikelihoodSliderValue = parameters_likelihood_slider.get_current_value()

                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show settings')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)
                    if EditMode is False:
                        Continuous = WasContinuous

                    MenuOpen = CloseUIElements(all_menu_buttons)
                    settings_window_actual.hide()
                    if parameters_color_picker_dialog is not None: parameters_color_picker_dialog.kill()
                    if save_location is not None: save_location.kill()
                    if file_name_window is not None: file_name_window.kill()

                    for entryArray in all_parameters_entries[3:]:
                        helpers.manageNumberEntry(entryArray)

                    if parameters_custom_board_size_enable_button.text == '[ ]':
                        if ((int(w / previousWidth) != parameters_scale_slider.get_current_value()) and (int(h / previousHeight) != parameters_scale_slider.get_current_value())) or (pausedLikelihoodSliderValue != parameters_likelihood_slider.get_current_value()):
                            previousWidth = math.floor(w / parameters_scale_slider.get_current_value())
                            previousHeight = math.floor(h / parameters_scale_slider.get_current_value())
                            NewBoard = True
                    elif (previousWidth != int(parameters_custom_board_size_width_entry.get_text())) or (previousHeight != int(parameters_custom_board_size_height_entry.get_text())):
                        previousWidth = math.floor(int(parameters_custom_board_size_width_entry.get_text()))
                        previousHeight = math.floor(int(parameters_custom_board_size_height_entry.get_text()))
                        NewBoard = True

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

                if show_parameters_button.text == 'Hide settings':
                    show_parameters_button.set_text('Show settings')
                    settings_window_actual.hide()

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject, EditMode)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show settings':
                show_parameters_button.set_text('Hide settings')
                settings_window_actual.show()

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                show_parameters_button.set_text('Show settings')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject, EditMode)
                settings_window_actual.hide()

            if ((event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == edit_mode_button) or (MenuOpen is True and event.type == pygame.KEYUP and event.key == pygame.K_e and helpers.anyAliveElements(save_load_windows) is False)) and edit_mode_button.text == 'Enable edit mode (E)':
                edit_mode_button.set_text('Disable edit mode (E)')
                EditMode = True

            elif (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == edit_mode_button) or (MenuOpen is True and event.type == pygame.KEYUP and event.key == pygame.K_e and helpers.anyAliveElements(save_load_windows) is False):
                edit_mode_button.set_text('Enable edit mode (E)')
                EditMode = False
                HeldDownCells = []

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == save_button and helpers.anyAliveElements(save_load_windows) is False:
                save_location = PNGFilePicker(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, window_title='Pick save location', initial_file_path=DefaultSavePath, allow_picking_directories=True)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == save_location and save_location.window_display_title == 'Pick save location':
                save_path = event.text
                file_name_window = ChooseFileNameWindow(pygame.Rect((w / 2 - 80, h / 2 + 25), (600, 50)), manager=manager, window_title='Choose a filename to put in ' + save_path, width=w, height=h, save_path=save_path)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == file_name_window:
                save_path = event.text
                boardsurf_to_save = helpers.updateScreenWithBoard(Board, surf, infoObject, EditMode=True, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], Saving=True)
                helpers.savePNGWithBoardInfo(save_path, boardsurf_to_save, step_stack[-1])

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == load_button and helpers.anyAliveElements(save_load_windows) is False:
                save_location = PNGFilePicker(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, window_title='Pick .PNG board file', initial_file_path=DefaultSavePath, allow_picking_directories=False)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == save_location and save_location.window_display_title == 'Pick .PNG board file':
                load_path = event.text
                WasContinuous, load_status_message = helpers.loadPNGWithBoardInfo(load_path, step_stack, WasContinuous)
                print(load_status_message)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_slider_size_button:
                if parameters_scale_slider_size_button.text == '[ ]':
                    parameters_scale_slider_size_button.text = '[X]'
                    parameters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 80'
                    parameters_scale_slider.value_range = (1, 200)
                else:
                    parameters_scale_slider_size_button.text = '[ ]'
                    parameters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 200'
                    parameters_scale_slider_size_button.rebuild()
                    parameters_scale_slider.value_range = (1, 80)

                parameters_scale_slider_size_button.rebuild()
                parameters_scale_slider.rebuild()

            if event.type == pygame.MOUSEBUTTONUP and MenuOpen is False:
                if EditMode is False:
                    current_max_fps = parameters_max_fps_slider.get_current_value()
                    max_fps_slider_range = parameters_max_fps_slider.value_range
                    if event.button == 4:
                        parameters_max_fps_slider.set_current_value(min(current_max_fps + 1, max_fps_slider_range[1]))
                    elif event.button == 5:
                        parameters_max_fps_slider.set_current_value(max(current_max_fps - 1, max_fps_slider_range[0]))

                elif event.button == 1 and len(HeldDownCells) < 2 and SelectionBoxPresent is False:
                    mouse_pos = pygame.mouse.get_pos()
                    IsColliding, IsCollidingWithActionWindow, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h)
                    if IsColliding and not IsCollidingWithActionWindow:
                        board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)
                        if step_stack[-1][board_pos[0]][board_pos[1]] == 0:
                            step_stack[-1][board_pos[0]][board_pos[1]] = 1
                        else:
                            step_stack[-1][board_pos[0]][board_pos[1]] = 0

                    HeldDownCells = []

                elif event.button == 1 and len(HeldDownCells) == 2 and SelectionBoxPresent is False:
                    SelectionBoxPresent = True
                elif event.button == 1 and len(HeldDownCells) == 2 and SelectionBoxPresent is True and not helpers.isMouseCollidingWithActionWindow(action_window, pygame.mouse.get_pos()):
                    HeldDownCells = []
                    SelectionBoxPresent = False
                elif event.button == 4:
                    config_dict["EditCheckerboardBrightness"][0] = min(config_dict["EditCheckerboardBrightness"][0] + 1, MaxEditCheckerboardBrightness)
                elif event.button == 5:
                    config_dict["EditCheckerboardBrightness"][0] = max(config_dict["EditCheckerboardBrightness"][0] - 1, 0)

            if LeftClickHeldDown is True and EditMode is True and MenuOpen is False and SelectionBoxPresent is False:
                mouse_pos = pygame.mouse.get_pos()
                IsColliding, IsCollidingWithActionWindow, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h)
                if IsColliding and not IsCollidingWithActionWindow:
                    board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)

                    if len(HeldDownCells) < 2 and board_pos not in HeldDownCells:
                        HeldDownCells.append(board_pos)
                    elif len(HeldDownCells) == 2 and board_pos == HeldDownCells[0]:
                        HeldDownCells.pop(1)
                    elif len(HeldDownCells) == 2:
                        HeldDownCells[1] = board_pos

            if event.type == pygame.MOUSEBUTTONUP and settings_window.vert_scroll_bar is not None:
                mouse_pos = pygame.mouse.get_pos()
                if settings_window.rect.collidepoint(mouse_pos):
                    scroll_amount = settings_window.vert_scroll_bar.bottom_limit / 30
                    if event.button == 4:
                        settings_window.vert_scroll_bar.scroll_position = max(settings_window.vert_scroll_bar.scroll_position - scroll_amount, 0)

                    elif event.button == 5:
                        settings_window.vert_scroll_bar.scroll_position = min(settings_window.vert_scroll_bar.scroll_position + scroll_amount, settings_window.vert_scroll_bar.bottom_limit - settings_window.vert_scroll_bar.sliding_button.rect.height)

                    settings_window.vert_scroll_bar.start_percentage = settings_window.vert_scroll_bar.scroll_position / settings_window.vert_scroll_bar.scrollable_height
                    settings_window.vert_scroll_bar.has_moved_recently = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_slider_size_button:
                if parameters_max_fps_slider_size_button.text == '[ ]':
                    parameters_max_fps_slider_size_button.text = '[X]'
                    parameters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 50'
                    parameters_max_fps_slider.value_range = (1, 1000)
                else:
                    parameters_max_fps_slider_size_button.text = '[ ]'
                    parameters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 1000'
                    parameters_max_fps_slider.value_range = (1, 50)

                parameters_max_fps_slider_size_button.rebuild()
                parameters_max_fps_slider.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_slider_size_button:
                if parameters_likelihood_slider_size_button.text == '[ ]':
                    parameters_likelihood_slider_size_button.text = '[X]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 30'
                    parameters_likelihood_slider.value_range = (1, 100)
                else:
                    parameters_likelihood_slider_size_button.text = '[ ]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 100'
                    parameters_likelihood_slider.value_range = (1, 30)

                parameters_likelihood_slider_size_button.rebuild()
                parameters_likelihood_slider.rebuild()

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_custom_board_size_enable_button) or CustomBoardSizeEnabledDict is True:
                CustomBoardSizeEnabledDict = False
                scale_elements = [parameters_scale_slider, parameters_scale_entry, parameters_scale_slider_size_button, parameters_scale_default_button]
                custom_board_size_elements = [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry]

                if parameters_custom_board_size_enable_button.text == '[ ]':
                    parameters_custom_board_size_enable_button.text = '[X]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Disable to use the scale option instead.'
                    for element in scale_elements:
                        element.disable()
                        element.rebuild()
                        element.enable()
                        element.disable()
                    for element in custom_board_size_elements: element.enable()
                    config_dict["CustomBoardSizeEnabled"][0] = True
                else:
                    parameters_custom_board_size_enable_button.text = '[ ]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Enable to enter a custom board size. Disables scale option.'
                    for element in scale_elements: element.enable()
                    for element in custom_board_size_elements:
                        element.disable()
                        element.rebuild()
                        element.enable()
                        element.disable()
                    config_dict["CustomBoardSizeEnabled"][0] = False

                parameters_custom_board_size_enable_button.rebuild()

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_random_cell_button) or RandomColorByPixelDict is True:
                RandomColorByPixelDict = False
                if parameters_color_random_cell_button.text == '[ ]':
                    parameters_color_random_cell_button.text = '[X]'
                    parameters_color_random_cell_button.tool_tip_text = 'Disable to go back to using normal colors.'
                    for element in all_parameters_color_elements[1:]: element.disable()
                    config_dict["RandomColorByPixel"][0] = True
                else:
                    parameters_color_random_cell_button.text = '[ ]'
                    parameters_color_random_cell_button.tool_tip_text = 'Enable to randomize the color of each cell.'
                    for element in all_parameters_color_elements[1:]: element.enable()
                    config_dict["RandomColorByPixel"][0] = False

                parameters_color_random_cell_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_picker_button:
                parameters_color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, initial_colour=color, window_title='Pick a color...')
                for element in all_parameters_color_elements: element.disable()

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == parameters_color_picker_dialog and config_dict["RandomColorByPixel"][0] is False:
                for element in all_parameters_color_elements: element.enable()

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == action_window:
                HeldDownCells = []
                ActionWindowAlive = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and ActionWindowAlive is True and event.ui_element == action_window.zoom_button:
                Zoom = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and ActionWindowAlive is True and event.ui_element == action_window.set_custom_board_size_entries_button:
                current_width = step_stack[-1].shape[0]
                current_height = step_stack[-1].shape[1]

                parameters_custom_board_size_width_entry.set_text(str(current_width))
                parameters_custom_board_size_height_entry.set_text(str(current_height))

                config_dict["CustomBoardSizeWidth"][0] = current_width
                config_dict["CustomBoardSizeHeight"][0] = current_height

                helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)

            if event.type == BOARDADJUSTBUTTON and event.ui_element == action_window:
                AdjustBoard = True
                AdjustBoardTuple = (event.side, event.plus)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_default_button: parameters_scale_slider.set_current_value(DefaultScale)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_default_button: parameters_max_fps_slider.set_current_value(DefaultMaxFps)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_default_button: parameters_likelihood_slider.set_current_value(DefaultLikelihood)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_default_button: color = pygame.Color(DefaultColorR, DefaultColorG, DefaultColorB)

            if (event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED or event.type == pygame_gui.UI_BUTTON_PRESSED) and (event.ui_element in all_buttons_with_tool_tips) and (show_parameters_button.text == 'Hide parameters') and (MenuOpen is not False):
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject, EditMode)

            manager.process_events(event)

        manager.update(time_delta)

        if (Continuous is False) and (Step is True):
            helpers.applyRules(step_stack[-1], step_stack)
            Step = False
        elif (Continuous is False) and (StepBack is True):
            helpers.stepBack(step_stack)
            StepBack = False
        elif (Continuous is True) and (Update is True):
            helpers.applyRules(step_stack[-1], step_stack)
            Step = False
            StepBack = False
            Update = False

        if SelectionBoxPresent is True:
            if ActionWindowAlive is False and MenuOpen is False:
                action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h)
            elif ActionWindowAlive is True and MenuOpen is True:
                action_window.kill()
        else:
            if ActionWindowAlive is True:
                action_window.kill()

        if NewBoard is True:
            Board = helpers.generateArray(previousHeight, previousWidth, parameters_likelihood_slider.get_current_value())
            Board = np.rot90(Board)
            step_stack.clear()
            step_stack.append(Board)
            # CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, EditMode, color=color)
            NewBoard = False

        if Zoom is True:
            x_1, y_1 = HeldDownCells[0][0], HeldDownCells[0][1]
            x_2, y_2 = HeldDownCells[1][0], HeldDownCells[1][1]

            left = min(x_1, x_2)
            right = max(x_1, x_2)
            top = min(y_1, y_2)
            bottom = max(y_1, y_2)

            Board = step_stack[-1][left:right + 1, top:bottom + 1]
            step_stack.append(Board)
            # CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, EditMode, color=color)

            HeldDownCells = []
            Zoom = False

        if AdjustBoard is True:
            Board = helpers.adjustBoardDimensions(step_stack[-1], AdjustBoardTuple)
            step_stack.append(Board)

            AdjustBoard = False

        if ClearBoard is True:
            step_stack.append(np.zeros_like(step_stack[-1]))
            ClearBoard = False

        if ClearHistory is True:
            current_board = step_stack[-1]
            step_stack.clear()
            step_stack.append(current_board)
            ClearHistory = False

        if QuickSave is True:
            print("Quicksaved to:", quick_save_path)
            boardsurf_to_save = helpers.updateScreenWithBoard(Board, surf, infoObject, EditMode=True, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], Saving=True)
            helpers.savePNGWithBoardInfo(quick_save_path, boardsurf_to_save, step_stack[-1])
            QuickSave = False

        if QuickLoad is True:
            load_status_message = None
            if os.path.exists(quick_save_path):
                WasContinuous, load_status_message = helpers.loadPNGWithBoardInfo(quick_save_path, step_stack, WasContinuous)
            else:
                load_status_message = 'No quicksave exists to be loaded!'

            print(load_status_message)
            QuickLoad = False

        CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, EditMode, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], DefaultEditCheckerboardBrightness=config_dict["EditCheckerboardBrightness"][0], SelectedCells=HeldDownCells)
        if MenuOpen is True:
            if show_controls_button.text == 'Hide controls':
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

        ScaledHeldDownCells = helpers.getScaledHeldDownCells(step_stack[-1], CurrentBoardSurf, HeldDownCells, w, h)
        if len(ScaledHeldDownCells) == 2:
            helpers.showSelectionBoxSize(surf, ScaledHeldDownCells, HeldDownCells, sidebar_header_font)


        helpers.manageSliderAndEntryWithArray(all_parameters_elements_matched)
        config_dict["Scale"][0] = all_parameters_elements_matched[0][2] = parameters_scale_slider.get_current_value()
        all_parameters_elements_matched[0][3] = parameters_scale_entry.get_text()
        config_dict["MaxFps"][0] = all_parameters_elements_matched[1][2] = parameters_max_fps_slider.get_current_value()
        all_parameters_elements_matched[1][3] = parameters_max_fps_entry.get_text()
        config_dict["Likelihood"][0] = all_parameters_elements_matched[2][2] = parameters_likelihood_slider.get_current_value()
        all_parameters_elements_matched[2][3] = parameters_likelihood_entry.get_text()
        config_dict["CustomBoardSizeWidth"][0] = all_parameters_elements_matched[3][2] = parameters_custom_board_size_width_slider.get_current_value()
        all_parameters_elements_matched[3][3] = parameters_custom_board_size_width_entry.get_text()
        config_dict["CustomBoardSizeHeight"][0] = all_parameters_elements_matched[4][2] = parameters_custom_board_size_height_slider.get_current_value()
        all_parameters_elements_matched[4][3] = parameters_custom_board_size_height_entry.get_text()

        for entryArray in all_parameters_entries[3:]:
            if entryArray[0].is_focused is not True:
                helpers.manageNumberEntry(entryArray)

        # If the height or width of the settings window has changed...
        if (settings_window_actual.get_real_width(), settings_window_actual.get_real_height()) != previousSettingsWindowDimensions:
            parameters_warning_text.set_dimensions((settings_window.get_real_width() - 10, -1))
            parameters_warning_text.rebuild()
            parameters_scale_slider.rebuild()
            parameters_custom_board_size_width_slider.rebuild()
            parameters_custom_board_size_height_slider.rebuild()

            parameters_height_total = helpers.getHeightOfElements(all_parameters_height_references) + 10
            settings_window_actual.set_dimensions((settings_window_actual.get_relative_rect().width, min(settings_window_actual.get_relative_rect().height, parameters_height_total)))
            settings_window.set_scrollable_area_dimensions((settings_window.get_real_width(), parameters_height_total / 1.145 - 2))

            previousSettingsWindowDimensions = (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())

        config_dict["R"][0], config_dict["G"][0], config_dict["B"][0] = color.r, color.g, color.b

        manager.draw_ui(surf)
        pygame.display.update()


def OpenUIElements(ButtonsArray):
    for button in ButtonsArray:
        button.show()

    return True

def CloseUIElements(ButtonsArray):
    for button in ButtonsArray:
        button.hide()

    return False


if __name__ == "__main__":
    main()
