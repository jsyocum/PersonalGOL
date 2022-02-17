import helpers as h
import pygame
import numpy as np

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
    Scale = 6
    Likelihood = 10
    Board = h.generateArray(int(infoObject.current_h / Scale), int(infoObject.current_w / Scale), Likelihood)
    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Allow the game of life to commence
        Board = h.applyRules(Board)
        boardSurf = pygame.surfarray.make_surface(Board)
        boardSurf = pygame.transform.scale(boardSurf, (infoObject.current_w, infoObject.current_h))
        surf.blit(boardSurf, (0, 0))
        pygame.display.update()


if __name__ == "__main__":
    main()
