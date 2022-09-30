import os
import re
import helpers
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIElement, UIContainer
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.elements import UIVerticalScrollBar, UIButton
from pathlib import Path
from typing import Union, Dict, Tuple, List, Iterable
from pathvalidate import sanitize_filename, sanitize_filepath
from copy import deepcopy

class SettingsWindow(pygame_gui.elements.UIWindow):
    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'Settings',
                 object_id: Union[ObjectID, str] = ObjectID('#settings_window', None),
                 visible: int = 1,
                 width: int = 500,
                 height: int = 500,
                 w: int = 0,  # Pixel width of pygame window
                 h: int = 0,  # Pixel height of pygame window
                 config_dict: {} = {},
                 color: pygame.color = None,
                 COLORCHANGED: int = 0,
                 SETTINGSAPPLIED: int = 0):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        self.config_dict = deepcopy(config_dict)
        self.og_config_dict = deepcopy(config_dict)
        self.w = w
        self.h = h
        self.color = color
        self.previous_color = color
        self.og_color = color
        self.COLORCHANGED = COLORCHANGED
        self.SETTINGSAPPLIED = SETTINGSAPPLIED

        self.DefaultScale = 20
        self.DefaultMaxFps = 18
        self.DefaultLikelihood = 5
        self.DefaultColorR = 255
        self.DefaultColorG = 255
        self.DefaultColorB = 255

        if self.config_dict["CustomBoardSizeEnabled"][0] is True:
            self.CustomBoardSizeEnabledDict = True
        else:
            self.CustomBoardSizeEnabledDict = False

        if self.config_dict["RandomColorByPixel"][0] is True:
            self.RandomColorByPixelDict = True
        else:
            self.RandomColorByPixelDict = False

        self.set_dimensions((width, height))
        self.set_minimum_dimensions((330, 200))

        # sc == Scroll Container
        self.sc = WrappedScrollContainer(relative_rect=pygame.Rect((0, 0), (self.get_real_width(), self.get_real_height())), manager=manager, container=self, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

        self.warning_text = pygame_gui.elements.ui_text_box.UITextBox('<font face=arial color=regular_text><font color=#989898 size=2>'
                                                                      '<b>After changing scale, likelihood, or board size, click apply and reset the board with "R" to see the effects.</b></font></font>',
                                                                      pygame.Rect((10, 10), (self.sc.get_real_width() - 10, -1)), manager=manager, container=self.sc)

        self.scale_text = pygame_gui.elements.ui_label.UILabel(text='Scale:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.warning_text})
        scale_slider_size_button_text, scale_slider_size_limit = helpers.determine_slider_button_text_and_limit(80, 200, config_dict["Scale"][0])
        self.scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["Scale"][0], value_range=(1, scale_slider_size_limit), manager=manager, container=self.sc, click_increment=5, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.scale_text})
        self.scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text=scale_slider_size_button_text, manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 200', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.warning_text})
        self.scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(self.DefaultScale), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.warning_text})
        self.scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.scale_text})

        self.max_fps_text = pygame_gui.elements.ui_label.UILabel(text='Max fps:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.scale_slider})
        max_fps_slider_size_button_text, max_fps_slider_size_limit = helpers.determine_slider_button_text_and_limit(50, 1000, config_dict["MaxFps"][0])
        self.max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["MaxFps"][0], value_range=(1, max_fps_slider_size_limit), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.max_fps_text})
        self.max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text=max_fps_slider_size_button_text, manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 1000', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.scale_slider})
        self.max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(self.DefaultMaxFps), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.scale_slider})
        self.max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.max_fps_text})

        self.likelihood_text = pygame_gui.elements.ui_label.UILabel(text='Likelihood:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.max_fps_slider})
        likelihood_slider_size_button_text, likelihood_slider_size_limit = helpers.determine_slider_button_text_and_limit(30, 100, config_dict["Likelihood"][0])
        self.likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["Likelihood"][0], value_range=(1, likelihood_slider_size_limit), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.likelihood_text})
        self.likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text=likelihood_slider_size_button_text, manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 100', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.max_fps_slider})
        self.likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(self.DefaultLikelihood), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.max_fps_slider})
        self.likelihood_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.likelihood_text})

        self.color_text = pygame_gui.elements.ui_label.UILabel(text='Color:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.likelihood_slider})
        self.color_picker_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-110, 10), (50, 25)), text='...', manager=manager, container=self.sc, tool_tip_text='Use a color picker to choose a color.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.likelihood_slider})
        self.color_random_cell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=self.sc, tool_tip_text='Enable to randomize the color of each cell.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.likelihood_slider})
        self.color_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default: White', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.likelihood_slider})
        self.color_picker_dialog = None
        self.color = pygame.Color(config_dict["R"][0], config_dict["G"][0], config_dict["B"][0])

        self.custom_board_size_text = pygame_gui.elements.ui_label.UILabel(text='Set custom board size:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.color_text})
        self.custom_board_size_enable_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='[ ]', manager=manager, container=self.sc, tool_tip_text='Enable to enter a custom board size. Disables scale option.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.color_text})
        self.custom_board_size_width_text = pygame_gui.elements.ui_label.UILabel(text='Width:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.custom_board_size_text})
        self.custom_board_size_height_text = pygame_gui.elements.ui_label.UILabel(text='Height:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.custom_board_size_width_text})
        self.custom_board_size_height_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 50 - self.custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeHeight"][0], value_range=(1, h), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                       'left_target': self.custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                       'top_target': self.custom_board_size_width_text})
        self.custom_board_size_height_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': self.custom_board_size_height_slider, 'top_target': self.custom_board_size_width_text})
        self.custom_board_size_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 50 - self.custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeWidth"][0], value_range=(1, w), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                     'left_target': self.custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                     'top_target': self.custom_board_size_text})
        self.custom_board_size_width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': self.custom_board_size_width_slider, 'top_target': self.custom_board_size_text})
        self.custom_board_size_width_entry.set_text(str(config_dict["CustomBoardSizeWidth"][0]))
        self.custom_board_size_height_entry.set_text(str(config_dict["CustomBoardSizeHeight"][0]))
        for element in [self.custom_board_size_width_slider, self.custom_board_size_width_entry, self.custom_board_size_height_slider, self.custom_board_size_height_entry]: element.disable()

        self.cancel_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 10), (-1, 25)), text='Cancel', manager=manager, container=self.sc, tool_tip_text='Exit without saving changes to settings.', anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.custom_board_size_height_text})
        self.apply_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-5, 10), (-1, 25)), text='Apply', manager=manager, container=self.sc, tool_tip_text='Apply settings.', anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top', 'right_target': self.cancel_button, 'top_target': self.custom_board_size_height_text})

        self.set_dimensions(self.minimum_dimensions)
        self.warning_text.set_dimensions((self.sc.get_real_width() - 10, -1))
        self.warning_text.rebuild()

        self.all_height_references = [self.warning_text, self.scale_text, self.scale_slider, self.max_fps_text, self.max_fps_slider,
                                      self.likelihood_text, self.likelihood_slider, self.color_text,
                                      self.custom_board_size_text, self.custom_board_size_width_text, self.custom_board_size_height_text,
                                      self.apply_button]
        self.height_total = helpers.getHeightOfElements(self.all_height_references) + 10
        self.set_dimensions((self.minimum_dimensions[0], self.height_total))
        self.sc.set_scrollable_area_dimensions((self.minimum_dimensions[0], self.height_total))

        self.previousSettingsWindowDimensions = None
        self.previousScaleSliderValue = None
        self.previousScaleEntryValue = None
        self.previousMaxFpsSliderValue = None
        self.previousMaxFpsEntryValue = None
        self.previousLikelihoodSliderValue = None
        self.previousLikelihoodEntryValue = None
        self.previousCustomBoardSizeWidthSliderValue = None
        self.previousCustomBoardSizeWidthEntryValue = None
        self.previousCustomBoardSizeHeightSliderValue = None
        self.previousCustomBoardSizeHeightEntryValue = None

        self.scale_elements = [self.scale_slider, self.scale_entry, self.scale_slider_size_button, self.scale_default_button]
        self.custom_board_size_elements = [self.custom_board_size_width_slider, self.custom_board_size_width_entry, self.custom_board_size_height_slider, self.custom_board_size_height_entry]

        self.color_elements = [self.color_random_cell_button, self.color_default_button, self.color_picker_button]

        self.all_parameters_entries = [[self.scale_entry, 1, 80], [self.max_fps_entry, 1, 50], [self.likelihood_entry, 1, 30],
                                       [self.custom_board_size_width_entry, 1, w], [self.custom_board_size_height_entry, 1, h]]

        self.all_parameters_elements_matched = [[self.scale_slider, self.scale_entry, self.previousScaleSliderValue, self.previousScaleEntryValue, "Scale"],
                                                [self.max_fps_slider, self.max_fps_entry, self.previousMaxFpsSliderValue, self.previousMaxFpsEntryValue, "MaxFps"],
                                                [self.likelihood_slider, self.likelihood_entry, self.previousLikelihoodSliderValue, self.previousLikelihoodEntryValue, "Likelihood"],
                                                [self.custom_board_size_width_slider, self.custom_board_size_width_entry, self.previousCustomBoardSizeWidthSliderValue, self.previousCustomBoardSizeWidthEntryValue, "CustomBoardSizeWidth"],
                                                [self.custom_board_size_height_slider, self.custom_board_size_height_entry, self.previousCustomBoardSizeHeightSliderValue, self.previousCustomBoardSizeHeightEntryValue, "CustomBoardSizeHeight"]]

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. There are a lot of buttons in the
        file dialog.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        handled = super().process_event(event)

        if event.type == pygame.MOUSEBUTTONUP and self.sc.vert_scroll_bar is not None:
            mouse_pos = pygame.mouse.get_pos()
            if self.sc.rect.collidepoint(mouse_pos):
                scroll_amount = self.sc.vert_scroll_bar.bottom_limit / 30
                if event.button == 4:
                    self.sc.vert_scroll_bar.scroll_position = max(self.sc.vert_scroll_bar.scroll_position - scroll_amount, 0)

                elif event.button == 5:
                    self.sc.vert_scroll_bar.scroll_position = min(self.sc.vert_scroll_bar.scroll_position + scroll_amount, self.sc.vert_scroll_bar.bottom_limit - self.sc.vert_scroll_bar.sliding_button.rect.height)

                self.sc.vert_scroll_bar.start_percentage = self.sc.vert_scroll_bar.scroll_position / self.sc.vert_scroll_bar.scrollable_height
                self.sc.vert_scroll_bar.has_moved_recently = True

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.scale_slider_size_button:
            if self.scale_slider_size_button.text == '[ ]':
                self.scale_slider_size_button.text = '[X]'
                self.scale_slider_size_button.tool_tip_text = 'Change slider maximum to 80'
                self.scale_slider.value_range = (1, 200)
            else:
                self.scale_slider_size_button.text = '[ ]'
                self.scale_slider_size_button.tool_tip_text = 'Change slider maximum to 200'
                self.scale_slider_size_button.rebuild()
                self.scale_slider.value_range = (1, 80)

            self.scale_slider_size_button.rebuild()
            self.scale_slider.rebuild()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.max_fps_slider_size_button:
            if self.max_fps_slider_size_button.text == '[ ]':
                self.max_fps_slider_size_button.text = '[X]'
                self.max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 50'
                self.max_fps_slider.value_range = (1, 1000)
            else:
                self.max_fps_slider_size_button.text = '[ ]'
                self.max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 1000'
                self.max_fps_slider.value_range = (1, 50)

            self.max_fps_slider_size_button.rebuild()
            self.max_fps_slider.rebuild()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.likelihood_slider_size_button:
            if self.likelihood_slider_size_button.text == '[ ]':
                self.likelihood_slider_size_button.text = '[X]'
                self.likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 30'
                self.likelihood_slider.value_range = (1, 100)
            else:
                self.likelihood_slider_size_button.text = '[ ]'
                self.likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 100'
                self.likelihood_slider.value_range = (1, 30)

            self.likelihood_slider_size_button.rebuild()
            self.likelihood_slider.rebuild()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.color_picker_button:
            self.color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((self.w / 2 - 80, self.h / 2 + 25), (420, 400)), manager=self.ui_manager, initial_colour=self.color, window_title='Pick a color...')
            self.og_picker_color = deepcopy(self.color)
            for element in self.color_elements: element.disable()

        if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.color_picker_dialog and self.config_dict["RandomColorByPixel"][0] is False:
            for element in self.color_elements: element.enable()
            self.color = self.og_picker_color

        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED and event.ui_element == self.color_picker_dialog:
            self.og_picker_color = event.colour

        if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.color_random_cell_button) or self.RandomColorByPixelDict is True:
            self.RandomColorByPixelDict = False

            if self.color_random_cell_button.text == '[ ]':
                self.color_random_cell_button.text = '[X]'
                self.color_random_cell_button.tool_tip_text = 'Disable to go back to using normal colors.'
                for element in self.color_elements[1:]: element.disable()
                self.config_dict["RandomColorByPixel"][0] = True
            else:
                self.color_random_cell_button.text = '[ ]'
                self.color_random_cell_button.tool_tip_text = 'Enable to randomize the color of each cell.'
                for element in self.color_elements[1:]: element.enable()
                self.config_dict["RandomColorByPixel"][0] = False

            self.color_random_cell_button.rebuild()

        if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.custom_board_size_enable_button) or self.CustomBoardSizeEnabledDict is True:
            self.CustomBoardSizeEnabledDict = False

            if self.custom_board_size_enable_button.text == '[ ]':
                self.custom_board_size_enable_button.text = '[X]'
                self.likelihood_slider_size_button.tool_tip_text = 'Disable to use the scale option instead.'
                for element in self.scale_elements:
                    element.disable()
                    element.rebuild()
                    element.enable()
                    element.disable()
                for element in self.custom_board_size_elements: element.enable()
                self.config_dict["CustomBoardSizeEnabled"][0] = True
            else:
                self.custom_board_size_enable_button.text = '[ ]'
                self.likelihood_slider_size_button.tool_tip_text = 'Enable to enter a custom board size. Disables scale option.'
                for element in self.scale_elements: element.enable()
                for element in self.custom_board_size_elements:
                    element.disable()
                    element.rebuild()
                    element.enable()
                    element.disable()
                self.config_dict["CustomBoardSizeEnabled"][0] = False

            self.custom_board_size_enable_button.rebuild()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.scale_default_button: self.scale_slider.set_current_value(self.DefaultScale)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.max_fps_default_button: self.max_fps_slider.set_current_value(self.DefaultMaxFps)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.likelihood_default_button: self.likelihood_slider.set_current_value(self.DefaultLikelihood)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.color_default_button: self.color = pygame.Color(self.DefaultColorR, self.DefaultColorG, self.DefaultColorB)

        helpers.manageSliderAndEntryWithArray(self.all_parameters_elements_matched)
        self.all_parameters_elements_matched, self.config_dict = helpers.setParametersValues(self.all_parameters_elements_matched, self.config_dict)

        for entryArray in self.all_parameters_entries[3:]:
            if entryArray[0].is_focused is not True:
                helpers.manageNumberEntry(entryArray)

        # If the height or width of the settings window has changed...
        if (self.get_real_width(), self.get_real_height()) != self.previousSettingsWindowDimensions:
            self.warning_text.set_dimensions((self.sc.get_real_width() - 10, -1))
            self.warning_text.rebuild()
            self.scale_slider.rebuild()
            self.custom_board_size_width_slider.rebuild()
            self.custom_board_size_height_slider.rebuild()

            self.height_total = helpers.getHeightOfElements(self.all_height_references) + 10
            self.set_dimensions((self.get_relative_rect().width, min(self.get_relative_rect().height, self.height_total)))
            self.sc.set_scrollable_area_dimensions((self.sc.get_real_width(), self.height_total / 1.145 - 2))

            self.previousSettingsWindowDimensions = (self.get_real_width(), self.get_real_height())

        self.config_dict["R"][0], self.config_dict["G"][0], self.config_dict["B"][0] = self.color.r, self.color.g, self.color.b
        if self.color != self.previous_color:
            helpers.quick_post(self, 'color', self.color, self.COLORCHANGED)

            self.previous_color = self.color

        if self.config_dict == self.og_config_dict:
            self.apply_button.disable()
        else:
            self.apply_button.enable()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.apply_button:
            helpers.quick_post(self, 'config_dict', self.config_dict, self.SETTINGSAPPLIED)
            self.og_config_dict = self.config_dict

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.cancel_button:
            self.kill()

        return handled

    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class OldSettingsWindow(pygame_gui.elements.UIWindow):
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

            self.save_path = '\\'.join(save_path.split('\\')[:-1])

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

            helpers.quick_post(self, 'text', self.save_path, pygame_gui.UI_FILE_DIALOG_PATH_PICKED)

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
                 window_title: str = 'Edit mode actions',
                 object_id: Union[ObjectID, str] = ObjectID('#actions_dialog', None),
                 visible: int = 1,
                 width: int = 500,
                 height: int = 500,
                 SelMode: bool = True,
                 EraserMode: bool = False,
                 BOARDADJUSTBUTTON: int = 0,
                 AutoAdjust: bool = False,
                 AutoAdjustments: {} = {
                     "Top": 0,
                     "Bottom": 0,
                     "Left": 0,
                     "Right": 0
                 }):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=False,
                         visible=visible)

        self.BOARDADJUSTBUTTON = BOARDADJUSTBUTTON
        self.set_dimensions((width, height))

        # Row 1
        self.message = pygame_gui.elements.ui_label.UILabel(text='Actions:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'})


        # Row 2
        self.zoom_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (-1, 30)), text='Zoom', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.message})


        # Row 3
        self.plus_top_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ top row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.zoom_button})
        self.plus_bottom_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ bottom row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_top_row_button, 'top_target': self.zoom_button})
        self.plus_left_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ left column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_bottom_row_button, 'top_target': self.zoom_button})
        self.plus_right_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='+ right column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.plus_left_column_button, 'top_target': self.zoom_button})


        # Row 4
        self.minus_top_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- top row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.plus_top_row_button})
        self.minus_bottom_row_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- bottom row', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_top_row_button, 'top_target': self.plus_top_row_button})
        self.minus_left_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- left column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_bottom_row_button, 'top_target': self.plus_top_row_button})
        self.minus_right_column_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='- right column', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_left_column_button, 'top_target': self.plus_top_row_button})

        plus_minus_buttons = [self.plus_top_row_button, self.plus_bottom_row_button, self.plus_left_column_button, self.plus_right_column_button,
                              self.minus_top_row_button, self.minus_bottom_row_button, self.minus_left_column_button, self.minus_right_column_button]

        l_w = 0
        for button in plus_minus_buttons:
            b_w = button.get_relative_rect().width
            if b_w > l_w:
                l_w = b_w

        for button in plus_minus_buttons:
            b_h = button.get_relative_rect().height
            button.set_dimensions((b_w, b_h))


        # Row 5
        self.auto_adjust_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (self.minus_top_row_button.get_relative_rect().width, 30)), text='Auto-adjust: [ ]', tool_tip_text='Enable auto-adjust mode to allow the board to automatically resize to fit the cells.',
                                                                    manager=self.ui_manager, object_id=pygame_gui.core.ObjectID(object_id='#less_dead_zone_button'), container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.minus_top_row_button})

        adjustment_buttons_width = (self.minus_bottom_row_button.get_relative_rect().width - 10) / 3
        self.apply_adjustments_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (adjustment_buttons_width, 30)), text='+', tool_tip_text='Apply the auto adjustments made again to the current board.',
                                                                     manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.auto_adjust_mode_button, 'top_target': self.minus_top_row_button})
        self.clear_adjustments_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (adjustment_buttons_width, 30)), text='*', tool_tip_text='Clear the auto adjustments made over time.',
                                                                     manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.apply_adjustments_button, 'top_target': self.minus_top_row_button})
        self.set_custom_board_size_entries_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (adjustment_buttons_width, 30)), text='#', tool_tip_text='Set the custom board size settings to the board\'s current size', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.clear_adjustments_button, 'top_target': self.minus_top_row_button})


        # Row 1 (Set here so that sizes / positions can be relative to buttons in row 3)
        self.selection_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (self.minus_bottom_row_button.get_relative_rect().width, 30)), text='Sel. mode: [X]', tool_tip_text='Turn off to paint with the mouse',
                                                                  manager=self.ui_manager, object_id=pygame_gui.core.ObjectID(object_id='#less_dead_zone_button'), container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.minus_top_row_button})
        self.eraser_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (self.minus_left_column_button.get_relative_rect().width, 30)), text='Eraser: [ ]', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.selection_mode_button})

        if EraserMode is True:
            self.eraser_mode_button.text = 'Eraser: [X]'
            self.eraser_mode_button.rebuild()

        if SelMode is False:
            self.selection_mode_button.text = 'Sel. mode: [ ]'
            self.selection_mode_button.rebuild()
        else:
            self.eraser_mode_button.disable()

        if AutoAdjust is True:
            self.auto_adjust_mode_button.set_text('Auto-adjust: [X]')

        if sum(AutoAdjustments.values()) == 0:
            self.apply_adjustments_button.disable()
            self.clear_adjustments_button.disable()


        # Row 2 (Set here so that sizes / positions can be relative to buttons in row 3)
        self.cut_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (-1, 30)), text='Cut', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.zoom_button, 'top_target': self.message})
        zoom_button_width = self.plus_top_row_button.get_relative_rect().width - self.cut_button.get_relative_rect().width
        self.zoom_button.set_dimensions((zoom_button_width, 30))

        self.copy_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='Copy', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.cut_button, 'top_target': self.message})
        paste_button_width = self.plus_bottom_row_button.get_relative_rect().width - self.copy_button.get_relative_rect().width - 5
        self.paste_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (paste_button_width, 30)), text='Paste', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.copy_button, 'top_target': self.message})

        self.fill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='Fill', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.paste_button, 'top_target': self.message})
        clear_button_width = self.plus_left_column_button.get_relative_rect().width - self.fill_button.get_relative_rect().width - 5
        self.clear_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (clear_button_width, 30)), text='Clear', manager=self.ui_manager, object_id=pygame_gui.core.ObjectID(object_id='#less_dead_zone_button', class_id=None), container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.fill_button, 'top_target': self.message})

        self.rotate_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (-1, 30)), text='Rotate', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.clear_button, 'top_target': self.message})
        flip_button_width = self.plus_right_column_button.get_relative_rect().width - self.rotate_button.get_relative_rect().width - 5
        self.flip_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 10), (flip_button_width, 30)), text='Flip', manager=self.ui_manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.rotate_button, 'top_target': self.message})

        self.buttons_require_sel_box = [self.zoom_button, self.cut_button, self.copy_button, self.fill_button, self.clear_button, self.rotate_button, self.flip_button]
        min_w = helpers.getWidthOfElements([self.plus_top_row_button, self.plus_bottom_row_button, self.plus_left_column_button, self.plus_right_column_button]) - 30
        min_h = helpers.getHeightOfElements([self.message, self.zoom_button, self.plus_top_row_button, self.minus_top_row_button, self.auto_adjust_mode_button]) + 45
        self.set_dimensions((min_w, min_h))

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
            pygame.event.post(pygame.event.Event(self.BOARDADJUSTBUTTON, event_data))

        return handled

    def get_width(self):
        return self.get_relative_rect().width - 30

    def get_height(self):
        return self.get_relative_rect().height - 58

