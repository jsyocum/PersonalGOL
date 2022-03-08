import helpers
from classes import SettingsWindow, OldSettingsWindow, WrappedScrollContainer, PNGFilePicker, ChooseFileNameWindow, ActionWindow
import pygame
import pygame_gui
import numpy as np
import os
import math
import appdirs
from pathlib import Path
from collections import deque

BOARDADJUSTBUTTON = pygame.event.custom_type()

def get_version_number():
    # major.minor.patch
    # major: major changes, like a rewrite of the project
    # minor: new functionality
    # patch: minor changes or bug fixes
    version = '1.0.1'

    return version

def main():
    # Set up pygame
    pygame.init()
    logo = pygame.image.load(helpers.resource_path('logo.png'))
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Personal Game Of Life - " + get_version_number())
    surf = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    w = surf.get_width()
    h = surf.get_height()
    manager = pygame_gui.UIManager((w, h), helpers.resource_path('LessDeadZoneButton.json'))

    clock = pygame.time.Clock()
    time_delta_stack = deque([])
    step_stack = deque([])
    running = True

    Continuous = True
    WasContinuous = True
    Update = True
    Step = False
    StepBack = False
    NewBoard = False
    EditMode = False
    MenuOpen = False
    ClearHistory = False
    QuickSave = False
    QuickLoad = False
    Load = False
    CurrentBoardSurf = None
    LeftClickHeldDown = [False, 0]
    SelectionBoxPresent = False
    SelMode = True
    EraseMode = False
    AutoAdjust = False
    AdjustBoard = False
    AdjustBoardTuple = None
    ApplyAdjustments = False
    AutoAdjustments = {
        "Top": 0,
        "Bottom": 0,
        "Left": 0,
        "Right": 0
    }
    Zoom = False
    Cut = False
    Copy = False
    Paste = False
    Fill = False
    Clear = False
    Rotate = False
    Flip = False
    EvenOrOdd = 0
    time_delta_added = 0

    save_location = None
    file_name_window = None

    config_file_dir = appdirs.user_data_dir("PersonalGOL", "jsyocum")
    config_file_path = Path(config_file_dir + '/config.ini')
    print('Config file path:', config_file_path)

    SavePath = ''
    quick_save_path = Path(config_file_dir + '/Patterns/quick_save.png')
    DefaultSavePath = Path(config_file_dir + '/Patterns')
    BackupSavePath = os.path.expanduser("~/Desktop")
    if os.path.exists(BackupSavePath) is not True:
        BackupSavePath = Path(BackupSavePath.removesuffix("/Desktop") + "/OneDrive/Desktop")

    if os.path.exists(DefaultSavePath) is not True:
        Path(DefaultSavePath).mkdir(parents=True, exist_ok=True)

    if os.path.exists(DefaultSavePath) is True:
        SavePath = DefaultSavePath
    else:
        SavePath = BackupSavePath

    DefaultScale = 20
    DefaultMaxFps = 18
    DefaultLikelihood = 5

    DefaultColorR = 255
    DefaultColorG = 255
    DefaultColorB = 255
    DefaultRandomColorByPixel = False

    DefaultCustomBoardSizeWidth = int(w / DefaultScale)
    DefaultCustomBoardSizeHeight = int(h / DefaultScale)

    DefaultEditCheckerboardBrightness = 15
    MaxEditCheckerboardBrightness = 200

    config_dict = {
        "Scale": [DefaultScale, 80],
        "MaxFps": [DefaultMaxFps, 50],
        "Likelihood": [DefaultLikelihood, 30],
        "R": [DefaultColorR, 255],
        "G": [DefaultColorG, 255],
        "B": [DefaultColorB, 255],
        "RandomColorByPixel": [DefaultRandomColorByPixel, False],
        "CustomBoardSizeWidth": [DefaultCustomBoardSizeWidth, w],
        "CustomBoardSizeHeight": [DefaultCustomBoardSizeHeight, h],
        "CustomBoardSizeEnabled": [False, False],
        "EditCheckerboardBrightness": [DefaultEditCheckerboardBrightness, 200],
        "SelectionMode": [SelMode, True],
        "Eraser": [EraseMode, False],
        "AutoAdjust": [AutoAdjust, False]
    }

    helpers.initialConfigCheck(config_file_dir, config_file_path, config_dict)


    action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], AutoAdjust=config_dict["AutoAdjust"][0])
    action_window.kill()


    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show settings', manager=manager, visible=0)
    edit_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Enable edit mode (E)', manager=manager, visible=0)
    save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 200), (400, 50)), text='Save board', manager=manager, visible=0)
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 250), (400, 50)), text='Load board', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 300), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, edit_mode_button, save_button, load_button, quit_game_button]

    settings_window_new = SettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, w=w, h=h, config_dict=config_dict)
    settings_window_actual = OldSettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, resizable=True, window_display_title='Settings', visible=0)
    settings_window_actual.set_minimum_dimensions((330, 200))
    settings_window_actual.set_dimensions((w, h))
    settings_window = WrappedScrollContainer(relative_rect=pygame.Rect((0, 0), (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())), manager=manager, container=settings_window_actual, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

    parameters_warning_text = pygame_gui.elements.ui_text_box.UITextBox('<font face=arial color=regular_text><font color=#989898 size=2>'
                                                                        '<b>Changing scale, likelihood, or board size will reset the board</b></font></font>',
                                                                        pygame.Rect((10, 10), (settings_window.get_real_width() - 10, -1)), manager=manager, container=settings_window)

    parameters_scale_text = pygame_gui.elements.ui_label.UILabel(text='Scale:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_warning_text})
    parameters_scale_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["Scale"][0], value_range=(1, 80), manager=manager, container=settings_window, click_increment=5, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_text})
    parameters_scale_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 200', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultScale), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_warning_text})
    parameters_scale_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_scale_slider, 'top_target': parameters_scale_text})

    parameters_max_fps_text = pygame_gui.elements.ui_label.UILabel(text='Max fps:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_scale_slider})
    parameters_max_fps_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["MaxFps"][0], value_range=(1, 50), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_text})
    parameters_max_fps_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 1000', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultMaxFps), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_scale_slider})
    parameters_max_fps_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_max_fps_slider, 'top_target': parameters_max_fps_text})

    parameters_likelihood_text = pygame_gui.elements.ui_label.UILabel(text='Likelihood:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_max_fps_slider})
    parameters_likelihood_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 40, 25)), start_value=config_dict["Likelihood"][0], value_range=(1, 30), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_text})
    parameters_likelihood_slider_size_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Change slider maximum to 100', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default value: ' + str(DefaultLikelihood), anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_max_fps_slider})
    parameters_likelihood_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_text})

    parameters_color_text = pygame_gui.elements.ui_label.UILabel(text='Color:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_likelihood_slider})
    parameters_color_picker_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-110, 10), (50, 25)), text='...', manager=manager, container=settings_window, tool_tip_text='Use a color picker to choose a color.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_random_cell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-50, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to randomize the color of each cell.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_default_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='*', manager=manager, container=settings_window, tool_tip_text='Reset to default: White', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_likelihood_slider})
    parameters_color_picker_dialog = None
    color = pygame.Color(config_dict["R"][0], config_dict["G"][0], config_dict["B"][0])

    parameters_custom_board_size_text = pygame_gui.elements.ui_label.UILabel(text='Set custom board size:', relative_rect=pygame.Rect((10, 10), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_color_text})
    parameters_custom_board_size_enable_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (50, 25)), text='[ ]', manager=manager, container=settings_window, tool_tip_text='Enable to enter a custom board size. Disables scale option.', anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'left_target': parameters_likelihood_slider, 'top_target': parameters_color_text})
    parameters_custom_board_size_width_text = pygame_gui.elements.ui_label.UILabel(text='Width:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_height_text = pygame_gui.elements.ui_label.UILabel(text='Height:', relative_rect=pygame.Rect((10, 5), (-1, -1)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top', 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeHeight"][0], value_range=(1, h), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                                               'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                                               'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_height_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_height_slider, 'top_target': parameters_custom_board_size_width_text})
    parameters_custom_board_size_width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 5), (settings_window.get_real_width() - 50 - parameters_custom_board_size_height_text.get_relative_rect().width, 25)), start_value=config_dict["CustomBoardSizeWidth"][0], value_range=(1, w), manager=manager, container=settings_window, click_increment=1, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top',
                                                                                                                                                                                                                                                                                                                                                                                             'left_target': parameters_custom_board_size_height_text,
                                                                                                                                                                                                                                                                                                                                                                                             'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 5), (50, 25)), manager=manager, container=settings_window, anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top', 'left_target': parameters_custom_board_size_width_slider, 'top_target': parameters_custom_board_size_text})
    parameters_custom_board_size_width_entry.set_text(str(config_dict["CustomBoardSizeWidth"][0]))
    parameters_custom_board_size_height_entry.set_text(str(config_dict["CustomBoardSizeHeight"][0]))
    for element in [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry]: element.disable()

    settings_window_actual.set_dimensions(settings_window_actual.minimum_dimensions)
    parameters_warning_text.set_dimensions((settings_window.get_real_width() - 10, -1))
    parameters_warning_text.rebuild()

    all_parameters_height_references = [parameters_warning_text, parameters_scale_text, parameters_scale_slider, parameters_max_fps_text, parameters_max_fps_slider,
                                        parameters_likelihood_text, parameters_likelihood_slider, parameters_color_text,
                                        parameters_custom_board_size_text, parameters_custom_board_size_width_text, parameters_custom_board_size_height_text]
    parameters_height_total = helpers.getHeightOfElements(all_parameters_height_references) + 10
    settings_window_actual.set_dimensions((settings_window_actual.minimum_dimensions[0], parameters_height_total))
    settings_window.set_scrollable_area_dimensions((settings_window_actual.minimum_dimensions[0], parameters_height_total))

    previousSettingsWindowDimensions = None
    previousScaleSliderValue = None
    previousScaleEntryValue = None
    previousMaxFpsSliderValue = None
    previousMaxFpsEntryValue = None
    previousLikelihoodSliderValue = None
    previousLikelihoodEntryValue = None
    previousCustomBoardSizeWidthSliderValue = None
    previousCustomBoardSizeWidthEntryValue = None
    previousCustomBoardSizeHeightSliderValue = None
    previousCustomBoardSizeHeightEntryValue = None

    HeldDownCells = []
    CopiedBoard = None

    previousWidth = int(w / config_dict["Scale"][0])
    previousHeight = int(h / config_dict["Scale"][0])

    pausedLikelihoodSliderValue = DefaultLikelihood

    all_parameters_color_elements = [parameters_color_random_cell_button, parameters_color_default_button, parameters_color_picker_button]

    all_parameters_entries = [[parameters_scale_entry, 1, 80], [parameters_max_fps_entry, 1, 50], [parameters_likelihood_entry, 1, 30],
                              [parameters_custom_board_size_width_entry, 1, w], [parameters_custom_board_size_height_entry, 1, h]]

    all_parameters_elements_matched = [[parameters_scale_slider, parameters_scale_entry, previousScaleSliderValue, previousScaleEntryValue],
                                       [parameters_max_fps_slider, parameters_max_fps_entry, previousMaxFpsSliderValue, previousMaxFpsEntryValue],
                                       [parameters_likelihood_slider, parameters_likelihood_entry, previousLikelihoodSliderValue, previousLikelihoodEntryValue],
                                       [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, previousCustomBoardSizeWidthSliderValue, previousCustomBoardSizeWidthEntryValue],
                                       [parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry, previousCustomBoardSizeHeightSliderValue, previousCustomBoardSizeHeightEntryValue]]

    for entry in all_parameters_entries: entry[0].set_allowed_characters('numbers')


    sidebar_header_font = pygame.font.SysFont('arial', size=30, bold=True)
    sidebar_font = pygame.font.SysFont('arial', size=18)

    controls_header_text = sidebar_header_font.render("Controls", True, (190, 190, 190))
    controls_pause_text = sidebar_font.render("Pause: SPACEBAR", True, (152, 152, 152))
    controls_step_forward_text = sidebar_font.render("Step forward: W", True, (152, 152, 152))
    controls_step_backward_text = sidebar_font.render("Step backwards: S", True, (152, 152, 152))
    controls_reset_text = sidebar_font.render("Reset: R", True, (152, 152, 152))
    controls_increase_max_fps_text = sidebar_font.render("+ max fps: MWHEELUP", True, (152, 152, 152))
    controls_decrease_max_fps_text = sidebar_font.render("-  max fps: MWHEELDOWN", True, (152, 152, 152))
    controls_edit_mode_text = sidebar_font.render("Toggle edit mode: E", True, (152, 152, 152))
    controls_action_menu_text = sidebar_font.render("Open action menu: Tab", True, (152, 152, 152))
    controls_clear_history_text = sidebar_font.render("Clear history: H", True, (152, 152, 152))
    controls_quick_save_text = sidebar_font.render("Quick save: F5", True, (152, 152, 152))
    controls_quick_load_text = sidebar_font.render("Quick load: F6", True, (152, 152, 152))
    controls_rect = pygame.Rect((w / 2 - 510, h / 4 + 2), (300, 400))

    controls_text_array = [controls_pause_text, controls_step_forward_text, controls_step_backward_text, controls_reset_text, controls_increase_max_fps_text,
                           controls_decrease_max_fps_text, controls_edit_mode_text, controls_action_menu_text, controls_clear_history_text,
                           controls_quick_save_text, controls_quick_load_text]

    CustomBoardSizeEnabledDict = False
    RandomColorByPixelDict = False

    if config_dict["CustomBoardSizeEnabled"][0] is True:
        CustomBoardSizeEnabledDict = True
        parameters_scale_entry.set_text(str(config_dict["Scale"][0]))
        previousWidth = config_dict["CustomBoardSizeWidth"][0]
        previousHeight = config_dict["CustomBoardSizeHeight"][0]

    if config_dict["RandomColorByPixel"][0] is True:
        RandomColorByPixelDict = True

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    if config_dict["CustomBoardSizeEnabled"][0] is False:
        Board = helpers.generateArray(int(h / config_dict["Scale"][0]), int(w / config_dict["Scale"][0]), config_dict["Likelihood"][0])
    else:
        Board = helpers.generateArray(config_dict["CustomBoardSizeHeight"][0], config_dict["CustomBoardSizeWidth"][0], config_dict["Likelihood"][0])

    # Rotate the array. For some reason pygame.surfarray.make_surface flips it 90 degrees
    Board = np.rot90(Board)
    step_stack.append(Board.copy())

    while running:
        time_delta = clock.tick(120) / 1000.0
        time_delta_stack.append(time_delta)
        if len(time_delta_stack) > 2000:
            time_delta_stack.popleft()

        if len(HeldDownCells) < 2:
            SelectionBoxPresent = False

        keys = pygame.key.get_pressed()

        time_delta_added = time_delta_added + time_delta
        if time_delta_added >= (1 / parameters_max_fps_slider.get_current_value()):
            Update = True
            time_delta_added = 0

        save_load_windows = [save_location, file_name_window]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)
                running = False

            if MenuOpen is False:
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    Continuous = not Continuous
                elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                    Step = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_s:
                    StepBack = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_r:
                    NewBoard = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_h:
                    ClearHistory = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_F5:
                    QuickSave = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_F6:
                    QuickLoad = True
                elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                    if Continuous is True and EditMode is False:
                        WasContinuous = True
                        Continuous = False
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                    elif Continuous is False and EditMode is False:
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                    elif EditMode is True:
                        Continuous = WasContinuous
                        WasContinuous = False
                        EditMode = False
                        HeldDownCells = []
                        action_window.kill()
                        edit_mode_button.set_text('Enable edit mode (E)')
                elif event.type == pygame.KEYUP and event.key == pygame.K_TAB:
                    if Continuous is True and EditMode is False:
                        WasContinuous = True
                        Continuous = False
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], AutoAdjust=config_dict["AutoAdjust"][0])
                    elif Continuous is False and EditMode is False:
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], AutoAdjust=config_dict["AutoAdjust"][0])
                    elif EditMode is True and not action_window.alive():
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], AutoAdjust=config_dict["AutoAdjust"][0])
                    elif EditMode is True and action_window.alive():
                        action_window.kill()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not helpers.isMouseCollidingWithActionWindow(action_window, pygame.mouse.get_pos()):
                    LeftClickHeldDown = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    LeftClickHeldDown = False


            if (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == back_to_game_button):
                if MenuOpen is False:
                    WasContinuous = Continuous
                    Continuous = False

                    LeftClickHeldDown = False
                    if len(HeldDownCells) == 2:
                        SelectionBoxPresent = True

                    action_window.hide()

                    pausedLikelihoodSliderValue = parameters_likelihood_slider.get_current_value()

                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show settings')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    Continuous = WasContinuous

                    if SelectionBoxPresent is True:
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], AutoAdjust=config_dict["AutoAdjust"][0])

                    action_window.show()
                    MenuOpen = CloseUIElements(all_menu_buttons)
                    settings_window_actual.hide()
                    if parameters_color_picker_dialog is not None: parameters_color_picker_dialog.kill()
                    if save_location is not None: save_location.kill()
                    if file_name_window is not None: file_name_window.kill()

                    for entryArray in all_parameters_entries[3:]:
                        helpers.manageNumberEntry(entryArray)

                    if parameters_custom_board_size_enable_button.text == '[ ]':
                        if ((int(w / previousWidth) != parameters_scale_slider.get_current_value()) and (int(h / previousHeight) != parameters_scale_slider.get_current_value())) or (pausedLikelihoodSliderValue != parameters_likelihood_slider.get_current_value()):
                            previousWidth = math.floor(w / parameters_scale_slider.get_current_value())
                            previousHeight = math.floor(h / parameters_scale_slider.get_current_value())
                            NewBoard = True
                    elif (previousWidth != int(parameters_custom_board_size_width_entry.get_text())) or (previousHeight != int(parameters_custom_board_size_height_entry.get_text())):
                        previousWidth = math.floor(int(parameters_custom_board_size_width_entry.get_text()))
                        previousHeight = math.floor(int(parameters_custom_board_size_height_entry.get_text()))
                        NewBoard = True

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

                if show_parameters_button.text == 'Hide settings':
                    show_parameters_button.set_text('Show settings')
                    settings_window_actual.hide()

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, EditMode)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show settings':
                show_parameters_button.set_text('Hide settings')
                settings_window_actual.show()

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                show_parameters_button.set_text('Show settings')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, EditMode)
                settings_window_actual.hide()

            if ((event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == edit_mode_button) or (MenuOpen is True and event.type == pygame.KEYUP and event.key == pygame.K_e and helpers.anyAliveElements(save_load_windows) is False)) and edit_mode_button.text == 'Enable edit mode (E)':
                edit_mode_button.set_text('Disable edit mode (E)')
                EditMode = True

            elif (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == edit_mode_button) or (MenuOpen is True and event.type == pygame.KEYUP and event.key == pygame.K_e and helpers.anyAliveElements(save_load_windows) is False):
                edit_mode_button.set_text('Enable edit mode (E)')
                EditMode = False
                HeldDownCells = []

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == save_button and helpers.anyAliveElements(save_load_windows) is False:
                save_location = PNGFilePicker(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, window_title='Pick save location', initial_file_path=SavePath, allow_picking_directories=True)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == save_location and save_location.window_display_title == 'Pick save location':
                save_path = event.text
                file_name_window = ChooseFileNameWindow(pygame.Rect((w / 2 - 80, h / 2 + 25), (600, 50)), manager=manager, window_title='Choose a filename to put in ' + save_path, width=w, height=h, save_path=save_path)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == file_name_window:
                save_path = event.text
                boardsurf_to_save = helpers.updateScreenWithBoard(Board, surf, EditMode=True, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], Saving=True)
                helpers.savePNGWithBoardInfo(save_path, boardsurf_to_save, step_stack[-1])

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == load_button and helpers.anyAliveElements(save_load_windows) is False:
                save_location = PNGFilePicker(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, window_title='Pick .PNG board file', initial_file_path=SavePath, allow_picking_directories=False)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == save_location and save_location.window_display_title == 'Pick .PNG board file':
                load_path = event.text
                Load = True

            if event.type == pygame.DROPFILE:
                load_path = event.file
                Load = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_slider_size_button:
                if parameters_scale_slider_size_button.text == '[ ]':
                    parameters_scale_slider_size_button.text = '[X]'
                    parameters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 80'
                    parameters_scale_slider.value_range = (1, 200)
                else:
                    parameters_scale_slider_size_button.text = '[ ]'
                    parameters_scale_slider_size_button.tool_tip_text = 'Change slider maximum to 200'
                    parameters_scale_slider_size_button.rebuild()
                    parameters_scale_slider.value_range = (1, 80)

                parameters_scale_slider_size_button.rebuild()
                parameters_scale_slider.rebuild()

            if event.type == pygame.MOUSEBUTTONUP and MenuOpen is False:
                current_max_fps = parameters_max_fps_slider.get_current_value()
                max_fps_slider_range = parameters_max_fps_slider.value_range
                if Continuous is True:
                    if event.button == 4:
                        parameters_max_fps_slider.set_current_value(min(current_max_fps + 1, max_fps_slider_range[1]))
                    elif event.button == 5:
                        parameters_max_fps_slider.set_current_value(max(current_max_fps - 1, max_fps_slider_range[0]))

                elif event.button == 1 and len(HeldDownCells) < 2 and EditMode is True and SelectionBoxPresent is False and config_dict["SelectionMode"][0] is True:
                    mouse_pos = pygame.mouse.get_pos()
                    IsColliding, IsCollidingWithActionWindow, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h)
                    if IsColliding and not IsCollidingWithActionWindow:
                        board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)
                        Board = step_stack[-1].copy()
                        if Board[board_pos] == 0:
                            Board[board_pos] = 1
                        else:
                            Board[board_pos] = 0

                        helpers.appendToStepStack(Board, step_stack)

                    HeldDownCells = []

                elif event.button == 1 and len(HeldDownCells) == 2 and SelectionBoxPresent is False:
                    SelectionBoxPresent = True
                elif event.button == 1 and len(HeldDownCells) == 2 and SelectionBoxPresent is True and not helpers.isMouseCollidingWithActionWindow(action_window, pygame.mouse.get_pos()):
                    HeldDownCells = []
                    SelectionBoxPresent = False

            if LeftClickHeldDown is True and EditMode is True and MenuOpen is False and SelectionBoxPresent is False:
                mouse_pos = pygame.mouse.get_pos()
                IsColliding, IsCollidingWithActionWindow, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h)
                if IsColliding and not IsCollidingWithActionWindow:
                    board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)

                    if config_dict["SelectionMode"][0] is True:
                        if len(HeldDownCells) < 2 and board_pos not in HeldDownCells:
                            HeldDownCells.append(board_pos)
                        elif len(HeldDownCells) == 2 and board_pos == HeldDownCells[0]:
                            HeldDownCells.pop(1)
                        elif len(HeldDownCells) == 2:
                            HeldDownCells[1] = board_pos

                    else:
                        Board = step_stack[-1].copy()
                        if config_dict["Eraser"][0] is False:
                            Board[board_pos] = 1
                        else:
                            Board[board_pos] = 0

                        helpers.appendToStepStack(Board, step_stack)

            if event.type == pygame.MOUSEBUTTONUP and settings_window.vert_scroll_bar is not None:
                mouse_pos = pygame.mouse.get_pos()
                if settings_window.rect.collidepoint(mouse_pos):
                    scroll_amount = settings_window.vert_scroll_bar.bottom_limit / 30
                    if event.button == 4:
                        settings_window.vert_scroll_bar.scroll_position = max(settings_window.vert_scroll_bar.scroll_position - scroll_amount, 0)

                    elif event.button == 5:
                        settings_window.vert_scroll_bar.scroll_position = min(settings_window.vert_scroll_bar.scroll_position + scroll_amount, settings_window.vert_scroll_bar.bottom_limit - settings_window.vert_scroll_bar.sliding_button.rect.height)

                    settings_window.vert_scroll_bar.start_percentage = settings_window.vert_scroll_bar.scroll_position / settings_window.vert_scroll_bar.scrollable_height
                    settings_window.vert_scroll_bar.has_moved_recently = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_slider_size_button:
                if parameters_max_fps_slider_size_button.text == '[ ]':
                    parameters_max_fps_slider_size_button.text = '[X]'
                    parameters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 50'
                    parameters_max_fps_slider.value_range = (1, 1000)
                else:
                    parameters_max_fps_slider_size_button.text = '[ ]'
                    parameters_max_fps_slider_size_button.tool_tip_text = 'Change slider maximum to 1000'
                    parameters_max_fps_slider.value_range = (1, 50)

                parameters_max_fps_slider_size_button.rebuild()
                parameters_max_fps_slider.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_slider_size_button:
                if parameters_likelihood_slider_size_button.text == '[ ]':
                    parameters_likelihood_slider_size_button.text = '[X]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 30'
                    parameters_likelihood_slider.value_range = (1, 100)
                else:
                    parameters_likelihood_slider_size_button.text = '[ ]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Change slider maximum to 100'
                    parameters_likelihood_slider.value_range = (1, 30)

                parameters_likelihood_slider_size_button.rebuild()
                parameters_likelihood_slider.rebuild()

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_custom_board_size_enable_button) or CustomBoardSizeEnabledDict is True:
                CustomBoardSizeEnabledDict = False
                scale_elements = [parameters_scale_slider, parameters_scale_entry, parameters_scale_slider_size_button, parameters_scale_default_button]
                custom_board_size_elements = [parameters_custom_board_size_width_slider, parameters_custom_board_size_width_entry, parameters_custom_board_size_height_slider, parameters_custom_board_size_height_entry]

                if parameters_custom_board_size_enable_button.text == '[ ]':
                    parameters_custom_board_size_enable_button.text = '[X]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Disable to use the scale option instead.'
                    for element in scale_elements:
                        element.disable()
                        element.rebuild()
                        element.enable()
                        element.disable()
                    for element in custom_board_size_elements: element.enable()
                    config_dict["CustomBoardSizeEnabled"][0] = True
                else:
                    parameters_custom_board_size_enable_button.text = '[ ]'
                    parameters_likelihood_slider_size_button.tool_tip_text = 'Enable to enter a custom board size. Disables scale option.'
                    for element in scale_elements: element.enable()
                    for element in custom_board_size_elements:
                        element.disable()
                        element.rebuild()
                        element.enable()
                        element.disable()
                    config_dict["CustomBoardSizeEnabled"][0] = False

                parameters_custom_board_size_enable_button.rebuild()

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_random_cell_button) or RandomColorByPixelDict is True:
                RandomColorByPixelDict = False
                if parameters_color_random_cell_button.text == '[ ]':
                    parameters_color_random_cell_button.text = '[X]'
                    parameters_color_random_cell_button.tool_tip_text = 'Disable to go back to using normal colors.'
                    for element in all_parameters_color_elements[1:]: element.disable()
                    config_dict["RandomColorByPixel"][0] = True
                else:
                    parameters_color_random_cell_button.text = '[ ]'
                    parameters_color_random_cell_button.tool_tip_text = 'Enable to randomize the color of each cell.'
                    for element in all_parameters_color_elements[1:]: element.enable()
                    config_dict["RandomColorByPixel"][0] = False

                parameters_color_random_cell_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_picker_button:
                parameters_color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, initial_colour=color, window_title='Pick a color...')
                for element in all_parameters_color_elements: element.disable()

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == parameters_color_picker_dialog and config_dict["RandomColorByPixel"][0] is False:
                for element in all_parameters_color_elements: element.enable()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.selection_mode_button:
                if action_window.selection_mode_button.text == 'Sel. mode: [X]':
                    action_window.selection_mode_button.text = 'Sel. mode: [ ]'
                    action_window.tool_tip_text = 'Turn on to select things and use the other actions.'
                    config_dict["SelectionMode"][0] = False
                    HeldDownCells = []
                    action_window.eraser_mode_button.enable()

                else:
                    action_window.selection_mode_button.text = 'Sel. mode: [X]'
                    action_window.tool_tip_text = 'Turn off to paint with the mouse.'
                    config_dict["SelectionMode"][0] = True
                    action_window.eraser_mode_button.disable()

                action_window.selection_mode_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.eraser_mode_button:
                if action_window.eraser_mode_button.text == 'Eraser: [ ]':
                    action_window.eraser_mode_button.text = 'Eraser: [X]'
                    action_window.tool_tip_text = 'Disable the eraser to create cells with the mouse.'
                    config_dict["Eraser"][0] = True

                else:
                    action_window.eraser_mode_button.text = 'Eraser: [ ]'
                    action_window.tool_tip_text = 'Enable the eraser to only delete cells with the mouse.'
                    config_dict["Eraser"][0] = False

                action_window.eraser_mode_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.set_custom_board_size_entries_button:
                current_width = step_stack[-1].shape[0]
                current_height = step_stack[-1].shape[1]

                parameters_custom_board_size_width_entry.set_text(str(current_width))
                parameters_custom_board_size_height_entry.set_text(str(current_height))

                config_dict["CustomBoardSizeWidth"][0] = current_width
                config_dict["CustomBoardSizeHeight"][0] = current_height

                helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.zoom_button:
                Zoom = True

            if keys[pygame.K_LCTRL] and event.type == pygame.KEYUP and event.key == pygame.K_a and MenuOpen is False and EditMode is True and config_dict["SelectionMode"][0] is True:
                if SelectionBoxPresent is False:
                    HeldDownCells = [(0, 0), (step_stack[-1].shape[0] - 1, step_stack[-1].shape[1] - 1)]
                    SelectionBoxPresent = True

                else:
                    if HeldDownCells != [(0, 0), (step_stack[-1].shape[0] - 1, step_stack[-1].shape[1] - 1)]:
                        HeldDownCells = [(0, 0), (step_stack[-1].shape[0] - 1, step_stack[-1].shape[1] - 1)]

                    else:
                        HeldDownCells = []
                        SelectionBoxPresent = False

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.cut_button) or (keys[pygame.K_LCTRL] and event.type == pygame.KEYUP and event.key == pygame.K_x and SelectionBoxPresent is True):
                Cut = True

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.copy_button) or (keys[pygame.K_LCTRL] and event.type == pygame.KEYUP and event.key == pygame.K_c and SelectionBoxPresent is True):
                Copy = True

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.paste_button) or (keys[pygame.K_LCTRL] and event.type == pygame.KEYUP and event.key == pygame.K_v and SelectionBoxPresent is True):
                Paste = True

            if keys[pygame.K_LCTRL] and keys[pygame.K_v] and MenuOpen is False and EditMode is True and SelectionBoxPresent is False and CopiedBoard is not None:
                mouse_pos = pygame.mouse.get_pos()
                IsColliding, IsCollidingWithActionWindow, rel_mouse_pos = helpers.isMouseCollidingWithBoardSurfOrActionWindow(CurrentBoardSurf, action_window, mouse_pos, w, h)
                if IsColliding and not IsCollidingWithActionWindow:
                    board_pos = helpers.getBoardPosition(step_stack[-1], rel_mouse_pos, w, h)
                    Board = helpers.paste(step_stack[-1].copy(), [board_pos, [board_pos[0] + 1, board_pos[1] + 1]], CopiedBoard)
                    helpers.appendToStepStack(Board, step_stack)

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.fill_button) or (event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE and SelectionBoxPresent is True):
                Fill = True

            if (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.clear_button) or (event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE and SelectionBoxPresent is True):
                Clear = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.rotate_button:
                Rotate = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.flip_button:
                Flip = True

            if event.type == BOARDADJUSTBUTTON and event.ui_element == action_window:
                AdjustBoard = True
                AdjustBoardTuple = (event.side, event.plus)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.auto_adjust_mode_button:
                if action_window.auto_adjust_mode_button.text == 'Auto-adjust: [ ]':
                    action_window.auto_adjust_mode_button.text = 'Auto-adjust: [X]'
                    action_window.tool_tip_text = 'Disable auto-adjust mode to keep the board from automatically resizing to fit the cells.'
                    config_dict["AutoAdjust"][0] = True

                else:
                    action_window.auto_adjust_mode_button.text = 'Auto-adjust: [ ]'
                    action_window.tool_tip_text = 'Enable auto-adjust mode to allow the board to automatically resize to fit the cells.'
                    config_dict["AutoAdjust"][0] = False

                action_window.auto_adjust_mode_button.rebuild()

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.apply_adjustments_button:
                ApplyAdjustments = True

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == action_window.clear_adjustments_button:
                AutoAdjustments = dict.fromkeys(AutoAdjustments, 0)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_scale_default_button: parameters_scale_slider.set_current_value(DefaultScale)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_max_fps_default_button: parameters_max_fps_slider.set_current_value(DefaultMaxFps)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_likelihood_default_button: parameters_likelihood_slider.set_current_value(DefaultLikelihood)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == parameters_color_default_button: color = pygame.Color(DefaultColorR, DefaultColorG, DefaultColorB)

            manager.process_events(event)

        manager.update(time_delta)

        for element in action_window.buttons_require_sel_box:
            if SelectionBoxPresent is True and element.is_enabled is False:
                element.enable()
            elif SelectionBoxPresent is False and element.is_enabled is True:
                element.disable()

        if (CopiedBoard is None or SelectionBoxPresent is False) and action_window.paste_button.is_enabled is True:
            action_window.paste_button.disable()
        elif CopiedBoard is not None and SelectionBoxPresent is True and action_window.paste_button.is_enabled is False:
            action_window.paste_button.enable()

        if EditMode is True:
            if keys[pygame.K_UP]:
                config_dict["EditCheckerboardBrightness"][0] = min(config_dict["EditCheckerboardBrightness"][0] + 1, MaxEditCheckerboardBrightness)
            elif keys[pygame.K_DOWN]:
                config_dict["EditCheckerboardBrightness"][0] = max(config_dict["EditCheckerboardBrightness"][0] - 1, 0)

        if config_dict["AutoAdjust"][0] is True:
            if Continuous is True or (Continuous is False and Step is True):
                Board, EvenOrOdd, AutoAdjustments = helpers.autoAdjustBoardDimensions(step_stack[-1].copy(), w, h, HeldDownCells, EvenOrOdd, AutoAdjustments)
                helpers.appendToStepStack(Board, step_stack)

        if Continuous is False and Step is True:
            helpers.applyRules(step_stack[-1], step_stack)
            Step = False
        elif Continuous is False and StepBack is True:
            helpers.stepBack(step_stack)
            StepBack = False
        elif Continuous is True and Update is True:
            helpers.applyRules(step_stack[-1], step_stack)
            Step = False
            StepBack = False
            Update = False

        if NewBoard is True:
            Board = helpers.generateArray(previousHeight, previousWidth, parameters_likelihood_slider.get_current_value())
            Board = np.rot90(Board)
            step_stack.append(Board)

            NewBoard = False

        if Zoom is True:
            Board = helpers.zoom(step_stack[-1], HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)
            HeldDownCells = []

            Zoom = False

        if Cut is True:
            CopiedBoard = helpers.zoom(step_stack[-1], HeldDownCells)
            Board = helpers.cut(step_stack[-1].copy(), HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)

            Cut = False

        if Copy is True:
            CopiedBoard = helpers.zoom(step_stack[-1], HeldDownCells)

            Copy = False

        if Paste is True:
            Board = helpers.paste(step_stack[-1].copy(), HeldDownCells, CopiedBoard)
            helpers.appendToStepStack(Board, step_stack)

            Paste = False

        if Fill is True:
            Board = helpers.cut(step_stack[-1].copy(), HeldDownCells, Fill=Fill)
            helpers.appendToStepStack(Board, step_stack)

            Fill = False

        if Clear is True:
            Board = helpers.cut(step_stack[-1].copy(), HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)

            Clear = False

        if Rotate is True:
            Board = helpers.rotate(step_stack[-1].copy(), HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)

            Rotate = False

        if Flip is True:
            Board = helpers.flip(step_stack[-1].copy(), HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)

            Flip = False

        if AdjustBoard is True:
            Board, EvenOrOdd, adjustments_made = helpers.adjustBoardDimensions(step_stack[-1].copy(), AdjustBoardTuple, w, h, HeldDownCells, EvenOrOdd)
            helpers.appendToStepStack(Board, step_stack)

            AdjustBoard = False

        if sum(AutoAdjustments.values()) > 0:
            action_window.apply_adjustments_button.enable()
            action_window.clear_adjustments_button.enable()
        else:
            action_window.apply_adjustments_button.disable()
            action_window.clear_adjustments_button.disable()

        if ApplyAdjustments is True:
            Board, EvenOrOdd, adjustments_made = helpers.adjustBoardDimensions(step_stack[-1].copy(), (None, None), w, h, HeldDownCells, EvenOrOdd, AutoAdjustments)
            helpers.appendToStepStack(Board, step_stack)

            ApplyAdjustments = False

        if ClearHistory is True:
            current_board = step_stack[-1]
            step_stack.clear()
            step_stack.append(current_board)
            ClearHistory = False

        if os.path.exists(DefaultSavePath) is True:
            SavePath = DefaultSavePath
        else:
            SavePath = BackupSavePath

        if QuickSave is True:
            print("Quicksaved to:", quick_save_path)
            boardsurf_to_save = helpers.updateScreenWithBoard(Board, surf, EditMode=True, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], Saving=True)
            helpers.savePNGWithBoardInfo(quick_save_path, boardsurf_to_save, step_stack[-1])
            QuickSave = False

        if QuickLoad is True:
            load_status_message = 'No quicksave exists to be loaded!'
            if os.path.exists(quick_save_path):
                loaded, load_status_message = helpers.loadPNGWithBoardInfo(quick_save_path, step_stack)

            if loaded is True and len(HeldDownCells) == 2:
                HeldDownCells, SelectionBoxPresent = helpers.fixSelectionBoxAfterLoad(step_stack[-1], HeldDownCells)

            print(load_status_message)
            QuickLoad = False

        if Load is True:
            load_status_message = ''
            loaded, load_status_message = helpers.loadPNGWithBoardInfo(load_path, step_stack)
            print(load_status_message)
            if loaded is True:
                Continuous = False
                WasContinuous = False

                if len(HeldDownCells) == 2:
                    HeldDownCells, SelectionBoxPresent = helpers.fixSelectionBoxAfterLoad(step_stack[-1], HeldDownCells)

            Load = False

        CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, EditMode, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], DefaultEditCheckerboardBrightness=config_dict["EditCheckerboardBrightness"][0], SelectedCells=HeldDownCells, EvenOrOdd=EvenOrOdd)
        if MenuOpen is True:
            if show_controls_button.text == 'Hide controls':
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

        ScaledHeldDownCells = helpers.getScaledHeldDownCells(step_stack[-1], CurrentBoardSurf, HeldDownCells, w, h)
        if len(ScaledHeldDownCells) == 2:
            helpers.showSelectionBoxSize(surf, step_stack[-1].copy(), ScaledHeldDownCells, HeldDownCells, sidebar_header_font)


        helpers.manageSliderAndEntryWithArray(all_parameters_elements_matched)
        config_dict["Scale"][0] = all_parameters_elements_matched[0][2] = parameters_scale_slider.get_current_value()
        all_parameters_elements_matched[0][3] = parameters_scale_entry.get_text()
        config_dict["MaxFps"][0] = all_parameters_elements_matched[1][2] = parameters_max_fps_slider.get_current_value()
        all_parameters_elements_matched[1][3] = parameters_max_fps_entry.get_text()
        config_dict["Likelihood"][0] = all_parameters_elements_matched[2][2] = parameters_likelihood_slider.get_current_value()
        all_parameters_elements_matched[2][3] = parameters_likelihood_entry.get_text()
        config_dict["CustomBoardSizeWidth"][0] = all_parameters_elements_matched[3][2] = parameters_custom_board_size_width_slider.get_current_value()
        all_parameters_elements_matched[3][3] = parameters_custom_board_size_width_entry.get_text()
        config_dict["CustomBoardSizeHeight"][0] = all_parameters_elements_matched[4][2] = parameters_custom_board_size_height_slider.get_current_value()
        all_parameters_elements_matched[4][3] = parameters_custom_board_size_height_entry.get_text()

        for entryArray in all_parameters_entries[3:]:
            if entryArray[0].is_focused is not True:
                helpers.manageNumberEntry(entryArray)

        # If the height or width of the settings window has changed...
        if (settings_window_actual.get_real_width(), settings_window_actual.get_real_height()) != previousSettingsWindowDimensions:
            parameters_warning_text.set_dimensions((settings_window.get_real_width() - 10, -1))
            parameters_warning_text.rebuild()
            parameters_scale_slider.rebuild()
            parameters_custom_board_size_width_slider.rebuild()
            parameters_custom_board_size_height_slider.rebuild()

            parameters_height_total = helpers.getHeightOfElements(all_parameters_height_references) + 10
            settings_window_actual.set_dimensions((settings_window_actual.get_relative_rect().width, min(settings_window_actual.get_relative_rect().height, parameters_height_total)))
            settings_window.set_scrollable_area_dimensions((settings_window.get_real_width(), parameters_height_total / 1.145 - 2))

            previousSettingsWindowDimensions = (settings_window_actual.get_real_width(), settings_window_actual.get_real_height())

        config_dict["R"][0], config_dict["G"][0], config_dict["B"][0] = color.r, color.g, color.b

        manager.draw_ui(surf)
        pygame.display.update()


def OpenUIElements(ButtonsArray):
    for button in ButtonsArray:
        button.show()

    return True

def CloseUIElements(ButtonsArray):
    for button in ButtonsArray:
        button.hide()

    return False


if __name__ == "__main__":
    main()
