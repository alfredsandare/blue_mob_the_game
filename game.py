import pygame
import time
import json
import random
import math
from copy import copy

pygame.init()

path = __file__[:-7]
print(path)

class Frame:
    def __init__(self):
        self.size = (960, 540)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Game')

        self.images = {
            'bg': pygame.image.load(path+'graphics\\bg.png'),
            'player': pygame.image.load(path+'graphics\\player.png'),
            'coin': pygame.image.load(path+'graphics\\coin.png'),
            'bullet': pygame.image.load(path+'graphics\\bullet.png'),
            'bullet2': pygame.image.load(path+'graphics\\bullet2.png'),
            'enemy1': pygame.image.load(path+'graphics\\enemy1.png'),
            'enemy2': pygame.image.load(path+'graphics\\enemy2.png'),
            'game_over': pygame.image.load(path+'graphics\\game_over.png'),
            'purchase_bar': pygame.image.load(path+'graphics\\purchase_bar.png')
        }

frame = Frame()

class Coin:
    def __init__(self, pos):
        self.pos = pos

    def check_collision(self):
        return entities_overlap(self.pos, (20, 20), player.pos, (40, 40))


class Bullet:
    def __init__(self, direction, pos, is_friendly=True):
        self.pos = pos
        self.direction = direction  # angle in radians
        self.is_friendly = is_friendly

    def move(self):
        self.pos[1] += 10 * math.sin(self.direction) * [1, -1][self.is_friendly]
        self.pos[0] += 10 * math.cos(self.direction)

    def check_collision(self):
        # check collision with walls
        for entity in map_data:
            if entities_overlap(self.pos, (20, 20), (entity[0], entity[1]), (entity[2], entity[3])):
                return True

        # for enemy bullets, check collision with player
        if not self.is_friendly:
            if entities_overlap(self.pos, (20, 20), player.pos, (40, 40)):
                if not player.god_mode:
                    player.hp -= 1
                blood_flash.flash()
                return True

        #if the bullet is not in frame, delete it
        if not entities_overlap(self.pos, (20, 20), (0, 0), frame.size):
            return True
        return False


class Enemy:
    def __init__(self, pos=[0, 0], behaviour='charge', texture='enemy1', attack_type='hit'):
        self.pos = pos
        self.behaviour = behaviour
        self.walk_queue = None
        self.texture = texture
        self.size = 40
        self.vel = 1.5
        self.hp = 3
        self.coin_drop_chance = 0.8
        self.attack_type = attack_type  # 'hit' or 'shoot'
        self.frames_since_last_attack = 0

    def move(self):
        if self.behaviour == 'charge':
            # charge right at the player
            direction = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0])

            to_move_x = math.cos(direction) * self.vel
            to_move_y = math.sin(direction) * self.vel

        

        elif self.behaviour == 'long-distance':
            # always trying to be between 200-300 pixels from the player

            if self.walk_queue == None:
                to_move_x, to_move_y = 0, 0
                distance_to_player = math.sqrt((self.pos[0] - player.pos[0])**2 + (self.pos[1] - player.pos[1])**2)
                if distance_to_player < 200:  # walk away from the player
                    direction = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0]) + math.pi
                    self.walk_queue = [math.cos(direction) * self.vel, math.sin(direction) * self.vel, random.randint(30, 120)] 
                elif distance_to_player > 400:  # walk towards the player
                    direction = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0])
                    self.walk_queue = [math.cos(direction) * self.vel, math.sin(direction) * self.vel, random.randint(30, 120)]
                else:
                    if random.random() < 0.005:
                        direction = random.random() * 2 * math.pi
                        self.walk_queue = [math.cos(direction) * self.vel, math.sin(direction) * self.vel, random.randint(30, 120)] 

            else:
                to_move_x, to_move_y = self.walk_queue[0], self.walk_queue[1]
                self.walk_queue[2] -= 1
                if self.walk_queue[2] == 0:
                    self.walk_queue = None

        # move the enemy if there are no walls in the way
        if to_move_x < 0 and (all([not (entity[0] - 40 < self.pos[0] < entity[2] + entity[0] + to_move and
            entity[1] - 40 < self.pos[1] < entity[3] + entity[1]) for entity in map_data]) or self.pos[0] > frame.size[0] - 40):
            self.pos[0] += to_move_x
    
        if to_move_x > 0 and (all([not (entity[0] - 40 - to_move < self.pos[0] < entity[2] + entity[0] and
            entity[1] - 40 < self.pos[1] < entity[3] + entity[1]) for entity in map_data]) or self.pos[0] < 0):
            self.pos[0] += to_move_x

        if to_move_y < 0 and (all([not (entity[1] - 40 < self.pos[1] < entity[3] + entity[1] + to_move and
            entity[0] - 40 < self.pos[0] < entity[2] + entity[0]) for entity in map_data]) or self.pos[1] > frame.size[1] -40):
            self.pos[1] += to_move_y

        if to_move_y > 0 and (all([not (entity[1] - 40 - to_move < self.pos[1] < entity[3] + entity[1] and
            entity[0] - 40 < self.pos[0] < entity[2] + entity[0]) for entity in map_data]) or self.pos[1] < 0):
            self.pos[1] += to_move_y
    

    def check_collision(self):
        for i, bullet in enumerate(bullets):
            if bullet.is_friendly:
                if entities_overlap(self.pos, (40, 40), bullet.pos, (20, 20)):
                    del bullets[i]
                    return True
        return False

    def attack(self):
        if self.attack_type == 'hit':
            distance_to_player = math.sqrt((self.pos[0] - player.pos[0])**2 + (self.pos[1] - player.pos[1])**2)
            if distance_to_player < 60 and self.frames_since_last_attack > 60:
                if not player.god_mode:
                    player.hp -= 1
                self.frames_since_last_attack = 0
                blood_flash.flash()
        else:  # shoot
            if self.frames_since_last_attack > 120:
                direction_to_player = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0])
                bullets.append(Bullet(direction_to_player, copy(self.pos), is_friendly=False))
                self.frames_since_last_attack = 0

    def blit_id(self, id):
        # for debug. Puts the enemy id number on the enemy
        font = pygame.font.SysFont('arial', 32)
        text = str(id)
        rendered_text = font.render(text, True, (255, 255, 255))
        #size = font.size(text)
        frame.screen.blit(rendered_text, self.pos)


