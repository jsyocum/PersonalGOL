import numpy as np
import random
import os
import ast
import pygame
import totalsize
import math
import sys
from scipy import signal
from PIL.PngImagePlugin import PngImageFile, PngInfo
from configparser import ConfigParser
from pathlib import Path
from get_shapes_dict import position_shape, get_shapes_dict

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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def convert_themes_array_to_strings(array):
    strings_array = []
    for theme in array:
        strings_array.append(str(theme))

    return strings_array

def convert_strings_to_themes_array(strings_array):
    array = []
    for string in strings_array:
        theme = convert_string_to_theme(string)
        array.append(theme)

    return array

def convert_string_to_theme(string):
    theme = ast.literal_eval(string)
    for i, color in enumerate(theme):
        if i > 0:
            theme[i] = pygame.Color(color)

    return theme

# Generates a matrix of the specified height and width. Randomizes each cell as either 0 or 1.
def generateArray(height, width, likelihood):
    array = np.zeros((height, width))
    chanceArray = np.zeros(likelihood - 1)
    chanceArray = np.append(chanceArray, 1)
    for SubArray in array:
        for i, cell in enumerate(SubArray):
            SubArray[i] = random.choice(chanceArray)

    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    array = np.rot90(array)
    theme_board = np.zeros(array.shape, dtype=int)

    return array, theme_board

def determineWidthAndHeight(config_dict, w, h):
    if config_dict["CustomBoardSizeEnabled"][0] is True:
        width = config_dict["CustomBoardSizeWidth"][0]
        height = config_dict["CustomBoardSizeHeight"][0]
    else:
        width = w / config_dict["Scale"][0]
        height = h / config_dict["Scale"][0]

    return int(width), int(height)

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
    if not np.array_equal(Board, step_stack[-1]):
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

def add_selection_to_color(color, select_color):
    if color.r > 230 and color.g > 230 and color.b > 230:
        colors_added = pygame.Color(int(color.r * 0.5) + select_color.r, int(color.g * 0.5) + select_color.g, int(color.b * 0.5) + select_color.b)
    else:
        colors_added = pygame.Color(min(color.r + select_color.r, 255), min(color.g + select_color.g, 255), min(color.b + select_color.b, 255))

    return colors_added


def get_random_theme_board(board):
    theme_board = np.zeros(board.shape, dtype=int)
    chanceArray = range(0, 5)
    for SubArray in theme_board:
        for i, cell in enumerate(SubArray):
            SubArray[i] = random.choice(chanceArray)

    return theme_board

# The theme_board is the same shape as the board. The default theme is 0, which is just a square of solid color.
# The themes array contains tuples of information that defines the theme for its index. So at index 0, it describes the shape as being a square with a solid color.
# The user can create as many themes as they want, each with different shape and/or color.
# This function takes the information from the board and theme_board to bring them together into a properly scaled surface.
def complex_blit_array(board, theme_board, themes, shapes_dict, surf, EditMode, EditCheckerboardBrightness, EvenOrOdd, SelectedCells) -> pygame.surface:
    Scale = getScale(board, surf.get_width(), surf.get_height())[0]
    boardSurf = pygame.Surface((board.shape[0] * Scale, board.shape[1] * Scale))
    checkerboard_color = pygame.Color(EditCheckerboardBrightness, EditCheckerboardBrightness, EditCheckerboardBrightness)

    for subi, SubArray in enumerate(board):
        for i, Square in enumerate(SubArray):
            select_color = pygame.Color('Black')
            if len(SelectedCells) == 2:
                x_1, y_1 = SelectedCells[0][0], SelectedCells[0][1]
                x_2, y_2 = SelectedCells[1][0], SelectedCells[1][1]
                if min(x_1, x_2) <= subi <= max(x_1, x_2):
                    if min(y_1, y_2) <= i <= max(y_1, y_2):
                        select_color = pygame.Color(27, 69, 109)

            if EditMode is True:
                square = pygame.Rect((subi * Scale, i * Scale), (Scale, Scale))
                checkerboard_color_final = pygame.Color('Black')

                if (subi % 2) == 0:
                    if (i % 2) == EvenOrOdd:
                        checkerboard_color_final = checkerboard_color
                else:
                    if (i % 2) != EvenOrOdd:
                        checkerboard_color_final = checkerboard_color

                checkerboard_color_final = add_selection_to_color(checkerboard_color_final, select_color)
                pygame.draw.rect(boardSurf, checkerboard_color_final, square)

            if Square == 1:
                theme_index = theme_board[subi][i]
                theme = themes[theme_index]

                shapes = shapes_dict[theme[0]]
                for s, shape in enumerate(shapes):
                    color_for_shape = theme[s + 1]
                    color_for_shape = add_selection_to_color(color_for_shape, select_color)

                    top_left = (subi * Scale, i * Scale)
                    shape = position_shape(shape, top_left)
                    if shape[1] is True:
                        square = pygame.Rect(shape[0])
                        pygame.draw.rect(boardSurf, color_for_shape, square)

                    else:
                        pygame.draw.polygon(boardSurf, color_for_shape, shape[0])

    blitBoardOnScreenEvenly(surf, boardSurf, EditMode)

    return boardSurf

