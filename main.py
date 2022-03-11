import helpers
from classes import SettingsWindow, PNGFilePicker, ChooseFileNameWindow, ActionWindow
import pygame
import pygame_gui
import os
import appdirs
from pathlib import Path
from collections import deque
from get_shapes_dict import get_shapes_dict

COLORCHANGED = pygame.event.custom_type()
SETTINGSAPPLIED = pygame.event.custom_type()
BOARDADJUSTBUTTON = pygame.event.custom_type()

def get_version_number():
    # major.minor.patch
    # major: major changes, like a rewrite of the project
    # minor: new functionality
    # patch: minor changes or bug fixes
    version = '1.1.1'

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

    Scale = None
    Continuous = True
    WasContinuous = True
    Update = True
    Step = False
    StepBack = False
    NewBoard = True
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

    themes = [[19, pygame.Color('Green'), pygame.Color('Blue'), pygame.Color('Purple'), pygame.Color('Red')]]

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
    color = pygame.Color(config_dict["R"][0], config_dict["G"][0], config_dict["B"][0])


    action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], BOARDADJUSTBUTTON=BOARDADJUSTBUTTON, AutoAdjust=config_dict["AutoAdjust"][0])
    action_window.kill()


    back_to_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4), (400, 50)), text='Return (ESC)', manager=manager, visible=0)
    show_controls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 50), (400, 50)), text='Show controls', manager=manager, visible=0)
    show_parameters_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 100), (400, 50)), text='Show settings', manager=manager, visible=0)
    edit_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 150), (400, 50)), text='Enable edit mode (E)', manager=manager, visible=0)
    save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 200), (400, 50)), text='Save board', manager=manager, visible=0)
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 250), (400, 50)), text='Load board', manager=manager, visible=0)
    quit_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((w / 2 - 200, h / 4 + 300), (400, 50)), text='Quit (F4)', manager=manager, visible=0)

    all_menu_buttons = [back_to_game_button, show_controls_button, show_parameters_button, edit_mode_button, save_button, load_button, quit_game_button]

    settings_window = SettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, w=w, h=h, config_dict=config_dict, color=[color][0], COLORCHANGED=COLORCHANGED, SETTINGSAPPLIED=SETTINGSAPPLIED)
    settings_window.kill()

    HeldDownCells = []
    CopiedBoard = None

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

    # Generate array which is a fraction of the user's monitor size according to scale. There is a liklihood
    # of 1 / Likelihood that any given cell will start alive
    if config_dict["CustomBoardSizeEnabled"][0] is False:
        Board, theme_board = helpers.generateArray(int(h / config_dict["Scale"][0]), int(w / config_dict["Scale"][0]), config_dict["Likelihood"][0])
    else:
        Board, theme_board = helpers.generateArray(config_dict["CustomBoardSizeHeight"][0], config_dict["CustomBoardSizeWidth"][0], config_dict["Likelihood"][0])

    step_stack.append(Board.copy())

    while running:
        if Scale != helpers.getScale(Board, w, h):
            Scale, Which = helpers.getScale(Board, w, h)
            shapes_dict = get_shapes_dict(Scale, Board)

        time_delta = clock.tick(120) / 1000.0
        time_delta_stack.append(time_delta)
        if len(time_delta_stack) > 2000:
            time_delta_stack.popleft()

        if len(HeldDownCells) < 2:
            SelectionBoxPresent = False

        keys = pygame.key.get_pressed()

        time_delta_added = time_delta_added + time_delta
        if time_delta_added >= (1 / config_dict["MaxFps"][0]):
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
                    HeldDownCells = []
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
                elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                    themes[0][0] = max(themes[0][0] - 1, 0)
                    print('theme_int:', themes[0][0])
                elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                    themes[0][0] = min(themes[0][0] + 1, 19)
                    print('theme_int:', themes[0][0])
                elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                    if EditMode is False:
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                    elif EditMode is True:
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
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], BOARDADJUSTBUTTON=BOARDADJUSTBUTTON, AutoAdjust=config_dict["AutoAdjust"][0])
                    elif Continuous is False and EditMode is False:
                        EditMode = True
                        edit_mode_button.set_text('Disable edit mode (E)')
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], BOARDADJUSTBUTTON=BOARDADJUSTBUTTON, AutoAdjust=config_dict["AutoAdjust"][0])
                    elif EditMode is True and not action_window.alive():
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], BOARDADJUSTBUTTON=BOARDADJUSTBUTTON, AutoAdjust=config_dict["AutoAdjust"][0])
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

                    show_controls_button.set_text('Show controls')
                    show_parameters_button.set_text('Show settings')
                    MenuOpen = OpenUIElements(all_menu_buttons)
                else:
                    Continuous = WasContinuous

                    if SelectionBoxPresent is True:
                        action_window = ActionWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, width=w, height=h, SelMode=config_dict["SelectionMode"][0], EraserMode=config_dict["Eraser"][0], BOARDADJUSTBUTTON=BOARDADJUSTBUTTON, AutoAdjust=config_dict["AutoAdjust"][0])

                    action_window.show()
                    MenuOpen = CloseUIElements(all_menu_buttons)
                    settings_window.kill()

                    if save_location is not None: save_location.kill()
                    if file_name_window is not None: file_name_window.kill()

            if (event.type == pygame.KEYUP and event.key == pygame.K_F4) or (event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == quit_game_button):
                helpers.writeDictToConfig(config_file_dir, config_file_path, config_dict)
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button and show_controls_button.text == 'Show controls':
                show_controls_button.set_text('Hide controls')
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

                if show_parameters_button.text == 'Hide settings':
                    show_parameters_button.set_text('Show settings')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_controls_button:
                show_controls_button.set_text('Show controls')
                helpers.blitBoardOnScreenEvenly(surf, CurrentBoardSurf, EditMode)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button and show_parameters_button.text == 'Show settings':
                show_parameters_button.set_text('Hide settings')
                settings_window = SettingsWindow(rect=pygame.Rect((w / 2 - 525, h / 4 - 13), (330, 458)), manager=manager, w=w, h=h, config_dict=config_dict, color=[color][0], COLORCHANGED=COLORCHANGED, SETTINGSAPPLIED=SETTINGSAPPLIED)

                if show_controls_button.text == 'Hide controls':
                    show_controls_button.set_text('Show controls')

            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == show_parameters_button:
                settings_window.kill()

            if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == settings_window:
                show_parameters_button.set_text('Show settings')

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
                helpers.savePNGWithBoardInfo(save_path, boardsurf_to_save, step_stack[-1], theme_board)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == load_button and helpers.anyAliveElements(save_load_windows) is False:
                save_location = PNGFilePicker(pygame.Rect((w / 2 - 80, h / 2 + 25), (420, 400)), manager=manager, window_title='Pick .PNG board file', initial_file_path=SavePath, allow_picking_directories=False)

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and event.ui_element == save_location and save_location.window_display_title == 'Pick .PNG board file':
                load_path = event.text
                Load = True

            if event.type == pygame.DROPFILE:
                load_path = event.file
                Load = True

            if event.type == pygame.MOUSEBUTTONUP and MenuOpen is False:
                current_max_fps = config_dict["MaxFps"][0]
                max_fps_slider_range = settings_window.max_fps_slider.value_range
                if Continuous is True:
                    if event.button == 4:
                        config_dict["MaxFps"][0] = min(current_max_fps + 1, max_fps_slider_range[1])
                    elif event.button == 5:
                        config_dict["MaxFps"][0] = max(current_max_fps - 1, max_fps_slider_range[0])

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

                    if config_dict["SelectionMode"][0] is True and Continuous is False:
                        if len(HeldDownCells) < 2 and board_pos not in HeldDownCells:
                            HeldDownCells.append(board_pos)
                        elif len(HeldDownCells) == 2 and board_pos == HeldDownCells[0]:
                            HeldDownCells.pop(1)
                        elif len(HeldDownCells) == 2:
                            HeldDownCells[1] = board_pos

                    elif config_dict["SelectionMode"][0] is False:
                        Board = step_stack[-1].copy()
                        if config_dict["Eraser"][0] is False:
                            Board[board_pos] = 1
                        else:
                            Board[board_pos] = 0

                        helpers.appendToStepStack(Board, step_stack)

            if event.type == SETTINGSAPPLIED and event.ui_element == settings_window:
                config_dict = event.config_dict

            if event.type == COLORCHANGED and event.ui_element == settings_window:
                color = event.color

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
            width, height = helpers.determineWidthAndHeight(config_dict, w, h)
            Board, theme_board = helpers.generateArray(height, width, config_dict["Likelihood"][0])
            step_stack.append(Board)

            if len(HeldDownCells) == 2:
                HeldDownCells, SelectionBoxPresent = helpers.fixSelectionBoxAfterLoad(step_stack[-1], HeldDownCells)

            NewBoard = False

        if Zoom is True:
            Board, theme_board = helpers.zoom(step_stack[-1], theme_board, HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)
            HeldDownCells = []

            Zoom = False

        if Cut is True:
            CopiedBoard, none = helpers.zoom(step_stack[-1], theme_board, HeldDownCells)
            Board = helpers.cut(step_stack[-1].copy(), HeldDownCells)
            helpers.appendToStepStack(Board, step_stack)

            Cut = False

        if Copy is True:
            CopiedBoard, none = helpers.zoom(step_stack[-1], theme_board, HeldDownCells)

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
            Board, theme_board, EvenOrOdd, adjustments_made = helpers.adjustBoardDimensions(step_stack[-1].copy(), theme_board, AdjustBoardTuple, w, h, HeldDownCells, EvenOrOdd)
            helpers.appendToStepStack(Board, step_stack)

            AdjustBoard = False

        if sum(AutoAdjustments.values()) > 0:
            action_window.apply_adjustments_button.enable()
            action_window.clear_adjustments_button.enable()
        else:
            action_window.apply_adjustments_button.disable()
            action_window.clear_adjustments_button.disable()

        if ApplyAdjustments is True:
            Board, theme_board, EvenOrOdd, adjustments_made = helpers.adjustBoardDimensions(step_stack[-1].copy(), theme_board, (None, None), w, h, HeldDownCells, EvenOrOdd, AutoAdjustments)
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
            helpers.savePNGWithBoardInfo(quick_save_path, boardsurf_to_save, step_stack[-1], theme_board)
            QuickSave = False

        if QuickLoad is True:
            load_status_message = 'No quicksave exists to be loaded!'
            if os.path.exists(quick_save_path):
                loaded, load_status_message, theme_board = helpers.loadPNGWithBoardInfo(quick_save_path, step_stack)

            if loaded is True:
                Continuous = False
                WasContinuous = False

                if len(HeldDownCells) == 2:
                    HeldDownCells, SelectionBoxPresent = helpers.fixSelectionBoxAfterLoad(step_stack[-1], HeldDownCells)

            print(load_status_message)

            QuickLoad = False

        if Load is True:
            load_status_message = ''
            loaded, load_status_message, theme_board = helpers.loadPNGWithBoardInfo(load_path, step_stack)
            if loaded is True:
                Continuous = False
                WasContinuous = False

                if len(HeldDownCells) == 2:
                    HeldDownCells, SelectionBoxPresent = helpers.fixSelectionBoxAfterLoad(step_stack[-1], HeldDownCells)

            print(load_status_message)

            Load = False

        # CurrentBoardSurf = helpers.updateScreenWithBoard(step_stack[-1], surf, EditMode, color=color, RandomColorByPixel=config_dict["RandomColorByPixel"][0], DefaultEditCheckerboardBrightness=config_dict["EditCheckerboardBrightness"][0], SelectedCells=HeldDownCells, EvenOrOdd=EvenOrOdd)
        CurrentBoardSurf = helpers.complex_blit_array(step_stack[-1], theme_board, themes, shapes_dict, surf, EditMode, config_dict["EditCheckerboardBrightness"][0], EvenOrOdd, HeldDownCells)
        if MenuOpen is True:
            if show_controls_button.text == 'Hide controls':
                helpers.showControls(surf, w, h, controls_rect, controls_header_text, controls_text_array)

        ScaledHeldDownCells = helpers.getScaledHeldDownCells(step_stack[-1], CurrentBoardSurf, HeldDownCells, w, h)
        if len(ScaledHeldDownCells) == 2:
            helpers.showSelectionBoxSize(surf, step_stack[-1].copy(), ScaledHeldDownCells, HeldDownCells, sidebar_header_font)

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
