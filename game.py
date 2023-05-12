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
            'game_over': pygame.image.load(path+'graphics\\game_over.png')
        }

frame = Frame()

class Coin:
    def __init__(self, pos):
        #self.pos = [random.randint(0, 960), random.randint(0, 540)]
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
        if self.is_friendly:  # check collisions with enemy
            for entity in map_data:
                if entities_overlap(self.pos, (20, 20), (entity[0], entity[1]), (entity[2], entity[3])):
                    return True
        else:
            if entities_overlap(self.pos, (20, 20), player.pos, (40, 40)):
                if not player.god_mode:
                    player.hp -= 1
                blood_flash.flash()
                return True

        #if the bullet is not in frame, delete it
        if not entities_overlap(self.pos, (20, 20), (0, 0,), frame.size):
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
        self.coin_drop_chance = 1
        self.attack_type = attack_type  # 'hit' or 'shoot'
        self.frames_since_last_attack = 0

    def move(self):
        if self.behaviour == 'charge':
            # charge right at the player
            direction = math.atan2(player.pos[1] - self.pos[1], player.pos[0] - self.pos[0])

            to_move_x = math.cos(direction) * self.vel
            to_move_y = math.sin(direction) * self.vel

        elif self.behaviour == 'clueless':
            # just walkin' around
            if self.walk_queue == None:
                to_move_x, to_move_y = 0, 0
                if random.random() < 0.007:  # 0.7% chance
                    direction = random.random() * 2 * math.pi
                    self.walk_queue = [math.cos(direction) * self.vel, math.sin(direction) * self.vel, random.randint(30, 120)] 
            else:
                to_move_x, to_move_y = self.walk_queue[0], self.walk_queue[1]
                self.walk_queue[2] -= 1
                if self.walk_queue[2] == 0:
                    self.walk_queue = None

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



        '''
        if to_move_x < 0 and not all([not (entity[0] - self.size < self.pos[0] < entity[2] + entity[0] + to_move_x and
            entity[1] - self.size < self.pos[1] < entity[3] + entity[1]) for entity in map_data]):
            to_move_x = 0
        
        if to_move_x > 0 and not all([not (entity[0] - self.size - to_move_x < self.pos[0] < entity[2] + entity[0] and
            entity[1] - self.size < self.pos[1] < entity[3] + entity[1]) for entity in map_data]):
            to_move_x = 0

        if to_move_y < 0 and not all([not (entity[1] - self.size < self.pos[1] < entity[3] + entity[1] + to_move_y and
            entity[0] - self.size < self.pos[0] < entity[2] + entity[0]) for entity in map_data]):
            to_move_y = 0

        if to_move_y > 0 and not all([not (entity[1] - self.size - to_move_y < self.pos[1] < entity[3] + entity[1] and
            entity[0] - self.size < self.pos[0] < entity[2] + entity[0]) for entity in map_data]):
            to_move_y = 0
        '''
        
        self.pos[0] += to_move_x
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


class Player:
    def __init__(self):
        self.pos = [600, 300]
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
    #print(direction)

with open(path+'data\\map_data.json') as file:
    map_data = json.load(file)


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


enemies.append(Enemy(pos=[200, 200], behaviour='long-distance', attack_type='shoot'))



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
        elif event.type == 769:
            current_keydowns.remove(event.unicode)
        elif event.type == 1024:
            mouse_pos = event.pos
        elif event.type == 1025:
            shoot()

    to_move = player.vel
    if sum([int(letter in current_keydowns) for letter in ['w', 'a', 's', 'd']]) > 1:  # if moving diagonally
        to_move *= 1/math.sqrt(2)

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
    #pygame.draw.line(frame.screen, (0, 0, 0), mouse_pos, (player.pos[0]+20, player.pos[1]+20))

    blood_flash.update()
    hp_bar.update()
    coin_count.update()

    '''
    if random.random() < intensity_factor:
        pos = [random.randint(0, 960), random.randint(0, 540)]
        #behaviour = 'charge' if random.random() < 0.6 else 'clueless'
        behaviour = 'long-distance'
        enemies.append(Enemy(pos=pos, behaviour=behaviour, attack_type='shoot'))
    '''

    print(enemies_spawned_this_wave, current_wave * 3 +5)
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

        enemy_sets = [['long-distance', 'shoot'], ['charge', 'hit']]
        if random.random() < 0.4 * math.e**(-0.1*current_wave) + 0.3:
            enemy_type = 1
        else:
            enemy_type = 0
        enemies.append(Enemy(pos=pos, behaviour=enemy_sets[enemy_type][0], attack_type=enemy_sets[enemy_type][1]))
        enemies_spawned_this_wave += 1

    if enemies_spawned_this_wave == current_wave * 3 + 5 and len(enemies) == 0: #reset wave
        print('resetinn wave')
        current_wave += 1
        enemies_spawned_this_wave = 0


    if player.hp < 1:
        frame.screen.blit(frame.images['game_over'], (0, 0))


    pygame.display.flip()
    clock.tick(60)

    #print(1 / (time.perf_counter() - timeStamp))
