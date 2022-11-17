# Import the pygame library and initialise the game engine
import pygame
from paddle import Paddle
from ball import Ball
from network import Network
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
        self.paddleA.rect.x = 20
        self.paddleA.rect.y = 200

        self.paddleB = Paddle(WHITE, 10, 100)
        self.paddleB.rect.x = self.WIDTH - 20
        self.paddleB.rect.y = 200

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

    def Update(self, p1, p2, ball, velo):
        arg = self.network.Update(p1, p2, ball, velo)
        self.paddleA.rect.x = arg[2]
        self.paddleA.rect.y = arg[3]
        self.paddleB.rect.x = arg[4]
        self.paddleB.rect.y = arg[5]
        self.ball.rect.x = arg[6]
        self.ball.rect.y = arg[7]
        self.ball.velocity[0] = arg[8]
        self.ball.velocity[0] = arg[9]

    def WinRound(self):

        # Check if the self.ball is bouncing against any of the 4 walls:
        if self.ball.rect.x >= self.WIDTH - 10:
            self.scoreA += 1
            # self.ball.velocity[0] = -self.ball.velocity[0]
            self.ball.rect.x = self.WIDTH / 2
            self.ball.rect.y = self.HEIGHT / 2
            self.ball.velocity[0] = -4
            self.ball.velocity[1] = -4

        if self.ball.rect.x <= 0:
            self.scoreB += 1
            self.ball.rect.x = self.WIDTH / 2
            self.ball.rect.y = self.HEIGHT / 2
            self.ball.velocity[0] = 4
            self.ball.velocity[1] = -4
        if self.ball.rect.y > self.HEIGHT - 10:
            self.ball.velocity[1] = -self.ball.velocity[1]
        if self.ball.rect.y < 10:
            self.ball.velocity[1] = -self.ball.velocity[1]

    def RunGame(self):

        # -------- Main Program Loop -----------
        while self.carry_on:

            # --- Limit to 60 frames per second
            self.clock.tick(60)

            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.carry_on = False  # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                        self.network.DisconnectSession()
                        self.carry_on = False
            if not self.network.match:
                print(self.network.Connetion_establish)
                if self.network.Connetion_establish != 1:
                    self.network.CheckConnetion()
                    print(self.network.Connetion_establish)
                print("match  ", not self.network.match)

                if not self.network.match and not self.network.CheckSession():
                    continue

                # if self.network.player % 2 == 0:
                #     my

            # --- Game logic should go here
            self.all_sprites_list.update()
            self.network.Request(self.paddleA.rect.x)
            list_p1 = [self.paddleA.rect.x, self.paddleA.rect.y]
            list_p2 = [self.paddleB.rect.x, self.paddleB.rect.y]
            list_ball = [self.ball.rect.x, self.ball.rect.y]
            list_velo = self.ball.velocity

            # if int(self.network.player) % 2 == 1 and self.network.init == 0:
            #     self.Update(list_p1, list_p2, list_ball, list_velo)
            self.network.Update()

            self.WinRound()
            # Detect collisions between the self.ball and the paddles
            if pygame.sprite.collide_mask(self.ball, self.paddleA) or pygame.sprite.collide_mask(self.ball, self.paddleB):
                if pygame.sprite.collide_mask(self.ball, self.paddleA):
                    self.paddleA.last_bounced = 1
                    self.paddleB.last_bounced = 0
                elif pygame.sprite.collide_mask(self.ball, self.paddleA):
                    self.paddleA.last_bounced = 0
                    self.paddleB.last_bounced = 1
                self.ball.bounce()

            # Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.paddleA.moveUp(5)
            if keys[pygame.K_s]:
                self.paddleA.moveDown(5)
            if keys[pygame.K_UP]:
                self.paddleB.moveUp(5)
            if keys[pygame.K_DOWN]:
                self.paddleB.moveDown(5)
            if keys[pygame.K_n]:
                self.ball.skill()

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


if __name__ == "__main__":
    game = Game()
    game.RunGame()
