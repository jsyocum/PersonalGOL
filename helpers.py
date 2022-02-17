import numpy as np
import random
import os
import pygame

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

# Modifies existing 2D array using specified rules
def applyRules(ogArray):
    array = ogArray
    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            ArrayHeight = ogArray.shape[0]
            ArrayWidth = ogArray.shape[1]

            AliveCount = 0

            if (subi - 1 >= 0) and (i - 1 >= 0):
                AliveCount = AliveCount + int(ogArray[subi - 1][i - 1]) / 255

            if (subi - 1 >= 0):
                AliveCount = AliveCount + int(ogArray[subi - 1][i]) / 255

            if (subi - 1 >= 0) and (i + 1 < ArrayWidth):
                AliveCount = AliveCount + int(ogArray[subi - 1][i + 1]) / 255

            if (i - 1 >= 0):
                AliveCount = AliveCount + int(ogArray[subi][i - 1]) / 255

            if (i + 1 < ArrayWidth):
                AliveCount = AliveCount + int(ogArray[subi][i + 1]) / 255

            if (subi + 1 < ArrayHeight) and (i - 1 >= 0):
                AliveCount = AliveCount + int(ogArray[subi + 1][i - 1]) / 255

            if (subi + 1 < ArrayHeight):
                AliveCount = AliveCount + int(ogArray[subi + 1][i]) / 255

            if (subi + 1 < ArrayHeight) and (i + 1 < ArrayWidth):
                AliveCount = AliveCount + int(ogArray[subi + 1][i + 1]) / 255

            # print(subi, i, AliveCount)

            if (cell == 255) and ((AliveCount <= 1) or (AliveCount > 3)):
                array[subi][i] = 0
            elif (cell == 0) and (AliveCount == 3):
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
