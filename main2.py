# Import the pygame library and initialise the game engine
import pygame
from paddle import Paddle
from ball import Ball
from network2 import Network
from protocol2 import Protocol
from time import sleep


ITEMSIZE = 50
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 255, 0)


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
        pygame.display.set_caption("Pong")

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

    # def IsConnectionEstablished(self):
    #     Network.ConnetionCheck()

    def Update(self,dt,arr):
        self.network.protocol.pad_up=arr[0]
        self.network.protocol.pad_dn=arr[1]
        self.network.protocol.player = self.network.player
        self.network.protocol.counter_player = self.network.counter_player
        self.network.protocol.game = self.network.game
        self.network.protocol.dt = dt
        response_msg = self.network.Update()
        print("response_msg, ",response_msg)
        self.other_paddle.rect.x = response_msg.other_paddle_x
        self.other_paddle.rect.y = response_msg.other_paddle_y
        self.my_paddle.rect.x = response_msg.my_paddle_x
        self.my_paddle.rect.y = response_msg.my_paddle_y
        self.ball.rect.x = response_msg.ball_x
        self.ball.rect.y = response_msg.ball_y
        self.scoreA = response_msg.score[0]
        self.scoreB = response_msg.score[1]
        print("dt: ",dt," ball.velo.x: ",self.ball.velocity[0])
        print("rep counter  ", response_msg.counter_player)
        print("player: ", self.network.player,
              " counter: ", self.network.counter_player)

    def RunGame(self):
        up: bool = False
        dn: bool = False
        # -------- Main Program Loop -----------
        while self.carry_on:
            dt = self.clock.tick(60) / 10
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.carry_on = False  # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                        self.carry_on = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        up = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        dn = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        up = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        dn = False
            arr = [up,dn]

            if not self.network.match:
                print(self.network.Connetion_establish)
                if self.network.Connetion_establish != 1:
                    self.network.CheckConnetion()
                    print("conn establish ", self.network.Connetion_establish)
                print("match  ", not self.network.match)
                print("player ", self.network.player)
                if not self.network.match and not self.network.CheckSession():
                    continue
                # 1P 2P 구분
                if self.network.player % 2 == 0 :  # 1P
                    self.my_paddle = self.paddleB
                    self.other_paddle = self.paddleA
                    self.network.counter_player = self.network.player - 1
                else:                           # 2P
                    self.my_paddle = self.paddleA
                    self.other_paddle = self.paddleB
                    self.network.counter_player = self.network.player + 1
                print("player: ", self.network.player,
                      " counter: ", self.network.counter_player)
            # --- Game logic should go here
            self.all_sprites_list.update()

            # Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_n]:
                self.ball.skill()
            self.Update(dt,arr)

            # --- Drawing code should go here
            # First, clear the self.screen to black.
            self.screen.fill(BLACK)
            # Draw the net
            pygame.draw.line(self.screen, WHITE, [
                             self.WIDTH/2, 0], [self.WIDTH/2, self.HEIGHT], 2)

            # Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
            self.all_sprites_list.draw(self.screen)

            if self.item.rect.x < self.ball.rect.x + ITEMSIZE and self.ball.rect.x < self.item.rect.x:
                if self.item.rect.y < self.ball.rect.y + ITEMSIZE and self.ball.rect.y < self.item.rect.y:
                    if self.paddleA.last_bounced:
                        self.paddleA.skill_point += 1
                    elif self.paddleB.last_bounced:
                        self.paddleB.skill_point += 1

            # Display scores:
            font = pygame.font.Font(None, 74)
            text = font.render(str(self.scoreA), 1, WHITE)
            self.screen.blit(text, (self.WIDTH/2-110, 10))
            text = font.render(str(self.scoreB), 1, WHITE)
            self.screen.blit(text, (self.WIDTH/2+110, 10))

            # --- Go ahead and update the self.screen with what we've drawn.
            pygame.display.flip()

        # Once we have exited the main program loop we can stop the game engine:
        pygame.quit()
        self.network.DisconnectSession()


if __name__ == "__main__":
    game = Game()
    game.RunGame()