class Player:
    def __init__(self):
        self.pos = [460, 250]
        self.size = 40
        self.vel = 3
        self.hp = 20
        self.coins = 0
        self.god_mode = False

player = Player()


class BloodFlash:
    def __init__(self):
        self.image = pygame.image.load(path+'graphics\\blood_flash.png')
        self.gradient = 0

    def flash(self):
        self.gradient = 250

    def update(self):
        if self.gradient > 0:
            self.gradient -= 10
            self.image.set_alpha(self.gradient)
            frame.screen.blit(self.image, (0, 0))

blood_flash = BloodFlash()

class HPBar:
    def __init__(self):
        self.bar_image = pygame.image.load(path+'graphics\\hp_bar.png')
        self.heart_image = pygame.image.load(path+'graphics\\hp_heart.png')
        self.pos = (20, 10)

    def update(self):
        frame.screen.blit(self.bar_image, self.pos)
        pygame.draw.rect(frame.screen, (237, 28, 36), pygame.Rect(self.pos[0]+3, self.pos[1]+3, 244 * player.hp/20, 24))
        frame.screen.blit(self.heart_image, (self.pos[0]-15, self.pos[1]-5))

hp_bar = HPBar()

class CoinCount:
    def __init__(self):
        self.coin_image = pygame.image.load(path+'graphics\\coin_big.png')
        self.pos = (5, 55)

    def update(self):
        frame.screen.blit(self.coin_image, self.pos)
        font = pygame.font.SysFont('arial', 32)
        text = font.render(str(player.coins), True, (255, 255, 255))
        height = font.size(str(player.coins))[1]
        frame.screen.blit(text, (self.pos[0]+50, self.pos[1]-height/2+20))

coin_count = CoinCount()


class WaveCount:
    def __init__(self):
        self.pos = (950, 10) #top-right corner is the anchor point

    def update(self):
        font = pygame.font.SysFont('arial', 32)
        text = f'{current_wave+1}{get_number_suffix(current_wave+1)} wave'
        rendered_text = font.render(text, True, (255, 255, 255))
        size = font.size(text)
        frame.screen.blit(rendered_text, (self.pos[0]-size[0], self.pos[1]))

wave_count = WaveCount()

