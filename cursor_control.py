import pyautogui as pag


def move_mouse(movement_direction: tuple, sensitivity: float =1):
    pag.move(movement_direction[0] * sensitivity, movement_direction[1] * sensitivity, 0)