class ThemeManagerWindow(pygame_gui.elements.UIWindow):
    def __init__(self,
                 rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 window_title: str = 'Theme Manager',
                 object_id: Union[ObjectID, str] = ObjectID('#theme_manager_window', None),
                 visible: int = 1,
                 width: int = 330,
                 height: int = 600,
                 w: int = 0,  # Pixel width of pygame window
                 h: int = 0,  # Pixel height of pygame window
                 config_dict: {} = {},
                 themes: [] = [],
                 themes_file_path: str = '',
                 config_file_dir: str = '',
                 diameter: int = 50,
                 right_clickable_elements: [] = []
                 ):

        super().__init__(rect=rect, manager=manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        self.set_dimensions((width, height))
        self.set_minimum_dimensions((330, 600))
        self.previousWindowDimensions = None
        self.w = w
        self.h = h

        self.themes = themes
        self.previous_themes = None
        self.theme_index = 0
        self.selected_index = 0
        self.selected = True

        self.themes_file_path = themes_file_path
        self.config_file_dir = config_file_dir

        # self.sc = WrappedScrollContainer(relative_rect=pygame.Rect((0, 0), (self.get_real_width(), self.get_real_height())), manager=manager, container=self, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

        self.header_text = pygame_gui.elements.UILabel(text='Select a theme to edit:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'})


        self.theme_list = theme_selection_list(relative_rect=pygame.Rect(10, 10, diameter * 1.5, self.get_real_height() - 195), item_list=[], manager=manager, container=self, themes=self.themes, diameter=diameter, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'bottom', 'top_target': self.header_text})
        self.theme_list.set_list_item_height(diameter + 20)


        self.choose_pattern_text = pygame_gui.elements.UILabel(text='Change pattern:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.header_text})
        patterns = helpers.get_example_themes()
        self.patterns_selection_list = theme_dropdown_list(options_list=[], themes=patterns, starting_option='', relative_rect=pygame.Rect(10, 5, 100, 30), manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.choose_pattern_text})
        self.patterns_selection_list.disable()


        self.color_preview_context_menu_buttons = ['Copy', 'Paste']
        self.change_colors_text = pygame_gui.elements.UILabel(text='Change colors:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.patterns_selection_list})

        self.color_surf_1 = pygame.Surface((30, 30))
        self.color_surf_1.fill(self.themes[0][1])
        self.color_preview_1 = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surf_1.get_size()), image_surface=self.color_surf_1, manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.change_colors_text})
        self.color_preview_1.context_menu_buttons = self.color_preview_context_menu_buttons
        self.pick_color_button_1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_preview_1, 'top_target': self.change_colors_text})

        self.color_surf_2 = pygame.Surface((30, 30))
        self.color_surf_2.fill(self.themes[0][2])
        self.color_preview_2 = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surf_2.get_size()), image_surface=self.color_surf_2, manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.color_preview_1})
        self.color_preview_2.context_menu_buttons = self.color_preview_context_menu_buttons
        self.pick_color_button_2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_preview_2, 'top_target': self.color_preview_1})

        self.color_surf_3 = pygame.Surface((30, 30))
        self.color_surf_3.fill(self.themes[0][3])
        self.color_preview_3 = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surf_3.get_size()), image_surface=self.color_surf_3, manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.color_preview_2})
        self.color_preview_3.context_menu_buttons = self.color_preview_context_menu_buttons
        self.pick_color_button_3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_preview_3, 'top_target': self.color_preview_2})

        self.color_surf_4 = pygame.Surface((30, 30))
        self.color_surf_4.fill(self.themes[0][4])
        self.color_preview_4 = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surf_4.get_size()), image_surface=self.color_surf_4, manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.color_preview_3})
        self.color_preview_4.context_menu_buttons = self.color_preview_context_menu_buttons
        self.pick_color_button_4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_preview_4, 'top_target': self.color_preview_3})

        self.color_surf_5 = pygame.Surface((30, 30))
        self.color_surf_5.fill(self.themes[0][5])
        self.color_preview_5 = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surf_5.get_size()), image_surface=self.color_surf_5, manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.color_preview_4})
        self.color_preview_5.context_menu_buttons = self.color_preview_context_menu_buttons
        self.pick_color_button_5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_preview_5, 'top_target': self.color_preview_4})

        self.previous_colors = deepcopy(themes[self.theme_index][1:])
        self.all_color_surfs = [self.color_surf_1, self.color_surf_2, self.color_surf_3, self.color_surf_4, self.color_surf_5]
        self.all_color_previews = [self.color_preview_1, self.color_preview_2, self.color_preview_3, self.color_preview_4, self.color_preview_5]
        self.all_pick_color_buttons = [self.pick_color_button_1, self.pick_color_button_2, self.pick_color_button_3, self.pick_color_button_4, self.pick_color_button_5]
        self.color_picker_killed = False
        self.kill_color_picker = False

        for e in self.all_color_previews: right_clickable_elements.append(e)

        button_width = self.theme_list.get_relative_rect().width / 2 - 2.5
        self.create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (button_width, 30)), text='+', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.theme_list})
        self.delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (button_width, 30)), text='-', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.create_button, 'top_target': self.theme_list})
        self.move_up_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (button_width, 30)), text='▲', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.create_button})
        self.move_down_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (button_width, 30)), text='▼', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.move_up_button, 'top_target': self.create_button})
        self.move_top_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (button_width, 30)), text='▲▲', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.move_up_button})
        self.move_bottom_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (button_width, 30)), text='▼▼', manager=manager, container=self, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.move_top_button, 'top_target': self.move_up_button})

        self.all_theme_list_buttons = [self.create_button, self.delete_button, self.move_up_button, self.move_down_button, self.move_top_button, self.move_bottom_button]
        for button in self.all_theme_list_buttons[1:]: button.disable()

        self.save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (button_width, 30)), text='Save', manager=manager, container=self, object_id=pygame_gui.core.ObjectID(object_id='#less_dead_zone_button', class_id=None), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.move_top_button})
        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (button_width, 30)), text='Load', manager=manager, container=self, object_id=pygame_gui.core.ObjectID(object_id='#less_dead_zone_button', class_id=None), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.save_button, 'top_target': self.move_top_button})


        self.all_height_references = [self.header_text, self.theme_list, self.create_button]

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. There are a lot of buttons in the
        file dialog.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        handled = super().process_event(event)

        if self.kill_color_picker is True:
            self.kill_color_picker = False

            try:
                self.theme_color_picker_dialog.kill()
                self.color_picker_killed = True
            except: pass

        # Theme list stuff
        if (event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and event.ui_element == self.theme_list) or self.selected is True:
            for button in self.all_theme_list_buttons[1:]: button.enable()
            if len(self.themes) == 1:
                self.delete_button.disable()

            self.patterns_selection_list.enable()

            if self.selected is False:
                self.theme_index = event.index

            try:
                if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and event.ui_element == self.theme_list and self.themes[self.theme_index] != self.theme_color_picker_dialog.opened_on_theme:
                    self.kill_color_picker = True
            except: pass

            if self.theme_index == 0:
                self.move_up_button.disable()
                self.move_top_button.disable()

            if self.theme_index == len(self.themes) - 1:
                self.move_down_button.disable()
                self.move_bottom_button.disable()

            patterns = helpers.get_example_themes(self.themes[self.theme_index])
            self.patterns_selection_list.set_options_list(patterns)

            self.selected_index = self.theme_index
            self.selected = False

        if event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION and event.ui_element == self.theme_list and self.theme_list.get_single_selection() is None:
            for button in self.all_theme_list_buttons[1:]: button.disable()
            self.patterns_selection_list.disable()
            self.selected_index = -1

        # Theme list buttons stuff
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.create_button:
            self.themes.append(helpers.generate_random_theme())

            self.selected_index = len(self.themes) - 1

            if self.theme_list.scroll_bar is not None:
                self.theme_list.scroll_bar.scroll_position = self.theme_list.scroll_bar.scrollable_height

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.delete_button:
            self.themes.pop(self.theme_index)

            if self.theme_index < len(self.themes):
                self.selected_index = self.theme_index
            else:
                self.selected_index = self.theme_index - 1

            self.kill_color_picker = True

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.move_up_button:
            self.themes, self.selected_index = helpers.move_item_in_list(self.themes, self.theme_index, -1)

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.move_down_button:
            self.themes, self.selected_index = helpers.move_item_in_list(self.themes, self.theme_index, 1)

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.move_top_button:
            self.themes, self.selected_index = helpers.move_item_in_list(self.themes, self.theme_index, 0, 'bottom')

            if self.theme_list.scroll_bar is not None:
                self.theme_list.scroll_bar.scroll_position = 0

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.move_bottom_button:
            self.themes, self.selected_index = helpers.move_item_in_list(self.themes, self.theme_index, 0, 'top')

            if self.theme_list.scroll_bar is not None:
                self.theme_list.scroll_bar.scroll_position = self.theme_list.scroll_bar.scrollable_height

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.save_button:
            helpers.write_themes_file(self.config_file_dir, self.themes_file_path, self.themes)
            self.theme_list.rebuild_and_set_scroll_bar_back()

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.load_button:
            if os.path.isfile(self.themes_file_path) is True:
                self.themes.clear()
                for theme in helpers.read_themes_file(self.themes_file_path):
                    self.themes.append(theme)

                self.selected_index = min(self.selected_index, len(self.themes) - 1)

        # Drop down menu stuff
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.patterns_selection_list:
            self.themes[self.theme_index][0] = event.theme[0]

        # Color stuff
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element in self.all_pick_color_buttons:
            self.color_button_pressed = self.all_pick_color_buttons.index(event.ui_element) + 1
            color = self.themes[self.theme_index][self.color_button_pressed]
            self.previous_color = deepcopy(color)
            self.theme_color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((self.w / 2 - 80, self.h / 2 + 25), (420, 400)), manager=self.ui_manager, initial_colour=color, window_title='Pick a color...')
            self.theme_color_picker_dialog.opened_on_theme = self.themes[self.theme_index]
            for element in self.all_pick_color_buttons: element.disable()

        try:
            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.theme_color_picker_dialog and self.color_picker_killed is False:
                self.theme_color_picker_dialog.opened_on_theme[self.color_button_pressed] = self.previous_color
                for element in self.all_pick_color_buttons: element.enable()
        except: pass

        if self.color_picker_killed is True:
            for element in self.all_pick_color_buttons: element.enable()
            self.color_picker_killed = False

        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED and event.ui_element == self.theme_color_picker_dialog:
            self.previous_color = event.colour

        try:
            if self.previous_colors != self.themes[self.theme_index][1:]:
                for t, theme_color in enumerate(self.themes[self.theme_index][1:]):
                    self.all_color_surfs[t].fill(theme_color)
                    self.all_color_previews[t].set_image(self.all_color_surfs[t])

                self.previous_colors = deepcopy(self.themes[self.theme_index][1:])
        except: pass

        if (self.get_real_width(), self.get_real_height()) != self.previousWindowDimensions:
            # height_of_others = helpers.getHeightOfElements([self.header_text, self.create_button])
            # self.theme_list.set_dimensions((self.theme_list.get_relative_rect().width, self.get_real_height() - height_of_others))

            # self.height_total = helpers.getHeightOfElements(self.all_height_references)
            # self.sc.set_scrollable_area_dimensions((self.get_real_width(), self.get_real_height()))

            self.theme_list.rebuild_themes(self.themes)

            self.previousWindowDimensions = (self.get_real_width(), self.get_real_height())

        if self.themes != self.previous_themes:
            if self.selected_index >= 0:
                self.theme_list.selected_index = self.selected_index
                self.theme_index = self.selected_index
                self.selected = True

            self.theme_list.rebuild_themes(self.themes)
            self.previous_themes = deepcopy(self.themes)

            for button in self.all_theme_list_buttons[1:]: button.disable()
            self.patterns_selection_list.disable()

        return handled

    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class theme_dropdown_list(pygame_gui.elements.UIDropDownMenu):
    def __init__(self,
                 options_list: List[str],
                 starting_option: str,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 expansion_height_limit: Union[int, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 themes: [] = [],
                 selected_theme: [] = []
                 ):

        super().__init__(relative_rect=relative_rect, manager=manager, container=container,
                         # starting_height=0,
                         options_list=options_list,
                         starting_option=starting_option,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='drop_down_menu')

        self.selected_theme = selected_theme

        self.options_list = helpers.convert_themes_array_to_strings(themes)
        self.selected_option = starting_option
        self.open_button_width = 20

        self.expansion_height_limit = expansion_height_limit

        self.border_width = None
        self.shadow_width = None

        self.background_colour = None
        self.border_colour = None
        self.disabled_background_colour = None
        self.disabled_border_colour = None

        self.shape = "rectangle"
        self.shape_corner_radius = 2

        self.current_state = None
        self.background_rect = None
        self.expand_direction = None

        self.menu_states = {}
        self.rebuild_from_changed_theme_data()
        self.menu_states = {'closed': pygame_gui.elements.ui_drop_down_menu.UIClosedDropDownState(self,
                                                                                                  self.selected_option,
                                                                                                  self.background_rect,
                                                                                                  self.open_button_width,
                                                                                                  self.expand_direction,
                                                                                                  self.ui_manager,
                                                                                                  self,
                                                                                                  self.element_ids,
                                                                                                  self.object_ids,
                                                                                                  self.visible),
                            'expanded': theme_expanded_dropdown_list(self,
                                                                     self.options_list,
                                                                     self.selected_option,
                                                                     self.background_rect,
                                                                     self.open_button_width,
                                                                     self.expand_direction,
                                                                     self.ui_manager,
                                                                     self,
                                                                     self.element_ids,
                                                                     self.object_ids
                                                                     )}
        self.current_state = self.menu_states['closed']
        self.current_state.start(should_rebuild=True)

    def set_options_list(self, themes):
        self.options_list = helpers.convert_themes_array_to_strings(themes)

        self.menu_states = {'closed': theme_closed_dropdown_list(self,
                                                                 self.selected_option,
                                                                 self.background_rect,
                                                                 self.open_button_width,
                                                                 self.expand_direction,
                                                                 self.ui_manager,
                                                                 self,
                                                                 self.element_ids,
                                                                 self.object_ids,
                                                                 self.visible),
                            'expanded': theme_expanded_dropdown_list(self,
                                                                     self.options_list,
                                                                     self.selected_option,
                                                                     self.background_rect,
                                                                     self.open_button_width,
                                                                     self.expand_direction,
                                                                     self.ui_manager,
                                                                     self,
                                                                     self.element_ids,
                                                                     self.object_ids
                                                                     )}

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles various interactions with the drop down menu by passing them along to the
        active state.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        consumed_event = False
        if self.is_enabled:
            consumed_event = self.current_state.process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id in ['#theme_manager_window.drop_down_menu.#selected_option', '#theme_manager_window.drop_down_menu.#expand_button'] and self.is_enabled is True:
            self.current_state.should_transition = True

        return consumed_event

class theme_expanded_dropdown_list(pygame_gui.elements.ui_drop_down_menu.UIExpandedDropDownState):
    def start(self, should_rebuild: bool = True):
        """
        Called each time we enter the expanded state. It creates the necessary elements, the
        selected option, all the other available options and the close button.

        """
        self.should_transition = False

        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.active_buttons = []
        self.selected_option_button = pygame_gui.elements.UIButton(pygame.Rect((border_and_shadow, border_and_shadow),
                                                                               (self.base_position_rect.width - self.close_button_width,
                                                                                self.base_position_rect.height)),
                                                                   '',
                                                                   self.ui_manager,
                                                                   self.ui_container,
                                                                   starting_height=2,
                                                                   parent_element=self.drop_down_menu_ui,
                                                                   object_id=ObjectID('#selected_option', None))
        self.drop_down_menu_ui.join_focus_sets(self.selected_option_button)
        self.active_buttons.append(self.selected_option_button)

        expand_button_symbol = '▼'

        list_object_id = '#drop_down_options_list'
        list_object_ids = self.drop_down_menu_ui.object_ids[:]
        list_object_ids.append(list_object_id)
        list_class_ids = self.drop_down_menu_ui.class_ids[:]
        list_class_ids.append(None)
        list_element_ids = self.drop_down_menu_ui.element_ids[:]
        list_element_ids.append('selection_list')

        final_ids = self.ui_manager.get_theme().build_all_combined_ids(list_element_ids,
                                                                       list_class_ids,
                                                                       list_object_ids)

        self._calculate_options_list_sizes(final_ids)
        if self.expand_direction is not None:
            if self.expand_direction == 'up':
                expand_button_symbol = '▲'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    self.drop_down_menu_ui.expansion_height_limit = self.base_position_rect.top

                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.top - self.options_list_height

            elif self.expand_direction == 'down':
                expand_button_symbol = '▼'

                if self.drop_down_menu_ui.expansion_height_limit is None:
                    height_limit = (self.drop_down_menu_ui.ui_container.relative_rect.height -
                                    self.base_position_rect.bottom)
                    self.drop_down_menu_ui.expansion_height_limit = height_limit

                self.options_list_height = min(self.options_list_height,
                                               self.drop_down_menu_ui.expansion_height_limit)

                self.option_list_y_pos = self.base_position_rect.bottom

        if self.close_button_width > 0:
            close_button_x = (border_and_shadow +
                              self.base_position_rect.width -
                              self.close_button_width)

            self.close_button = pygame_gui.elements.UIButton(pygame.Rect((close_button_x,
                                                                          border_and_shadow),
                                                                         (self.close_button_width,
                                                                          self.base_position_rect.height)),
                                                             expand_button_symbol,
                                                             self.ui_manager,
                                                             self.ui_container,
                                                             starting_height=2,
                                                             parent_element=self.drop_down_menu_ui,
                                                             object_id='#expand_button')
            self.drop_down_menu_ui.join_focus_sets(self.close_button)
            self.active_buttons.append(self.close_button)
        # list_rect = pygame.Rect(self.drop_down_menu_ui.relative_rect.left,
        #                         self.option_list_y_pos,
        #                         (self.drop_down_menu_ui.relative_rect.width -
        #                          self.close_button_width),
        #                         self.options_list_height)
        list_rect = pygame.Rect(self.drop_down_menu_ui.relative_rect.left,
                                self.option_list_y_pos,
                                100,
                                self.options_list_height)

        self.options_selection_list = theme_selection_list(list_rect,
                                                           starting_height=3,
                                                           item_list=[],
                                                           allow_double_clicks=False,
                                                           manager=self.ui_manager,
                                                           parent_element=self.drop_down_menu_ui,
                                                           container=self.drop_down_menu_ui.ui_container,
                                                           anchors=self.drop_down_menu_ui.anchors,
                                                           object_id='#drop_down_options_list',
                                                           themes=helpers.convert_strings_to_themes_array(self.options_list),
                                                           diameter=50)
        self.options_selection_list.set_list_item_height(70)
        self.drop_down_menu_ui.join_focus_sets(self.options_selection_list)

        if should_rebuild:
            self.rebuild()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Processes events for the closed state of the drop down.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element in self.active_buttons:
            self.should_transition = True

        if (event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and
                event.ui_element == self.options_selection_list):
            selection = self.options_selection_list.get_single_selection()
            self.drop_down_menu_ui.selected_option = selection
            self.should_transition = True

            # new event
            event_data = {'text': self.drop_down_menu_ui.selected_option,
                          'theme': event.theme,
                          'index': event.index,
                          'ui_element': self.drop_down_menu_ui,
                          'ui_object_id': self.drop_down_menu_ui.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame_gui.UI_DROP_DOWN_MENU_CHANGED, event_data))

        return False  # don't consume any events

