import numpy as np
import random
import os
import pygame
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
def applyRules(ogArray):
    array = ogArray
    AliveCountArray = sumOfNeighbors(ogArray) / 255

    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            if (cell == 255) and ((AliveCountArray[subi][i] <= 1) or (AliveCountArray[subi][i] > 3)):
                array[subi][i] = 0
            elif (cell == 0) and (AliveCountArray[subi][i] == 3):
                array[subi][i] = 255

    return array

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

def updateGOL(Board, surf, infoObject):
    Board = applyRules(Board)
    updateScreenWithBoard(Board, surf, infoObject)

def updateScreenWithBoard(Board, surf, infoObject):
    boardSurf = pygame.surfarray.make_surface(Board)
    boardSurf = pygame.transform.scale(boardSurf, (infoObject.current_w, infoObject.current_h))
    surf.blit(boardSurf, (0, 0))
