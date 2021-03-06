import pygame, pygame.mixer
import os
import sys
import sqlite3
from pygame.locals import *
from operator import itemgetter

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

game_mode = 1  # Режим игры: 0 - пассивная фаза, 1 - активная фаза

BULLET_TIMER = 1

# События по таймеру
MOVED_LEFT = 10
MOVED_RIGHT = 15
MOVED_UP = 20
MOVED_DOWN = 25
SHOOT_ON = 30

HP = 3
POINTS = 0
level_map = None
NAME_FLAG = False


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 200, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(heart_sprite)
        self.image = load_image('heart.png', color_key=-1)
        self.rect = self.image.get_rect().move(x, y)


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
        return not self.rect.x + 70 < 611

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
        if window_status == '%':
            ralf.jump_ralf()
            tile = level_map[ralf.rect.y // 114][ralf.rect.x // 71 - 2]
            tile.image = tile_images['damaged_window']
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(10)
            pygame.display.flip()
        elif window_status == '#':
            ralf.jump_ralf()
            tile = level_map[ralf.rect.y // 114][ralf.rect.x // 71 - 2]
            tile.image = tile_images['damaged_window']
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(10)
            pygame.display.flip()
            ralf.jump_ralf()
            tile = level_map[ralf.rect.y // 114][ralf.rect.x // 71 - 2]
            tile.image = tile_images['empty_window']
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(10)
            pygame.display.flip()

    def init_ralf(self, lvl_ralf):
        ralf_way = lvl_ralf[-1::-1]
        # Инициализируем уровень - Ральф пробегаем по всем окнам и ломает некоторые
        for y in range(len(ralf_way) - 1):
            if y % 2 == 0:
                row = list(ralf_way[y])
                row = row[-1::-1]
                z = 0
                while not ralf.reachLeft():
                    z += 1
                    ralf.breakWindow(row[z])
                    self.moveLeft()
                    screen.fill((0, 0, 0))
                    tiles_group.draw(screen)
                    screen.blit(fon, (0, hh))
                    ralf_sprite.draw(screen)
                    clock.tick(10)
                    pygame.display.flip()
            else:
                row = list(ralf_way[y])

                z = 0
                while not ralf.reachRight():
                    z += 1
                    ralf.breakWindow(row[z])
                    self.moveRight()

                    screen.fill((0, 0, 0))
                    tiles_group.draw(screen)
                    screen.blit(fon, (0, hh))
                    ralf_sprite.draw(screen)
                    clock.tick(10)
                    pygame.display.flip()
            self.moveUp()
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(10)
            pygame.display.flip()

    def jump_ralf(self):
        for i in range(4):
            self.rect.y -= 10
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(20)
            pygame.display.flip()
        for j in range(4):
            self.rect.y += 10
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            screen.blit(fon, (0, hh))
            ralf_sprite.draw(screen)
            clock.tick(20)
            pygame.display.flip()

    def shoot(self):
        global game_mode
        if game_mode == 1:
            bullet1 = Bullet()
            # bullet2 = Bullet()
            all_sprites.add(bullet1)
            # all_sprites.add(bullet2)
            return bullet1


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
        self.mask = pygame.mask.from_surface(self.image)

    def moveUp(self):
        if self.rect.y - 114 > 114:
            super().moveUp()

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
        global POINTS
        lvl = self.lvl
        x = (pos_x - 200) // 71
        y = pos_y // 114
        if lvl[y][x] == '#':
            fix_sound.play()
            POINTS += 100
            s = lvl[y]
            b = s[:x] + '%' + s[x + 1:]
            lvl[y] = b
            tile = level_map[y][x]
            tile.image = tile_images['damaged_window']
        elif lvl[y][x] == '%':
            fix_sound.play()
            POINTS += 100
            s = lvl[y]
            b = s[:x] + '.' + s[x + 1:]
            lvl[y] = b
            tile = level_map[y][x]
            tile.image = tile_images['full_window']

    def next_lvl(self):
        player_group.empty()


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(bullet_group)
        self.image = pygame.transform.scale(load_image('bullet.png'), (20, 20))
        self.rect = self.image.get_rect()
        # Позиционирует вылет пули по центру низа Ральфа
        self.rect.x = ralf.rect.x + int(ralf_width / 2) - 8
        self.rect.y = ralf.rect.y + ralf_height + 1

    def update(self):
        self.rect.y += 3


class lvl_class:

    def __init__(self, _lvl):
        self.lvl = _lvl
        self.flag = 0
        self.counter = 0

    # Проверяет закончился уровень или нет
    def check_lvl(self):
        stroka = ''
        for i in range(len(self.lvl)):
            stroka += self.lvl[i]
        if stroka == '(......)(......)(......)(......)(......)(@...&.)':
            return True


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


# Рисует основное игровое поле (дом)
def generate_level(level):
    x, y = None, None
    map = []
    for y in range(len(level)):
        l = []
        for x in range(len(level[y])):
            if level[y][x] == '#':
                # Рисуем целое окно, которое сломает Ральф при инициализации
                l.append(Tile('full_window', x, y))
            if level[y][x] == '@':
                l.append(Tile('full_window', x, y))
            elif level[y][x] == '|':
                l.append(Tile('wall2', x, y))
            elif level[y][x] == '%':
                # Рисуем целое окно, которое сломает Ральф при инициализации
                l.append(Tile('full_window', x, y))
            elif level[y][x] == '.':
                l.append(Tile('full_window', x, y))
            elif level[y][x] == ')':
                l.append(Tile('r_wall', x, y))
            elif level[y][x] == '(':
                l.append(Tile('l_wall', x, y))
            elif level[y][x] == '&':
                l.append(Tile('full_window', x, y))
        map.append(l)
    return x, y, map


# Выводит окно для ввода имени игрока
def draw_text():
    global name
    if text_flag:
        font = pygame.font.Font(None, 50)
        text = font.render(f"{name}", 1, (0, 0, 0))
        pygame.draw.rect(screen, (0, 0, 0), (357, 255, 253, 176))
        pygame.draw.rect(screen, (128, 128, 128), (394, 313, 183, 63))
        pygame.draw.rect(screen, (51, 51, 51), (394, 313, 183, 63), 5)
        screen.blit(text, (407, 339))


def blit_text(surface, text, pos, font, color=pygame.Color('white')):
    words = [word.split(' ') for word in text.splitlines()]  # 2х уровнеый массив где каждая строка это список слов
    space = font.size(' ')[0]  # Ширина пробела
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Переопределяем х.
                y += word_height  # Начало новой строки.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Переставляем х.
        y += word_height  # Начало на новой строке.


game_over_flag = True


def game_over():
    global game_over_flag
    pygame.mixer.music.load('game_over_music.wav')
    pygame.mixer.music.play(1)
    while game_over_flag:
        fon = pygame.transform.scale(load_image('game_over.jpg'), (w, h))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                con.close()
                pygame.quit()
                sys.exit()
            elif keys[pygame.K_RETURN]:
                game_over_flag = game_over_flag and False
            elif keys[pygame.K_ESCAPE]:
                con.close()
                pygame.quit()
                sys.exit()
        pygame.display.flip()


done = True
lvl = None


# Прорисовываю экран начального меню
def menu():
    global lvl
    global done

    # Запускаю музыку
    pygame.mixer.music.load('zero.wav')
    pygame.mixer.music.play(-1)

    # Формирую таблицу лучших 10 результатов
    _names = cur.execute('''SELECT * FROM scores WHERE score > 0 ''').fetchall()  # Выборка из базы
    _names.sort(key=itemgetter(1))
    _names.reverse()
    _names = _names[:10]
    score_txt = ''
    name_txt = ''
    place_txt = ''

    for i in range(len(_names)):  # Наполняю списки
        name_txt += f'{_names[i][0]}\n'
        score_txt += f'{_names[i][1]}\n'
        place_txt += f'{i + 1}\n'
    font = pygame.font.Font(None, 50)
    placemant_txt = font.render("#    name         score", 1, (255, 255, 255))  # А это заголовок таблицы результатов

    while done:
        # Вывожу таблицу результатов
        fon = pygame.transform.scale(load_image('menu.png'), (w, h))
        screen.blit(fon, (0, 0))
        screen.blit(placemant_txt, (320, 250))
        blit_text(screen, name_txt, (370, 300), font)
        blit_text(screen, score_txt, (550, 300), font)
        blit_text(screen, place_txt, (320, 300), font)

        # Жду от пользователя выбор уровня
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                con.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = pygame.mouse.get_pos()
                print(coords)
                if coords[0] >= 820 and coords[0] <= 971:
                    if coords[1] >= 275 and coords[1] <= 380:
                        done = done and False
                        lvl = load_level('ralf_map.txt')
                    if coords[1] >= 408 and coords[1] <= 512:
                        done = done and False
                        print(123)
                        lvl = load_level('ralf_map2.txt')
                        print(lvl)
                    if coords[1] >= 550 and coords[1] <= 651:
                        done = done and False
                        lvl = load_level('ralf_map3.txt')
        pygame.display.flip()


# Перезапускаю игру и выставляю начальные установки
def restart():
    global HP
    global game_over_flag
    global done
    global level_map
    global NAME_FLAG
    global game_mode
    global minutes
    global seconds
    global milliseconds
    global lvl
    global text_flag
    global level
    global heart1
    global heart2
    global heart3
    global player
    global heart_lst
    global POINTS
    heart_lst = []
    heart_sprite.empty()
    player.next_lvl()
    level_x, level_y, level_map = generate_level(lvl)
    level = lvl_class(lvl)
    ralf.rect.x, ralf.rect.y = 680, 603
    player.rect.x, player.rect.y = 295, 615
    player = Felix(load_image("felix_move_spritelist.png", color_key=-1), 2, 1, 295, 615, lvl)
    bullet_group.empty()
    ralf.init_ralf(lvl)
    HP = 3
    POINTS = 0
    heart1 = Heart(860, 0)
    heart_lst.append(heart1)
    heart2 = Heart(916, 0)
    heart_lst.append(heart2)
    heart3 = Heart(972, 0)
    heart_lst.append(heart3)
    minutes = 0
    seconds = 0
    milliseconds = 0
    game_over_flag = True
    done = True
    NAME_FLAG = NAME_FLAG and False
    text_flag = False
    game_mode = 1


# Начало
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

# Создаю словарь для используемых изображений
tile_images = {'r_wall': load_image('right_wall.jpg'),
               'l_wall': load_image('left_wall.jpg'),
               'full_window': load_image('full_okno.jpg'),
               'damaged_window': load_image('damaged_okno.jpg'),
               'empty_window': load_image('empty_okno.jpg'),
               'ralf': load_image('ralf_1.png', color_key=-1),
               'bullet': load_image('bullet.png', color_key=-1)}

# Создаю спрайты: игровое поле = Дом, Ральфа, Феликса, бомбочки и спрайт для всех обьектов
tiles_group = pygame.sprite.Group()
ralf_sprite = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
heart_sprite = pygame.sprite.Group()
# Загружаю уровень игры из файла

heart_lst = []
# Инициализирую переменные
flag_screen = True
text_flag = True
running = True
hh = 684
# подключение к базе данных
con = sqlite3.connect('ralf_base.db')
cur = con.cursor()
name = ""
minutes = 0
seconds = 0
milliseconds = 0

# Инициирую звуки
hurt_sound = pygame.mixer.Sound('hit.wav')
fix_sound = pygame.mixer.Sound('fix_sound.wav')

# Создаю объекты игры
menu()
level = lvl_class(lvl)
fon = load_image('earth.jpg')
level_x, level_y, level_map = generate_level(lvl)
game_mode = 0
player = Felix(load_image("felix_move_spritelist.png", color_key=-1), 2, 1, 295, 615, lvl)
ralf = Ralf('ralf')
all_sprites.add(ralf)
all_sprites.add(player)

screen.fill((0, 0, 0))
tiles_group.draw(screen)
screen.blit(fon, (0, hh))
ralf.init_ralf(lvl)
game_mode = 1
# Включаю режим стрельбы
pygame.time.set_timer(SHOOT_ON, shoot_frequency)
bullet1 = ralf.shoot()

# Инициализация жизнией на экране в виде сердец
heart1 = Heart(860, 0)
heart_lst.append(heart1)
heart2 = Heart(916, 0)
heart_lst.append(heart2)
heart3 = Heart(972, 0)
heart_lst.append(heart3)

# Игровой цикл
myfont = pygame.font.SysFont("monospace", 25)
names = []

# Основной игровой цикл
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            con.close()
            pygame.quit()
            sys.exit()
        elif event.type == SHOOT_ON:
            if game_mode == 1:
                bullet1 = ralf.shoot()
        if event.type == KEYDOWN and NAME_FLAG:
            if event.unicode.isalpha():
                name += event.unicode
                if len(name) > 6:
                    name = name[:6]
            elif event.key == K_BACKSPACE:
                name = name[:-1]
            elif event.key == K_RETURN and game_mode == 0:
                names_and_scores = cur.execute('''SELECT * FROM scores WHERE score > 0 ''').fetchall()
                score = POINTS // (minutes * 60 + seconds)
                for i in range(len(names_and_scores)):
                    names.append(names_and_scores[i][0])
                if name not in names:
                    cur.execute('''INSERT INTO scores(name, score) VALUES(?, ?)''', (name, score))
                elif name in names and \
                        cur.execute('''SELECT score FROM scores WHERE name == ?''', (name,)).fetchall()[0][0] < POINTS:
                    cur.execute('''UPDATE scores
                                SET score = ?
                                WHERE name = ? ''', (score, name))
                con.commit()
                name = ""
                menu()
                restart()
        if keys[pygame.K_LEFT]:
            player.moveLeft()
            clock.tick(20)
            pygame.display.flip()
        elif keys[pygame.K_RIGHT]:
            player.moveRight()
            clock.tick(20)
            pygame.display.flip()
        elif keys[pygame.K_UP]:
            player.moveUp()
            clock.tick(20)
            pygame.display.flip()
        elif keys[pygame.K_DOWN]:
            player.moveDown()
            clock.tick(20)
            pygame.display.flip()
        if event.type == pygame.MOUSEBUTTONDOWN or keys[pygame.K_SPACE]:
            player.fix(player.rect.x, player.rect.y)

    screen.fill((0, 0, 0))
    if milliseconds > 1000:
        seconds += 1
        milliseconds -= 1000
    if seconds > 60:
        minutes += 1
        seconds -= 60
    timelabel = myfont.render(f'{minutes}:{seconds}', True, (255, 0, 0))
    screen.blit(timelabel, (0, 0))
    # Рисуем игровое поле = Дом
    tiles_group.draw(screen)
    heart_sprite.draw(screen)
    # Рисуем Феликса
    player_group.draw(screen)
    # Рисуем  Ральфа
    ralf_sprite.draw(screen)
    # Рисуем бомбочку
    bullet_group.draw(screen)
    screen.blit(fon, (0, hh))
    block_hit_list = pygame.sprite.spritecollide(player, bullet_group, True)
    if len(block_hit_list):
        hurt_sound.play()
        HP -= 1
        heart_lst[0].kill()
        del heart_lst[0]
        POINTS -= 50
        print(heart_lst)
    if HP == 0:
        game_over()
        menu()
        restart()

    # Ральф плавно следует за Феликсом
    distance = abs((player.rect.x + player.rect.w // 2) - (ralf.rect.x + ralf.rect.w // 2))
    if distance > 0:
        vector = ((player.rect.x + player.rect.w // 2) - (ralf.rect.x + ralf.rect.w // 2)) / distance
    else:
        vector = 0
    if distance > 20:
        v = 20
    else:
        v = distance
    ralf.rect.x += vector * v * clock.tick() / 10

    # Рисует все спрайты
    all_sprites.update()

    lvl_check_flag = level.check_lvl()
    if lvl_check_flag:
        # draw_text()
        game_mode = 0
        player.next_lvl()
        text_flag = True
        NAME_FLAG = True
        draw_text()
        done = True
    score_txt = myfont.render(f"score:{POINTS}", 1, (255, 0, 0))
    screen.blit(score_txt, (0, 25))
    pygame.display.flip()
    if game_mode == 1:
        milliseconds += clock.tick_busy_loop(60)
pygame.quit()
