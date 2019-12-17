import pygame
import os
import sys

pygame.init()
size = w, h = 1000, 1000
screen = pygame.display.set_mode(size)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    print(list(map(lambda x: x.ljust(max_width, '.'), level_map)))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


flag = True


def start_screen():
    global flag
    while flag:
        fon = pygame.transform.scale(load_image('fon.jpg'), (w, h))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                flag = flag and False
        pygame.display.flip()


tile_images = {'wall': load_image('dom1.jpg')}
player_image1 = load_image('ralf_1.png')
player_image = pygame.transform.scale(player_image1, (-1000, +50))

tile_width = 424
tile_height = 114
player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('wall', x, y)
                new_player = Player(x, y)

    return new_player, x, y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - w // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - h // 2)


player, level_x, level_y = generate_level(load_level('ralf_map.txt'))
camera = Camera()
running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LEFT]:
            player.rect.x -= 10
        elif keys[pygame.K_RIGHT]:
            player.rect.x += 10
        elif keys[pygame.K_UP]:
            player.rect.y -= 10
        elif keys[pygame.K_DOWN]:

            player.rect.y += 10
            print(player.rect.x, player.rect.y)

    screen.fill((0, 0, 0))
    start_screen()
    camera.update(player)
    all_sprites.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    pygame.display.flip()
pygame.quit()
