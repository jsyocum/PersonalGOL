import numpy as np
import random
import os
import traceback
import ast
import pygame
import pygame_gui
import totalsize
import math
import sys
from classes import ContextMenu, RightClickableElement
from scipy import signal
from PIL.PngImagePlugin import PngImageFile, PngInfo
from configparser import ConfigParser
from pathlib import Path
from copy import deepcopy
from get_shape_points import get_shape_points, get_pattern_types, get_max_patterns, get_max_shapes

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

def move_item_in_list(list, index, move_int, bottom_offset=0, top_offset=0, bottom_or_top='none'):
    bottom_or_top = bottom_or_top.lower()
    index_item = deepcopy(list[index])
    list.pop(index)

    new_index = deepcopy(index) + move_int

    # Check to make sure new_index is within bounds
    if new_index < 0 + bottom_offset:
        new_index = 0 + bottom_offset
    elif new_index > len(list) - top_offset:
        new_index = len(list) - top_offset

    if bottom_or_top != 'none':
        if bottom_or_top == 'bottom':
            new_index = 0 + bottom_offset

        elif bottom_or_top == 'top':
            new_index = len(list) - top_offset

        else:
            print(bottom_or_top, ' is not a valid argument for move_item_in_list function. Must be either bottom or top.')

    list.insert(new_index, index_item)

    return list, new_index

def get_distance_between_points(point_a, point_b):
    return math.sqrt((point_b[0] - point_a[0])**2 + (point_b[1] - point_a[1])**2)

def determine_slider_button_text_and_limit(lower_limit, upper_limit, value):
    if value > lower_limit:
        return '[X]', upper_limit

    else:
        return '[ ]', lower_limit

def convert_themes_array_to_strings(array):
    strings_array = []
    for theme in array:
        strings_array.append(str(theme))

    return strings_array

def convert_string_themes_array_to_real_array(string_array):
    themes = ast.literal_eval(string_array)
    for t, theme in enumerate(themes):
        themes[t] = convert_string_to_theme(theme)

    return themes

def convert_strings_to_themes_array(strings_array):
    array = []
    for string in strings_array:
        theme = convert_string_to_theme(string)
        array.append(theme)

    return array

def convert_string_to_theme(string):
    if type(string) == str:
        theme = ast.literal_eval(string)
    else:
        theme = string

    theme = fix_colors_in_theme(theme)

    return theme

def fix_colors_in_theme(theme):
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

    array[AliveCountArray < 2] = 0
    array[AliveCountArray == 3] = 1
    array[AliveCountArray > 3] = 0

    return array

def appendToStepStack(board, theme_board, step_stack):
    appended = False
    step = []

    if len(step_stack) == 0 or np.array_equal(board, step_stack[-1][0]) is False:
        step.append(board.copy())
        appended = True
    else:
        step.append(step_stack[-1][0].copy())

    if len(step_stack) == 0 or np.array_equal(theme_board, step_stack[-1][1]) is False:
        step.append(theme_board.copy())
        appended = True
    else:
        step.append(step_stack[-1][1].copy())

    if appended is True:
        step_stack.append(step)

    if totalsize.total_size(step_stack) > 1e+9:
        step_stack.popleft()

    return appended

def stepBack(step_stack):
    if len(step_stack) > 1:
        step_stack.pop()
        return True

    else:
        return False

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
    chanceArray = range(5)
    for SubArray in theme_board:
        for i, cell in enumerate(SubArray):
            SubArray[i] = random.choice(chanceArray)

    return theme_board

def should_redraw_surf(Appended, themes, previous_themes, edit_mode_changed, edit_checkerboard_brightness_changed, HeldDownCells, previous_HeldDownCells, DebugThemePatterns_changed):
    if Appended or edit_mode_changed or edit_checkerboard_brightness_changed or DebugThemePatterns_changed:
        return True

    elif themes != previous_themes:
        return True

    else:
        return False

