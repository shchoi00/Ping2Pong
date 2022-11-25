import pygame
import sys
import pygame.freetype
import time
import sys
import itertools
from pygame.locals import *
import threading


# light shade of the button when it's hovered
color_light = (173, 216, 230)

# dark shade of the button
color_dark = (135, 206, 250)

BG = (65, 105, 225)  # (106, 159, 181)
WHITE = (255, 255, 255)

mainClock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption('Ping2Pong')

screen = pygame.display.set_mode((800, 600), 0, 32)
width = screen.get_width()
height = screen.get_height()


font = pygame.font.SysFont("microsoftjhengheimicrosoftjhengheiuibold", 40)
Bigfont = pygame.font.SysFont("microsoftjhengheimicrosoftjhengheiuibold", 48)

"""
A function write text on the screen
"""


def put_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


'''This function changes loadingC value to change bar in FindingOpponentScreen function'''


def LoadingBar():
    global done
    done = False
    global loadingC
    for c in itertools.cycle(['|', '/', '-', '\\']):

        if done:
            break
        loadingC = c
        time.sleep(0.33)


'''This function contains 2 buttons of Play and Quit'''


def main_menu():

    loadingC = ''
    done = False
    while True:

        screen.fill(BG)
        put_text('Welcome to Ping2Pong Game', Bigfont, WHITE, screen, 180, 40)

        for ev in pygame.event.get():
            keys = pygame.key.get_pressed()

            if ev.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit(0)

            # checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:

                # if the user clicked certain area,
                if width/2-80 <= mouse[0] <= width/2+60 and height/2+100 <= mouse[1] <= height/2+140:
                    pygame.quit()  # it quit
                    sys.exit(0)
                if width/2-80 <= mouse[0] <= width/2+60 and height/2-100 <= mouse[1] <= height/2+-60:
                    FindingOpponentScreen()  # goes to Finding Opponent Screen

        mouse = pygame.mouse.get_pos()  # get mouse's position
        if width/2-80 <= mouse[0] <= width/2+60 and height/2+100 <= mouse[1] <= height/2+140:
            put_text('QUIT', Bigfont, WHITE, screen, width/2-27, height/2+110)
        else:
            put_text('QUIT', font, WHITE, screen, width/2-27, height/2+110)

        if width/2-80 <= mouse[0] <= width/2+60 and height/2-100 <= mouse[1] <= height/2-60:
            put_text('PLAY', Bigfont, WHITE, screen, width/2-27, height/2-100)
        else:
            put_text('PLAY', font, WHITE, screen, width/2-27, height/2-100)

        pygame.display.update()


count = 0

"""
This function is called when the "PLAY" button is clicked.
"""


def FindingOpponentScreen():
    running = True
    t = threading.Thread(target=LoadingBar)

    while running:
        screen.fill(BG)

        for ev in pygame.event.get():
            keys = pygame.key.get_pressed()

            if ev.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit(0)

            # checks if the user clicked it
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if width/2-400 <= mouse[0] <= width/2-50 and height/2+250 <= mouse[1] <= height/2+290:
                    done = True
                    main_menu()  # go back to the main menu

        mouse = pygame.mouse.get_pos()
        if width/2-383 <= mouse[0] <= width/2-33 and height/2+250 <= mouse[1] <= height/2+290:
            pygame.draw.rect(screen, color_light, [
                             width/2-383, height/2+250, 350, 40])
        else:
            pygame.draw.rect(screen, color_dark, [
                             width/2-383, height/2+250, 350, 40])

        if not t.is_alive():  # if the thread is dead
            t.start()
            put_text('Finding Opponent ... ', font, WHITE,
                     screen, width/2-120, height/2-50)
        else:  # alive
            put_text('Finding Opponent ... ' + loadingC, font,
                     WHITE, screen, width/2-120, height/2-50)

        put_text("Return to main menu", font, WHITE,
                 screen, width/2-350, height/2+255)

        pygame.display.update()


if __name__ == "__main__":
    main_menu()
