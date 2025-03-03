import pyautogui as pag
import pydirectinput as pdi

def move_mouse(movement_direction: tuple, sensitivity: float =1):
    x = int(movement_direction[0] * sensitivity)
    y = int(movement_direction[1] * sensitivity)
    pdi.move(x, y, 0)