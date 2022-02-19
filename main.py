import helpers
import pygame
import pygame_gui
import numpy as np
import time
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
    running = True

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    Scale = 20
    Likelihood = 5
    Board = helpers.generateArray(int(h / Scale), int(w / Scale), Likelihood)
    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)

    Continuous = True
    WasContinuous = True
    Step = False
    NewBoard = False
    MenuOpen = False
    CurrentBoardSurf = None

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3

    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Quit (F4)', manager=manager, visible=0)
    all_buttons = [back_to_game_button, show_controls_button, quit_game_button]

    controls_header_font = pygame.font.SysFont('arial', size=30, bold=True)
    controls_font = pygame.font.SysFont('arial', size=18)

    controls_header_text = controls_header_font.render("Controls", True, (190, 190, 190))
    controls_pause_text = controls_font.render("Pause: spacebar", True, (152, 152, 152))
    controls_step_text = controls_font.render("Step: w (only works while paused)", True, (152, 152, 152))
    controls_reset_text = controls_font.render("Reset: r", True, (152, 152, 152))
    controls_rect = pygame.Rect((w / 2 - 510, h / 4 + 2), (300, 400))

    while running:
        time_delta = clock.tick(120)/1000.0
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
                elif event.type == pygame.KEYUP and event.key == pygame.K_r:
                    NewBoard = True

            if (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_to_game_button):
                if MenuOpen is False:
                    WasContinuous = Continuous
                    Continuous = False
                    CurrentBoardSurf = helpers.updateScreenWithBoard(Board, surf, infoObject, True)
                    show_controls_button.set_text('Show controls')
                    MenuOpen = OpenMenu(all_buttons)
                else:
                    Continuous = WasContinuous
                    MenuOpen = CloseMenu(all_buttons)
                    CurrentBoardSurf = helpers.updateScreenWithBoard(Board, surf, infoObject)

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                pygame.draw.rect(surf, (76, 80, 82), controls_rect)
                surf.blit(controls_header_text, (w / 2 - 500, h / 4 + 12))
                surf.blit(controls_pause_text, (w / 2 - 500, h / 4 + 50))
                surf.blit(controls_step_text, (w / 2 - 500, h / 4 + 75))
                surf.blit(controls_reset_text, (w / 2 - 500, h / 4 + 100))
                pygame.display.update(controls_rect)
            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                surf.blit(CurrentBoardSurf, (0, 0))

            manager.process_events(event)

        manager.update(time_delta)

        if (Continuous is False) and (Step is True):
            CurrentBoardSurf = helpers.updateGOL(Board, surf, infoObject)
            Step = False
        elif Continuous is True:
            CurrentBoardSurf = helpers.updateGOL(Board, surf, infoObject)

        if NewBoard is True:
            Board = helpers.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
            Board = np.rot90(Board)
            CurrentBoardSurf = helpers.updateGOL(Board, surf, infoObject)
            NewBoard = False

        manager.draw_ui(surf)
        pygame.display.update()



def OpenMenu(ButtonsArray):
    for button in ButtonsArray:
        # button.visible = 1
        button.show()

    return True

def CloseMenu(ButtonsArray):
    for button in ButtonsArray:
        # button.visible = 0
        button.hide()

    return False


if __name__ == "__main__":
    main()
