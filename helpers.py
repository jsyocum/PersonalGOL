import numpy as np
import random
import os
import pygame
import totalsize
import math
from scipy import signal
from PIL.PngImagePlugin import PngImageFile, PngInfo
from configparser import ConfigParser
from pathlib import Path

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

def updateScreenWithBoard(Board, surf, infoObject, EditMode, color=pygame.Color('White'), RandomColor=False, RandomColorByPixel=False, Saving=False, DefaultEditCheckerboardBrightness=15, SelectedCells=[], EvenOrOdd=0):
    if RandomColorByPixel is False:
        if RandomColor is True:
            color = pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

        colorAsInt = surf.map_rgb(color)
        coloredBoard = Board.copy() * colorAsInt
    else:
        coloredBoard = Board.copy()
        for subi, SubArray in enumerate(coloredBoard):
            for i, Pixel in enumerate(SubArray):
                coloredBoard[subi][i] = coloredBoard[subi][i] * surf.map_rgb(pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))

    if EditMode is True:
        for subi, SubArray in enumerate(coloredBoard):
            for i, Pixel in enumerate(SubArray):
                if coloredBoard[subi][i] == 0:
                    if (subi % 2) == 0:
                        if (i % 2) == EvenOrOdd:
                            coloredBoard[subi][i] = surf.map_rgb(pygame.Color(DefaultEditCheckerboardBrightness, DefaultEditCheckerboardBrightness, DefaultEditCheckerboardBrightness))
                    else:
                        if (i % 2) != EvenOrOdd:
                            coloredBoard[subi][i] = surf.map_rgb(pygame.Color(DefaultEditCheckerboardBrightness, DefaultEditCheckerboardBrightness, DefaultEditCheckerboardBrightness))

                if len(SelectedCells) == 2:
                    x_1, y_1 = SelectedCells[0][0], SelectedCells[0][1]
                    x_2, y_2 = SelectedCells[1][0], SelectedCells[1][1]
                    if min(x_1, x_2) <= subi <= max(x_1, x_2):
                        if min(y_1, y_2) <= i <= max(y_1, y_2):
                            cell_color = surf.unmap_rgb(int(coloredBoard[subi][i]))
                            select_color = pygame.Color(27, 69, 109)

                            if cell_color.r > 230 and cell_color.g > 230 and cell_color.b > 230:
                                cell_color = pygame.Color(int(cell_color.r * 0.5) + select_color.r, int(cell_color.g * 0.5) + select_color.g, int(cell_color.b * 0.5) + select_color.b)
                            else:
                                cell_color = pygame.Color(min(cell_color.r + select_color.r, 255), min(cell_color.g + select_color.g, 255), min(cell_color.b + select_color.b, 255))

                            coloredBoard[subi][i] = surf.map_rgb(cell_color)

    Scale = getScale(Board, infoObject.current_w, infoObject.current_h)[0]
    boardSurf = pygame.Surface(Board.shape)
    pygame.surfarray.blit_array(boardSurf, coloredBoard)
    boardSurf = pygame.transform.scale(boardSurf, (boardSurf.get_width() * Scale, boardSurf.get_height() * Scale))

    if Saving is False:
        blitBoardOnScreenEvenly(surf, boardSurf, infoObject, EditMode)

    return boardSurf

def getScale(board, w, h):
    board_w = board.shape[0]
    board_h = board.shape[1]

    ScreenRatio = w / h
    BoardSurfRatio = board_w / board_h
    Scale = None
    Which = 0

    # If the ratio between width and height of the board surface is the same as the screen, scale it up directly
    if ScreenRatio == BoardSurfRatio:
        Scale = w / board_w

    # If the ratio of the screen's size is greater, then the board surface's width is disproprotionately smaller
    elif ScreenRatio > BoardSurfRatio:
        Scale = h / board_h
        Which = 1

    else:
        Scale = w / board_w
        Which = 2

    return Scale, Which

def isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h):
    IsCollidingWithBoardSurf = False
    IsCollidingWithActionWindow = isMouseCollidingWithActionWindow(action_window, mouse_pos)
    rel_mouse_pos = None

    x_start = w / 2 - CurrentBoardSurf.get_width() / 2
    x_stop = w / 2 + CurrentBoardSurf.get_width() / 2
    y_start = h / 2 - CurrentBoardSurf.get_height() / 2
    y_stop = h / 2 + CurrentBoardSurf.get_height() / 2

    if (x_start <= mouse_pos[0] <= x_stop) and (y_start <= mouse_pos[1] <= y_stop):
        rel_mouse_pos = (mouse_pos[0] - x_start, mouse_pos[1] - y_start)
        IsCollidingWithBoardSurf = True

    return IsCollidingWithBoardSurf, IsCollidingWithActionWindow, rel_mouse_pos

def isMouseCollidingWithActionWindow(action_window, mouse_pos):
    IsCollidingWithActionWindow = False

    if action_window is not None and action_window.alive():
        IsCollidingWithActionWindow = action_window.get_relative_rect().collidepoint(mouse_pos)

    return IsCollidingWithActionWindow

def getBoardPosition(board, mouse_pos, w, h):
    scale, which = getScale(board, w, h)
    board_pos = (int(math.ceil(mouse_pos[0] / scale) - 1), int(math.ceil(mouse_pos[1] / scale) - 1))

    return board_pos

def getScaledHeldDownCells(board, boardSurf, HeldDownCellsArray, w, h):
    ScaledHeldDownCells = []
    if len(HeldDownCellsArray) == 2:
        ScaledHeldDownCells = [getScaledBoardPosition(board, boardSurf, HeldDownCellsArray[0], w, h), getScaledBoardPosition(board, boardSurf, HeldDownCellsArray[1], w, h)]

    return ScaledHeldDownCells

def getScaledBoardPosition(board, boardSurf, board_pos, w, h):
    scale, which = getScale(board, w, h)
    width_dif = (w - boardSurf.get_width()) / 2
    height_dif = (h - boardSurf.get_height()) / 2
    scaled_board_pos = (board_pos[0] * scale + width_dif, board_pos[1] * scale + height_dif)

    return scaled_board_pos

def getPositions(HeldDownCells):
    x_1, y_1 = HeldDownCells[0][0], HeldDownCells[0][1]
    x_2, y_2 = HeldDownCells[1][0], HeldDownCells[1][1]

    return x_1, y_1, x_2, y_2

def getCorners(HeldDownCells):
    x_1, y_1, x_2, y_2 = getPositions(HeldDownCells)

    left = min(x_1, x_2)
    right = max(x_1, x_2)
    top = min(y_1, y_2)
    bottom = max(y_1, y_2)

    return left, right, top, bottom

def showSelectionBoxSize(surf, ScaledHeldDownCells, HeldDownCells, font):
    cell_x_1, cell_y_1, cell_x_2, cell_y_2 = getPositions(HeldDownCells)

    cell_width = max(cell_x_1, cell_x_2) - min(cell_x_1, cell_x_2) + 1
    cell_height = max(cell_y_1, cell_y_2) - min(cell_y_1, cell_y_2) + 1

    x_1, y_1, x_2, y_2 = getPositions(ScaledHeldDownCells)

    x_mid = (x_1 + x_2) / 2
    y_mid = (y_1 + y_2) / 2

    left, right, top, bottom = getCorners(ScaledHeldDownCells)

    width = right - left
    individual_cell_length = width / max(cell_width - 1, 1)

    width_text = font.render(str(cell_width), True, (190, 190, 190))
    height_text = font.render(str(cell_height), True, (190, 190, 190))

    width_text_pos = ()
    height_text_pos = ()

    if top - width_text.get_height() - 5 > 0:
        width_text_pos = (x_mid - width_text.get_width() / 2 + individual_cell_length / 2, top - width_text.get_height() - 5)
    else:
        width_text_pos = (x_mid - width_text.get_width() / 2 + individual_cell_length / 2, top + 5)


    if left - height_text.get_width() - 10 > 0:
        height_text_pos = (left - height_text.get_width() - 10, y_mid - height_text.get_height() / 2 + individual_cell_length / 2)
    else:
        height_text_pos = (left + 10, y_mid - height_text.get_height() / 2 + individual_cell_length / 2)

    surf.blit(width_text, width_text_pos)
    surf.blit(height_text, height_text_pos)

# Just copies that section of the board, so can use for zooming or copy/pasting
def zoom(board, HeldDownCells):
    left, right, top, bottom = getCorners(HeldDownCells)

    return board[left:right + 1, top:bottom + 1]

