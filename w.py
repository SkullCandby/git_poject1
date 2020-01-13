import pygame
import os
import sys

# Глобальные переменные
size = w, h = 1000, 1000
v = 10
tile_width = 71
tile_height = 114
wall_width = 39
wall_height = 112

ralf_height = 50
ralf_width = 100
ralf_follow_delay = 400
shoot_frequency = 4000

game_mode = 1  # Режим игры: 0 - подготовка, 1 - активная фаза

BULLET_TIMER = 1

# События по таймеру
MOVED_LEFT = 10
MOVED_RIGHT = 15
MOVED_UP = 20
MOVED_DOWN = 25
SHOOT_ON = 30

hp = 3


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 200, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Persona(pygame.sprite.Sprite):
    def moveLeft(self):
        if self.rect.x - 70 > 244:
            self.rect.x -= 71

    def reachLeft(self):
        return not self.rect.x - 70 > 244

    def moveRight(self):
        if self.rect.x + 70 < 691:
            self.rect.x += 71

    def reachRight(self):
        return not self.rect.x + 70 < 691

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
        self.rect = self.image.get_rect().move(680, 603)
        self.ralf_way = load_level('ralf_map.txt')
        self.ralf_line = 5
        self.ralf_start_x = 5
        self.front_flag = True
        self.set = set()
        self.v = 114
    def breakWindow(self, window_status):
        window_status1 = window_status[-1::-1]
        print(window_status1)
        if window_status1 == '%':
            Tile('damaged_window', ((ralf.rect.x - 200) // 71) * 71, (ralf.rect.y // 114) * 114)
            print(((ralf.rect.x - 200) // 71) * 71, (ralf.rect.y // 114) * 114)
        elif window_status1 == '#':
            print(341441561)

    def init_ralf(self):
        ralf_way = lvl[-1::-1]
        # Инициализируем уровень - Ральф пробегаем по всем окнам и ломает некоторые
        for y in range(len(ralf_way) - 1):
            if y % 2 == 0:
                row = list(ralf_way[y])
                row = row[-1::-1]
                z = 0
                while not ralf.reachLeft():
                    ralf.breakWindow(row[z])
                    self.moveLeft()
                    z += 1
                    ralf_sprite.draw(screen)
                    clock.tick(10)
                    pygame.display.flip()
            else:
                row = list(ralf_way[y])
                z = 0
                while not ralf.reachRight():
                    ralf.breakWindow(row[z])
                    self.moveRight()
                    z += 1
                    ralf_sprite.draw(screen)
                    clock.tick(10)
                    pygame.display.flip()
            self.moveUp()
            ralf_sprite.draw(screen)
            clock.tick(10)
            pygame.display.flip()

    def shoot(self):

        bullet1 = Bullet()
        # bullet2 = Bullet()
        all_sprites.add(bullet1)
        # all_sprites.add(bullet2)
        print(pygame.sprite.spritecollideany(bullet1, player_group))
    ''' def damage(self):
        global hp
        if pygame.sprite.spritecollideany(bullet1, player_group):
            hp -= 1
'''


'''            hp -= 1
            print(hp)'''


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
        self.hp = 0

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


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(bullet_group)
        self.image = pygame.transform.scale(load_image('bullet.jpg'), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = ralf.rect.x + int(ralf_width / 2) - 8
        self.rect.y = ralf.rect.y + ralf_height + 1

    def update(self):
        self.rect.y += 3

class lvl_class:

    def __init__(self, _lvl):
        self.lvl = _lvl
        self.flag = 0
        self.counter = 0

    def check_lvl(self):
        stroka = ''
        for i in range(len(self.lvl)):
            stroka += self.lvl[i]
        if stroka == '(......)(......)(......)(......)(......)(@...&.)':
            return True


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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    global flag_screen
    while flag_screen:
        fon = pygame.transform.scale(load_image('menu.png'), (w, h))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                print(event)
                flag_screen = flag_screen and False
        pygame.display.flip()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    lst = list(map(lambda x: x.ljust(max_width, '.'), level_map))[:6]
    return lst


def move_lvl(main_sprite):
    rect_lst = []
    # level_x, level_y = generate_level2(load_level('ralf_map.txt'))
    for sprite in main_sprite:
        rect_lst.append(sprite.rect.y)
        sprite.rect.y = sprite.rect.y + 114
        pygame.time.delay(10)
        if min(rect_lst) == 1140:
            return True


def generate_level(level):
    ralf, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('damaged_window', x, y)
            if level[y][x] == '@':
                Tile('full_window', x, y)
            elif level[y][x] == '|':
                Tile('wall2', x, y)
            elif level[y][x] == '%':
                Tile('nefull_window', x, y)
            elif level[y][x] == '.':
                Tile('full_window', x, y)
            elif level[y][x] == ')':
                Tile('r_wall', x, y)
            elif level[y][x] == '(':
                Tile('l_wall', x, y)
            elif level[y][x] == '&':
                #  print(x, y)
                Tile('full_window', x, y)
                ralf = Ralf('ralf')
    return x, y, ralf


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

'''
def load_ralf_way(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    lst = list(map(lambda x: x.ljust(max_width, '.'), level_map))[7:]
    return lst
'''

pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# Создаю словарь для используемых изображений
tile_images = {'r_wall': load_image('right_wall.jpg'),
               'l_wall': load_image('left_wall.jpg'),
               'full_window': load_image('full_okno.jpg'),
               'damaged_window': load_image('damaged_okno.jpg'),
               'nefull_window': load_image('nefull_okno.jpg'),
               'ralf': load_image('ralf_1.png', color_key=-1),
               'bullet': load_image('bullet.jpg')}

# Создаю спрайты: игровое поле = Дом, Ральфа, Феликса, бомбочки и спрайт для всех обьектов
tiles_group = pygame.sprite.Group()
ralf_sprite = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Загружаю уровень игры из файла
lvl = load_level('ralf_map.txt')

# Инициализирую переменные
flag_screen = True
text_flag = True
running = True
hh = 684

# Создаю объекты игры
level = lvl_class(lvl)
fon = load_image('earth.jpg')
level_x, level_y, ralf = generate_level(load_level('ralf_map.txt'))
game_mode = 0
player = Felix(load_image("felix_move_spritelist.png", color_key=-1), 2, 1, 295, 615, lvl)

all_sprites.add(ralf)
all_sprites.add(player)

#
screen.fill((0, 0, 0))
tiles_group.draw(screen)
screen.blit(fon, (0, hh))
ralf.init_ralf()
game_mode = 1
# Включаю режим стрельбы
pygame.time.set_timer(SHOOT_ON, shoot_frequency)

# Игровой цикл
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOVED_LEFT:
            ralf.moveLeft()
            if game_mode == 1:
                ralf.shoot()
            pygame.time.set_timer(MOVED_LEFT, 0)
        elif event.type == MOVED_RIGHT:
            ralf.moveRight()
            if game_mode == 1:
                ralf.shoot()
            pygame.time.set_timer(MOVED_RIGHT, 0)
        elif event.type == MOVED_UP:
            if game_mode == 1:
                ralf.shoot()
            pygame.time.set_timer(MOVED_UP, 0)
        elif event.type == MOVED_DOWN:
            if game_mode == 1:
                ralf.shoot()
            pygame.time.set_timer(MOVED_DOWN, 0)
        elif event.type == SHOOT_ON:
            if game_mode == 1:
                ralf.shoot()

        if keys[pygame.K_LEFT]:
            player.moveLeft()
            pygame.time.set_timer(MOVED_LEFT, ralf_follow_delay)
        elif keys[pygame.K_RIGHT]:
            player.moveRight()
            pygame.time.set_timer(MOVED_RIGHT, ralf_follow_delay)
        elif keys[pygame.K_UP]:
            pygame.time.set_timer(MOVED_UP, ralf_follow_delay)
            player.moveUp()
        elif keys[pygame.K_DOWN]:
            pygame.time.set_timer(MOVED_DOWN, ralf_follow_delay)
            player.moveDown()
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.fix(player.rect.x, player.rect.y)
            print(pygame.mouse.get_pos())
            '''print(len(lvl_class.dd))'''

    screen.fill((0, 0, 0))
    '''start_screen()'''
    if flag_screen:
        # Рисуем игровое поле = Дом
        tiles_group.draw(screen)
        # Рисуем Феликса
        player_group.draw(screen)
        # Рисуем  Ральфа
        ralf_sprite.draw(screen)
        # Рисуем бомбочку
        bullet_group.draw(screen)
        screen.blit(fon, (0, hh))
        #  ralf.damage()
        all_sprites.update()

        lvl_check_flag = level.check_lvl()
        if lvl_check_flag:
            # draw_text()
            player.next_lvl()
            move_lvl(tiles_group)
            # move_lvl2(tiles_group2)
            hh += 114
            # screen.blit(load_image('game_over.jpg'), (0, 0))
        clock.tick(20)
        pygame.display.flip()
pygame.quit()
