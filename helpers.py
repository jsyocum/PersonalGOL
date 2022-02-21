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
    chanceArray = np.append(chanceArray, 255)
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
    array = ogArray
    AliveCountArray = sumOfNeighbors(ogArray) / 255

    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            if (cell == 255) and ((AliveCountArray[subi][i] <= 1) or (AliveCountArray[subi][i] > 3)):
                array[subi][i] = 0
            elif (cell == 0) and (AliveCountArray[subi][i] == 3):
                array[subi][i] = 255

    appendToStepStack(array, step_stack)
    return array

def stepBack(step_stack, surf, infoObject):
    if len(step_stack) > 1:
        step_stack.pop()

    PreviousBoard = step_stack[-1]

    return updateScreenWithBoard(PreviousBoard, surf, infoObject)

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

def updateGOL(Board, surf, infoObject, step_stack):
    Board = applyRules(Board.copy(), step_stack)
    return updateScreenWithBoard(Board, surf, infoObject)

def updateScreenWithBoard(Board, surf, infoObject, darken=False):
    if darken is False:
        boardSurf = pygame.surfarray.make_surface(Board)
    else:
        boardSurf = pygame.surfarray.make_surface(Board / 255 * random.randint(0, 255))
    boardSurf = pygame.transform.scale(boardSurf, (infoObject.current_w, infoObject.current_h))
    surf.blit(boardSurf, (0, 0))
    return boardSurf

def appendToStepStack(Board, step_stack):
    if np.array_equal(Board, step_stack[-1]):
        pass
    else:
        step_stack.append(Board.copy())

    if totalsize.total_size(step_stack) > 1e+9:
        step_stack.popleft()

def printLinesOfText(surf, left, top, spacing, lines):
    for i, line in enumerate(lines):
        surf.blit(line, (left, top + (spacing * i)))

def showParameters(surf, w, h, controls_rect, all_paramaters_texts):
    pygame.draw.rect(surf, (76, 80, 82), controls_rect)
    surf.blit(all_paramaters_texts[0], (w / 2 - 500, h / 4 + 12))
    printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, [all_paramaters_texts[1], all_paramaters_texts[2]])
    printLinesOfText(surf, w / 2 - 500, h / 4 + 100, 60, [all_paramaters_texts[3], all_paramaters_texts[4], all_paramaters_texts[5], all_paramaters_texts[6]])
    surf.blit(all_paramaters_texts[7], (w / 2 - 442, h / 4 + 305))
    surf.blit(all_paramaters_texts[8], (w / 2 - 367, h / 4 + 305))

def manageSliderAndEntryWithArray(array):
    for tuple in array:
        manageSliderAndEntry(tuple[0], tuple[1], tuple[2], tuple[3])

def manageSliderAndEntry(slider, entry, previousSliderValue, PreviousEntryValue):
    if PreviousEntryValue is not None:
        if (entry.get_text() == '') or (slider.value_range[0] > int(entry.get_text())):
            entry.set_text(str(slider.value_range[0]))

        elif (int(entry.get_text()) > slider.value_range[1]):
            entry.set_text(str(slider.value_range[1]))

    if previousSliderValue != slider.get_current_value():
        entry.set_text(str(slider.get_current_value()))

    elif PreviousEntryValue != entry.get_text():
        slider.set_current_value(int(entry.get_text()))

def manageNumberEntry(entry, min, max):
    if (entry.get_text() == '') or (min > int(entry.get_text())):
        entry.set_text(str(min))

    elif (int(entry.get_text()) > max):
        entry.set_text(str(max))
