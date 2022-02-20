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
    Scale = 20
    Likelihood = 5
    StepsPerSecond = 18
    Board = helpers.generateArray(int(h / Scale), int(w / Scale), Likelihood)
    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)
    step_stack.append(Board.copy())

    Continuous = True
    WasContinuous = True
    Step = False
    StepBack = False
    NewBoard = False
    MenuOpen = False
    CurrentBoardSurf = None

    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show parameters', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Quit (F4)', manager=manager, visible=0)
    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, quit_game_button]

    parameters_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 125), (225, 25)), start_value=20, value_range=(1, 200), manager=manager, visible=0, click_increment=5)
    parameters_max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 185), (225, 25)), start_value=18, value_range=(0.1, 1000), manager=manager, visible=0, click_increment=10)
    parameters_likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((w / 2 - 500, h / 4 + 245), (225, 25)), start_value=5, value_range=(1, 100), manager=manager, visible=0, click_increment=5)
    all_parameters_elements = [parameters_scale_slider, parameters_max_fps_slider, parameters_likelihood_slider]

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
    paramters_warning1_text = sidebar_font_bold.render("Changing any of these", True, (152, 152, 152))
    paramters_warning2_text = sidebar_font_bold.render("will reset the board.", True, (152, 152, 152))
    parameters_scale_text = sidebar_font.render("Scale:", True, (152, 152, 152))
    parameters_max_fps_text = sidebar_font.render("Max fps:", True, (152, 152, 152))
    parameters_likelihood_text = sidebar_font.render("Likelihood:", True, (152, 152, 152))

    while running:
        time_delta = clock.tick(StepsPerSecond)/1000.0
        time_delta_stack.append(time_delta)
        if len(time_delta_stack) > 2000:
            time_delta_stack.popleft()

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
                    CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject, True)
                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show parameters')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    Continuous = WasContinuous
                    MenuOpen = CloseUIElements(all_menu_buttons)
                    CloseUIElements(all_parameters_elements)
                    CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject)

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                pygame.draw.rect(surf, (76, 80, 82), controls_rect)
                surf.blit(controls_header_text, (w / 2 - 500, h / 4 + 12))
                helpers.printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, [controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text])
                pygame.display.update(controls_rect)

                if show_parameters_button.text == 'Hide parameters':
                    show_parameters_button.set_text('Show parameters')
                    CloseUIElements(all_parameters_elements)

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                surf.blit(CurrentBoardSurf, (0, 0))

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show parameters':
                show_parameters_button.set_text('Hide parameters')
                pygame.draw.rect(surf, (76, 80, 82), controls_rect)
                surf.blit(paramaters_header_text, (w / 2 - 500, h / 4 + 12))
                helpers.printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, [paramters_warning1_text, paramters_warning2_text])
                helpers.printLinesOfText(surf, w / 2 - 500, h / 4 + 100, 60, [parameters_scale_text, parameters_max_fps_text, parameters_likelihood_text])
                OpenUIElements(all_parameters_elements)

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                show_parameters_button.set_text('Show parameters')
                surf.blit(CurrentBoardSurf, (0, 0))
                CloseUIElements(all_parameters_elements)

            manager.process_events(event)

        manager.update(time_delta)

        if (Continuous is False) and (Step is True):
            CurrentBoardSurf = helpers.updateGOL(step_stack[-1], surf, infoObject, step_stack)
            Step = False
        elif (Continuous is False) and (StepBack is True):
            CurrentBoardSurf = helpers.stepBack(step_stack, surf, infoObject)
            StepBack = False
        elif Continuous is True:
            CurrentBoardSurf = helpers.updateGOL(step_stack[-1], surf, infoObject, step_stack)
            Step = False
            StepBack = False

        if NewBoard is True:
            Board = helpers.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
            Board = np.rot90(Board)
            step_stack.clear()
            step_stack.append(Board)
            CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, infoObject)
            NewBoard = False

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
