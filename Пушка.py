import pygame
import random
import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

WIDTH = 600
HEIGHT = 400

frame_sleep_time = 100
dt = 0.1  # time slice
g = 9.8
screen = None

def random_target_color():
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (0, 255, 255),
              (255, 255, 0), (255, 0, 255)]
    return random.choice(colors)


class Ball:
    def __init__(self, x, y, vx, vy, r, color):
        self.r = r
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.actual = True  # The actuality of the object - it is alive or already shot down (out of the game)

    def draw(self):
        if not self.actual:
            return
        pygame.draw.ellipse(screen, self.color,
                            [self.x - self.r, self.y - self.r,
                             2 * self.r, 2 * self.r])

    def move(self):
        if not self.actual:
            return
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt + g * dt ** 2 / 2
        self.vy += g * dt
        if new_x < self.r or new_x > WIDTH - self.r:
            new_x = self.x
            self.vx = -self.vx
        if new_y < self.r or new_y > HEIGHT - self.r:
            new_y = self.y
            self.vy = -self.vy
        self.x, self.y = new_x, new_y

    def collide(self, ball):
        """
        Checks the condition for the Pythagorean theorem L <= self.r + ball.r
        """
        dx, dy = self.x - ball.x, self.y - ball.y
        return (dx**2 + dy**2)**0.5 <= self.r + ball.r


class Target(Ball):
    min_radius = 10
    max_radius = 50
    max_initial_speed = 10

    def __init__(self):
        r = random.randint(self.min_radius, self.max_radius)
        x, y = self.generate_random_target_coord(r)
        vx, vy = self.generate_random_target_velocity()
        color = random_target_color()
        super().__init__(x, y, vx, vy, r, color)

    def generate_random_target_coord(self, r):
        x = random.randint(r, WIDTH - r)
        y = random.randint(r, HEIGHT - r)
        return x, y

    def generate_random_target_velocity(self):
        return [random.randint(-self.max_initial_speed,
                               +self.max_initial_speed) for _ in range(2)]

# TODO: SuperTarget
# class SuperTarget(Target):
#     def __init__(self):
#         radius = 10
#         x, y = self.generate_random_target_coord(radius)
#         vx, vy = 10, 10
#         color =
#
#         super().__init__(x, y, vx, vy, radius, color)


class Shell(Ball):
    shell_color = BLACK

    def __init__(self, actual, x=0, y=0, vx=0, vy=0, r=0):
        super().__init__(x, y, vx, vy, r, self.shell_color)
        self.actual = actual


class Cannon:
    cannon_width = 8

    def __init__(self):
        self.x = 0
        self.y = HEIGHT
        self.lx = 30
        self.ly = 30
        self.draw()

    def draw(self):
        pygame.draw.line(screen, BLACK,
                         [self.x, self.y],
                         [self.x + self.lx, self.y + self.ly], self.cannon_width)

    def aim(self, x, y):
        L = ((x - self.x)**2 + (y - self.y)**2)**0.5
        self.lx = 40 * (x - self.x) / L
        self.ly = 40 * (y - self.y) / L
        self.draw()

    def shoot(self, speed_factor):
        x, y = self.x + self.lx, self.y + self.ly
        L = (self.lx**2 + self.ly**2)**0.5
        vx = self.lx / L * speed_factor / 10
        vy = self.ly / L * speed_factor / 10
        return Shell(True, x, y, vx, vy, self.cannon_width//2)


def init_screen(*size):
    screen = pygame.display.set_mode(size)
    screen.fill(WHITE)
    pygame.display.set_caption("My Game")
    pygame.display.flip()
    return screen


def main():
    global screen  # global variable - screen
    pygame.init()
    screen = init_screen(WIDTH, HEIGHT)

    cannon = Cannon()
    game_over = False
    cannon.draw()
    targets = [Target()]
    shell = Shell(False)
    clock = pygame.time.Clock()
    score = 0
    game_time = time.time()

    while not game_over:

        if random.randint(1, 200) == 1:
            targets.append(Target())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                time_click = time.time()
            elif event.type == pygame.MOUSEBUTTONUP:
                time_click -= time.time()
                time_click = abs(time_click)
                time_click = int(time_click * 10 // 0.1)
                if time_click > 110:
                    time_click = 110
                time_of_mouse_button_press = 500 + (time_click - 10) * 10
                shell = cannon.shoot(time_of_mouse_button_press)

        # the calculation of new locations of the bodies
        shell.move()
        for target in targets:
            if target.actual:
                if shell.collide(target) and shell.actual:  # the collision of shell and target
                    shell.actual = target.actual = False
                    score += 10
            target.move()

        # display new locations of the bodies
        screen.fill(WHITE)
        shell.draw()
        for i in range(len(targets)):
            if targets[i].actual:
                targets[i].draw()
        cannon.aim(*pygame.mouse.get_pos())

        label_time = pygame.font.SysFont("comicsansms", 16).render("Time " + str(int(time.time() - game_time)) + "/60", True, BLUE)
        screen.blit(label_time, (500, 21))

        label_score = pygame.font.SysFont("comicsansms", 20).render("Score " + str(score), True, RED)
        screen.blit(label_score, (20, 20))

        if time.time() - game_time >= 60:
            game_over = True
            label_game_over = pygame.font.SysFont("comicsansms", 30).render("GAME OVER", True, BLACK)
            screen.blit(label_game_over, (220, 180))
            pygame.display.flip()
            time.sleep(10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()