# The theme_board is the same shape as the board. The default theme is 0, which is just a square of solid color.
# The themes array contains tuples of information that defines the theme for its index. So at index 0, it describes the shape as being a square with a solid color.
# The user can create as many themes as they want, each with different shape and/or color.
# This function takes the information from the board and theme_board to bring them together into a properly scaled surface.
def complex_blit_array(board, theme_board, themes, previous_themes, surf, EditMode, EditCheckerboardBrightness, select_color, EvenOrOdd, SelectedCells, DebugThemePatterns, DebugThemePatterns_changed, CurrentBoardSurf, previous_boards, edit_mode_changed, edit_checkerboard_brightness_changed) -> pygame.surface:
    Scale = getScale(board, surf.get_width(), surf.get_height())[0]
    surf_size = (board.shape[0] * Scale, board.shape[1] * Scale)

    if CurrentBoardSurf is not None and previous_boards is not None and previous_boards[0].shape == board.shape and DebugThemePatterns == 0 and not DebugThemePatterns_changed and not edit_mode_changed and not edit_checkerboard_brightness_changed:
        boardSurf = CurrentBoardSurf.copy()
        same_surf = True
    else:
        boardSurf = pygame.Surface(surf_size)
        same_surf = False

    checkerboard_color = pygame.Color(EditCheckerboardBrightness, EditCheckerboardBrightness, EditCheckerboardBrightness)
    blank_color = pygame.Color('Black')


    if EditMode is True and DebugThemePatterns > 0:
        for subi, SubArray in enumerate(board):
            for i, Square in enumerate(SubArray):
                if Square == 0:
                    draw_edit_mode_checker(subi, i, boardSurf, (subi * Scale, i * Scale), Scale, checkerboard_color, EvenOrOdd)


    for subi, SubArray in enumerate(board):
        for i, Square in enumerate(SubArray):
            top_left = (subi * Scale, i * Scale)
            final_select_color = pygame.Color('Black')


            checker_drawn = False
            if EditMode is True and Square == 0 and DebugThemePatterns == 0:
                checker_drawn = draw_edit_mode_checker(subi, i, boardSurf, top_left, Scale, checkerboard_color, EvenOrOdd)


            if same_surf is False:
                if Square == 1:
                    draw_cell(subi, i, boardSurf, theme_board, themes, top_left, Scale, final_select_color, DebugThemePatterns)

            else:
                if Square != previous_boards[0][subi][i] or theme_board[subi][i] != previous_boards[1][subi][i] or themes[theme_board[subi][i]] != previous_themes[theme_board[subi][i]]:
                    if Square == 1:
                        draw_cell(subi, i, boardSurf, theme_board, themes, top_left, Scale, final_select_color, DebugThemePatterns)
                    elif checker_drawn is False:
                        pygame.draw.rect(boardSurf, blank_color, pygame.Rect(top_left[0], top_left[1], Scale, Scale))

    previous_boards = [board, theme_board]
    return boardSurf, previous_boards

def draw_edit_mode_checker(subi, i, boardSurf, top_left, Scale, checkerboard_color, EvenOrOdd):
    checker_drawn = False
    if (subi % 2) == 0:
        if (i % 2) == EvenOrOdd:
            pygame.draw.rect(boardSurf, checkerboard_color, pygame.Rect(top_left[0], top_left[1], Scale, Scale))
            checker_drawn = True
    else:
        if (i % 2) != EvenOrOdd:
            pygame.draw.rect(boardSurf, checkerboard_color, pygame.Rect(top_left[0], top_left[1], Scale, Scale))
            checker_drawn = True

    return checker_drawn

def draw_cell(subi, i, boardSurf, theme_board, themes, top_left, Scale, final_select_color, debug_theme_patterns):
    theme_index = max(min(theme_board[subi][i], len(themes) - 1), 0)
    theme = themes[theme_index]

    shapes = get_shape_points(theme[0][0], theme[0][1], top_left, Scale)
    boardSurf = draw_theme_shapes(shapes, theme, boardSurf, final_select_color, debug_theme_patterns)

def draw_selection(board, surf, select_color, SelectedCells):
    if len(SelectedCells) == 2:
        Scale = getScale(board, surf.get_width(), surf.get_height())[0]
        SelectedCells_abs_pos = []
        for cell in SelectedCells:
            SelectedCells_abs_pos.append((cell[0] * Scale, cell[1] * Scale))

        top_left = (min(SelectedCells_abs_pos[0][0], SelectedCells_abs_pos[1][0]), min(SelectedCells_abs_pos[0][1], SelectedCells_abs_pos[1][1]))
        bottom_right = (max(SelectedCells_abs_pos[0][0], SelectedCells_abs_pos[1][0]) + Scale, max(SelectedCells_abs_pos[0][1], SelectedCells_abs_pos[1][1]) + Scale)
        selection_rect = pygame.Rect(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])

        temp_surf = pygame.Surface(selection_rect.size, pygame.SRCALPHA)
        temp_surf.fill(select_color)

        surf.blit(temp_surf, selection_rect.topleft)

        return selection_rect

