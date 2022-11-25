# Import the pygame library and initialise the game engine
from random import randint
from urllib import response
import pygame
from paddle import Paddle
from ball import Ball
from network import Network
from protocol import Protocol

from time import sleep
import itertools
import sys
from threading import Thread

ITEMSIZE = 50
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 255, 0)
YELLOW = (250, 182, 40)
BG = (65, 105, 225)  # (106, 159, 181)


class Item(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface([ITEMSIZE, ITEMSIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        pygame.draw.rect(self.image, color, [0, 0, ITEMSIZE, ITEMSIZE])
        self.rect = self.image.get_rect()


class Game():
    def __init__(self):
        pygame.init()

        # Define some colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 255, 0)

        ITEMSIZE = 50

        self.WIDTH = 800
        self.HEIGHT = 600
        # Open a new window
        self.size = (self.WIDTH, self.HEIGHT)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Ping 2 Pong")

        self.paddleA = Paddle(WHITE, 10, 100)
        self.paddleA.rect.x = 10
        self.paddleA.rect.y = 200

        self.paddleB = Paddle(WHITE, 10, 100)
        self.paddleB.rect.x = self.WIDTH - 20
        self.paddleB.rect.y = 200

        self.my_paddle: Paddle
        self.other_paddle: Paddle

        self.ball = Ball(WHITE, 10, 10)
        self.ball.rect.x = 345
        self.ball.rect.y = 195

        self.item = Item(RED, 300, 300)
        self.item.rect.x = 300
        self.item.rect.y = 300

        self.network = Network()

        self.ready = False

        # This will be a list that will contain all the sprites we intend to use in our game.
        self.all_sprites_list = pygame.sprite.Group()

        # Add the 2 paddles and the self.ball to the list of objects
        self.all_sprites_list.add(self.paddleA)
        self.all_sprites_list.add(self.paddleB)
        self.all_sprites_list.add(self.ball)
        self.all_sprites_list.add(self.item)

        # The loop will carry on until the user exits the game (e.g. clicks the close button).
        self.carry_on = True

        # The self.clock will be used to control how fast the self.screen updates
        self.clock = pygame.time.Clock()

        # Initialise player scores
        self.scoreA = 0
        self.scoreB = 0

        # light shade of the button when it's hovered
        self.color_light = (173, 216, 230)

        # dark shade of the button
        self.color_dark = (135, 206, 250)

        self.BG = (65, 105, 225)  # (106, 159, 181)

        self.font = pygame.font.SysFont(
            "microsoftjhengheimicrosoftjhengheiuibold", 40)
        self.Bigfont = pygame.font.SysFont(
            "microsoftjhengheimicrosoftjhengheiuibold", 48)

    """
    A function write text on the screen
    """

    def put_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def LoadingBar(self):
        global done
        done = False
        global loadingC
        for c in itertools.cycle(['|', '/', '-', '\\']):

            if done:
                break
            loadingC = c
            sleep(0.33)

    def MainMenu(self):
        print("READY  ", self.ready)
        if self.ready:
            self.FindingOpponentScreen()  # goes to Finding Opponent Screen
        else:
            self.screen.fill(BG)
            self.put_text('Welcome to Ping2Pong Game',
                          self.Bigfont, WHITE, self.screen, 180, 40)
            mouse = pygame.mouse.get_pos()  # get mouse's position
            for ev in pygame.event.get():
                keys = pygame.key.get_pressed()

                if ev.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    pygame.quit()
                    sys.exit(0)

                # checks if a mouse is clicked
                if ev.type == pygame.MOUSEBUTTONDOWN:

                    # if the user clicked certain area,
                    if self.WIDTH/2-80 <= mouse[0] <= self.WIDTH/2+60 and self.HEIGHT/2+100 <= mouse[1] <= self.HEIGHT/2+140:
                        self.network.DisconnectSession()
                        pygame.quit()  # it quit
                        sys.exit(0)
                    if self.WIDTH/2-80 <= mouse[0] <= self.WIDTH/2+60 and self.HEIGHT/2-100 <= mouse[1] <= self.HEIGHT/2+-60:
                        # self.FindingOpponentScreen()  # goes to Finding Opponent Screen
                        self.ready = True

            # mouse = pygame.mouse.get_pos()  # get mouse's position
            if self.WIDTH/2-80 <= mouse[0] <= self.WIDTH/2+60 and self.HEIGHT/2+100 <= mouse[1] <= self.HEIGHT/2+140:
                self.put_text('QUIT', self.Bigfont, WHITE,
                              self.screen, self.WIDTH/2-27, self.HEIGHT/2+110)
            else:
                self.put_text('QUIT', self.font, WHITE, self.screen,
                              self.WIDTH/2-27, self.HEIGHT/2+110)

            if self.WIDTH/2-80 <= mouse[0] <= self.WIDTH/2+60 and self.HEIGHT/2-100 <= mouse[1] <= self.HEIGHT/2-60:
                self.put_text('PLAY', self.Bigfont, WHITE, self.screen,
                              self.WIDTH/2-27, self.HEIGHT/2-100)
            else:
                self.put_text('PLAY', self.font, WHITE, self.screen,
                              self.WIDTH/2-27, self.HEIGHT/2-100)
            sleep(0.1)
            pygame.display.update()

    def FindingOpponentScreen(self):
        t = Thread(target=self.LoadingBar)

        self.screen.fill(BG)
        mouse = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            keys = pygame.key.get_pressed()

            if ev.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit(0)

            # checks if the user clicked it
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if self.WIDTH/2-400 <= mouse[0] <= self.WIDTH/2-50 and self.HEIGHT/2+250 <= mouse[1] <= self.HEIGHT/2+290:
                    self.ready = False

        if self.WIDTH/2-383 <= mouse[0] <= self.WIDTH/2-33 and self.HEIGHT/2+250 <= mouse[1] <= self.HEIGHT/2+290:
            pygame.draw.rect(self.screen, self.color_light, [
                self.WIDTH/2-383, self.HEIGHT/2+250, 350, 40])
        else:
            pygame.draw.rect(self.screen, self.color_dark, [
                self.WIDTH/2-383, self.HEIGHT/2+250, 350, 40])

        if not t.is_alive():  # if the thread is dead
            t.start()

            self.put_text('Finding Opponent ... ', self.font, WHITE,
                          self.screen, self.WIDTH/2-120, self.HEIGHT/2-50)
        else:  # alive
            self.put_text('Finding Opponent ... ' + loadingC, self.font,
                          WHITE, self.screen, self.WIDTH/2-120, self.HEIGHT/2-50)

        self.put_text("Return to main menu", self.font, WHITE,
                      self.screen, self.WIDTH/2-350, self.HEIGHT/2+255)
        sleep(0.1)
        pygame.display.update()

    def Update(self, dt):
        self.network.protocol.player = self.network.player
        self.network.protocol.counter_player = self.network.counter_player
        self.network.protocol.game = self.network.game
        self.network.protocol.dt = dt
        response_msg = self.network.Update()
        self.other_paddle.rect.x = response_msg.other_paddle_x
        self.other_paddle.rect.y = response_msg.other_paddle_y
        self.my_paddle.rect.x = response_msg.my_paddle_x
        self.my_paddle.rect.y = response_msg.my_paddle_y
        self.ball.rect.x = response_msg.ball_x
        self.ball.rect.y = response_msg.ball_y
        self.scoreA = response_msg.score[0]
        self.scoreB = response_msg.score[1]
        self.item.rect.x = response_msg.item_x
        self.item.rect.y = response_msg.item_y
        self.my_paddle.height = response_msg.my_paddle_height
        self.other_paddle.height = response_msg.other_paddle_height
        self.network.protocol.has_item = response_msg.has_item
        self.network.protocol.other_has_item = response_msg.other_has_item
        self.network.protocol.item_type = response_msg.item_type

        if response_msg.ball_shine[0] or response_msg.ball_shine[1]:
            self.ball.color = (
                randint(0, 255), randint(0, 255), randint(0, 255))
        else:
            self.ball.color = (WHITE)

    def RunGame(self):
        # -------- Main Program Loop -----------

        while self.carry_on:

            if not self.network.protocol.game_ready:  # 게임이 레디상태 아니면 if문 실행
                self.network.protocol.player = self.network.player
                self.network.protocol.my_ready = self.ready  # 나의 레디 상태 전송
                self.MainMenu()
                print(self.network.Connetion_establish)
                if self.network.Connetion_establish != 1:
                    self.network.CheckConnetion()
                    print("conn establish ", self.network.Connetion_establish)
                print("match  ", not self.network.match)
                print("player ", self.network.player)
                if self.ready:
                    if not self.network.CheckSession():
                        continue

                # 1P 2P 구분
                if self.network.player % 2 == 0:  # 1P
                    self.my_paddle = self.paddleB
                    self.other_paddle = self.paddleA
                    self.network.counter_player = self.network.player - 1
                else:                           # 2P
                    self.my_paddle = self.paddleA
                    self.other_paddle = self.paddleB
                    self.network.counter_player = self.network.player + 1
                print("player: ", self.network.player,
                      " counter: ", self.network.counter_player)

            if not self.network.protocol.game_ready:  # 게임이 레디상태가 아니면 여기서 정지
                continue

            dt = self.clock.tick(60) / 10
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.carry_on = False  # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                        self.carry_on = False

                        # 컨트롤 제어 코드
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.network.protocol.pad_up = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.network.protocol.pad_dn = True
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        if self.network.protocol.has_item:

                            self.network.protocol.item_use = True
                            self.network.protocol.has_item = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.network.protocol.pad_up = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.network.protocol.pad_dn = False
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        self.network.protocol.item_use = False

            # --- Game logic should go here
            self.all_sprites_list.update()

            # Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B)
            self.Update(dt)

            # --- Drawing code should go here
            # First, clear the self.screen to black.
            self.screen.fill(BLACK)
            # Draw the net
            pygame.draw.line(self.screen, WHITE, [
                             self.WIDTH/2, 0], [self.WIDTH/2, self.HEIGHT], 2)

            # Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
            self.all_sprites_list.draw(self.screen)

            # Display scores:
            font = pygame.font.Font(None, 74)
            text = font.render(str(self.scoreA), 1, WHITE)
            self.screen.blit(text, (self.WIDTH/2-110, 10))
            text = font.render(str(self.scoreB), 1, WHITE)
            self.screen.blit(text, (self.WIDTH/2+110, 10))

            if self.network.protocol.has_item:
                self.my_paddle.color = YELLOW
            else:
                self.my_paddle.color = WHITE

            if self.network.protocol.other_has_item:
                self.other_paddle.color = YELLOW
            else:
                self.other_paddle.color = WHITE

            # --- Go ahead and update the self.screen with what we've drawn.
            pygame.display.flip()

        # Once we have exited the main program loop we can stop the game engine:
        pygame.quit()
        self.network.DisconnectSession()


if __name__ == "__main__":
    game = Game()
    game.RunGame()
