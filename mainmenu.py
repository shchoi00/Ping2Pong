import pygame, sys
import pygame.freetype
#import time
import sys
#import itertools
from pygame.locals import *


# light shade of the button 
color_light = (173,216,230) 
  
# dark shade of the button 
color_dark = (135,206,250) 

BG = (65,105,225)  #(106, 159, 181)
WHITE = (255,255,255)

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Ping2Pong')

screen = pygame.display.set_mode((840, 600),0,32)
width = screen.get_width()
height = screen.get_height()


font = pygame.font.SysFont("microsoftjhengheimicrosoftjhengheiuibold", 40)
Bigfont = pygame.font.SysFont("microsoftjhengheimicrosoftjhengheiuibold", 48)
#font = pygame.freetype.SysFont("Courier", font_size, bold=True)

"""
A function write text on the screen
"""
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
 
# A variable to check for the status later
 
# Main container function that holds the buttons and game functions
def main_menu():
    while True:
 
        screen.fill(BG)
        draw_text('Welcome to Ping2Pong Game', font, WHITE, screen, 250, 40)

        for ev in pygame.event.get(): 
          
            if ev.type == pygame.QUIT: 
                pygame.quit() 
                
            #checks if a mouse is clicked 
            if ev.type == pygame.MOUSEBUTTONDOWN: 
                
                #if the mouse is clicked on the 
                # button the game is terminated 
                if width/2-80 <= mouse[0] <= width/2+60 and height/2+100 <= mouse[1] <= height/2+140: 
                    pygame.quit()   #quit button
                if width/2-80 <= mouse[0] <= width/2+60 and height/2-100 <= mouse[1] <= height/2+-60: 
                    game()
                
    
        
        mouse = pygame.mouse.get_pos() 
        if width/2-80 <= mouse[0] <= width/2+60 and height/2+100 <= mouse[1] <= height/2+140:
            draw_text('QUIT', Bigfont, WHITE, screen, width/2-27,height/2+110)
            #pygame.draw.rect(screen,color_light,[width/2-80,height/2+100,140,40]) 
        else: 
            draw_text('QUIT', font, WHITE, screen, width/2-27,height/2+110)
            #pygame.draw.rect(screen,color_dark,[width/2-80,height/2+100,140,40]) 
            
            
        if width/2-80 <= mouse[0] <= width/2+60 and height/2-100 <= mouse[1] <= height/2-60: 
            draw_text('PLAY', Bigfont, WHITE, screen, width/2-27,height/2-100)
            #pygame.draw.rect(screen,color_light,[width/2-80,height/2-100,140,40]) 
        else: 
            draw_text('PLAY', font, WHITE, screen, width/2-27,height/2-100)
            #pygame.draw.rect(screen,color_dark,[width/2-80,height/2-100,140,40]) 
        
        pygame.display.update()
        #mainClock.tick(60)
 
count = 0

"""
This function is called when the "PLAY" button is clicked.
"""
def game():
    running = True
    while running:
        screen.fill(BG)


        for ev in pygame.event.get(): 
          
            if ev.type == pygame.QUIT: 
                pygame.quit() 
                
            #checks if a mouse is clicked 
            if ev.type == pygame.MOUSEBUTTONDOWN: 
                
                #if the mouse is clicked on the 
                # button the game is terminated 
                if width/2-400 <= mouse[0] <= width/2-150 and height/2+250 <= mouse[1] <= height/2+290: 
                    main_menu()   #go back to main menu
        
        mouse = pygame.mouse.get_pos() 
        if width/2-400 <= mouse[0] <= width/2-50 and height/2+250 <= mouse[1] <= height/2+290: 
            pygame.draw.rect(screen,color_light,[width/2-400,height/2+250,350,40]) 
        else: 
            pygame.draw.rect(screen,color_dark,[width/2-400,height/2+250,350,40]) 
        
        draw_text('Finding Opponent ... ', font, WHITE, screen, width/2-120,height/2-50) 
            
        
        draw_text("Return to main menu", font, WHITE, screen, width/2-390, height/2+250)
        '''
        for c in itertools.cycle(['|', '/', '-', '\\']):
            
            #if done:
            #    draw_text('QUIT', font, WHITE, screen, width/2-27,height/2+110)
            draw_text('loading ' + c, font, WHITE, screen, width/2-27,height/2+110) 
            #sys.stdout.write('\rloading ' + c)
            #sys.stdout.flush()
            time.sleep(1000)
        time.sleep(0.1)
        '''
        ################### Loading Screen ########################
        '''
        if count == 0:
            draw_text("Looking for an opponent \\", font, WHITE, screen, width/2-390, height/2+250)
            count = 1
        elif count == 1:
            draw_text("Looking for an opponent |", font, WHITE, screen, width/2-390, height/2+250)
            count = 2
        elif count==2:
            draw_text("Looking for an opponent /", font, WHITE, screen, width/2-390, height/2+250)
            count = 3
        elif count == 3:
            draw_text("Looking for an opponent -", font, WHITE, screen, width/2-390, height/2+250)
            count = 0
        '''
        
        ####
        pygame.display.update()
        #mainClock.tick(60)

 
main_menu()