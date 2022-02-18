import helpers as h
import pygame
import numpy as np
import time

def main():
    # Set up pygame
    pygame.init()
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Personal Game Of Life")
    surf = pygame.display.set_mode((0, 0))
    running = True
    infoObject = pygame.display.Info()

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    Scale = 20
    Likelihood = 5
    Board = h.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)

    Continuous = True
    Step = False
    NewBoard = False

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                Continuous = not Continuous
            elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
                Step = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == MIDDLE:
                NewBoard = True

        if (Continuous is False) and (Step is True):
            h.updateGOL(Board, surf, infoObject)
            Step = False
        elif Continuous is True:
            h.updateGOL(Board, surf, infoObject)

        if NewBoard is True:
            Board = h.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
            Board = np.rot90(Board)
            h.updateGOL(Board, surf, infoObject)
            NewBoard = False



if __name__ == "__main__":
    main()
