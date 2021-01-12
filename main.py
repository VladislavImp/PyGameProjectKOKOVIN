import sys
import os
import pygame
import random

FPS = 60
WIDTH = 1920
HEIGHT = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()

player = None

all_sprites = pygame.sprite.Group()
wall_tiles_group = pygame.sprite.Group()
structure_tiles_group = pygame.sprite.Group()
passage_tiles_group = pygame.sprite.Group()
destructible_tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemys_group = pygame.sprite.Group()
error_tiles_group = pygame.sprite.Group()


#случайность уровня
def random_level():
    return random.choice(['map1.txt', 'map2.txt', 'map3.txt'])


#случайность изображения игрока
def random_skin_player():
    n = random.choice(['1', '2', '3'])
    return load_image(f"player{n}.png")


#случайность текстуры врага
def random_enemy_texture():
    n = random.choice(['1', '2', '3', '4', '5'])
    return load_image(f"enemy'{n}'.png")


#случайность текстур
def random_texture(objectname):
    n = random.choice(['1', '2', '3'])
    return load_image(f"{objectname + n}.png")


#функция загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        fullname = os.path.join('data', 'error.png')
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image.convert_alpha()
    return image


bad_coords = [] #координаты куда игрок попасть не может

#текстуры
wall_tiles_image = {'W': random_texture('wall')}

structure_tiles_image = {
    'S': random_texture('surface'),
    '@': load_image('psz.png'),
    'F': random_texture('flour'),
    '#': load_image('flour2.png')
}

passage_tiles_image = {
    'w': load_image('window.png'),
    'd': load_image('door.png')
}

destructible_tiles_image = {
    'c': load_image('concrete.png'),
    'b': load_image('boards.png'),
    'destroyed': load_image('destroying.png')
}

error_tiles_image = {
    'error': load_image('error.png')
}
player_image = random_skin_player()

tile_width = tile_height = 64
tile_size = tile_width


#загрузка уровня
def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, 'S'), level_map))


#создание уровня
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'W':
                Walls_Tile('W', x, y)
            elif level[y][x] == 'S':
                Structure_Tile('S', x, y)
            elif level[y][x] == 'F':
                Structure_Tile('F', x, y)
            elif level[y][x] == '#':
                Structure_Tile('#', x, y)
            elif level[y][x] == 'w':
                Structure_Tile('F', x, y)
                Passage_Tile('w', x, y)
            elif level[y][x] == 'd':
                Structure_Tile('F', x, y)
                Passage_Tile('d', x, y)
            elif level[y][x] == 'c':
                Structure_Tile('F', x, y)
                Destructible_Tile('c', x, y)
            elif level[y][x] == 'b':
                Structure_Tile('F', x, y)
                Destructible_Tile('b', x, y)
            elif level[y][x] == '@':
                Structure_Tile('S', x, y)
                playerx = x
                playery = y
            new_player = Player(playerx, playery)
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


#стартовый экран
def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


#класс пола
class Structure_Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(structure_tiles_group, all_sprites)
        self.image = structure_tiles_image[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


#класс стен
class Walls_Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_tiles_group, all_sprites)
        self.image = wall_tiles_image[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        bad_coords.append([range(tile_width * pos_x - 32, tile_width * pos_x + 48),
                           range(tile_height * pos_y - 62, tile_height * pos_y + 2)])


#класс проходов
class Passage_Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(passage_tiles_group, all_sprites)
        self.image = passage_tiles_image[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


#класс других стен
class Destructible_Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(destructible_tiles_group, all_sprites)
        self.image = destructible_tiles_image[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        bad_coords.append([range(tile_width * pos_x - 32, tile_width * pos_x + 48),
                           range(tile_height * pos_y - 62, tile_height * pos_y + 2)])

    def destroying(self, *args):
        pass


#класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos = (pos_x, pos_y)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self):
        self.x = 0
        self.y = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.x = -10
        if key[pygame.K_RIGHT]:
            self.x = 10
        if key[pygame.K_DOWN]:
            self.y = 10
        if key[pygame.K_UP]:
            self.y = -10
        flag = True
        for i in bad_coords:
            if self.rect.x + self.x in i[0] and self.rect.y + self.y in i[1]:
                flag = False
        if self.rect.x + self.x > WIDTH - 48 or self.rect.x + self.x < 0:
            flag = False
        if self.rect.y + self.y > HEIGHT - 50 or self.rect.y + self.y < 0:
            flag = False
        if flag:
            self.rect.x += self.x
            self.rect.y += self.y

    def get_pos(self):
        return self.rect.x, self.rect.y


class Enemy(pygame.sprite.Sprite):
    pass


level = load_level(random_level())
player, level_x, level_y = generate_level(level)

start_screen()
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for destroy in destructible_tiles_group:
                Destructible_Tile.destroying(event)

    destructible_tiles_group.update()
    all_sprites.update()
    player_group.update()
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()