class theme_closed_dropdown_list(pygame_gui.elements.ui_drop_down_menu.UIClosedDropDownState):
    def start(self, should_rebuild: bool = True):
        """
        Called each time we enter the closed state. It creates the necessary elements, the
        selected option and the open button.
        """
        if should_rebuild:
            self.rebuild()

        self.should_transition = False

        border_and_shadow = (self.drop_down_menu_ui.shadow_width +
                             self.drop_down_menu_ui.border_width)
        self.active_buttons = []
        self.selected_option_button = pygame_gui.elements.UIButton(pygame.Rect((border_and_shadow, border_and_shadow),
                                                                               (self.base_position_rect.width -
                                                                                self.open_button_width,
                                                                                self.base_position_rect.height)),
                                                                   '',
                                                                   self.ui_manager,
                                                                   self.ui_container,
                                                                   starting_height=2,
                                                                   parent_element=self.drop_down_menu_ui,
                                                                   object_id='#selected_option',
                                                                   visible=self.visible)
        self.drop_down_menu_ui.join_focus_sets(self.selected_option_button)
        self.active_buttons.append(self.selected_option_button)

        if self.open_button_width > 0:
            open_button_x = (border_and_shadow +
                             self.base_position_rect.width -
                             self.open_button_width)
            expand_button_symbol = '▼'
            if self.expand_direction is not None:
                if self.expand_direction == 'up':
                    expand_button_symbol = '▲'
                elif self.expand_direction == 'down':
                    expand_button_symbol = '▼'
            self.open_button = pygame_gui.elements.UIButton(pygame.Rect((open_button_x,
                                                                         border_and_shadow),
                                                                        (self.open_button_width,
                                                                         self.base_position_rect.height)),
                                                            expand_button_symbol,
                                                            self.ui_manager,
                                                            self.ui_container,
                                                            starting_height=2,
                                                            parent_element=self.drop_down_menu_ui,
                                                            object_id='#expand_button',
                                                            visible=self.visible)
            self.drop_down_menu_ui.join_focus_sets(self.open_button)
            self.active_buttons.append(self.open_button)

