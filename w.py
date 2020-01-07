import pygame
import os
import sys

pygame.init()
size = w, h = 1000, 1000
screen = pygame.display.set_mode(size)
v = 10
clock = pygame.time.Clock()


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
    lst = list(map(lambda x: x.ljust(max_width, '.'), level_map))[:6]
    return lst


'''
def load_ralf_way(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    lst = list(map(lambda x: x.ljust(max_width, '.'), level_map))[7:]
    return lst
'''

ralf_sprite = pygame.sprite.Group()
ralf_pic = load_image('mar.png')

tile_images = {'r_wall': load_image('right_wall.jpg'),
               'l_wall': load_image('left_wall.jpg'),
               'full_window': load_image('full_okno.jpg'),
               'damaged_window': load_image('damaged_okno.jpg'),
               'nefull_window': load_image('nefull_okno.jpg'),
               'ralf': load_image('ralf_1.png')}
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

tiles_group2 = pygame.sprite.Group()
player_group2 = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 200, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


lvl = load_level('ralf_map.txt')


class Persona(pygame.sprite.Sprite):
    def moveLeft(self):
        if self.rect.x - 70 > 244:
            self.rect.x -= 70

    def moveRight(self):
        if self.rect.x + 70 < 691:
            self.rect.x += 70

    def moveUp(self):
        if self.rect.y - 114 > 0:
            self.rect.y -= 114

    def moveDown(self):
        if self.rect.y + 114 < 665:
            self.rect.y += 114


class Ralf(Persona):
    move_flag = True

    def __init__(self, tile_type):
        super().__init__(ralf_sprite)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(509, 603)
        self.ralf_way = load_level('ralf_map.txt')
        self.ralf_line = 5
        self.ralf_start_x = 5
        self.front_flag = True
        self.set = set()
        self.v = 114

    def move_ralf(self):
        ralf_way = lvl[-1::-1]
        print(ralf_way)
        for y in range(len(ralf_way)):
            if '%' not in ralf_way[y] and '#' not in ralf_way[y]:
                self.rect.y -= self.v * clock.tick() / 1000
            if ralf_way[y].find('%') > -1 or ralf_way[y].find('#') > -1:
                # print(ralf_way[y].find('%'), ralf_way[y].find('#'), ralf_way[y], y)
                self.v = 0


'''    def move_ralf(self):
        if Ralf.move_flag:
            for y in range(len(self.ralf_way)):
                for x in range(len(self.ralf_way[y])):
                    if '#' in self.ralf_way[y]:
                        self.set.add(y)

                    elif '%' in self.ralf_way[y]:

                        self.set.add(y)
        lst = list(self.set)
        print(lst)
        for i in range(len(lvl)):
            while '%' not in lvl[i] and '#' not in lvl[i]:

                self.rect.y -= v * clock.tick() / 1000
        Ralf.move_flag = False'''

# pygame.time.delay(100)
'''print(load_ralf_way('ralf_map.txt'))'''
'''class Window:
    def __init__(self, lst, status):
        self.lvl = lst
        self.status = ''
    def compile(self):
        for i in range(len(self.lvl)):
            for j in range(len(self.lvl[i])):'''


class Felix(Persona):
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
        if stroka == '(......)(......)(......)(......)(......)(@...&.)':
            return True


def move_lvl(main_sprite):
    rect_lst = []
    for sprite in main_sprite:
        rect_lst.append(sprite.rect.x)
        sprite.rect.y = sprite.rect.y + 114
        pygame.time.delay(10)


tile_width = 71
tile_height = 114
wall_width = 39
wall_height = 112
player = None


def generate_level(level):
    ralf, x, y = None, None, None
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
            elif level[y][x] == '&':
                print(x, y)
                Tile('full_window', x, y)
                ralf = Ralf('ralf')
    return x, y, ralf


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


text_flag = True
'''def draw_text():
    global text_flag
    if text_flag:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 50)
        text = font.render("Уровень 1, сложность 2", 1, (100, 255, 100))
        text_x = w // 2 - text.get_width() // 2
        text_y = h // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))'''
level = lvl_class(lvl)
fon = load_image('earth.jpg')
level_x, level_y, ralf = generate_level(load_level('ralf_map.txt'))

'''ralf_x, ralf_y = generate_ralf_way(load_ralf_way('ralf_map.txt'))'''
'''print(ralf_x, ralf_y)'''
player = Felix(load_image("felix_move_spritelist.png"), 2, 1, 293, 615, lvl)
camera = Camera()
running = True
hh = 684

while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LEFT]:
            player.moveLeft()
        elif keys[pygame.K_RIGHT]:
            player.moveRight()
        if keys[pygame.K_UP]:
            player.moveUp()
        elif keys[pygame.K_DOWN]:
            player.moveDown()
        if event.type == pygame.MOUSEBUTTONDOWN:
            ralf.move_ralf()
            player.fix(player.rect.x, player.rect.y)
            print(pygame.mouse.get_pos())
            '''print(len(lvl_class.dd))'''

    screen.fill((0, 0, 0))
    # start_screen()
    tiles_group.draw(screen)
    for sprite in all_sprites:
        camera.apply(sprite)
    player_group.draw(screen)

    ralf_sprite.draw(screen)

    screen.blit(fon, (0, hh))
    camera.update(player)
    player.update()
    a = level.check_lvl()
    if a:
        # draw_text()
        player.next_lvl()
        move_lvl(tiles_group)
        hh += 114

        # screen.blit(load_image('game_over.jpg'), (0, 0))
    pygame.display.flip()

    # pygame.time.delay(250)
pygame.quit()
