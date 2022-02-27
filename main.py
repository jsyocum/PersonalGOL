import helpers
import pygame
import pygame_gui
import numpy as np
import math
from collections import deque

class SettingsWindow(pygame_gui.elements.UIWindow):
    def on_close_window_button_pressed(self):
        self.hide()

    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
        return self.get_relative_rect().height - 58

class SettingsWindowScrollContainer(pygame_gui.elements.ui_scrolling_container.UIScrollingContainer):
    def get_real_width(self):
        return self.get_relative_rect().width - 30

    def get_real_height(self):
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

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    DefaultScale = 20
    DefaultMaxFps = 18
    DefaultLikelihood = 5
    Board = helpers.generateArray(int(h / DefaultScale), int(w / DefaultScale), DefaultLikelihood)
    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)
    step_stack.append(Board.copy())

    Continuous = True
    WasContinuous = True
    Update = True
    Step = False
    StepBack = False
    NewBoard = False
    EditMode = False
    MenuOpen = False
    CurrentBoardSurf = None
    time_delta_added = 0

    DefaultColorR = 255
    DefaultColorG = 255
    DefaultColorB = 255
    RandomColorByPixel = False


    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show settings', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, quit_game_button]


    settings_window_actual = SettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, resizable=True, window_display_title='Settings', visible=0)
    settings_window_actual.set_minimum_dimensions((330, 200))
    settings_window_actual.set_dimensions((w, h))
    settings_window = SettingsWindowScrollContainer(relative_rect=pygame.Rect((0, 0), (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())), manager=manager, container=settings_window_actual, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

    parameters_warning_text = pygame_gui.elements.ui_text_box.UITextBox('<font face=arial color=regular_text><font color=#989898 size=2>'
                                                                        '<b>Changing scale, likelihood, or board size will reset the board</b></font></font>',
                                                                        pygame.Rect((10, 10), (settings_window.get_real_width() - 10, -1)), manager=manager, container=settings_window)

    parameters_scale_text = pygame_gui.elements.ui_label.UILabel(text='Scale:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_warning_text})
    parameters_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=20, value_range=(1, 80), manager=manager, container=settings_window, click_increment=5, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_text})
    parameters_scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 200', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultScale), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_scale_text})

    parameters_max_fps_text = pygame_gui.elements.ui_label.UILabel(text='Max fps:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_slider})
    parameters_max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=18, value_range=(1, 50), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_text})
    parameters_max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 1000', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultMaxFps), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_max_fps_text})

    parameters_likelihood_text = pygame_gui.elements.ui_label.UILabel(text='Likelihood:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_slider})
    parameters_likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=5, value_range=(1, 30), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_text})
    parameters_likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 100', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultLikelihood), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_text})

    parameters_color_text = pygame_gui.elements.ui_label.UILabel(text='Color:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_slider})
    parameters_color_picker_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-110, 10), (50, 25)), text='...', manager=manager, container=settings_window, tool_tip_text='Use a color picker to choose a color.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_random_cell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to randomize the color of each cell.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default: White', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_picker_dialog = None
    color = pygame.Color(DefaultColorR, DefaultColorG, DefaultColorB)

    parameters_custom_board_size_text = pygame_gui.elements.ui_label.UILabel(text='Set custom board size:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_color_text})
    parameters_custom_board_size_enable_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to enter a custom board size. Disables scale option.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_color_text})
    parameters_custom_board_size_width_text = pygame_gui.elements.ui_label.UILabel(text='Width:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_height_text = pygame_gui.elements.ui_label.UILabel(text='Height:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=int(h / DefaultScale), value_range=(1, h), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                             'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_height_slider, 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=int(w / DefaultScale), value_range=(1, w), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                            'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_width_slider, 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry.set_text(str(int(w / DefaultScale)))
    parameters_custom_board_size_height_entry.set_text(str(int(h / DefaultScale)))
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

    previousWidth = int(w / DefaultScale)
    previousHeight = int(h / DefaultScale)

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
    controls_rect = pygame.Rect((w / 2 - 510, h / 4 + 2), (300, 400))

    controls_text_array = [controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text, controls_increase_max_fps_text, controls_decrease_max_fps_text]

    while running:
        time_delta = clock.tick(120) / 1000.0
        time_delta_stack.append(time_delta)
        if len(time_delta_stack) > 2000:
            time_delta_stack.popleft()

        time_delta_added = time_delta_added + time_delta
        if time_delta_added >= (1 / parameters_max_fps_slider.get_current_value()):
            Update = True
            time_delta_added = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if MenuOpen is False:
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    Continuous = not Continuous
                elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                    Step = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_s:
                    StepBack = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_r:
                    NewBoard = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                    Continuous = not Continuous
                    EditMode = not EditMode

            if (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_to_game_button):
                if MenuOpen is False:
                    WasContinuous = Continuous
                    Continuous = False

                    pausedLikelihoodSliderValue = parameters_likelihood_slider.get_current_value()

                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show settings')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    Continuous = WasContinuous
                    MenuOpen = CloseUIElements(all_menu_buttons)
                    settings_window_actual.hide()
                    if parameters_color_picker_dialog is not None: parameters_color_picker_dialog.kill()

                    for entryArray in all_parameters_entries[3:]:
                        helpers.manageNumberEntry(entryArray)

                    if parameters_custom_board_size_enable_button.text == '[ ]':
                        if (w / previousWidth != parameters_scale_slider.get_current_value()) or (h / previousHeight != parameters_scale_slider.get_current_value()) or (pausedLikelihoodSliderValue != parameters_likelihood_slider.get_current_value()):
                            previousWidth = int(w / parameters_scale_slider.get_current_value())
                            previousHeight = int(h / parameters_scale_slider.get_current_value())
                            NewBoard = True
                    elif (previousWidth != int(parameters_custom_board_size_width_entry.get_text())) or (previousHeight != int(parameters_custom_board_size_height_entry.get_text())):
                        previousWidth = int(parameters_custom_board_size_width_entry.get_text())
                        previousHeight = int(parameters_custom_board_size_height_entry.get_text())
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
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show settings':
                show_parameters_button.set_text('Hide settings')
                settings_window_actual.show()

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                show_parameters_button.set_text('Show settings')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)
                settings_window_actual.hide()

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
                current_max_fps = parameters_max_fps_slider.get_current_value()
                max_fps_slider_range = parameters_max_fps_slider.value_range
                if event.button == 4:
                    parameters_max_fps_slider.set_current_value(min(current_max_fps + 1, max_fps_slider_range[1]))
                elif event.button == 5:
                    parameters_max_fps_slider.set_current_value(max(current_max_fps - 1, max_fps_slider_range[0]))

                if EditMode is True and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    IsColliding, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurf(CurrentBoardSurf, mouse_pos, w, h)
                    if IsColliding:
                        board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)
                        if step_stack[-1][board_pos[0]][board_pos[1]] == 0:
                            step_stack[-1][board_pos[0]][board_pos[1]] = 1
                        else:
                            step_stack[-1][board_pos[0]][board_pos[1]] = 0

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

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_custom_board_size_enable_button:
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
                else:
                    parameters_custom_board_size_enable_button.text = '[ ]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Enable to enter a custom board size. Disables scale option.'
                    for element in scale_elements: element.enable()
                    for element in custom_board_size_elements:
                        element.disable()
                        element.rebuild()
                        element.enable()
                        element.disable()

                parameters_custom_board_size_enable_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_random_cell_button:
                if parameters_color_random_cell_button.text == '[ ]':
                    parameters_color_random_cell_button.text = '[X]'
                    parameters_color_random_cell_button.tool_tip_text = 'Disable to go back to using normal colors.'
                    for element in all_parameters_color_elements[1:]: element.disable()
                    RandomColorByPixel = True
                else:
                    parameters_color_random_cell_button.text = '[ ]'
                    parameters_color_random_cell_button.tool_tip_text = 'Enable to randomize the color of each cell.'
                    for element in all_parameters_color_elements[1:]: element.enable()
                    RandomColorByPixel = False

                parameters_color_random_cell_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_picker_button:
                parameters_color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, initial_colour=color, window_title='Pick a color...')
                for element in all_parameters_color_elements: element.disable()

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == parameters_color_picker_dialog and RandomColorByPixel is False:
                for element in all_parameters_color_elements: element.enable()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_default_button: parameters_scale_slider.set_current_value(DefaultScale)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_default_button: parameters_max_fps_slider.set_current_value(DefaultMaxFps)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_default_button: parameters_likelihood_slider.set_current_value(DefaultLikelihood)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_default_button: color = pygame.Color(DefaultColorR, DefaultColorG, DefaultColorB)

            if (event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED or event.type == pygame_gui.UI_BUTTON_PRESSED) and (event.ui_element in all_buttons_with_tool_tips) and (show_parameters_button.text == 'Hide parameters') and (MenuOpen is not False):
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)

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

        if NewBoard is True:
            Board = helpers.generateArray(previousHeight, previousWidth, parameters_likelihood_slider.get_current_value())
            Board = np.rot90(Board)
            step_stack.clear()
            step_stack.append(Board)
            CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, color=color)
            NewBoard = False


        CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, color=color, RandomColorByPixel=RandomColorByPixel)
        if MenuOpen is True:
            if show_controls_button.text == 'Hide controls':
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)


        helpers.manageSliderAndEntryWithArray(all_parameters_elements_matched)
        all_parameters_elements_matched[0][2] = parameters_scale_slider.get_current_value()
        all_parameters_elements_matched[0][3] = parameters_scale_entry.get_text()
        all_parameters_elements_matched[1][2] = parameters_max_fps_slider.get_current_value()
        all_parameters_elements_matched[1][3] = parameters_max_fps_entry.get_text()
        all_parameters_elements_matched[2][2] = parameters_likelihood_slider.get_current_value()
        all_parameters_elements_matched[2][3] = parameters_likelihood_entry.get_text()
        all_parameters_elements_matched[3][2] = parameters_custom_board_size_width_slider.get_current_value()
        all_parameters_elements_matched[3][3] = parameters_custom_board_size_width_entry.get_text()
        all_parameters_elements_matched[4][2] = parameters_custom_board_size_height_slider.get_current_value()
        all_parameters_elements_matched[4][3] = parameters_custom_board_size_height_entry.get_text()

        for entryArray in all_parameters_entries[3:]:
            if entryArray[0].is_focused is not True:
                helpers.manageNumberEntry(entryArray)

        # If the height or width of the settings window has changed...
        if (settings_window_actual.get_real_width(), settings_window_actual.get_real_height()) != previousSettingsWindowDimensions:
            parameters_warning_text.set_dimensions((settings_window.get_real_width() - 10, -1))
            parameters_warning_text.rebuild()
            parameters_custom_board_size_width_slider.rebuild()
            parameters_custom_board_size_height_slider.rebuild()

            parameters_height_total = helpers.getHeightOfElements(all_parameters_height_references) + 10
            settings_window_actual.set_dimensions((settings_window_actual.get_relative_rect().width, min(settings_window_actual.get_relative_rect().height, parameters_height_total)))
            settings_window.set_scrollable_area_dimensions((settings_window.get_real_width(), parameters_height_total / 1.145 - 2))

            previousSettingsWindowDimensions = (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())

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