def get_example_themes(shapes_dict, theme_for_colors=None):
    if theme_for_colors is None:
        color_1 = pygame.Color(29, 125, 170)
        color_2 = pygame.Color(29, 33, 170)
        color_3 = pygame.Color(102, 29, 170)
        color_4 = pygame.Color(142, 29, 170)
    else:
        color_1 = theme_for_colors[1]
        color_2 = theme_for_colors[2]
        color_3 = theme_for_colors[3]
        color_4 = theme_for_colors[4]

    example_themes = []
    for p, pattern in enumerate(shapes_dict):
        example_themes.append([p, color_1, color_2, color_3, color_4])

    return example_themes

def generate_random_color():
    return pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

def generate_random_theme(size_of_patterns, max_colors):
    theme = [np.random.randint(0, size_of_patterns)]
    for i in range(max_colors):
        theme.append(generate_random_color())

    return theme

def create_theme_surf(theme, diameter) -> pygame.surface:
    surf = pygame.Surface((diameter, diameter))

    shapes_dict = get_shapes_dict(diameter)
    shapes = shapes_dict[theme[0]]
    for s, shape in enumerate(shapes):
        color_for_shape = theme[s + 1]

        if shape[1] is True:
            square = pygame.Rect(shape[0])
            pygame.draw.rect(surf, color_for_shape, square)

        else:
            pygame.draw.polygon(surf, color_for_shape, shape[0])

    return surf

def save_theme_surf_png(surf, theme_path, theme_index):
    if os.path.exists(theme_path) is not True:
        return None

    save_path = Path(str(theme_path) + '/' + str(theme_index) + '.png')
    pygame.image.save(surf, save_path)

def create_and_save_themes(themes, diameter, theme_path):
    for i, theme in enumerate(themes):
        surf = create_theme_surf(theme, diameter)
        save_theme_surf_png(surf, theme_path, i)

def updateScreenWithBoard(Board, surf, EditMode, color=pygame.Color('White'), RandomColor=False, RandomColorByPixel=False, Saving=False, DefaultEditCheckerboardBrightness=15, SelectedCells=[], EvenOrOdd=0):
    if RandomColorByPixel is False:
        if RandomColor is True:
            color = generate_random_color()

        colorAsInt = surf.map_rgb(color)
        coloredBoard = Board.copy() * colorAsInt
    else:
        coloredBoard = Board.copy()
        for subi, SubArray in enumerate(coloredBoard):
            for i, Pixel in enumerate(SubArray):
                coloredBoard[subi][i] = coloredBoard[subi][i] * surf.map_rgb(generate_random_color())

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

    Scale = getScale(Board, surf.get_width(), surf.get_height())[0]
    boardSurf = pygame.Surface(Board.shape)
    pygame.surfarray.blit_array(boardSurf, coloredBoard)
    boardSurf = pygame.transform.scale(boardSurf, (boardSurf.get_width() * Scale, boardSurf.get_height() * Scale))

    if Saving is False:
        blitBoardOnScreenEvenly(surf, boardSurf, EditMode)

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

    return math.ceil(Scale), Which

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
    board_pos = (max(int(math.ceil(mouse_pos[0] / scale) - 1), 0), max(int(math.ceil(mouse_pos[1] / scale) - 1), 0))

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

def showSelectionBoxSize(surf, board, ScaledHeldDownCells, HeldDownCells, font):
    cell_x_1, cell_y_1, cell_x_2, cell_y_2 = getPositions(HeldDownCells)

    cell_width = max(cell_x_1, cell_x_2) - min(cell_x_1, cell_x_2) + 1
    cell_height = max(cell_y_1, cell_y_2) - min(cell_y_1, cell_y_2) + 1

    x_1, y_1, x_2, y_2 = getPositions(ScaledHeldDownCells)

    x_mid = (x_1 + x_2) / 2
    y_mid = (y_1 + y_2) / 2

    left, right, top, bottom = getCorners(ScaledHeldDownCells)

    individual_cell_length, Which = getScale(board, surf.get_width(), surf.get_height())

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
def zoom(board, theme_board, HeldDownCells):
    left, right, top, bottom = getCorners(HeldDownCells)

    return board[left:right + 1, top:bottom + 1], theme_board[left:right + 1, top:bottom + 1]

def cut(board, HeldDownCells, Fill=False):
    left, right, top, bottom = getCorners(HeldDownCells)
    if Fill is False:
        board[left:right + 1, top:bottom + 1] = 0
    else:
        board[left:right + 1, top:bottom + 1] = 1

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