class Turret:
    def __init__(self, pos=[0, 0]):
        self.pos = pos
        self.timer = 600  # how many frames left until turret is destroyed
        self.frames_since_last_attack = 0
        self.shoot_frequency = 30
        self.closest_enemy = -1
        self.fg_image_angle = 45

        self.bg_image = pygame.image.load(path+'graphics\\turret_bg.png')
        self.fg_image = pygame.image.load(path+'graphics\\turret_fg.png')

    def update(self, blit_target_id=False):
        frame.screen.blit(self.bg_image, self.pos)
        rotated_fg_image = pygame.transform.rotate(self.fg_image, self.fg_image_angle+180)
        rect = rotated_fg_image.get_rect(center=self.fg_image.get_rect(topleft=(self.pos[0]+7, self.pos[1]+7)).center)
        frame.screen.blit(rotated_fg_image, rect) #(self.pos[0]+7, self.pos[1]+7))

        pygame.draw.rect(frame.screen, (0, 0, 0), pygame.Rect(self.pos[0]+2, self.pos[1]+44, 36, 6))
        pygame.draw.rect(frame.screen, (237, 28, 36), pygame.Rect(self.pos[0]+3, self.pos[1]+45, 34 * self.timer/600, 4))

        if len(enemies) > 0:
            #find the closest enemy
            smallest_distance = 999
            for i, enemy in enumerate(enemies):
                distance_to_enemy = math.sqrt((enemy.pos[0]-self.pos[0])**2 + (enemy.pos[1]-self.pos[1])**2)
                if distance_to_enemy < smallest_distance and 0 < enemy.pos[0] < frame.size[0] and 0 < enemy.pos[1] < frame.size[1]:
                    smallest_distance = distance_to_enemy
                    self.closest_enemy = i

            #calculate the angle
            target_pos = enemies[self.closest_enemy].pos
            pos = [self.pos[0]+20, self.pos[1]+20]
            shoot_direction = math.atan((pos[1] - (target_pos[1]+20))/((target_pos[0]+20) - pos[0]))
            if target_pos[0]+20 < pos[0]:
                shoot_direction += math.pi
            self.fg_image_angle = math.degrees(shoot_direction)

            #shoot the closest enemy
            if self.frames_since_last_attack >= self.shoot_frequency and len(enemies) > 0:
                bullets.append(Bullet(shoot_direction, pos))
                self.frames_since_last_attack = 0
            else:
                self.frames_since_last_attack += 1


        if blit_target_id:
            # for debug. Puts the enemy id number on the enemy
            font = pygame.font.SysFont('arial', 32)
            text = str(self.closest_enemy)
            rendered_text = font.render(text, True, (255, 255, 255))
            #size = font.size(text)
            frame.screen.blit(rendered_text, self.pos)

        self.timer -= 1


turrets = []


def entities_overlap(coords1, size1, coords2, size2):
    ''' There are two rectangles, 1 and 2.
    Given one coordinate and the size of the first rectangle, we get 4 coords.
    If any of those coords are within the second rectangle, return True.'''
    coords1 = [coords1, [coords1[0]+size1[0], coords1[1]], [coords1[0], coords1[1]+size1[1]], [coords1[0]+size1[0], coords1[1]+size1[1]]]
    for coords in coords1:
        if coords2[0] < coords[0] <= coords2[0] + size2[0] and coords2[1] < coords[1] <= coords2[1] + size2[1]:
            return True
    return False

def shoot():
    direction = math.atan((player.pos[1] - (mouse_pos[1]-20))/((mouse_pos[0]-20) - player.pos[0]))
    if mouse_pos[0]-20 < player.pos[0]:
        direction += math.pi
    pos = [player.pos[0]+20, player.pos[1]+20]  # start at the player's position
    bullets.append(Bullet(direction, pos))

with open(path+'data\\map_data.json') as file:
    map_data = json.load(file)

def get_number_suffix(n):
    ''' returns the english suffix from any given positive integer '''
    return ['st', 'nd', 'rd'][n-1] if 0 < n < 4 else 'th'

coins = []
bullets = []
enemies = []
current_keydowns = []
mouse_pos = ()
clock = pygame.time.Clock()
timeStamp = 0
intensity_factor = 0.01  # chance of spawning a new enemy per frame
current_wave = 0
enemies_spawned_this_wave = 0



