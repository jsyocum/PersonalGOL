import warnings
from typing import Union, Tuple, Dict

import pygame
import pygame_gui

from pygame_gui._constants import UI_BUTTON_PRESSED, UI_HORIZONTAL_SLIDER_MOVED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_PICKED, UI_TEXT_ENTRY_FINISHED
from pygame_gui._constants import UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED, OldType

from pygame_gui.core.interfaces import IUIManagerInterface, IContainerLikeInterface
from pygame_gui.core import UIElement, UIContainer, ObjectID

from pygame_gui.elements import UIWindow, UIButton, UIImage
from pygame_gui.elements import UIHorizontalSlider, UILabel, UITextEntryLine


class SettingsDialog(UIWindow):
    """
    A colour picker window that gives us a small range of UI tools to pick a final colour.

    :param rect: The size and position of the colour picker window. Includes the size of shadow,
                 border and title bar.
    :param manager: The manager for the whole of the UI.
    :param initial_colour: The starting colour for the colour picker, defaults to black.
    :param window_title: The title for the window, defaults to 'Colour Picker'
    :param object_id: The object ID for the window, used for theming - defaults to
                      '#colour_picker_dialog'
    :param visible: Whether the element is visible by default.
    """

    def __init__(self, rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 *,
                 # initial_colour: pygame.Color = pygame.Color(0, 0, 0, 255),
                 window_title: str = "Settings",
                 object_id: Union[ObjectID, str] = ObjectID('#settings_dialog', None),
                 visible: int = 1):

        super().__init__(rect, manager,
                         window_display_title=window_title,
                         object_id=object_id,
                         resizable=True,
                         visible=visible)

        minimum_dimensions = (300, 400)
        if rect.width < minimum_dimensions[0] or rect.height < minimum_dimensions[1]:
            warn_string = ("Initial size: " + str(rect.size) + " is less than minimum dimensions: " + str(minimum_dimensions))
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self.warning_text = pygame_gui.elements.ui_text_box(html_text="<br>Changing scale, likelihood, or board size will reset the board.</br>",
                                                            relative_rect=pygame.Rect(10, 10, -1, -1),
                                                            manager=self.ui_manager,
                                                            container=self,
                                                            object_id='#warning_text',
                                                            anchors={'left': 'right',
                                                                     'right': 'right',
                                                                     'top': 'bottom',
                                                                     'bottom': 'bottom'})

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                      text='pygame-gui.Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

        self.ok_button = UIButton(relative_rect=pygame.Rect(-10, -40, -1, 30),
                                  text='pygame-gui.OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id='#ok_button',
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom',
                                           'right_target': self.cancel_button})

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles events that this UI element is interested in. In this case we are responding to
        the colour channel elements being changed, the OK or Cancel buttons being pressed or the
        user clicking the mouse inside of the Saturation & Value picking square.

        :param event: The pygame Event to process.

        :return: True if event is consumed by this element and should not be passed on to other
                 elements.

        """
        consumed_event = super().process_event(event)
        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.cancel_button:
            self.kill()

        if event.type == UI_BUTTON_PRESSED and event.ui_element == self.ok_button:
            # old event - to be removed in 0.8.0
            event_data = {'user_type': OldType(UI_COLOUR_PICKER_COLOUR_PICKED),
                          'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            # new event
            event_data = {'colour': self.current_colour,
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            pygame.event.post(pygame.event.Event(UI_COLOUR_PICKER_COLOUR_PICKED, event_data))
            self.kill()

        return consumed_event
