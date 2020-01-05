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
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'r_wall': load_image('right_wall.jpg'),
               'l_wall': load_image('left_wall.jpg'),
               'full_window': load_image('full_okno.jpg'),
               'damaged_window': load_image('damaged_okno.jpg'),
               'nefull_window': load_image('nefull_okno.jpg')}

tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

tiles_group2 = pygame.sprite.Group()
player_group2 = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 200, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


lvl = load_level('ralf_map.txt')

'''class Window:
    def __init__(self, lst, status):
        self.lvl = lst
        self.status = ''
    def compile(self):
        for i in range(len(self.lvl)):
            for j in range(len(self.lvl[i])):'''


class Felix(pygame.sprite.Sprite):
    player_move_flag = False

    def __init__(self, sheet, columns, rows, x, y, lvl):
        super().__init__(player_group)
        self.lvl = lvl
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        self.rect.x = x
        self.rect.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # while AnimatedSprite.player_move_flag:
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)

        self.image = self.frames[self.cur_frame]
        # Felix.player_move_flag = False

    def fix(self, pos_x, pos_y):
        lvl = self.lvl
        x = (pos_x - 200) // 71
        y = pos_y // 114
        if lvl[y][x] == '#':
            s = lvl[y]
            b = s[:x] + '%' + s[x + 1:]
            lvl[y] = b
            Tile('damaged_window', x, y)
        elif lvl[y][x] == '%':
            s = lvl[y]
            b = s[:x] + '.' + s[x + 1:]
            lvl[y] = b
            Tile('full_window', x, y)


    def next_lvl(self):
        player_group.empty()


class lvl_class:
    lst = []
    lst2 = lvl
    dd = {}

    def __init__(self, lvl):
        self.lvl = lvl
        self.flag = 0
        self.counter = 0

    '''def check_lvl(self, pos_x, pos_y):
        y = pos_x // 114
        x = pos_y - 200 // 71
        if self.lvl[y] == '(......)' or self.lvl[y] == '(@.....)':
            self.counter += 1
            lvl_class.dd[x, y, self.counter] = True
            lvl_class.lst.append(True)'''

    def check_lvl(self):
        stroka = ''
        for i in range(len(self.lvl)):
            stroka += self.lvl[i]
        if stroka == '(......)(......)(......)(......)(@.....)(......)':
            return True

def move_lvl(main_sprite):
    for sprite in main_sprite:
        sprite.rect.y = sprite.rect.y + 114
        pygame.time.delay(10)


flag = False
window_sprite = pygame.sprite.Group()

player_image1 = load_image('ralf_2.gif')
player_image = pygame.transform.scale(player_image1, (187, 87))

tile_width = 71
tile_height = 114
wall_width = 39
wall_height = 112
player = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('nefull_window', x, y)
            if level[y][x] == '@':
                Tile('full_window', x, y)
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


'''level2_x, level2_y = generate_level(load_level('ralf_map2.txt'))'''
level = lvl_class(lvl)
fon = load_image('earth.jpg')
level_x, level_y = generate_level(load_level('ralf_map.txt'))
print(level_x, level_y)
player = Felix(load_image("felix_move_spritelist.png"), 2, 1, 293, 615, lvl)
camera = Camera()
running = True
hh = 684
clock = pygame.time.Clock()
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LEFT]:
            if player.rect.x - 70 > 244:
                player.rect.x -= 70
        elif keys[pygame.K_RIGHT]:
            if player.rect.x + 70 < 691:
                player.rect.x += 70
        if keys[pygame.K_UP]:
            if player.rect.y - 114 > 0:
                player.rect.y -= 114
        elif keys[pygame.K_DOWN]:
            if player.rect.y + 114 < 665:
                player.rect.y += 114
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(level.check_lvl())
            player.fix(player.rect.x, player.rect.y)
            '''print(len(lvl_class.dd))'''
            print(lvl_class.dd)

    screen.fill((0, 0, 0))
    # start_screen()
    tiles_group.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    player_group.draw(screen)
    screen.blit(fon, (0, hh))
    camera.update(player)
    player.update()
    a = level.check_lvl()
    if a:
        player.next_lvl()
        move_lvl(tiles_group)
        hh += 114

        # screen.blit(load_image('game_over.jpg'), (0, 0))
    pygame.display.flip()

    # pygame.time.delay(250)
pygame.quit()