def cut(board, HeldDownCells):
    left, right, top, bottom = getCorners(HeldDownCells)
    board[left:right + 1, top:bottom + 1] = 0

    return board

def paste(board, HeldDownCells, CopiedBoard):
    width = board.shape[0]
    height = board.shape[1]

    c_width = CopiedBoard.shape[0]
    c_height = CopiedBoard.shape[1]

    left, right, top, bottom = getCorners(HeldDownCells)

    board[left:min(left + c_width, width), top:min(top + c_height, height)] = CopiedBoard[:min(c_width, width - left), :min(c_height, height - top)]

    return board

def rotate(board, HeldDownCells):
    left, right, top, bottom = getCorners(HeldDownCells)
    width = right - left
    height = bottom - top
    slice = board[left:right + 1, top:bottom + 1]

    if width != height:
        slice = np.rot90(slice)

    slice = np.rot90(slice)

    board[left:right + 1, top:bottom + 1] = slice

    return board

def flip(board, HeldDownCells):
    left, right, top, bottom = getCorners(HeldDownCells)
    width = right - left
    height = bottom - top
    slice = board[left:right + 1, top:bottom + 1]

    if height >= width:
        slice = np.fliplr(slice)
    else:
        slice = np.flipud(slice)

    board[left:right + 1, top:bottom + 1] = slice

    return board

def adjustBoardDimensions(board, AdjustBoardTuple, w, h, HeldDownCells, EvenOrOdd):
    board_w = board.shape[0]
    board_h = board.shape[1]
    new_board = None
    hdc = False

    if len(HeldDownCells) == 2:
        hdc = True

    same_x_pos = False
    same_y_pos = False
    if hdc and HeldDownCells[0][0] == HeldDownCells[1][0]:
        same_x_pos = True

    if hdc and HeldDownCells[0][1] == HeldDownCells[1][1]:
        same_y_pos = True

    if AdjustBoardTuple[1] is True:
        row = np.zeros((board_w, 1))
        column = np.zeros((1, board_h))

        if board_h < h:
            if AdjustBoardTuple[0] == 'Top':
                # same as doing EvenOrOdd = not EvenOrOdd
                EvenOrOdd ^= 1
                new_board = np.append(row, board, axis=1)
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0], HeldDownCells[0][1] + 1)
                    HeldDownCells[1] = (HeldDownCells[1][0], HeldDownCells[1][1] + 1)
            elif AdjustBoardTuple[0] == 'Bottom':
                new_board = np.append(board, row, axis=1)

        if board_w < w:
            if AdjustBoardTuple[0] == 'Left':
                EvenOrOdd ^= 1
                new_board = np.append(column, board, axis=0)
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0] + 1, HeldDownCells[0][1])
                    HeldDownCells[1] = (HeldDownCells[1][0] + 1, HeldDownCells[1][1])
            elif AdjustBoardTuple[0] == 'Right':
                new_board = np.append(board, column, axis=0)

    else:
        if board_h > 1:
            if AdjustBoardTuple[0] == 'Top':
                EvenOrOdd ^= 1
                new_board = board[:, 1:]
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0], max(HeldDownCells[0][1] - 1, 0))
                    HeldDownCells[1] = (HeldDownCells[1][0], max(HeldDownCells[1][1] - 1, 0))
            elif AdjustBoardTuple[0] == 'Bottom':
                new_board = board[:, :-1]
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0], min(HeldDownCells[0][1], board_h - 2))
                    HeldDownCells[1] = (HeldDownCells[1][0], min(HeldDownCells[1][1], board_h - 2))

            if hdc and same_y_pos and HeldDownCells[0][1] == HeldDownCells[1][1]:
                HeldDownCells.clear()

        else:
            new_board = board

        if board_w > 1:
            if AdjustBoardTuple[0] == 'Left':
                EvenOrOdd ^= 1
                new_board = board[1:, :]
                if hdc:
                    HeldDownCells[0] = (max(HeldDownCells[0][0] - 1, 0), HeldDownCells[0][1])
                    HeldDownCells[1] = (max(HeldDownCells[1][0] - 1, 0), HeldDownCells[1][1])
            elif AdjustBoardTuple[0] == 'Right':
                new_board = board[:-1, :]
                if hdc:
                    HeldDownCells[0] = (min(HeldDownCells[0][0], board_w - 2), HeldDownCells[0][1])
                    HeldDownCells[1] = (min(HeldDownCells[1][0], board_w - 2), HeldDownCells[1][1])

            if hdc and same_x_pos and HeldDownCells[0][0] == HeldDownCells[1][0]:
                HeldDownCells.clear()

        else:
            new_board = board

    return new_board, EvenOrOdd

