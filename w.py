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

flag_moove = True
def terminate():
    pygame.quit()
    sys.exit()


class AnimatedSprite(pygame.sprite.Sprite):
    player_move_flag = 1
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        '''while AnimatedSprite.player_move_flag:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)

            self.image = self.frames[self.cur_frame]'''



flag = True
tile_images = {'r_wall': load_image('right_wall.jpg'),
               'l_wall': load_image('left_wall.jpg'),
               'full_window': load_image('full_okno.jpg'),
               'damaged_window': load_image('damaged_okno.jpg'),
               'nefull_window': load_image('nefull_okno.jpg')}
player_image1 = load_image('ralf_2.gif')
player_image = pygame.transform.scale(player_image1, (187, 87))

tile_width = 71
tile_height = 114
wall_width = 39
wall_height = 112
player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y


class Player(pygame.sprite.Sprite):
    player_move_flag = True
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        # self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.rect.x = 422
        self.rect.y = 501
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('nefull_window', x, y)
            elif level[y][x] == '@':
                player = AnimatedSprite(load_image("felix_move_spritelist.png"), 3, 1, 697, 475)
                Tile('full_window', x, y)
                '''new_player = Player(x, y)'''
            elif level[y][x] == '|':
                Tile('wall2', x, y)
            elif level[y][x] == '%':
                Tile('damaged_window', x, y)
            elif level[y][x] == '.':
                Tile('full_window', x, y)
            elif level[y][x] == ')':
                Tile('r_wall', x, y)
            elif level[y][x] == '(':
                Tile('l_wall', x, y)

    return x, y


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


fon = load_image('earth.jpg')

level_x, level_y = generate_level(load_level('ralf_map.txt'))
player = AnimatedSprite(load_image("felix_move_spritelist.png"), 2, 1, 697, 475)
'''player.rect.x = 486
player.rect. = 561'''
camera = Camera()
running = True
hh = 640
clock = pygame.time.Clock()
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if pygame.sprite.collide_mask(player_group, tiles_group):
            if keys[pygame.K_LEFT]:
                player.rect.x -= 70
            elif keys[pygame.K_RIGHT]:
                AnimatedSprite.player_move_flag = True
                player.update()
                player.rect.x += 70
                AnimatedSprite.player_move_flag = False
            elif keys[pygame.K_UP]:
                hh += 114
                player.rect.y -= 114
            elif keys[pygame.K_DOWN]:
                hh -= 114
                player.rect.y += 114
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(pygame.mouse.get_pos())
    screen.fill((0, 0, 0))
    # start_screen()
    camera.update(player)

    tiles_group.draw(screen)
    all_sprites.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    player_group.draw(screen)

    screen.blit(fon, (0, hh))
    pygame.time.delay(150)
    pygame.display.flip()
pygame.quit()