def get_example_themes(theme_for_colors=None, pattern_type='Rectangles'):
    colors_array = []
    if theme_for_colors is None:
        for c in range(get_max_shapes() + 1):
            colors_array.append(generate_random_color())
    else:
        for color in theme_for_colors[1:]:
            colors_array.append(color)

    example_themes = []
    for int in range(get_max_patterns(pattern_type) + 1):
        example_themes.append(colors_array.copy())
        example_themes[-1].insert(0, [pattern_type, int])

    return example_themes

def generate_random_color():
    return pygame.Color(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

def clean_themes(themes):
    try:
        if themes == None or len(themes) == 0:
            return [generate_random_theme()]
    except: return [generate_random_theme()]

    for theme in themes:
        pattern_types = get_pattern_types()
        if theme[0][0] not in pattern_types[0]:
            theme[0][0] = pattern_types[np.random.randint(0, pattern_types[1] - 1)]

        max_patterns = get_max_patterns(theme[0][0])
        if theme[0][1] < 0 or theme[0][1] > max_patterns:
            theme[0][1] = np.random.randint(0, max_patterns)

        try:
            for c, color in theme[1:]:
                try: pygame.Color(color)
                except: theme[c + 1] = generate_random_color()
        except: pass

        try:
            colors_length = len(theme[1:])
        except:
            colors_length = 0
        max_shapes = get_max_shapes()
        if colors_length < max_shapes:
            for c in range(max_shapes - colors_length):
                theme.append(generate_random_color())

    return themes

def generate_random_theme():
    pattern_types, max_pattern_types = get_pattern_types()
    pattern_type = pattern_types[np.random.randint(0, max_pattern_types)]
    theme = [[pattern_type, np.random.randint(0, get_max_patterns(pattern_type))]]
    for i in range(get_max_shapes()):
        theme.append(generate_random_color())

    return theme

def create_theme_surf(theme, diameter) -> pygame.surface:
    surf = pygame.Surface((diameter, diameter))

    shapes = get_shape_points(theme[0][0], theme[0][1], (0, 0), diameter)
    surf = draw_theme_shapes(shapes, theme, surf)

    return surf

def draw_theme_shapes(shapes, theme, surf, select_color=pygame.Color('Black'), debug_theme_patterns=False):
    for s, shape in enumerate(shapes):
        color_for_shape = theme[s + 1]
        color_for_shape = add_selection_to_color(color_for_shape, select_color)

        if shape[1] == 'polygon':
            pygame.draw.polygon(surf, color_for_shape, shape[0])

        elif shape[1] == 'ellipse':
            size_of_ellipse_rect = get_size_of_rotated_rectangle(shape[0])
            size_of_ellipse_rect_rounded_down = (math.floor(size_of_ellipse_rect[0]), math.floor(size_of_ellipse_rect[1]))
            temp_surf = pygame.Surface(size_of_ellipse_rect_rounded_down, pygame.SRCALPHA)
            unrotated_ellipse_rect = temp_surf.get_rect()
            pygame.draw.ellipse(temp_surf, color_for_shape, unrotated_ellipse_rect)

            rotation_degrees, r = get_rotation_of_rectangle(shape[0])
            rotated_ellipse_surf = pygame.transform.rotate(temp_surf, rotation_degrees)
            rotated_ellipse_cropped_surf = rotated_ellipse_surf

            rotated_rectangle_dimensions = get_dimensions_of_rotated_rectangle(shape[0])
            scaled_rotated_ellipse_surf = pygame.transform.smoothscale(rotated_ellipse_cropped_surf, rotated_rectangle_dimensions)

            top_left = get_top_left_of_rotated_rectangle(shape[0])
            surf.blit(scaled_rotated_ellipse_surf, top_left)

        elif shape[1] == 'rectangle':
            pygame.draw.rect(surf, color_for_shape, shape[0])


    if debug_theme_patterns > 0:
        for s, shape in enumerate(shapes):
            for p, point in enumerate(shape[0]):
                color_for_shape = theme[s + 1]
                pygame.draw.rect(surf, pygame.Color('orange'), pygame.Rect(point[0] - 8, point[1] - 8, 16, 16))
                pygame.draw.rect(surf, color_for_shape, pygame.Rect(point[0] - 4, point[1] - 4, 8, 8))

                if debug_theme_patterns == 2:
                    pygame.draw.aaline(surf, color_for_shape, shape[0][p - 1], point)

    return surf

def get_dimensions_of_rotated_rectangle(rect_points):
    width = max(rect_points[0][0], rect_points[1][0], rect_points[2][0], rect_points[3][0]) - min(rect_points[0][0], rect_points[1][0], rect_points[2][0], rect_points[3][0])
    height = max(rect_points[0][1], rect_points[1][1], rect_points[2][1], rect_points[3][1]) - min(rect_points[0][1], rect_points[1][1], rect_points[2][1], rect_points[3][1])
    return (width + 1, height + 1)

def get_top_left_of_rotated_rectangle(rect_points):
    return (min(rect_points[0][0], rect_points[1][0]), min(rect_points[0][1], rect_points[3][1]))

def get_size_of_rotated_rectangle(rect_points):
    width = get_distance_between_points(rect_points[1], rect_points[2])
    height = get_distance_between_points(rect_points[0], rect_points[1])

    return (width, height)

def get_rotation_of_rectangle(rect_points):
    rotation_radians = math.atan((rect_points[0][0] - rect_points[1][0]) / (rect_points[0][1] - rect_points[1][1]))
    rotation_degrees = math.degrees(rotation_radians)
    return rotation_degrees, rotation_radians

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


    Scale = math.floor(Scale)

    return Scale, Which

def isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h):
    IsCollidingWithBoardSurf = False
    IsCollidingWithActionWindow = isMouseCollidingWithElement(action_window, mouse_pos)
    rel_mouse_pos = None

    x_start = w / 2 - CurrentBoardSurf.get_width() / 2
    x_stop = w / 2 + CurrentBoardSurf.get_width() / 2
    y_start = h / 2 - CurrentBoardSurf.get_height() / 2
    y_stop = h / 2 + CurrentBoardSurf.get_height() / 2

    if (x_start <= mouse_pos[0] <= x_stop) and (y_start <= mouse_pos[1] <= y_stop):
        rel_mouse_pos = (mouse_pos[0] - x_start, mouse_pos[1] - y_start)
        IsCollidingWithBoardSurf = True

    return IsCollidingWithBoardSurf, IsCollidingWithActionWindow, rel_mouse_pos