while 1:

    timeStamp = time.perf_counter()

    for event in pygame.event.get():
        #print(event)
        if event.type == 768:
            current_keydowns.append(event.unicode)
            if event.unicode == ' ':
                shoot()
            elif event.unicode == 'g':
                player.god_mode = not player.god_mode
            elif event.unicode == '1':
                if player.coins >= 10:
                    player.coins -= 10
                    player.hp += 10
                    if player.hp > 20:
                        player.hp = 20

            elif event.unicode == '2':
                turrets.append(Turret(pos=copy(player.pos)))

        elif event.type == 769:
            current_keydowns.remove(event.unicode)
        elif event.type == 1024:
            mouse_pos = event.pos
        elif event.type == 1025:
            shoot()

    to_move = player.vel
    if sum([int(letter in current_keydowns) for letter in ['w', 'a', 's', 'd']]) > 1:  # if moving diagonally
        to_move *= 1/math.sqrt(2)

    # only move the player if there are not any walls in the way
    if 'a' in current_keydowns and all([not (entity[0] - player.size < player.pos[0] < entity[2] + entity[0] + to_move and
        entity[1] - player.size < player.pos[1] < entity[3] + entity[1]) for entity in map_data]):
        player.pos[0] -= to_move
    
    if 'd' in current_keydowns and all([not (entity[0] - player.size - to_move < player.pos[0] < entity[2] + entity[0] and
        entity[1] - player.size < player.pos[1] < entity[3] + entity[1]) for entity in map_data]):
        player.pos[0] += to_move

    if 'w' in current_keydowns and all([not (entity[1] - player.size < player.pos[1] < entity[3] + entity[1] + to_move and
        entity[0] - player.size < player.pos[0] < entity[2] + entity[0]) for entity in map_data]):
        player.pos[1] -= to_move

    if 's' in current_keydowns and all([not (entity[1] - player.size - to_move < player.pos[1] < entity[3] + entity[1] and
        entity[0] - player.size < player.pos[0] < entity[2] + entity[0]) for entity in map_data]):
        player.pos[1] += to_move
    

    frame.screen.blit(frame.images['bg'], (0, 0))
    for entity in map_data:
        pygame.draw.rect(frame.screen, (0, 0, 0), pygame.Rect(*entity))

    coins_deleted = 0
    for i, coin in enumerate(coins):
        frame.screen.blit(frame.images['coin'], coin.pos)
        if coin.check_collision():
            del coins[i - coins_deleted]
            coins_deleted += 1
            player.coins += 1

    bullets_deleted = 0
    for i, bullet in enumerate(bullets):
        bullet.move()
        frame.screen.blit(frame.images['bullet' if bullet.is_friendly else 'bullet2'], bullet.pos)
        if bullet.check_collision():
            del bullets[i - bullets_deleted]
            bullets_deleted += 1

    enemies_deleted = 0
    for i, enemy in enumerate(enemies):
        enemy.move()
        enemy.frames_since_last_attack += 1
        enemy.attack()
        frame.screen.blit(frame.images[enemy.texture], enemy.pos)
        if enemy.check_collision():
            enemy.hp -= 1
            if enemy.hp == 0:
                if random.random() < enemy.coin_drop_chance:
                    coins.append(Coin(enemy.pos))
                del enemies[i - enemies_deleted]
                enemies_deleted += 1

    frame.screen.blit(frame.images['player'], player.pos)
    frame.screen.blit(frame.images['purchase_bar'], (360, 460))

    #ge spelaren en näsa
    #pygame.draw.line(frame.screen, (0, 0, 0), mouse_pos, (player.pos[0]+20, player.pos[1]+20))

    blood_flash.update()
    hp_bar.update()
    coin_count.update()
    wave_count.update()

    turrets_deleted = 0
    for i, turret in enumerate(turrets):
        turret.update()
        if turret.timer == 0:
            del turrets[i - turrets_deleted]

    if enemies_spawned_this_wave < current_wave * 3 + 5 and random.random() < intensity_factor:
        spawn_side = random.randint(0, 3)
        if spawn_side == 0:  # right side
            pos = [random.randint(960, 1060), random.randint(-100, 640)]
        elif spawn_side == 1:  # top side
            pos = [random.randint(-100, 1060), random.randint(-100, 0)]
        elif spawn_side == 2:  # left side
            pos = [random.randint(-100, 0), random.randint(-100, 640)]
        else:  # bottom side
            pos = [random.randint(-100, 1060), random.randint(540, 640)]

        enemy_sets = [['long-distance', 'shoot', 'enemy1'], ['charge', 'hit', 'enemy2']]
        if random.random() < 0.4 * math.e**(-0.1*current_wave) + 0.3:
            enemy_type = 1
        else:
            enemy_type = 0
        enemies.append(Enemy(pos=pos, behaviour=enemy_sets[enemy_type][0], attack_type=enemy_sets[enemy_type][1], texture=enemy_sets[enemy_type][2]))
        enemies_spawned_this_wave += 1

    if enemies_spawned_this_wave == current_wave * 3 + 5 and len(enemies) == 0: #reset wave
        current_wave += 1
        enemies_spawned_this_wave = 0
        intensity_factor *= 1.1


    if player.hp < 1:
        frame.screen.blit(frame.images['game_over'], (0, 0))


    pygame.display.flip()
    clock.tick(60)

    #print(1 / (time.perf_counter() - timeStamp))
