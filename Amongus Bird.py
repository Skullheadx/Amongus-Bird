import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import math
import random
import time

def format_number(num):
    if num < 1000:
        return num

    out = ""
    for i, val in enumerate((str(num)[::-1])):
        out += val
        if (i + 1) % 3 == 0 and i != len(str(num)) - 1:
            out += ","
    out = out[::-1]

    return out


def reset_game():
    global game
    game = Game()


class Label:
    horizontal_padding = 5
    vertical_padding = 5
    outline_thickness = 2

    def __init__(self, x, y, text, font_size, text_colour=(0, 0, 0), antialias=True, fill_colour=(150, 150, 150),
                 outline_colour=(0, 0, 0)):
        self.position = pygame.Vector2(x, y)
        self.font = pygame.font.Font("textures/MontserratBlack-ZVK6J.otf", font_size)
        self.text_colour = text_colour
        self.antialias = antialias
        self.fill_colour = fill_colour
        self.outline_colour = outline_colour
        self.raw_text = text
        self.text, self.width, self.height = self.create_text(self.raw_text)
        self.centering = pygame.Vector2(0, 0)

    def create_text(self, text):
        out = []
        max_width = 0
        max_height = 0
        for line in text:
            text_surface = self.font.render(line, self.antialias, self.text_colour)
            width = text_surface.get_width()
            height = text_surface.get_height()
            out.append((text_surface, width, height))
            max_width = max(max_width, width)
            max_height += height
        return out, max_width, max_height

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None, font_size=None):
        if new_text is not None:
            self.text, self.width, self.height = self.create_text(new_text)
        if font_size is not None:
            self.font = pygame.font.Font("textures/MontserratBlack-ZVK6J.otf", font_size)
            self.text, self.width, self.height = self.create_text(self.raw_text)
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour

    def draw(self, surface, centered_x=True, centered_y=True, outlined=False, filled=False):
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2
        if filled:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.fill_colour, r)
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)

        prev_height = 0
        for line in self.text:
            text_surface, width, height = line
            surface.blit(text_surface, self.position - self.centering + pygame.Vector2(0, prev_height))
            prev_height += height


class Button(Label):

    def __init__(self, x, y, text, font_size, text_colour=(0, 0, 0), antialias=True, fill_color=(150, 150, 150),
                 outline_colour=(0, 0, 0)):
        super().__init__(x, y, text, font_size, text_colour=text_colour, antialias=antialias, fill_colour=fill_color,
                         outline_colour=outline_colour)

    def is_touching_mouse_pointer(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (self.position.x - self.centering.x <= mouse_x <= self.position.x + self.width - self.centering.x
                and self.position.y - self.centering.y <= mouse_y <= self.position.y + self.height - self.centering.y):
            return True
        return False

    def lighten(self):
        self.fill_colour = (150, 150, 150)

    def darken(self):
        self.fill_colour = (170, 170, 170)

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None):
        super().update(delta, new_text=new_text, x=x, y=y, width=width, height=height, colour=colour)
        if self.is_touching_mouse_pointer():
            self.lighten()
        else:
            self.darken()

    def run_function(self, function):
        return function()


class Rectangle:
    horizontal_padding = 12
    vertical_padding = 12
    outline_colour = (80, 80, 80)
    outline_thickness = 5

    def __init__(self, x, y, width, height, colour):
        self.position = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.fill_colour = colour
        self.centering = pygame.Vector2(0, 0)

    def update(self, x=None, y=None, width=None, height=None, colour=None):
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour

    def draw(self, surface, centered_x=True, centered_y=True, outlined=True):
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2
        r = pygame.Rect(self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                        pygame.Vector2(self.width + 2 * self.horizontal_padding, self.height + self.vertical_padding))
        pygame.draw.rect(surface, self.fill_colour, r)
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)