class theme_selection_list(pygame_gui.elements.UISelectionList):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 item_list: Union[List[str], List[Tuple[str, str]]],
                 manager: IUIManagerInterface,
                 *,
                 allow_multi_select: bool = False,
                 allow_double_clicks: bool = True,
                 container: Union[IContainerLikeInterface, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 default_selection: Union[
                     str, Tuple[str, str],               # Single-selection lists
                     List[str], List[Tuple[str, str]],   # Multi-selection lists
                     None] = None,
                 themes: [] = [],
                 diameter: int = 50
                 ):

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         container=container,
                         starting_height=starting_height,
                         # layer_thickness=1,
                         item_list=item_list,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='selection_list')

        self.diameter = diameter

        self._parent_element = parent_element
        self.list_and_scroll_bar_container = None
        self.item_list_container = None
        self._raw_item_list = helpers.convert_themes_array_to_strings(themes)
        self._default_selection = default_selection
        self.item_list = []
        self.allow_multi_select = allow_multi_select
        self.allow_double_clicks = allow_double_clicks

        self.background_colour = None
        self.border_colour = None
        self.background_image = None
        self.border_width = 1
        self.shadow_width = 2
        self.shape_corner_radius = 0
        self.shape = 'rectangle'

        self.scroll_bar = None
        self.lowest_list_pos = 0
        self.total_height_of_list = 0
        self.list_item_height = diameter
        self.scroll_bar_width = 20
        self.current_scroll_bar_width = 0

        self.selected_index = -1
        self.special_rebuild = False
        self.scroll_bar_start_pressed = False
        self.scroll_top_start_pressed = False
        self.scroll_bottom_start_pressed = False

        self.rebuild_from_changed_theme_data()


        if self._default_selection is not None:
            self.set_default_selection()

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by
        derived classes but also has a little functionality to make sure the panel's layer
        'thickness' is accurate and to handle window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)

        if self.scroll_bar is not None and (self.scroll_bar.check_has_moved_recently() or self.special_rebuild is True):
            self.special_rebuild = False
            list_height_adjustment = min(self.scroll_bar.start_percentage * self.total_height_of_list,
                                         self.lowest_list_pos)
            for index, item in enumerate(self.item_list):
                new_height = int((index * self.list_item_height) - list_height_adjustment)
                if (-self.list_item_height <= new_height <= self.item_list_container.relative_rect.height):
                    if item['button_element'] is not None:
                        item['button_element'].set_relative_position((0, new_height))
                        if index == self.selected_index:
                            item['selected'] = True
                            item['button_element'].select()
                    else:
                        button_rect = pygame.Rect(0,
                                                  new_height,
                                                  self.item_list_container.relative_rect.width,
                                                  self.list_item_height)
                        button = theme_button(relative_rect=button_rect,
                                              text=item['text'],
                                              manager=self.ui_manager,
                                              parent_element=self,
                                              container=self.item_list_container,
                                              allow_double_clicks=self.allow_double_clicks,
                                              anchors={'left': 'left',
                                                       'right': 'right',
                                                       'top': 'top',
                                                       'bottom': 'top'})

                        self.join_focus_sets(button)
                        item['button_element'] = button
                        item['button_element'].index = index

                        if index == self.selected_index:
                            item['selected'] = True

                        if item['selected']:
                            item['button_element'].select()

                else:
                    if item['button_element'] is not None:
                        item['button_element'].kill()
                        item['button_element'] = None

                if item['button_element'] is not None and type(item['button_element']) != theme_button:
                    old_button_focus_set = item['button_element']._focus_set
                    item['button_element'] = theme_button(relative_rect=item['button_element'].get_relative_rect(),
                                                          text=item['button_element'].text,
                                                          manager=item['button_element'].ui_manager,
                                                          parent_element=self,
                                                          container=item['button_element'].ui_container,
                                                          allow_double_clicks=self.allow_double_clicks)

                    item['button_element'].index = index
                    item['button_element']._focus_set = old_button_focus_set

                    if index == self.selected_index:
                        item['selected'] = True
                        item['button_element'].select()

    def set_item_list(self, new_item_list: Union[List[str], List[Tuple[str, str]]]):
        """
        Set a new string list (or tuple of strings & ids list) as the item list for this selection
        list. This will change what is displayed in the list.

        Tuples should be arranged like so:

         (list_text, object_ID)

         - list_text: displayed in the UI
         - object_ID: used for theming and events

        :param new_item_list: The new list to switch to. Can be a list of strings or tuples.

        """
        self._raw_item_list = new_item_list
        self.item_list = []  # type: List[Dict]
        for new_item in new_item_list:
            if isinstance(new_item, str):
                new_item_list_item = {'text': new_item,
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': '#item_list_item'}
            elif isinstance(new_item, tuple):
                new_item_list_item = {'text': new_item[0],
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': new_item[1]}
            else:
                raise ValueError('Invalid item list')

            self.item_list.append(new_item_list_item)

        self.total_height_of_list = self.list_item_height * len(self.item_list)
        self.lowest_list_pos = (self.total_height_of_list - self.list_and_scroll_bar_container.relative_rect.height)
        inner_visible_area_height = self.list_and_scroll_bar_container.relative_rect.height

        if self.total_height_of_list > inner_visible_area_height:
            # we need a scroll bar
            self.current_scroll_bar_width = self.scroll_bar_width
            percentage_visible = inner_visible_area_height / max(self.total_height_of_list, 1)

            if self.scroll_bar is not None:
                self.scroll_bar.reset_scroll_position()
                self.scroll_bar.set_visible_percentage(percentage_visible)
                self.scroll_bar.start_percentage = 0
            else:
                self.scroll_bar = UIVerticalScrollBar(pygame.Rect(-self.scroll_bar_width,
                                                                  0,
                                                                  self.scroll_bar_width,
                                                                  inner_visible_area_height),
                                                      visible_percentage=percentage_visible,
                                                      manager=self.ui_manager,
                                                      parent_element=self,
                                                      container=self.list_and_scroll_bar_container,
                                                      anchors={'left': 'right',
                                                               'right': 'right',
                                                               'top': 'top',
                                                               'bottom': 'bottom'})
                self.join_focus_sets(self.scroll_bar)
        else:
            if self.scroll_bar is not None:
                self.scroll_bar.kill()
                self.scroll_bar = None
            self.current_scroll_bar_width = 0

        # create button list container
        if self.item_list_container is not None:
            self.item_list_container.clear()
            if (self.item_list_container.relative_rect.width != (self.list_and_scroll_bar_container.relative_rect.width - self.current_scroll_bar_width)):
                container_dimensions = (self.list_and_scroll_bar_container.relative_rect.width - self.current_scroll_bar_width,
                                        self.list_and_scroll_bar_container.relative_rect.height)
                self.item_list_container.set_dimensions(container_dimensions)
        else:
            self.item_list_container = UIContainer(
                pygame.Rect(0, 0,
                            self.list_and_scroll_bar_container.relative_rect.width - self.current_scroll_bar_width,
                            self.list_and_scroll_bar_container.relative_rect.height),
                manager=self.ui_manager,
                starting_height=0,
                parent_element=self,
                container=self.list_and_scroll_bar_container,
                object_id='#item_list_container',
                anchors={'left': 'left',
                         'right': 'right',
                         'top': 'top',
                         'bottom': 'bottom'})
            self.join_focus_sets(self.item_list_container)
        item_y_height = 0
        for index, item in enumerate(self.item_list):
            if item_y_height <= self.item_list_container.relative_rect.height:
                button_rect = pygame.Rect(0, item_y_height,
                                          self.item_list_container.relative_rect.width,
                                          self.list_item_height)
                item['button_element'] = theme_button(relative_rect=button_rect,
                                                      text=item['text'],
                                                      manager=self.ui_manager,
                                                      parent_element=self,
                                                      container=self.item_list_container,
                                                      allow_double_clicks=self.allow_double_clicks,
                                                      anchors={'left': 'left',
                                                               'right': 'right',
                                                               'top': 'top',
                                                               'bottom': 'top'})

                item['button_element'].index = index

                self.join_focus_sets(item['button_element'])
                item_y_height += self.list_item_height
            else:
                break

    def rebuild_and_set_scroll_bar_back(self):
        if self.scroll_bar is not None:
            scroll_position = self.scroll_bar.scroll_position
            self.special_rebuild = True
            self.rebuild()

            if self.scroll_bar is not None:
                self.scroll_bar.scroll_position = scroll_position
                self.scroll_bar.start_percentage = self.scroll_bar.scroll_position / self.scroll_bar.scrollable_height
                self.scroll_bar.rebuild()
                self.update(0)

        else:
            self.rebuild()

        try:
            if self.selected_index >= 0 and self.item_list[self.selected_index]['button_element'] is not None:
                self.item_list[self.selected_index]['selected'] = True
                self.item_list[self.selected_index]['button_element'].select()
        except: pass

    def rebuild_themes(self, themes):
        self._raw_item_list = helpers.convert_themes_array_to_strings(themes)
        self.rebuild_and_set_scroll_bar_back()

    def set_list_item_height(self, h):
        self.list_item_height = h
        self.rebuild()

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the panel.

        :param event: The event to process.

        :return: Should return True if this element makes use of this event.

        """
        if self.is_enabled and (
                event.type in [pygame_gui.UI_BUTTON_PRESSED, pygame_gui.UI_BUTTON_DOUBLE_CLICKED]
                and event.ui_element in self.item_list_container.elements):
            for item in self.item_list:
                if item['button_element'] == event.ui_element:
                    if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
                        # new event
                        event_data = {
                            'text': event.ui_element.text,
                            'theme': event.ui_element.theme,
                            'index': event.ui_element.index,
                            'ui_element': self,
                            'ui_object_id': self.most_specific_combined_id}
                        pygame.event.post(
                            pygame.event.Event(pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
                                               event_data))
                    else:
                        if item['selected']:
                            self.selected_index = -1
                            item['selected'] = False
                            event.ui_element.unselect()

                            # new event
                            event_data = {'text': event.ui_element.text,
                                          'theme': event.ui_element.theme,
                                          'index': event.ui_element.index,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(
                                pygame.event.Event(pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION, event_data))

                        else:
                            self.selected_index = event.ui_element.index
                            item['selected'] = True
                            event.ui_element.select()

                            # new event
                            event_data = {'text': event.ui_element.text,
                                          'theme': event.ui_element.theme,
                                          'index': event.ui_element.index,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            pygame.event.post(pygame.event.Event(pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
                                                                 event_data))

                elif not self.allow_multi_select:
                    if item['selected']:
                        item['selected'] = False
                        if item['button_element'] is not None:
                            item['button_element'].unselect()

                            # new event
                            event_data = {'text': item['text'],
                                          'theme': event.ui_element.theme,
                                          'index': event.ui_element.index,
                                          'ui_element': self,
                                          'ui_object_id': self.most_specific_combined_id}
                            drop_down_changed_event = pygame.event.Event(
                                pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION, event_data)
                            pygame.event.post(drop_down_changed_event)

        if self.scroll_bar is not None:
            if self.scroll_bar.sliding_button is not None:
                if self.scroll_bar.sliding_button.held is True:
                    self.scroll_bar_start_pressed = True

                if self.scroll_bar.sliding_button.held is False and self.scroll_bar_start_pressed is True:
                    self.rebuild_and_set_scroll_bar_back()
                    self.scroll_bar_start_pressed = False


            if self.scroll_bar.top_button is not None:
                if self.scroll_bar.top_button.held is True:
                    self.scroll_top_start_pressed = True

                if self.scroll_bar.top_button.held is False and self.scroll_top_start_pressed is True:
                    self.rebuild_and_set_scroll_bar_back()
                    self.scroll_top_start_pressed = False


            if self.scroll_bar.bottom_button is not None:
                if self.scroll_bar.bottom_button.held is True:
                    self.scroll_bottom_start_pressed = True

                if self.scroll_bar.bottom_button.held is False and self.scroll_bottom_start_pressed is True:
                    self.rebuild_and_set_scroll_bar_back()
                    self.scroll_bottom_start_pressed = False


        return False  # Don't consume any events

class theme_button(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect: pygame.Rect,
                 text: str,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 tool_tip_text: Union[str, None] = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 allow_double_clicks: bool = False,
                 generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
                 visible: int = 1
                 ):

        super().__init__(relative_rect=relative_rect, manager=manager, container=container, text=text,
                         starting_height=starting_height,
                         # layer_thickness=1,
                         anchors=anchors,
                         visible=visible)

        self._create_valid_ids(container=container,
                               parent_element=parent_element,
                               object_id=object_id,
                               element_id='button')

        self.text = ''

        self.dynamic_width = False
        self.dynamic_height = False
        self.dynamic_dimensions_orig_top_left = relative_rect.topleft
        # support for an optional 'tool tip' element attached to this button
        self.tool_tip_text = tool_tip_text
        self.tool_tip = None
        self.ui_root_container = self.ui_manager.get_root_container()

        # Some different states our button can be in, could use a state machine for this
        # if we wanted.
        self.held = False
        self.pressed = False
        self.is_selected = False
        # Used to check button pressed without going through pygame.Event system
        self.pressed_event = False

        # time the hovering
        self.hover_time = 0.0

        # timer for double clicks
        self.last_click_button = None
        self.allow_double_clicks = allow_double_clicks
        self.double_click_timer = self.ui_manager.get_double_click_time() + 1.0

        self.generate_click_events_from = generate_click_events_from

        self.text_surface = None
        self.aligned_text_rect = None

        self.set_image(None)

        # default range at which we 'let go' of a button
        self.hold_range = (0, 0)

        # initialise theme parameters
        self.colours = {}

        self.font = None

        self.normal_image = None
        self.hovered_image = None
        self.selected_image = None
        self.disabled_image = None

        self.tool_tip_delay = 1.0

        self.text_horiz_alignment = 'center'
        self.text_vert_alignment = 'center'
        self.text_horiz_alignment_padding = 0
        self.text_vert_alignment_padding = 0
        self.text_horiz_alignment_method = 'rect'
        self.shape = 'rectangle'
        self.text_shadow_size = 0
        self.text_shadow_offset = (0, 0)

        self.state_transitions = {}

        self.rebuild_from_changed_theme_data()

        self.theme = helpers.convert_string_to_theme(text)
        self.set_theme_image()

    def set_theme_image(self):
        theme_surf = helpers.create_theme_surf(self.theme, self.get_relative_rect().width - 20)
        self.normal_image = theme_surf

        surf_overlay = pygame.Surface(theme_surf.get_size(), pygame.SRCALPHA)
        surf_overlay.fill((255, 255, 255, 70))
        hovered_surf = theme_surf.copy()
        hovered_surf.blit(surf_overlay, (0, 0))
        self.hovered_image = hovered_surf

        surf_overlay = pygame.Surface(theme_surf.get_size(), pygame.SRCALPHA)
        surf_overlay.fill((0, 0, 0, 200))
        disabled_surf = theme_surf.copy()
        disabled_surf.blit(surf_overlay, (0, 0))
        self.disabled_image = disabled_surf

        surf_overlay = pygame.Surface(theme_surf.get_size(), pygame.SRCALPHA)
        surf_overlay.fill((27, 69, 109, 150))
        selected_surf = theme_surf.copy()
        selected_surf.blit(surf_overlay, (0, 0))
        self.selected_image = selected_surf

        self.rebuild()


class ContextMenu(pygame_gui.elements.UISelectionList):
    def process_event(self, event: pygame.event.Event) -> bool:
        super().process_event(event)

        helpers.set_scroll_container_min_h(self)

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if self.get_abs_rect().collidepoint(mouse_pos) is False:
                self.kill()

        if event.type == pygame.KEYUP:
            self.kill()

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION and event.ui_element == self:
            self.kill()

        return False  # Don't consume any events

    def set_item_list(self, new_item_list: Union[List[str], List[Tuple[str, str]]]):
        """
        Set a new string list (or tuple of strings & ids list) as the item list for this selection
        list. This will change what is displayed in the list.

        Tuples should be arranged like so:

         (list_text, object_ID)

         - list_text: displayed in the UI
         - object_ID: used for theming and events

        :param new_item_list: The new list to switch to. Can be a list of strings or tuples.

        """
        self._raw_item_list = new_item_list
        self.item_list = []  # type: List[Dict]
        for new_item in new_item_list:
            if isinstance(new_item, str):
                new_item_list_item = {'text': new_item,
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': '#item_list_item'}
            elif isinstance(new_item, tuple):
                new_item_list_item = {'text': new_item[0],
                                      'button_element': None,
                                      'selected': False,
                                      'object_id': new_item[1]}
            else:
                raise ValueError('Invalid item list')

            self.item_list.append(new_item_list_item)

        self.total_height_of_list = self.list_item_height * len(self.item_list)
        self.lowest_list_pos = (self.total_height_of_list -
                                self.list_and_scroll_bar_container.relative_rect.height)
        inner_visible_area_height = self.list_and_scroll_bar_container.relative_rect.height

        if self.total_height_of_list > inner_visible_area_height:
            # we need a scroll bar
            self.current_scroll_bar_width = self.scroll_bar_width
            percentage_visible = inner_visible_area_height / max(self.total_height_of_list, 1)

            if self.scroll_bar is not None:
                self.scroll_bar.reset_scroll_position()
                self.scroll_bar.set_visible_percentage(percentage_visible)
                self.scroll_bar.start_percentage = 0
            else:
                self.scroll_bar = UIVerticalScrollBar(pygame.Rect(-self.scroll_bar_width,
                                                                  0,
                                                                  self.scroll_bar_width,
                                                                  inner_visible_area_height),
                                                      visible_percentage=percentage_visible,
                                                      manager=self.ui_manager,
                                                      parent_element=self,
                                                      container=self.list_and_scroll_bar_container,
                                                      anchors={'left': 'right',
                                                               'right': 'right',
                                                               'top': 'top',
                                                               'bottom': 'bottom'})
                self.join_focus_sets(self.scroll_bar)
        else:
            if self.scroll_bar is not None:
                self.scroll_bar.kill()
                self.scroll_bar = None
            self.current_scroll_bar_width = 0

        # create button list container
        if self.item_list_container is not None:
            self.item_list_container.clear()
            if (self.item_list_container.relative_rect.width !=
                    (self.list_and_scroll_bar_container.relative_rect.width -
                     self.current_scroll_bar_width)):
                container_dimensions = (self.list_and_scroll_bar_container.relative_rect.width -
                                        self.current_scroll_bar_width,
                                        self.list_and_scroll_bar_container.relative_rect.height)
                self.item_list_container.set_dimensions(container_dimensions)
        else:
            self.item_list_container = UIContainer(
                pygame.Rect(0, 0,
                            self.list_and_scroll_bar_container.relative_rect.width -
                            self.current_scroll_bar_width,
                            self.list_and_scroll_bar_container.relative_rect.height),
                manager=self.ui_manager,
                starting_height=10,
                parent_element=self,
                container=self.list_and_scroll_bar_container,
                object_id='#item_list_container',
                anchors={'left': 'left',
                         'right': 'right',
                         'top': 'top',
                         'bottom': 'bottom'})
            self.join_focus_sets(self.item_list_container)
        item_y_height = 0
        for item in self.item_list:
            if item_y_height <= self.item_list_container.relative_rect.height:
                button_rect = pygame.Rect(0, item_y_height,
                                          self.item_list_container.relative_rect.width,
                                          self.list_item_height)
                item['button_element'] = UIButton(relative_rect=button_rect,
                                                  text=item['text'],
                                                  manager=self.ui_manager,
                                                  parent_element=self,
                                                  container=self.item_list_container,
                                                  object_id=ObjectID(
                                                      object_id=item['object_id'],
                                                      class_id='@selection_list_item'),
                                                  allow_double_clicks=self.allow_double_clicks,
                                                  anchors={'left': 'left',
                                                           'right': 'right',
                                                           'top': 'top',
                                                           'bottom': 'top'})
                self.join_focus_sets(item['button_element'])
                item_y_height += self.list_item_height
            else:
                break
