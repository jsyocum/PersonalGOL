import re
import helpers
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pathlib import Path
from typing import Union
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
                                                                      '<b>Changing scale, likelihood, or board size will reset the board</b></font></font>',
                                                                      pygame.Rect((10, 10), (self.sc.get_real_width() - 10, -1)), manager=manager, container=self.sc)

        self.scale_text = pygame_gui.elements.ui_label.UILabel(text='Scale:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.warning_text})
        self.scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["Scale"][0], value_range=(1, 80), manager=manager, container=self.sc, click_increment=5, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.scale_text})
        self.scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 200', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.warning_text})
        self.scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(config_dict["Scale"][1]), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.warning_text})
        self.scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.scale_slider, 'top_target': self.scale_text})

        self.max_fps_text = pygame_gui.elements.ui_label.UILabel(text='Max fps:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.scale_slider})
        self.max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["MaxFps"][0], value_range=(1, 50), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.max_fps_text})
        self.max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 1000', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.scale_slider})
        self.max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(config_dict["MaxFps"][1]), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.scale_slider})
        self.max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.max_fps_slider, 'top_target': self.max_fps_text})

        self.likelihood_text = pygame_gui.elements.ui_label.UILabel(text='Likelihood:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=self.sc, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': self.max_fps_slider})
        self.likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (self.sc.get_real_width() - 40, 25)), start_value=config_dict["Likelihood"][0], value_range=(1, 30), manager=manager, container=self.sc, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': self.likelihood_text})
        self.likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=self.sc, tool_tip_text='Change slider maximum to 100', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.max_fps_slider})
        self.likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=self.sc, tool_tip_text='Reset to default value: ' + str(config_dict["Likelihood"][1]), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.likelihood_slider, 'top_target': self.max_fps_slider})
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

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.apply_button:
            helpers.quick_post(self, 'config_dict', self.config_dict, self.SETTINGSAPPLIED)

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
