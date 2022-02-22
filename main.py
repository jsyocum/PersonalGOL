import helpers
import pygame
import pygame_gui
import numpy as np
from collections import deque

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
    MenuOpen = False
    CurrentBoardSurf = None
    time_delta_added = 0

    DefaultColorR = 255
    DefaultColorG = 255
    DefaultColorB = 255


    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show parameters', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, quit_game_button]


    parameters_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 125), (220, 25)), start_value=20, value_range=(1, 80), manager=manager, visible=0, click_increment=5)
    parameters_max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 185), (220, 25)), start_value=18, value_range=(1, 50), manager=manager, visible=0, click_increment=2)
    parameters_likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 245), (220, 25)), start_value=5, value_range=(1, 30), manager=manager, visible=0, click_increment=2)

    parameters_scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 125), (50, 25)), manager=manager, visible=0)
    parameters_max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 185), (50, 25)), manager=manager, visible=0)
    parameters_likelihood_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 245), (50, 25)), manager=manager, visible=0)

    paramters_scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 330, h / 4 + 100), (50, 25)), text='[ ]', manager=manager, tool_tip_text='Change slider maximum to 200', visible=0)
    paramters_max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 330, h / 4 + 160), (50, 25)), text='[ ]', manager=manager, tool_tip_text='Change slider maximum to 1000', visible=0)
    paramters_likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 330, h / 4 + 220), (50, 25)), text='[ ]', manager=manager, tool_tip_text='Change slider maximum to 100', visible=0)

    parameters_scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 100), (50, 25)), text='*', manager=manager, tool_tip_text='Reset to default value: ' + str(DefaultScale), visible=0)
    parameters_max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 160), (50, 25)), text='*', manager=manager, tool_tip_text='Reset to default value: ' + str(DefaultMaxFps), visible=0)
    parameters_likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 220), (50, 25)), text='*', manager=manager, tool_tip_text='Reset to default value: ' + str(DefaultLikelihood), visible=0)

    parameters_custom_board_size_enable_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 280), (50, 25)), text='[ ]', manager=manager, tool_tip_text='Enable to enter a custom board size. Disables scale option.', visible=0)
    paramaters_custom_board_size_width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 305), (50, 25)), manager=manager, visible=0)
    paramaters_custom_board_size_height_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 425, h / 4 + 305), (50, 25)), manager=manager, visible=0)
    paramaters_custom_board_size_width_entry.set_text(str(int(w / DefaultScale)))
    paramaters_custom_board_size_height_entry.set_text(str(int(h / DefaultScale)))
    paramaters_custom_board_size_width_entry.disable()
    paramaters_custom_board_size_height_entry.disable()

    parameters_color_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 340), (50, 25)), text='*', manager=manager, tool_tip_text='Reset to default values: R: ' + str(DefaultColorR) + ' G: ' + str(DefaultColorG) + ' B: ' + str(DefaultColorB), visible=0)
    parameters_color_R_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 480, h / 4 + 365), (50, 25)), manager=manager, visible=0)
    parameters_color_G_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 405, h / 4 + 365), (50, 25)), manager=manager, visible=0)
    parameters_color_B_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((w / 2 - 330, h / 4 + 365), (50, 25)), manager=manager, visible=0)
    parameters_color_picker_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 270, h / 4 + 365), (50, 25)), text='...', manager=manager, tool_tip_text='Use a color picker to choose a color.', visible=0)
    paramaters_color_picker_dialog = None

    parameters_color_R_entry.set_text(str(DefaultColorR))
    parameters_color_G_entry.set_text(str(DefaultColorG))
    parameters_color_B_entry.set_text(str(DefaultColorB))
    color = pygame.Color(int(parameters_color_R_entry.get_text()), int(parameters_color_G_entry.get_text()), int(parameters_color_B_entry.get_text()))

    previousScaleSliderValue = None
    previousScaleEntryValue = None
    previousMaxFpsSliderValue = None
    previousMaxFpsEntryValue = None
    previousLikelihoodSliderValue = None
    previousLikelihoodEntryValue = None

    previousWidth = int(w / DefaultScale)
    previousHeight = int(h / DefaultScale)

    pausedLikelihoodSliderValue = DefaultLikelihood

    all_parameters_elements = [parameters_scale_slider, parameters_max_fps_slider, parameters_likelihood_slider,
                               parameters_scale_entry, parameters_max_fps_entry, parameters_likelihood_entry,
                               parameters_scale_default_button, parameters_max_fps_default_button, parameters_likelihood_default_button,
                               paramters_scale_slider_size_button, paramters_max_fps_slider_size_button, paramters_likelihood_slider_size_button,
                               parameters_custom_board_size_enable_button, paramaters_custom_board_size_width_entry, paramaters_custom_board_size_height_entry,
                               parameters_color_default_button, parameters_color_R_entry, parameters_color_G_entry, parameters_color_B_entry, parameters_color_picker_button]

    all_paramaters_entries = [[parameters_scale_entry, 1, 80], [parameters_max_fps_entry, 1, 50], [parameters_likelihood_entry, 1, 30],
                              [paramaters_custom_board_size_width_entry, 1, w], [paramaters_custom_board_size_height_entry, 1, h],
                              [parameters_color_R_entry, 0, 255], [parameters_color_G_entry, 0, 255], [parameters_color_B_entry, 0, 255]]

    all_paramaters_elements_matched = [[parameters_scale_slider, parameters_scale_entry, previousScaleSliderValue, previousScaleEntryValue],
                                       [parameters_max_fps_slider, parameters_max_fps_entry, previousMaxFpsSliderValue, previousMaxFpsEntryValue],
                                       [parameters_likelihood_slider, parameters_likelihood_entry, previousLikelihoodSliderValue, previousLikelihoodEntryValue]]

    all_buttons_with_tool_tips = {paramters_scale_slider_size_button, parameters_scale_default_button, parameters_max_fps_default_button,
                                  parameters_likelihood_default_button, paramters_max_fps_slider_size_button, paramters_likelihood_slider_size_button,
                                  parameters_custom_board_size_enable_button,
                                  parameters_color_default_button, parameters_color_picker_button}

    for entry in all_paramaters_entries: entry[0].set_allowed_characters('numbers')


    sidebar_header_font = pygame.font.SysFont('arial', size=30, bold=True)
    sidebar_font = pygame.font.SysFont('arial', size=18)
    sidebar_font_bold = pygame.font.SysFont('arial', size=18, bold=True)

    controls_header_text = sidebar_header_font.render("Controls", True, (190, 190, 190))
    controls_pause_text = sidebar_font.render("Pause: SPACEBAR", True, (152, 152, 152))
    controls_step_forward_text = sidebar_font.render("Step forward: W", True, (152, 152, 152))
    controls_step_backward_text = sidebar_font.render("Step backwards: S", True, (152, 152, 152))
    controls_reset_text = sidebar_font.render("Reset: R", True, (152, 152, 152))
    controls_rect = pygame.Rect((w / 2 - 510, h / 4 + 2), (300, 400))

    paramaters_header_text = sidebar_header_font.render("Parameters", True, (190, 190, 190))
    paramaters_warning1_text = sidebar_font_bold.render("Changing scale or likelihood", True, (152, 152, 152))
    paramaters_warning2_text = sidebar_font_bold.render("will reset the board.", True, (152, 152, 152))
    parameters_scale_text = sidebar_font.render("Scale:", True, (152, 152, 152))
    parameters_max_fps_text = sidebar_font.render("Max fps:", True, (152, 152, 152))
    parameters_likelihood_text = sidebar_font.render("Likelihood:", True, (152, 152, 152))
    paramaters_custom_board_size_text = sidebar_font.render("Set custom board size:", True, (152, 152, 152))
    parameters_custom_board_size_x_text = sidebar_font.render("x", True, (152, 152, 152))
    paramaters_custom_board_size_hint_text = sidebar_font.render("(Width x Height)", True, (152, 152, 152))
    paramaters_color_text = sidebar_font.render("Color:", True, (152, 152, 152))
    paramaters_color_R_text = sidebar_font.render("R:", True, (152, 152, 152))
    paramaters_color_G_text = sidebar_font.render("G:", True, (152, 152, 152))
    paramaters_color_B_text = sidebar_font.render("B:", True, (152, 152, 152))

    all_paramaters_texts = [paramaters_header_text, paramaters_warning1_text, paramaters_warning2_text,
                            parameters_scale_text, parameters_max_fps_text, parameters_likelihood_text,
                            paramaters_custom_board_size_text, parameters_custom_board_size_x_text, paramaters_custom_board_size_hint_text,
                            paramaters_color_text, paramaters_color_R_text, paramaters_color_G_text, paramaters_color_B_text]

    while running:
        time_delta = clock.tick(120)/1000.0
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

            if (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_to_game_button):
                if MenuOpen is False:
                    WasContinuous = Continuous
                    Continuous = False
                    # CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, RandomColor=True)

                    pausedLikelihoodSliderValue = parameters_likelihood_slider.get_current_value()

                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show parameters')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    Continuous = WasContinuous
                    MenuOpen = CloseUIElements(all_menu_buttons)
                    CloseUIElements(all_parameters_elements)
                    if paramaters_color_picker_dialog is not None: paramaters_color_picker_dialog.kill()

                    for entryArray in all_paramaters_entries[3:]:
                        helpers.manageNumberEntry(entryArray)

                    if parameters_custom_board_size_enable_button.text == '[ ]':
                        if (w / previousWidth != parameters_scale_slider.get_current_value()) or (h / previousHeight != parameters_scale_slider.get_current_value()) or (pausedLikelihoodSliderValue != parameters_likelihood_slider.get_current_value()):
                            previousWidth = int(w / parameters_scale_slider.get_current_value())
                            previousHeight = int(h / parameters_scale_slider.get_current_value())
                            NewBoard = True
                    elif (previousWidth != int(paramaters_custom_board_size_width_entry.get_text())) or (previousHeight != int(paramaters_custom_board_size_height_entry.get_text())):
                        previousWidth = int(paramaters_custom_board_size_width_entry.get_text())
                        previousHeight = int(paramaters_custom_board_size_height_entry.get_text())
                        NewBoard = True

                    color = pygame.Color(int(parameters_color_R_entry.get_text()), int(parameters_color_G_entry.get_text()), int(parameters_color_B_entry.get_text()))
                    # CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, color=color)

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text)

                if show_parameters_button.text == 'Hide parameters':
                    show_parameters_button.set_text('Show parameters')
                    CloseUIElements(all_parameters_elements)

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show parameters':
                show_parameters_button.set_text('Hide parameters')
                helpers.showParameters(surf, w, h, controls_rect, all_paramaters_texts)
                OpenUIElements(all_parameters_elements)

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                show_parameters_button.set_text('Show parameters')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)
                CloseUIElements(all_parameters_elements)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == paramters_scale_slider_size_button:
                if paramters_scale_slider_size_button.text == '[ ]':
                    paramters_scale_slider_size_button.text = '[X]'
                    paramters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 80'
                    parameters_scale_slider.value_range = (1, 200)
                else:
                    paramters_scale_slider_size_button.text = '[ ]'
                    paramters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 200'
                    paramters_scale_slider_size_button.rebuild()
                    parameters_scale_slider.value_range = (1, 80)

                paramters_scale_slider_size_button.rebuild()
                parameters_scale_slider.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == paramters_max_fps_slider_size_button:
                if paramters_max_fps_slider_size_button.text == '[ ]':
                    paramters_max_fps_slider_size_button.text = '[X]'
                    paramters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 50'
                    parameters_max_fps_slider.value_range = (1, 1000)
                else:
                    paramters_max_fps_slider_size_button.text = '[ ]'
                    paramters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 1000'
                    parameters_max_fps_slider.value_range = (1, 50)

                paramters_max_fps_slider_size_button.rebuild()
                parameters_max_fps_slider.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == paramters_likelihood_slider_size_button:
                if paramters_likelihood_slider_size_button.text == '[ ]':
                    paramters_likelihood_slider_size_button.text = '[X]'
                    paramters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 30'
                    parameters_likelihood_slider.value_range = (1, 100)
                else:
                    paramters_likelihood_slider_size_button.text = '[ ]'
                    paramters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 100'
                    parameters_likelihood_slider.value_range = (1, 30)

                paramters_likelihood_slider_size_button.rebuild()
                parameters_likelihood_slider.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_custom_board_size_enable_button:
                if parameters_custom_board_size_enable_button.text == '[ ]':
                    parameters_custom_board_size_enable_button.text = '[X]'
                    paramters_likelihood_slider_size_button.tool_tip_text = 'Disable to use the scale option instead.'
                    for element in (parameters_scale_slider, parameters_scale_entry, paramters_scale_slider_size_button, parameters_scale_default_button): element.disable()
                    for element in (paramaters_custom_board_size_width_entry, paramaters_custom_board_size_height_entry): element.enable()
                else:
                    parameters_custom_board_size_enable_button.text = '[ ]'
                    paramters_likelihood_slider_size_button.tool_tip_text = 'Enable to enter a custom board size. Disables scale option.'
                    for element in (parameters_scale_slider, parameters_scale_entry, paramters_scale_slider_size_button, parameters_scale_default_button): element.enable()
                    for element in (paramaters_custom_board_size_width_entry, paramaters_custom_board_size_height_entry): element.disable()
                    paramaters_custom_board_size_width_entry.rebuild()
                    paramaters_custom_board_size_height_entry.rebuild()

                parameters_custom_board_size_enable_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_picker_button:
                paramaters_color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, initial_colour=color, window_title='Pick a color...')
                parameters_color_picker_button.disable()

            if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                parameters_color_R_entry.set_text(str(event.colour[0]))
                parameters_color_G_entry.set_text(str(event.colour[1]))
                parameters_color_B_entry.set_text(str(event.colour[2]))
                print('color picked')

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == paramaters_color_picker_dialog:
                parameters_color_picker_button.enable()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_default_button: parameters_scale_slider.set_current_value(DefaultScale)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_default_button: parameters_max_fps_slider.set_current_value(DefaultMaxFps)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_default_button: parameters_likelihood_slider.set_current_value(DefaultLikelihood)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_default_button:
                parameters_color_R_entry.set_text(str(DefaultColorR))
                parameters_color_G_entry.set_text(str(DefaultColorG))
                parameters_color_B_entry.set_text(str(DefaultColorB))

            if (event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED or event.type == pygame_gui.UI_BUTTON_PRESSED) and (event.ui_element in all_buttons_with_tool_tips) and (show_parameters_button.text == 'Hide parameters') and (MenuOpen is not False):
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, infoObject)
                helpers.showParameters(surf, w, h, controls_rect, all_paramaters_texts)

            manager.process_events(event)

        manager.update(time_delta)

        if (Continuous is False) and (Step is True):
            CurrentBoardSurf = helpers.updateGOL(step_stack[-1], surf, infoObject, step_stack, color=color)
            Step = False
        elif (Continuous is False) and (StepBack is True):
            CurrentBoardSurf = helpers.stepBack(step_stack, surf, infoObject, color=color)
            StepBack = False
        elif (Continuous is True) and (Update is True):
            CurrentBoardSurf = helpers.updateGOL(step_stack[-1], surf, infoObject, step_stack, color=color)
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

        if MenuOpen is True:
            CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, color=color)
            if show_controls_button.text == 'Hide controls':
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text)
            elif show_parameters_button.text == 'Hide parameters':
                helpers.showParameters(surf, w, h, controls_rect, all_paramaters_texts)


        helpers.manageSliderAndEntryWithArray(all_paramaters_elements_matched)
        all_paramaters_elements_matched[0][2] = parameters_scale_slider.get_current_value()
        all_paramaters_elements_matched[0][3] = parameters_scale_entry.get_text()
        all_paramaters_elements_matched[1][2] = parameters_max_fps_slider.get_current_value()
        all_paramaters_elements_matched[1][3] = parameters_max_fps_entry.get_text()
        all_paramaters_elements_matched[2][2] = parameters_likelihood_slider.get_current_value()
        all_paramaters_elements_matched[2][3] = parameters_likelihood_entry.get_text()

        for entryArray in all_paramaters_entries[3:]:
            if entryArray[0].is_focused is not True:
                helpers.manageNumberEntry(entryArray)


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