def fixSelectionBoxAfterLoad(board, HeldDownCells):
    SelectionBoxPresent = True
    board_w = board.shape[0]
    board_h = board.shape[1]

    if (HeldDownCells[0][0] > board_w - 1 and HeldDownCells[1][0] > board_w - 1) or (HeldDownCells[0][1] > board_h - 1 and HeldDownCells[1][1] > board_h - 1):
        HeldDownCells = []
        SelectionBoxPresent = False

    else:
        HeldDownCells[0] = (min(HeldDownCells[0][0], board_w - 1), min(HeldDownCells[0][1], board_h - 1))
        HeldDownCells[1] = (min(HeldDownCells[1][0], board_w - 1), min(HeldDownCells[1][1], board_h - 1))

    return HeldDownCells, SelectionBoxPresent

def adjustBoardDimensions(board, theme_board, AdjustBoardTuple, w, h, HeldDownCells, EvenOrOdd, AutoAdjust={"Top": 0, "Bottom": 0, "Left": 0, "Right": 0}):
    t = AutoAdjust["Top"]
    b = AutoAdjust["Bottom"]
    l = AutoAdjust["Left"]
    r = AutoAdjust["Right"]

    hdc = False
    adjustments_made = False
    initial_shape = board.shape

    if len(HeldDownCells) == 2:
        hdc = True

    same_x_pos = False
    same_y_pos = False
    if hdc and HeldDownCells[0][0] == HeldDownCells[1][0]:
        same_x_pos = True

    if hdc and HeldDownCells[0][1] == HeldDownCells[1][1]:
        same_y_pos = True

    if AdjustBoardTuple[1] is True or sum(AutoAdjust.values()) > 0:
        if board.shape[1] < h and (AdjustBoardTuple[0] == 'Top' or t > 0):
            if t % 2 == 1 or AdjustBoardTuple[0] == 'Top':
                EvenOrOdd ^= 1  # Same as doing EvenOrOdd = not EvenOrOdd

            top_row = np.zeros((board.shape[0], max(1, t)), dtype=int)
            board = np.append(top_row, board, axis=1)
            theme_board = np.append(top_row, theme_board, axis=1)
            if hdc:
                HeldDownCells[0] = (HeldDownCells[0][0], HeldDownCells[0][1] + 1 + t)
                HeldDownCells[1] = (HeldDownCells[1][0], HeldDownCells[1][1] + 1 + t)

        if board.shape[1] < h and (AdjustBoardTuple[0] == 'Bottom' or b > 0):
            bottom_row = np.zeros((board.shape[0], max(1, b)), dtype=int)
            board = np.append(board, bottom_row, axis=1)
            theme_board = np.append(theme_board, bottom_row, axis=1)

        if board.shape[0] < w and (AdjustBoardTuple[0] == 'Left' or l > 0):
            if l % 2 == 1 or AdjustBoardTuple[0] == 'Left':
                EvenOrOdd ^= 1

            left_column = np.zeros((max(1, l), board.shape[1]), dtype=int)
            board = np.append(left_column, board, axis=0)
            theme_board = np.append(left_column, theme_board, axis=0)
            if hdc:
                HeldDownCells[0] = (HeldDownCells[0][0] + 1 + l, HeldDownCells[0][1])
                HeldDownCells[1] = (HeldDownCells[1][0] + 1 + l, HeldDownCells[1][1])

        if board.shape[0] < w and (AdjustBoardTuple[0] == 'Right' or r > 0):
            right_column = np.zeros((max(1, r), board.shape[1]), dtype=int)
            board = np.append(board, right_column, axis=0)
            theme_board = np.append(theme_board, right_column, axis=0)

    else:
        if board.shape[1] > 1:
            if AdjustBoardTuple[0] == 'Top':
                EvenOrOdd ^= 1
                board = board[:, 1:]
                theme_board = theme_board[:, 1:]
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0], max(HeldDownCells[0][1] - 1, 0))
                    HeldDownCells[1] = (HeldDownCells[1][0], max(HeldDownCells[1][1] - 1, 0))
            elif AdjustBoardTuple[0] == 'Bottom':
                board = board[:, :-1]
                theme_board = theme_board[:, :-1]
                if hdc:
                    HeldDownCells[0] = (HeldDownCells[0][0], min(HeldDownCells[0][1], board.shape[1] - 1))
                    HeldDownCells[1] = (HeldDownCells[1][0], min(HeldDownCells[1][1], board.shape[1] - 1))

            if hdc and same_y_pos and HeldDownCells[0][1] == HeldDownCells[1][1]:
                HeldDownCells.clear()

        if board.shape[0] > 1:
            if AdjustBoardTuple[0] == 'Left':
                EvenOrOdd ^= 1
                board = board[1:, :]
                theme_board = theme_board[1:, :]
                if hdc:
                    HeldDownCells[0] = (max(HeldDownCells[0][0] - 1, 0), HeldDownCells[0][1])
                    HeldDownCells[1] = (max(HeldDownCells[1][0] - 1, 0), HeldDownCells[1][1])
            elif AdjustBoardTuple[0] == 'Right':
                board = board[:-1, :]
                theme_board = theme_board[:-1, :]
                if hdc:
                    HeldDownCells[0] = (min(HeldDownCells[0][0], board.shape[0] - 1), HeldDownCells[0][1])
                    HeldDownCells[1] = (min(HeldDownCells[1][0], board.shape[0] - 1), HeldDownCells[1][1])

            if hdc and same_x_pos and HeldDownCells[0][0] == HeldDownCells[1][0]:
                HeldDownCells.clear()

    if initial_shape != board.shape:
        adjustments_made = True

    return board, theme_board, EvenOrOdd, adjustments_made