class Player:
    width = 40
    height = 40
    gravity = 0.0180
    jump_strength = 0.35
    speed = 0.215
    jump_cooldown_length = 0
    path = "textures/Among us bird/Layer 1_bird_updated_"
    frames = []
    for i in range(1, 5):
        frames.append(pygame.image.load(path + str(i) + ".png"))
    bird = frames[0]
    crop = 2 * 40 / bird.get_width() * 1.75
    bird = pygame.transform.scale(bird, (width, height))

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.jump_cooldown = 200
        self.collision_rect = pygame.Rect(self.position.x - self.width / 2,
                                          (self.position.y - self.height / 2 + self.crop), self.width,
                                          self.height - 2 * self.crop)
        self.distance = 0
        self.current_frame = 0
        self.test = 0
        self.display_bird = self.bird
        self.direction = 0
        self.no_jump = 0
        self.help_label = Label(SCREEN_WIDTH/2, SCREEN_HEIGHT*4/5, ["Press SPACE to jump"], 20, (230,230,230))

    def update(self, delta, is_game_over):
        self.velocity *= self.no_jump
        if self.no_jump == 0:
            self.help_label.update(delta, y=SCREEN_HEIGHT * 4 /5 + 20 * math.sin(1.5 * time.time()))
        self.test += delta
        self.jump_cooldown -= delta

        if self.test > 500 / len(self.frames):
            self.bird = self.frames[self.current_frame]
            self.bird = pygame.transform.scale(self.bird, (self.width, self.height))
            self.current_frame += 1
            self.current_frame %= len(self.frames)
            self.test = 0
            if self.velocity.x < 0:
                self.bird = pygame.transform.flip(self.bird, True, True)

        self.display_bird = self.bird
        if self.velocity.y > 0.25:
            self.display_bird = pygame.transform.rotate(self.bird, self.direction)
            self.collision_rect = self.display_bird.get_rect(center=self.bird.get_rect(topleft=self.position).center)
            self.direction -= delta / 16
            self.direction = max(self.direction, -70)
        else:
            self.display_bird = self.bird
            self.direction = 0

        if not is_game_over:
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE] and self.jump_cooldown <= 0:
                self.jump()

        if self.is_out_of_bounds():
            return False

        self.position.x += self.velocity.x * delta
        for wall in game.wall_manager.walls:
            for collision_rect in wall.collision_rects:
                if self.is_colliding(collision_rect):
                    if self.position.x < wall.position.x + wall.width:
                        self.position.x = wall.position.x - self.width
                    else:
                        self.position.x = wall.position.x + wall.width + self.width
                    self.velocity.x *= -1
                    return False
        self.position.y += self.velocity.y * delta
        for wall in game.wall_manager.walls:
            for collision_rect in wall.collision_rects:
                if self.is_colliding(collision_rect):
                    if self.position.y < collision_rect.y + collision_rect.height:
                        self.position.y = collision_rect.y - self.height
                    else:
                        self.position.y = collision_rect.y + collision_rect.height + self.height
                    self.velocity.y *= -1
                    return False

        self.velocity.y += self.gravity
        return True

    def is_out_of_bounds(self):
        if self.position.y + self.height < 0 or self.position.y - self.height > SCREEN_HEIGHT:
            return True
        return False

    def is_colliding(self, rect):
        self.collision_rect = pygame.Rect(self.position.x - self.width / 2,
                                          self.position.y - self.height / 2 + self.crop, self.width,
                                          self.height - 2 * self.crop)
        if rect.colliderect(self.collision_rect):
            return True
        return False

    def jump(self):
        self.no_jump = 1
        self.velocity.y = -self.jump_strength
        self.jump_cooldown = self.jump_cooldown_length

    def draw(self, surface):
        # # pygame.draw.rect(surface, (255,255,0), self.collision_rect)
        surface.blit(self.display_bird, self.position - pygame.Vector2(self.width / 2, self.height / 2))
        if self.no_jump == 0:
            self.help_label.draw(screen)


