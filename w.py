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


class Felix(pygame.sprite.Sprite):
    player_move_flag = 1
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group)
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
        '''while AnimatedSprite.player_move_flag:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)

            self.image = self.frames[self.cur_frame]'''


horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


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
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('nefull_window', x, y)
            elif level[y][x] == '@':
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


'''Border(42, 666, 42, 4)
Border(42, 4, 522, 4)
Border(522, 4, 522, 666)
Border(522, 666, 42, 666)'''
fon = load_image('earth.jpg')
# status = pygame.sprite.spritecollide(all_sprites, tiles_group, True)
# print(status)
level_x, level_y = generate_level(load_level('ralf_map.txt'))
player = Felix(load_image("felix_move_spritelist.png"), 2, 1, 93, 615)
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
        # if pygame.sprite.spritecollide(player_group, tiles_group, True):
        if keys[pygame.K_LEFT]:
            if player.rect.x - 70 > 44:
                player.rect.x -= 70
        elif keys[pygame.K_RIGHT]:
            player.update()
            if player.rect.x + 70 < 491:
                player.rect.x += 70
        if keys[pygame.K_UP]:
            hh += 114
            if player.rect.y - 114 > 0:
                player.rect.y -= 114
        elif keys[pygame.K_DOWN]:
            hh -= 114
            if player.rect.y + 114 < 665:
                player.rect.y += 114
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())
    screen.fill((0, 0, 0))
    # start_screen()


    tiles_group.draw(screen)

    for sprite in all_sprites:
        camera.apply(sprite)
    player_group.draw(screen)

    screen.blit(fon, (0, 666))
    camera.update(player)
    pygame.display.flip()
pygame.quit()
