import numpy as np
import random
import os

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
def generateArray(height, width):
    array = np.zeros((height, width))
    for SubArray in array:
        for i, cell in enumerate(SubArray):
            SubArray[i] = random.choice([0, 0, 0, 0, 1])

    return array

# Modifies existing 2D array using specified rules
def applyRules(ogArray):
    array = ogArray
    for subi, SubArray in enumerate(ogArray):
        for i, cell in enumerate(SubArray):
            AliveCount = 0

            try:
                AliveCount = AliveCount + int(ogArray[subi - 1][i - 1])
                print(1)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi - 1][i])
                print(2)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi - 1][i + 1])
                print(3)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi][i - 1])
                print(4)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi][i + 1])
                print(5)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi + 1][i - 1])
                print(6)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi + 1][i])
                print(7)
            except Exception: pass

            try:
                AliveCount = AliveCount + int(ogArray[subi + 1][i + 1])
                print(8)
            except Exception: pass

            print(subi, i, AliveCount)

            if (cell == 1) and ((AliveCount <= 1) or (AliveCount > 3)):
                array[subi][i] = 0
            elif (cell == 0) and (AliveCount == 3):
                array[subi][i] = 1

    return array