def adjustBoardDimensionsFromDict(board, w, h, HeldDownCells, EvenOrOdd, AutoAdjustments):
    new_board = None

    return new_board, EvenOrOdd

def autoAdjustBoardDimensions(board, w, h, HeldDownCells, EvenOrOdd, AutoAdjustments):
    AutoAdjust = {"Top": 0, "Bottom": 0, "Left": 0, "Right": 0}

    if 1 in board[:, 0]:
        side = "Top"
        AutoAdjust[side] = 1
        AutoAdjustments[side] += 1

    if 1 in board[:, -1]:
        side = "Bottom"
        AutoAdjust[side] = 1
        AutoAdjustments[side] += 1

    if 1 in board[0, :]:
        side = "Left"
        AutoAdjust[side] = 1
        AutoAdjustments[side] += 1

    if 1 in board[-1, :]:
        side = "Right"
        AutoAdjust[side] = 1
        AutoAdjustments[side] += 1

    board, EvenOrOdd, adjustments_made = adjustBoardDimensions(board, (None, False), w, h, HeldDownCells, EvenOrOdd, AutoAdjust)

    return board, EvenOrOdd, AutoAdjustments

def blitBoardOnScreenEvenly(surf, boardSurf, EditMode):
    if EditMode is False:
        surf.fill((0, 0, 0))
    else:
        surf.fill((30, 30, 30))
    surf.blit(boardSurf, (surf.get_width() / 2 - boardSurf.get_width() / 2, surf.get_height() / 2 - boardSurf.get_height() / 2))

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

def setParametersValues(all_parameters_elements_matched, config_dict):
    for elements_array in all_parameters_elements_matched:
        config_dict[elements_array[4]][0] = elements_array[2] = elements_array[0].get_current_value()
        elements_array[3] = elements_array[1].get_text()

    return all_parameters_elements_matched, config_dict

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

def savePNGWithBoardInfo(save_path, CurrentBoardSurf, board, theme_board):
    save_path = str(save_path)
    save_path_dir = Path('/'.join(save_path.split('/')[:-1]))
    if os.path.exists(save_path_dir) is False:
        Path(save_path_dir).mkdir(parents=True, exist_ok=True)

    pygame.image.save(CurrentBoardSurf, save_path)

    targetImage = PngImageFile(save_path)
    metadata = PngInfo()

    board_string = convertArrayToString(board)
    theme_board_string = convertArrayToString(theme_board)
    metadata.add_text("BoardArray", board_string)
    metadata.add_text("ThemeBoardArray", theme_board_string)
    targetImage.save(save_path, pnginfo=metadata)

def loadPNGWithBoardInfo(load_path, step_stack):
    load_path = str(load_path)
    loaded = False
    if load_path.endswith('.png') is False:
        return loaded, load_path + ' is not a .png file'

    targetImage = PngImageFile(load_path)

    try:
        board_string = targetImage.text["BoardArray"]
        board = convertStringToArray(board_string)
    except:
        return loaded, load_path + ' does not contain a board array'

    try:
        theme_board_string = targetImage.text["ThemeBoardArray"]
        theme_board = convertStringToArray(theme_board_string)
    except:
        theme_board = np.zeros(board.shape, dtype=int)

    step_stack.clear()
    step_stack.append(board)

    loaded = True

    return loaded, 'Board loaded: ' + load_path, theme_board

def convertArrayToString(array):
    return '\n'.join('\t'.join('%0.3f' % x for x in y) for y in array)

def convertStringToArray(string):
    return np.array([[int(j) for j in i.split('\t')] for i in string.splitlines()])

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

def quick_post(self, data_name, data, event_id):
    event_data = {data_name: data,
                  'ui_element': self,
                  'ui_object_id': self.most_specific_combined_id}
    pygame.event.post(pygame.event.Event(event_id, event_data))