def isMouseCollidingWithElement(elements, mouse_pos):
    if not isinstance(elements, list):
        elements = [elements]

    for element in elements:
        try:
            if element is not None and element.alive():
                if element.get_relative_rect().collidepoint(mouse_pos) is True:
                    return True
        except: pass

    return False

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

def autoAdjustBoardDimensions(board, theme_board, w, h, HeldDownCells, EvenOrOdd, AutoAdjustments):
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

    board, theme_board, EvenOrOdd, adjustments_made = adjustBoardDimensions(board, theme_board, (None, False), w, h, HeldDownCells, EvenOrOdd, AutoAdjust)

    return board, theme_board, EvenOrOdd, AutoAdjustments

def blitBoardOnScreenEvenly(surf: pygame.Surface, boardSurf, EditMode):
    if EditMode is False:
        surf.fill((0, 0, 0))
    else:
        surf.fill((30, 30, 30))

    top_left = (surf.get_width() / 2 - boardSurf.get_width() / 2, surf.get_height() / 2 - boardSurf.get_height() / 2)
    surf.blit(boardSurf, top_left)

    return top_left

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

def get_elements_from_set_with_type(set, type_object):
    elements = []
    for element in set:
        try:
            if type(element) == type(type_object):
                elements.append(element)
        except: pass

    return elements

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

