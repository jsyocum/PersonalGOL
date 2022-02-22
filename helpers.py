import numpy as np
import random
import os
import pygame
import pygame_gui
import totalsize
from scipy import signal

# Clears the console screen
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# Forces user to input the object type specified
def _input(message, input_type=str):
    while True:
        try:
            UserInput = input_type(input(message))

            if (type(UserInput) is int) and (UserInput > 0):
                return UserInput
            elif (type(UserInput) is int) and (UserInput <= 0):
                print("ERR: Input must be greater than 0")
        except Exception: pass

# Generates a matrix of the specified height and width. Randomizes each cell as either 0 or 1.
def generateArray(height, width, likelihood):
    array = np.zeros((height, width))
    chanceArray = np.zeros(likelihood - 1)
    chanceArray = np.append(chanceArray, 1)
    for SubArray in array:
        for i, cell in enumerate(SubArray):
            SubArray[i] = random.choice(chanceArray)

    return array

def sumOfNeighbors(array):
    kernel = np.ones((3, 3), dtype=int)
    kernel[1, 1] = 0
    return signal.convolve2d(array, kernel, mode="same")

# Modifies existing 2D array using specified rules
def applyRules(ogArray, step_stack):
    array = ogArray.copy()
    AliveCountArray = sumOfNeighbors(ogArray)

    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            if (cell == 1) and ((AliveCountArray[subi][i] <= 1) or (AliveCountArray[subi][i] > 3)):
                array[subi][i] = 0
            elif (cell == 0) and (AliveCountArray[subi][i] == 3):
                array[subi][i] = 1

    appendToStepStack(array, step_stack)
    return array

def appendToStepStack(Board, step_stack):
    if np.array_equal(Board, step_stack[-1]):
        pass
        print("here")
    else:
        step_stack.append(Board.copy())

    if totalsize.total_size(step_stack) > 1e+9:
        step_stack.popleft()

def stepBack(step_stack):
    if len(step_stack) > 1:
        step_stack.pop()

# Returns an array with the on characters in the place of the 1's and the off characters in the place of the 0's
def interpretArray(ogArray, onChar, offChar):
    array = np.empty_like(ogArray, dtype=str)
    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            if int(cell) == 1:
                array[subi][i] = onChar
            else:
                array[subi][i] = offChar

    return array

def updateScreenWithBoard(Board, surf, infoObject, color=pygame.Color('White'), RandomColor=False, RandomColorByPixel=False):
    if RandomColorByPixel is False:
        if RandomColor is True:
            color = pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

        colorAsInt = surf.map_rgb(color)
        coloredBoard = Board * colorAsInt
    else:
        coloredBoard = Board.copy()
        for subi, SubArray in enumerate(coloredBoard):
            for i, Pixel in enumerate(SubArray):
                coloredBoard[subi][i] = coloredBoard[subi][i] * surf.map_rgb(pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))

    boardSurf = pygame.Surface(Board.shape)

    ScreenRatio = infoObject.current_w / infoObject.current_h
    BoardSurfRatio = boardSurf.get_width() / boardSurf.get_height()
    Scale = None

    # If the ratio between width and height of the board surface is the same as the screen, scale it up directly
    if ScreenRatio == BoardSurfRatio:
        Scale = infoObject.current_w / boardSurf.get_width()

    # If the ratio of the screen's size is greater, then the board surface's width is disproprotionately smaller
    elif ScreenRatio > BoardSurfRatio:
        Scale = infoObject.current_h / boardSurf.get_height()

    else:
        Scale = infoObject.current_w / boardSurf.get_width()

    pygame.surfarray.blit_array(boardSurf, coloredBoard)
    boardSurf = pygame.transform.scale(boardSurf, (boardSurf.get_width() * Scale, boardSurf.get_height() * Scale))

    blitBoardOnScreenEvenly(surf, boardSurf, infoObject)

    return boardSurf

def blitBoardOnScreenEvenly(surf, boardSurf, infoObject):
    surf.fill((0, 0, 0))
    surf.blit(boardSurf, (infoObject.current_w / 2 - boardSurf.get_width() / 2, infoObject.current_h / 2 - boardSurf.get_height() / 2))

def printLinesOfText(surf, left, top, spacing, lines):
    for i, line in enumerate(lines):
        surf.blit(line, (left, top + (spacing * i)))

def showControls(surf, w, h, controls_rect, controls_header_text, controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text):
    pygame.draw.rect(surf, (76, 80, 82), controls_rect)
    surf.blit(controls_header_text, (w / 2 - 500, h / 4 + 12))
    printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, [controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text])

def showParameters(surf, w, h, controls_rect, all_paramaters_texts):
    pygame.draw.rect(surf, (76, 80, 82), controls_rect)
    surf.blit(all_paramaters_texts[0], (w / 2 - 500, h / 4 + 12))
    printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, [all_paramaters_texts[1], all_paramaters_texts[2]])
    printLinesOfText(surf, w / 2 - 500, h / 4 + 100, 60, [all_paramaters_texts[3], all_paramaters_texts[4], all_paramaters_texts[5], all_paramaters_texts[6], all_paramaters_texts[9]])
    surf.blit(all_paramaters_texts[7], (w / 2 - 442, h / 4 + 305))
    surf.blit(all_paramaters_texts[8], (w / 2 - 367, h / 4 + 305))

    surf.blit(all_paramaters_texts[10], (w / 2 - 500, h / 4 + 365))
    surf.blit(all_paramaters_texts[11], (w / 2 - 425, h / 4 + 365))
    surf.blit(all_paramaters_texts[12], (w / 2 - 350, h / 4 + 365))


def manageSliderAndEntryWithArray(array):
    for tuple in array:
        manageSliderAndEntry(tuple[0], tuple[1], tuple[2], tuple[3])

def manageSliderAndEntry(slider, entry, previousSliderValue, PreviousEntryValue):
    if (PreviousEntryValue is not None) and (entry.is_focused is not True):
        if (entry.get_text() == '') or (slider.value_range[0] > int(entry.get_text())):
            entry.set_text(str(slider.value_range[0]))

        elif (int(entry.get_text()) > slider.value_range[1]):
            entry.set_text(str(slider.value_range[1]))

    if previousSliderValue != slider.get_current_value():
        entry.set_text(str(slider.get_current_value()))

    elif PreviousEntryValue != entry.get_text():
        if (entry.get_text() == '') or (slider.value_range[0] > int(entry.get_text())):
            slider.set_current_value(slider.value_range[0])

        elif (int(entry.get_text()) > slider.value_range[1]):
            slider.set_current_value(slider.value_range[1])

        else:
            slider.set_current_value(int(entry.get_text()))

def manageNumberEntry(entryArray):
    entry = entryArray[0]
    min = entryArray[1]
    max = entryArray[2]

    if (entry.get_text() == '') or (min > int(entry.get_text())):
        entry.set_text(str(min))

    elif (int(entry.get_text()) > max):
        entry.set_text(str(max))