class Wall:
    fill_colour = (0, 255, 0)
    hole_height = Player.height * 1.5
    width = Player.width
    pipe = pygame.image.load("textures/pipe.png")
    pipe = pygame.transform.scale(pipe, (width, width))
    end_pipe = pygame.image.load("textures/pipe_top.png")
    end_pipe = pygame.transform.scale(end_pipe, (width, width))

    def __init__(self, x, hole_y):
        self.position = pygame.Vector2(x, -Player.height)
        self.hole_y = hole_y
        self.collision_rects = [pygame.Rect(self.position.x, self.position.y, self.width, self.hole_y),
                                pygame.Rect(self.position.x, self.hole_y + self.hole_height, self.width,
                                            SCREEN_HEIGHT - (
                                                    self.hole_y + self.hole_height) + self.end_pipe.get_height())]
        self.centering = pygame.Vector2(0, 0)
        self.score_award = 1

    def update(self, delta, x):
        self.position.x -= x * delta
        self.collision_rects = [pygame.Rect(self.position.x, self.position.y, self.width, self.hole_y),
                                pygame.Rect(self.position.x, self.hole_y + self.hole_height, self.width,
                                            SCREEN_HEIGHT - (self.hole_y + self.hole_height) + Player.height)]

    def reset(self):
        self.position.x += SCREEN_WIDTH * 2
        self.hole_y = random.randint(round(self.hole_height * 0.5) + self.end_pipe.get_height() + Player.height,
                                     round(SCREEN_HEIGHT - self.hole_height * 1.5))
        self.score_award = 1

    def award_score(self):
        game.score += self.score_award
        self.score_award = 0

    def draw(self, surface):
        # for r in self.collision_rects:
        #     pygame.draw.rect(surface, self.fill_colour, r)
        r = self.collision_rects[1]
        surface.blit(self.end_pipe, (r.x, r.y))
        for i in range(SCREEN_HEIGHT // self.pipe.get_height()):
            if r.y + i * self.pipe.get_height() > SCREEN_HEIGHT:
                break
            surface.blit(self.pipe, (r.x, r.y + self.end_pipe.get_height() + i * self.pipe.get_height()))
        transformed_end_pipe = pygame.transform.flip(self.end_pipe, False, True)
        r = self.collision_rects[0]
        surface.blit(transformed_end_pipe, (r.x, r.y + r.height - transformed_end_pipe.get_width()))
        for i in range(1, SCREEN_HEIGHT // self.pipe.get_height()):
            if r.y + r.height - i * self.pipe.get_height() < 0:
                break
            surface.blit(self.pipe,
                         (r.x, r.y + r.height - transformed_end_pipe.get_height() - i * self.pipe.get_height()))


class WallManager:

    def __init__(self):
        self.wall_separation_distance = SCREEN_WIDTH / 2
        self.starting_position = SCREEN_WIDTH * 1.1
        self.walls = []
        for i in range(math.floor(SCREEN_WIDTH * 2/ self.wall_separation_distance)):
            self.walls.append(Wall(self.starting_position + self.wall_separation_distance * i,
                                   random.randint(round(Wall.hole_height * 0.5) + Player.height + Player.height,
                                              round(SCREEN_HEIGHT - Wall.hole_height * 1.5))))


    def update(self, delta, slow_down_effect):
        for wall in self.walls:
            wall.update(delta, Player.speed * slow_down_effect * game.player.no_jump)
            if wall.position.x + wall.width < 0:
                wall.reset()
            if game.player.position.x > wall.position.x + wall.width:
                wall.award_score()

    def draw(self, surface):
        for wall in self.walls:
            wall.draw(surface)


class Game:

    def __init__(self):
        self.wall_manager = WallManager()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.score = 0
        self.score_label = Label(SCREEN_WIDTH, 0, [f"Score: {format_number(self.score)}"], 20, (200, 200, 200),
                                 fill_colour=(50, 50, 50), outline_colour=(0, 0, 0))
        self.is_game_over = False
        self.slow_down_effect = 1.0
        self.background = Background((15, 15, 15))

    def update(self, delta):
        self.background.update(delta)
        self.wall_manager.update(delta, self.slow_down_effect)
        self.score_label.update(delta, new_text=[f"Score: {format_number(self.score)}"],
                                x=SCREEN_WIDTH - self.score_label.width - Label.horizontal_padding,
                                y=Label.vertical_padding)
        if not self.player.update(delta, self.is_game_over):
            if not self.is_game_over:
                self.game_over()
        if self.is_game_over:
            self.slow_down_effect /= delta
            if self.player.is_out_of_bounds():
                global game
                game = GameOverScreen(self.score)

    def game_over(self):
        self.player.velocity.x = -Player.speed
        self.is_game_over = True

    def draw(self, screen):
        self.background.draw(screen)
        self.wall_manager.draw(screen)
        self.score_label.draw(screen, centered_y=False, centered_x=False)
        self.player.draw(screen)


class GameOverScreen:

    def __init__(self, score):
        self.score = score
        global highest_score
        self.game_over_card = Rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH * 2 / 3,
                                        SCREEN_HEIGHT * 4 / 5, (50, 50, 50))
        self.title = Label(SCREEN_WIDTH / 2, self.game_over_card.height / 5, [f"Game Over!"], 50,
                           text_colour=(237, 37, 37))
        if score > highest_score:
            self.score_label = Label(SCREEN_WIDTH / 2, self.title.position.y + self.title.height,
                                     [f"NEW HIGHSCORE: {format_number(self.score)}"], 30, text_colour=(200, 200, 200))
            self.high_score_label = Label(SCREEN_WIDTH / 2, self.score_label.position.y + self.score_label.height,
                                          [f""], 30, text_colour=(200, 200, 200))
        else:
            self.score_label = Label(SCREEN_WIDTH / 2, self.title.position.y + self.title.height,
                                     [f"Your Score: {format_number(self.score)}"], 35, text_colour=(200, 200, 200))
            self.high_score_label = Label(SCREEN_WIDTH / 2, self.score_label.position.y + self.score_label.height,
                                          [f"Highscore: {format_number(highest_score)}"], 35,
                                          text_colour=(200, 200, 200))
        self.play_again = Button(SCREEN_WIDTH / 2,
                                 (self.game_over_card.position.y + self.game_over_card.height / 2) * 4 / 5,
                                 [f"   Play Again   "], 25, fill_color=(0, 0, 0), text_colour=(50, 50, 50))
        highest_score = max(highest_score, self.score)
        self.cooldown = 200

    def update(self, delta):
        if self.cooldown <= 0:
            for event in pygame.event.get(pygame.MOUSEBUTTONUP, pump=True):
                if event.button == 1:
                    if self.play_again.is_touching_mouse_pointer():
                        self.play_again.run_function(reset_game)
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                self.play_again.run_function(reset_game)
        # self.game_over_card.update(delta)
        self.title.update(delta, font_size=50 + math.floor(2.5 * math.sin(4 * time.time())))
        # self.score_label.update(delta)
        # self.high_score_label.update(delta)
        self.play_again.update(delta)
        self.cooldown -= delta

    def draw(self, surface):
        self.game_over_card.draw(surface)
        self.title.draw(surface)
        self.score_label.draw(surface)
        self.high_score_label.draw(surface)
        self.play_again.draw(surface, outlined=True, filled=True)


def sort_files(lis):
    out = []
    for item in lis:
        item = item[4:-4]
        out.append(int(item))
    return sorted(out)


class Start:

    def __init__(self, path, game_name):
        self.path = path
        self.directory = os.listdir(self.path)
        self.num = sort_files(self.directory)
        self.current_frame = 0
        self.current_file = None
        self.game_name = game_name

    def update(self, delta):
        if self.current_frame >= len(self.directory) - 1:
            pygame.time.wait(750)
            global game
            game = self.game_name()
        self.current_file = pygame.image.load(
            self.path + "/bruh" + str(self.num[math.floor(self.current_frame)]) + ".png")
        self.current_file = pygame.transform.scale(self.current_file, (
            self.current_file.get_width() * 5, self.current_file.get_height() * 5))
        self.current_frame += 1.25 / delta

    def draw(self, surface):
        surface.fill((153, 100, 249))
        surface.blit(self.current_file, (
            SCREEN_WIDTH / 2 - self.current_file.get_width() / 2,
            SCREEN_HEIGHT / 2 - self.current_file.get_height() / 2))


class Star:

    def __init__(self, x, y, size):
        self.position = pygame.Vector2(x, y)
        self.radius = size / 2
        self.colour = [200, 200, 200]
        self.n = random.random() * 365000

    def update(self, delta):
        # x = int(random.randint(-1,1) * random.random() * delta / 2)
        x = round(75 * math.sin(self.n / 1000) + 180)
        for i in range(3):
            self.colour[i] = x
        self.n += delta

    def draw(self, screen):
        # print(self.colour)
        pygame.draw.circle(screen, self.colour, self.position, self.radius)


class Background:

    def __init__(self, background_colour):
        self.background_colour = background_colour
        self.stars = []
        self.max_star_size = 4.25
        self.max_stars = SCREEN_WIDTH * SCREEN_HEIGHT // 750
        self.min_stars = SCREEN_WIDTH * SCREEN_HEIGHT // 900
        self.add_stars(random.randint(self.min_stars, self.max_stars))

    def add_stars(self, num):
        for i in range(num):
            self.stars.append(Star(random.random() * SCREEN_WIDTH, random.random() * SCREEN_HEIGHT,
                                   random.random() * self.max_star_size))

    def update(self, delta):
        for star in self.stars:
            star.update(delta)

    def draw(self, surface):
        screen.fill(self.background_colour)
        for star in self.stars:
            star.draw(screen)
        # a = pygame.Color(255,0,0,100)
        # pygame.draw.circle(screen, a, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 50)


pygame.init()

SCREEN_HEIGHT = 480
SCREEN_WIDTH = 540
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Amongus Bird")
icon = pygame.transform.scale(Player.bird, (32, 32))
pygame.display.set_icon(icon)

highest_score = 0

game = Start("textures/logo", Game)

fps_cap = 120
clock = pygame.time.Clock()
delta = 1000 // fps_cap

is_running = True
while is_running:

    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            is_running = False

    game.update(delta)
    game.draw(screen)

    pygame.display.update()
    delta = clock.tick(fps_cap)

pygame.quit()