def savePNGWithBoardInfo(save_path, CurrentBoardSurf, board, theme_board, themes):
    save_path = str(save_path)
    save_path_dir = Path('/'.join(save_path.split('/')[:-1]))
    if os.path.exists(save_path_dir) is False:
        Path(save_path_dir).mkdir(parents=True, exist_ok=True)

    pygame.image.save(CurrentBoardSurf, save_path)

    targetImage = PngImageFile(save_path)
    metadata = PngInfo()

    board_string = convertArrayToString(board)
    theme_board_string = convertArrayToString(theme_board)
    themes_string = convert_themes_array_to_strings(themes)
    themes_string = str(themes_string)

    metadata.add_text("BoardArray", board_string)
    metadata.add_text("ThemeBoardArray", theme_board_string)
    metadata.add_text("ThemesArray", themes_string)

    targetImage.save(save_path, pnginfo=metadata)

def loadPNGWithBoardInfo(load_path, step_stack, themes, load_themes=True):
    load_path = str(load_path)
    loaded = False
    if load_path.endswith('.png') is False:
        return loaded, load_path + ' is not a .png file', themes, False

    targetImage = PngImageFile(load_path)

    try:
        board_string = targetImage.text["BoardArray"]
        board = convertStringToArray(board_string)
    except:
        return loaded, load_path + ' does not contain a board array', themes, False

    try:
        theme_board_string = targetImage.text["ThemeBoardArray"]
        theme_board = convertStringToArray(theme_board_string)
    except:
        theme_board = np.zeros(board.shape, dtype=int)

    if load_themes is True:
        old_themes = deepcopy(themes)
        try:
            themes_string = targetImage.text["ThemesArray"]
            themes = convert_string_themes_array_to_real_array(themes_string)
            themes = clean_themes(themes)
        except:
            themes = old_themes
            print('No themes found in board metadata.')

    Appended = appendToStepStack(board, theme_board, step_stack)

    loaded = True

    return loaded, 'Board loaded: ' + load_path, themes, Appended

def convertArrayToString(array):
    return '\n'.join('\t'.join('%0.3f' % x for x in y) for y in array)

def convertStringToArray(string):
    return np.array([[int(float(j)) for j in i.split('\t')] for i in string.splitlines()])

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
                    try:
                        config_dict[key][0] = config.get('main', key)
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

def read_themes_file(themes_file_path):
    default_theme = [generate_random_theme()]

    if os.path.isfile(themes_file_path) is not True:
        return default_theme

    try:
        themes_file = ConfigParser()
        themes_file.read(themes_file_path)

        themes = []
        for section in themes_file.sections():
            theme = [[]]

            try:
                theme[0].append(themes_file.get(section, 'patterntype'))
            except:
                pattern_types, max_pattern_types = get_pattern_types()
                pattern_type = pattern_types[np.random.randint(0, max_pattern_types)]
                theme[0].append(pattern_type)

            try:
                theme[0].append(min(abs(themes_file.getint(section, 'pattern')), get_max_patterns(theme[0][0])))
            except:
                theme[0].append(np.random.randint(0, get_max_patterns(theme[0][0])))

            try:
                colors = themes_file.options(section)[2:]
                for color in colors:
                    try:
                        theme.append(pygame.Color(ast.literal_eval(themes_file.get(section, color))))
                    except:
                        theme.append(generate_random_color())

                try:
                    colors_length = len(colors)
                except:
                    colors_length = 0

                if colors_length < get_max_shapes():
                    for c in range(get_max_shapes() - colors_length):
                        theme.append(generate_random_color())

            except:
                for int in range(get_max_shapes()):
                    theme.append(generate_random_color())

            themes.append(theme)
    except:
        return default_theme

    themes = clean_themes(themes)
    return themes

def write_themes_file(config_file_dir, themes_file_path, themes):
    if os.path.exists(config_file_dir) is not True:
        Path(config_file_dir).mkdir(parents=True, exist_ok=True)

    if os.path.isfile(themes_file_path):
        os.remove(themes_file_path)

    themes_file = ConfigParser()
    themes_file.read(themes_file_path)

    for t, theme in enumerate(themes):
        section_name = 'theme ' + str(t + 1)
        themes_file.add_section(section_name)
        themes_file.set(section_name, 'patterntype', str(theme[0][0]))
        themes_file.set(section_name, 'pattern', str(theme[0][1]))
        # try: themes_file.set(section_name, 'pattern', str(theme[0][1]))
        # except: themes_file.set(section_name, 'pattern', str(np.random.randint(0, get_max_patterns(theme[0][0]))))
        for i, color in enumerate(theme[1:]):
            friendly_color = (color.r, color.g, color.b)
            themes_file.set(section_name, 'color ' + str(i + 1), str(friendly_color))

    with open(themes_file_path, 'w') as f:
        themes_file.write(f)

    print('Wrote themes file:', themes_file_path)

