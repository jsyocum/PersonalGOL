import helpers
import pygame
import pygame_gui
import numpy as np
import time

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

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3

    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (esc)', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    while running:
        time_delta = clock.tick(120)/1000.0
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
                    helpers.updateScreenWithBoard(Board, surf, infoObject, True)
                    MenuOpen = OpenMenu([back_to_game_button, quit_game_button])
                else:
                    Continuous = WasContinuous
                    MenuOpen = CloseMenu([back_to_game_button, quit_game_button])
                    helpers.updateScreenWithBoard(Board, surf, infoObject)

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                running = False

            manager.process_events(event)

        manager.update(time_delta)

        if (Continuous is False) and (Step is True):
            helpers.updateGOL(Board, surf, infoObject)
            Step = False
        elif Continuous is True:
            helpers.updateGOL(Board, surf, infoObject)

        if NewBoard is True:
            Board = helpers.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
            Board = np.rot90(Board)
            helpers.updateGOL(Board, surf, infoObject)
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