def blitBoardOnScreenEvenly(surf, boardSurf, infoObject, EditMode):
    if EditMode is False:
        surf.fill((0, 0, 0))
    else:
        surf.fill((30, 30, 30))
    surf.blit(boardSurf, (infoObject.current_w / 2 - boardSurf.get_width() / 2, infoObject.current_h / 2 - boardSurf.get_height() / 2))

def printLinesOfText(surf, left, top, spacing, lines):
    for i, line in enumerate(lines):
        surf.blit(line, (left, top + (spacing * i)))

def showControls(surf, w, h, controls_rect, controls_header_text, text_array):
    pygame.draw.rect(surf, (76, 80, 82), controls_rect)
    surf.blit(controls_header_text, (w / 2 - 500, h / 4 + 12))
    printLinesOfText(surf, w / 2 - 500, h / 4 + 50, 25, text_array)

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

def getHeightOfElements(array):
    total_height = 0
    for element in array:
        rel_rect = element.get_relative_rect()
        total_height += (rel_rect.height + rel_rect.top) * 1.145

    return total_height

def getWidthOfElements(array):
    total_width = 0
    for element in array:
        rel_rect = element.get_relative_rect()
        total_width += (rel_rect.width + rel_rect.left) * 1.145

    return total_width

def savePNGWithBoardInfo(save_path, CurrentBoardSurf, board):
    save_path_dir = '\\'.join(save_path.split('\\')[:-1])
    if os.path.exists(save_path_dir) is False:
        Path(save_path_dir).mkdir(parents=True, exist_ok=True)

    pygame.image.save(CurrentBoardSurf, save_path)

    targetImage = PngImageFile(save_path)
    metadata = PngInfo()

    board_string = convertArrayToString(board)
    metadata.add_text("BoardArray", board_string)
    targetImage.save(save_path, pnginfo=metadata)

def loadPNGWithBoardInfo(load_path, step_stack, WasContinuous):
    targetImage = PngImageFile(load_path)

    try:
        board_string = targetImage.text["BoardArray"]
    except:
        return WasContinuous, load_path + ' does not contain a board array'

    board = convertStringToArray(board_string)

    step_stack.clear()
    step_stack.append(board)

    return False, 'Board loaded: ' + load_path

def convertArrayToString(array):
    return '\n'.join('\t'.join('%0.3f' % x for x in y) for y in array)

def convertStringToArray(string):
    return np.array([[float(j) for j in i.split('\t')] for i in string.splitlines()])

def anyAliveElements(array):
    any = False
    for element in array:
        if element is not None and element.alive() is True:
            any = True

    return any

# Used to make sure a config exists and sets one up properly
def initialConfigCheck(config_file_dir, config_file_path, config_dict):
    if os.path.isfile(config_file_path) is not True:
        Path(config_file_dir).mkdir(parents=True, exist_ok=True)

        config = writeDict(config_file_path, config_dict)

    else:
        config = ConfigParser()
        config.read(config_file_path)
        try: config.add_section('main')
        except: pass

        for key in config_dict:
            try:
                config_dict[key][0] = min(config.getint('main', key), config_dict[key][1])
            except:
                try:
                    config_dict[key][0] = config.getboolean('main', key)
                except:
                    config.set('main', key, str(config_dict[key][0]))

    with open(config_file_path, 'w') as f:
        config.write(f)

# Used throughout the program to overwrite the config file with the current settings
def writeDictToConfig(config_file_dir, config_file_path, config_dict):
    if os.path.isfile(config_file_path) is not True:
        Path(config_file_dir).mkdir(parents=True, exist_ok=True)

    config = writeDict(config_file_path, config_dict)

    with open(config_file_path, 'w') as f:
        config.write(f)

# Just a helper function for the other two above it
def writeDict(config_file_path, config_dict):
    config = ConfigParser()
    config.read(config_file_path)

    try: config.add_section('main')
    except: pass
    for key in config_dict:
        config.set('main', key, str(config_dict[key][0]))

    return config