def kill_elements(elements):
    if len(elements) > 0:
        for element in elements:
            element.kill()

def build_theme_colors(self, manager):
    try: kill_elements(self.color_surfs)
    except: pass
    try: kill_elements(self.color_previews)
    except: pass
    try: kill_elements(self.pick_color_buttons)
    except: pass

    self.color_surfs = []
    self.color_previews = []
    self.pick_color_buttons = []

    for color in self.themes[self.theme_index][1:]:
        self.color_surfs.append(pygame.Surface((30, 30)))
        self.color_surfs[-1].fill(color)

        if len(self.color_surfs) == 1:
            color_preview_anchors = {'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.change_colors_text}
        else:
            color_preview_anchors = {'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.theme_list, 'top_target': self.color_previews[-1]}

        color_preview = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((10, 5), self.color_surfs[-1].get_size()), image_surface=self.color_surfs[-1], manager=manager, container=self, anchors=color_preview_anchors)
        color_preview.context_menu_buttons = self.color_preview_context_menu_buttons
        color_preview.context_menu_button_types = self.color_preview_context_menu_button_event_types
        self.color_previews.append(color_preview)

        if len(self.color_surfs) == 1:
            pick_color_button_anchors = {'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_previews[-1], 'top_target': self.change_colors_text}
        else:
            pick_color_button_anchors = {'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': self.color_previews[-1], 'top_target': self.color_previews[-2]}

        pick_color_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 5), (-1, 30)), text='...', manager=manager, container=self, anchors=pick_color_button_anchors)
        self.pick_color_buttons.append(pick_color_button)

        for e in self.color_previews: self.right_clickable_elements.append(e)

def quick_post(self, data_name, data, event_id):
    event_data = {data_name: data,
                  'ui_element': self,
                  'ui_object_id': self.most_specific_combined_id}
    pygame.event.post(pygame.event.Event(event_id, event_data))

def set_scroll_container_min_h(self):
    while self.scroll_bar is not None:
        size = self.get_relative_rect().size
        self.set_dimensions((size[0], size[1] + 1))
        self.rebuild()

def kill_right_clickable_element(name, right_clickable_elements):
    for e in right_clickable_elements:
        try:
            if e.name == name:
                right_clickable_elements.remove(e)
        except: pass

def create_right_clickable_element_and_append(name, rect, context_menu_buttons, context_menu_button_types, right_clickable_elements):
    kill_right_clickable_element(name, right_clickable_elements)
    element = RightClickableElement(name, rect, context_menu_buttons, context_menu_button_types)
    right_clickable_elements.append(element)

def get_right_clicked_element(mouse_pos, right_clickable_elements):
    if len(right_clickable_elements) == 0:
        return None

    for element in right_clickable_elements:
        try:
            if element.alive() and element.get_abs_rect().collidepoint(mouse_pos):
                return element
        except: pass

    return None

def create_context_menu_button_event_types(buttons):
    button_event_types = []
    for button in buttons:
        button_event_types.append(pygame.event.custom_type())

    return button_event_types

def create_context_menu(context_menu, right_clicked_element, manager, mouse_pos):
    try: context_menu.kill()
    except: pass

    max_chars = 0
    for button in right_clicked_element.context_menu_buttons:
        max_chars = max(max_chars, len(button))
    width = max(max_chars * 9, 150)
    height = min(len(right_clicked_element.context_menu_buttons) * 20, 600)
    rect = pygame.Rect(mouse_pos, (width, height))

    context_menu = ContextMenu(relative_rect=rect, manager=manager, object_id=pygame_gui.core.ObjectID(object_id='#context_menu'), item_list=right_clicked_element.context_menu_buttons)
    context_menu.right_clicked_element = right_clicked_element

    return context_menu
