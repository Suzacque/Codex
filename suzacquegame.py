import pygame
import sys
import math
import random

# Pygameの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("エンジェルアドベンチャー")

# 色の定義
SKY_BLUE = (135, 206, 250)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 128, 0)
BRICK_RED = (178, 34, 34)
GOLD = (255, 215, 0)
PINK = (255, 192, 203)
LIGHT_BROWN = (205, 133, 63)
CREAM = (255, 253, 208)
PEACH = (255, 218, 185)
HAIR_ORANGE = (255, 140, 90)
HAIR_DARK = (205, 92, 42)
LIGHT_SKY_BLUE_GRADIENT_TOP = (200, 230, 255)

MOUNTAIN_FAR = (170, 200, 230)
MOUNTAIN_MID = (120, 170, 150)
MOUNTAIN_NEAR = (80, 140, 100)
TREE_LEAF_LIGHT = (60, 180, 60)
TREE_LEAF_DARK = (40, 150, 40)
TREE_TRUNK = (100, 80, 60)

# ゲーム設定
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        try:
            loaded_image = pygame.image.load("suzacque.png")
        except pygame.error as e:
            print(f"Error loading player image 'suzacque.png': {e}")
            sys.exit()
            
        original_width = loaded_image.get_width()
        original_height = loaded_image.get_height()
        new_width = original_width // 10
        new_height = original_height // 10
        
        if new_width < 1: new_width = 1
        if new_height < 1: new_height = 1

        scaled_image = pygame.transform.smoothscale(loaded_image, (new_width, new_height))
        scaled_image.set_colorkey(CREAM) 
        self.image_orig = scaled_image.convert_alpha()
            
        self.image = self.image_orig
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.animation_counter = 0
        self.jump_animation = 0
        self.wing_flap = 0
        self.hair_flow = 0
        self.feathers = []
        
    def update(self, platforms, enemies, coins):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vel_x = -5
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vel_x = 5
            self.facing_right = True
        else:
            self.vel_x *= 0.8
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
            
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.jump_animation = 20
            for _ in range(5):
                self.feathers.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vel_x': random.uniform(-3, 3),
                    'vel_y': random.uniform(-5, -2),
                    'life': 30,
                    'rotation': random.uniform(0, 360)
                })
            
        self.vel_y += GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20
            
        self.x += self.vel_x
        self.rect.x = int(self.x)

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                self.x = float(self.rect.x)
                self.vel_x = 0

        self.y += self.vel_y
        self.rect.y = int(self.y)
        
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                self.y = float(self.rect.y)
                    
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery:
                    enemies.remove(enemy)
                    self.vel_y = JUMP_STRENGTH / 2
                    self.on_ground = False
                else:
                    return False
                    
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = float(self.rect.x)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = float(self.rect.x)
        
        self.animation_counter += 1
        if self.jump_animation > 0:
            self.jump_animation -= 1
        
        if not self.on_ground:
            self.wing_flap = math.sin(self.animation_counter * 0.3) * 20
        else:
            self.wing_flap = math.sin(self.animation_counter * 0.1) * 5
            
        self.hair_flow = math.sin(self.animation_counter * 0.05) * 3
        
        for feather in self.feathers[:]:
            feather['x'] += feather['vel_x']
            feather['y'] += feather['vel_y']
            feather['vel_y'] += 0.3
            feather['life'] -= 1
            feather['rotation'] += 5
            if feather['life'] <= 0:
                self.feathers.remove(feather)

        if self.facing_right:
            self.image = self.image_orig
        else:
            self.image = pygame.transform.flip(self.image_orig, True, False)
        
        return True
        
    def draw(self, screen):
        for feather in self.feathers:
            alpha = feather['life'] / 30
            size = int(10 * alpha)
            if size > 0:
                feather_color = (255, int(255 * alpha), int(255 * alpha))
                points = []
                for i in range(6):
                    angle = (i * 60 + feather['rotation']) * math.pi / 180
                    r = size if i % 2 == 0 else size // 2
                    px = feather['x'] + r * math.cos(angle)
                    py = feather['y'] + r * math.sin(angle)
                    points.append((px, py))
                if len(points) > 2:
                    pygame.draw.polygon(screen, feather_color, points)
        
        if self.on_ground:
            shadow_alpha = 150
            shadow_width_ratio = 0.8
            shadow_height_ratio = 0.2
        else:
            dist_to_ground_approx = SCREEN_HEIGHT - self.rect.bottom
            if dist_to_ground_approx < 0: dist_to_ground_approx = 0
            max_dist_for_shadow = 300
            if dist_to_ground_approx > max_dist_for_shadow:
                shadow_alpha = 0
            else:
                shadow_alpha = int(100 * (1 - dist_to_ground_approx / max_dist_for_shadow))
            shadow_width_ratio = 0.6 * (1 - dist_to_ground_approx / (max_dist_for_shadow * 2))
            shadow_height_ratio = 0.15 * (1 - dist_to_ground_approx / (max_dist_for_shadow * 2))
            if shadow_width_ratio < 0.1 : shadow_width_ratio = 0.1
            if shadow_height_ratio < 0.05 : shadow_height_ratio = 0.05

        if shadow_alpha > 0:
            shadow_surface = pygame.Surface((int(self.width * shadow_width_ratio), int(self.height * shadow_height_ratio)), pygame.SRCALPHA)
            shadow_surface.fill((0,0,0,0))
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())
            shadow_pos_x = self.rect.centerx - shadow_surface.get_width() // 2
            shadow_y = self.rect.bottom + 2
            closest_platform_top = SCREEN_HEIGHT
            found_platform_below = False
            for p in current_platforms_for_shadow:
                if p.rect.left < self.rect.centerx < p.rect.right and p.rect.top >= self.rect.bottom -5:
                    if p.rect.top < closest_platform_top:
                        closest_platform_top = p.rect.top
                        found_platform_below = True
            if found_platform_below:
                 shadow_y = closest_platform_top - shadow_surface.get_height() // 2 + 2
            else:
                shadow_y = self.rect.bottom + 5 - shadow_surface.get_height() // 2
            screen.blit(shadow_surface, (shadow_pos_x, shadow_y))
        
        screen.blit(self.image, self.rect)

class Platform:
    def __init__(self, x, y, width, height, platform_type="ground"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        self.animation_counter = 0
        
    def draw(self, screen):
        self.animation_counter += 1
        
        if self.type == "ground":
            pygame.draw.rect(screen, DARK_GREEN, self.rect)
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y, self.rect.width, 10))
            
            for i in range(0, self.rect.width, 15):
                grass_height = 8 + math.sin((self.animation_counter + i) * 0.05) * 2
                pygame.draw.polygon(screen, (0, 200, 0), [
                    (self.rect.x + i, self.rect.y + 10),
                    (self.rect.x + i + 3, self.rect.y + 10 - grass_height),
                    (self.rect.x + i + 6, self.rect.y + 10)
                ])
                pygame.draw.polygon(screen, (0, 150, 0), [
                    (self.rect.x + i + 7, self.rect.y + 10),
                    (self.rect.x + i + 10, self.rect.y + 10 - grass_height + 2),
                    (self.rect.x + i + 13, self.rect.y + 10)
                ])
                
        elif self.type == "brick":
            pygame.draw.rect(screen, BRICK_RED, self.rect)
            pygame.draw.rect(screen, (200, 60, 60), 
                           (self.rect.x, self.rect.y, self.rect.width, 4))
            pygame.draw.rect(screen, (120, 20, 20), 
                           (self.rect.x, self.rect.bottom - 4, self.rect.width, 4))
            for i in range(0, self.rect.width, 20):
                for j in range(0, self.rect.height, 15):
                    pygame.draw.rect(screen, (100, 20, 20), 
                                   (self.rect.x + i, self.rect.y + j, 19, 14), 1)
                    if (i + j) % 40 < 20:
                        pygame.draw.rect(screen, (160, 40, 40), 
                                       (self.rect.x + i + 2, self.rect.y + j + 2, 15, 10))
                                       
        elif self.type == "pipe":
            pygame.draw.rect(screen, GREEN, self.rect)
            highlight_x = self.rect.x + 5
            pygame.draw.rect(screen, (100, 255, 100), 
                           (highlight_x, self.rect.y, 8, self.rect.height))
            pygame.draw.rect(screen, (150, 255, 150), 
                           (highlight_x + 2, self.rect.y, 4, self.rect.height))
            pygame.draw.rect(screen, DARK_GREEN,
                           (self.rect.right - 10, self.rect.y, 10, self.rect.height))
            if self.rect.y > 100:
                pygame.draw.rect(screen, GREEN, 
                               (self.rect.x - 5, self.rect.y - 10, self.rect.width + 10, 15))
                pygame.draw.rect(screen, DARK_GREEN,
                               (self.rect.x - 5, self.rect.y - 10, self.rect.width + 10, 15), 3)
                pygame.draw.rect(screen, (100, 255, 100), 
                               (self.rect.x - 3, self.rect.y - 8, 10, 11))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.vel_x = 2
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation_counter = 0
        self.squash = 0
        
    def update(self, platforms):
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
        on_platform_edge = False
        for platform in platforms:
            foot_check_rect = pygame.Rect(self.rect.left, self.rect.bottom, self.width, 5)
            next_foot_check_rect = pygame.Rect(self.rect.left + self.vel_x, self.rect.bottom, self.width, 5)
            if foot_check_rect.colliderect(platform.rect):
                if not next_foot_check_rect.colliderect(platform.rect):
                    if (self.vel_x > 0 and self.rect.right >= platform.rect.right - abs(self.vel_x)) or \
                       (self.vel_x < 0 and self.rect.left <= platform.rect.left + abs(self.vel_x)):
                        on_platform_edge = True
                        break
        if on_platform_edge:
            self.vel_x *= -1

        if self.rect.left <= 0 :
            self.rect.left = 0
            self.vel_x *= -1
            self.x = float(self.rect.x)
        elif self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x *= -1
            self.x = float(self.rect.x)

        self.animation_counter += 1
        self.squash = math.sin(self.animation_counter * 0.2) * 3
            
    def draw(self, screen):
        cx = self.rect.centerx
        cy = self.rect.centery
        pygame.draw.ellipse(screen, (100, 100, 100), 
                          (self.rect.x + 2, self.rect.y + self.height - 5, self.width - 4, 8))
        body_height = self.height - 5 + self.squash
        pygame.draw.ellipse(screen, BROWN, 
                          (self.rect.x, self.rect.y + 5 - self.squash, self.width, body_height))
        pygame.draw.ellipse(screen, (160, 82, 45), 
                          (self.rect.x + 3, self.rect.y + 7 - self.squash, self.width - 6, 15))
        face_y = cy - 5 + self.squash // 2
        pygame.draw.ellipse(screen, BLACK, (cx - 10, face_y - 3, 6, 8))
        pygame.draw.ellipse(screen, WHITE, (cx - 9, face_y - 2, 2, 2))
        pygame.draw.ellipse(screen, BLACK, (cx + 4, face_y - 3, 6, 8))
        pygame.draw.ellipse(screen, WHITE, (cx + 5, face_y - 2, 2, 2))
        pygame.draw.line(screen, BLACK, (cx - 12, face_y - 6), (cx - 7, face_y - 4), 3)
        pygame.draw.line(screen, BLACK, (cx + 12, face_y - 6), (cx + 7, face_y - 4), 3)
        pygame.draw.arc(screen, BLACK, (cx - 8, face_y + 2, 16, 8), 0.3, 2.8, 2)
        pygame.draw.polygon(screen, WHITE, [
            (cx - 5, face_y + 4), (cx - 3, face_y + 7), (cx - 1, face_y + 4)])
        pygame.draw.polygon(screen, WHITE, [
            (cx + 1, face_y + 4), (cx + 3, face_y + 7), (cx + 5, face_y + 4)])
        foot_offset = math.sin(self.animation_counter * 0.3) * 3
        pygame.draw.ellipse(screen, (80, 40, 0), 
                          (self.rect.x + 5 + foot_offset, self.rect.y + self.height - 10, 12, 10))
        pygame.draw.ellipse(screen, BLACK, 
                          (self.rect.x + 7 + foot_offset, self.rect.y + self.height - 8, 8, 6))
        pygame.draw.ellipse(screen, (80, 40, 0), 
                          (self.rect.x + 18 - foot_offset, self.rect.y + self.height - 10, 12, 10))
        pygame.draw.ellipse(screen, BLACK, 
                          (self.rect.x + 20 - foot_offset, self.rect.y + self.height - 8, 8, 6))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 30, 30)
        self.animation_counter = 0
        self.sparkles = []
        
    def draw(self, screen):
        self.animation_counter += 1
        width = abs(30 * math.cos(self.animation_counter * 0.05))
        cx = self.rect.centerx
        cy = self.rect.centery
        if self.animation_counter % 10 == 0:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(15, 25)
            self.sparkles.append({
                'x': cx + math.cos(angle) * dist,
                'y': cy + math.sin(angle) * dist,
                'life': 20
            })
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= 1
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)
            else:
                size = sparkle['life'] // 5
                if size > 0:
                    pygame.draw.circle(screen, YELLOW, 
                                     (int(sparkle['x']), int(sparkle['y'])), size)
        if width > 2:
            pygame.draw.ellipse(screen, GOLD, 
                              (cx - width/2, cy - 15, width, 30))
            pygame.draw.ellipse(screen, YELLOW, 
                              (cx - width/2 + 2, cy - 13, width - 4, 26))
            if width > 20:
                star_points = []
                for i in range(10):
                    angle = i * math.pi / 5
                    r = 8 if i % 2 == 0 else 4
                    px = cx + r * math.cos(angle - math.pi / 2)
                    py = cy + r * math.sin(angle - math.pi / 2)
                    star_points.append((px, py))
                pygame.draw.polygon(screen, GOLD, star_points)
            if width > 15:
                pygame.draw.ellipse(screen, WHITE, 
                                  (cx - width/4, cy - 8, width/2, 8))

def draw_background(screen):
    for i in range(SCREEN_HEIGHT // 2):
        progress = i / (SCREEN_HEIGHT // 2)
        r = int(LIGHT_SKY_BLUE_GRADIENT_TOP[0] * (1 - progress) + SKY_BLUE[0] * progress)
        g = int(LIGHT_SKY_BLUE_GRADIENT_TOP[1] * (1 - progress) + SKY_BLUE[1] * progress)
        b = int(LIGHT_SKY_BLUE_GRADIENT_TOP[2] * (1 - progress) + SKY_BLUE[2] * progress)
        color = (max(0, min(r, 255)), max(0, min(g, 255)), max(0, min(b, 255)))
        pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))
    
    pygame.draw.rect(screen, SKY_BLUE, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

    sun_x, sun_y = 850, 100
    pygame.draw.circle(screen, YELLOW, (sun_x, sun_y), 40)
    pygame.draw.circle(screen, (255, 255, 200), (sun_x, sun_y), 35)
    for i in range(12):
        angle = i * math.pi / 6
        start_x = sun_x + 50 * math.cos(angle)
        start_y = sun_y + 50 * math.sin(angle)
        end_x = sun_x + 70 * math.cos(angle)
        end_y = sun_y + 70 * math.sin(angle)
        pygame.draw.line(screen, YELLOW, (start_x, start_y), (end_x, end_y), 3)
    
    cloud_positions = [(100, 100), (400, 150), (700, 80), (900, 130)]
    for x, y in cloud_positions:
        pygame.draw.ellipse(screen, (200, 200, 200, 150), (x + 5, y + 5, 80, 40))
        pygame.draw.ellipse(screen, (200, 200, 200, 150), (x - 15, y + 15, 60, 35))
        pygame.draw.ellipse(screen, (200, 200, 200, 150), (x + 45, y + 15, 60, 35))
        pygame.draw.ellipse(screen, WHITE, (x, y, 80, 40))
        pygame.draw.ellipse(screen, WHITE, (x - 20, y + 10, 60, 35))
        pygame.draw.ellipse(screen, WHITE, (x + 40, y + 10, 60, 35))
        pygame.draw.ellipse(screen, WHITE, (x + 10, y - 10, 60, 40))
    
    pygame.draw.polygon(screen, MOUNTAIN_FAR, [
        (-100, SCREEN_HEIGHT), (150, SCREEN_HEIGHT // 2 - 20),
        (300, SCREEN_HEIGHT // 2 - 60), (500, SCREEN_HEIGHT // 2 - 10),
        (650, SCREEN_HEIGHT)])
    pygame.draw.polygon(screen, MOUNTAIN_MID, [
        (100, SCREEN_HEIGHT), (350, SCREEN_HEIGHT // 2 + 30),
        (550, SCREEN_HEIGHT // 2 - 0), (750, SCREEN_HEIGHT)])
    pygame.draw.polygon(screen, MOUNTAIN_NEAR, [
        (450, SCREEN_HEIGHT), (650, SCREEN_HEIGHT // 2 + 80),
        (800, SCREEN_HEIGHT // 2 + 40), (SCREEN_WIDTH + 50, SCREEN_HEIGHT)])
    
    # 木のY座標を地面基準に修正
    ground_y = SCREEN_HEIGHT - 60 # 地面のY座標 (Platformの地面と同じ高さ)
    tree_total_height = 80 # 木の全体の高さ（葉の上端から幹の下端まで）
    trunk_height = 30 # 幹の高さ
    
    # tree_positionsのX座標のみ使用し、Y座標は地面基準で計算
    tree_x_positions = [100, 300, 750, 900] # X座標のリスト
    tree_scales = [0.8, 1.0, 0.9, 1.1] # 木の大きさにバリエーション

    for i, tx_center in enumerate(tree_x_positions):
        current_scale = tree_scales[i % len(tree_scales)] # スケールを適用
        current_trunk_height = int(trunk_height * current_scale)
        # 幹の下端が地面 (ground_y) に接するように計算
        trunk_bottom_y = ground_y
        trunk_top_y = trunk_bottom_y - current_trunk_height
        leaf_center_y = trunk_top_y - int(20 * current_scale) # 葉の中心Y座標 (幹の上端から少し上)
        
        trunk_width = int(14 * current_scale)
        leaf_radius_main = int(28 * current_scale)
        leaf_radius_sub1 = int(25 * current_scale)
        leaf_radius_sub2 = int(26 * current_scale)
        leaf_radius_sub3 = int(23 * current_scale)

        # 幹
        pygame.draw.rect(screen, TREE_TRUNK, 
                         (tx_center - trunk_width // 2, trunk_top_y, trunk_width, current_trunk_height))
        # 葉
        pygame.draw.circle(screen, TREE_LEAF_DARK, (tx_center, leaf_center_y), leaf_radius_main)
        pygame.draw.circle(screen, TREE_LEAF_LIGHT, (tx_center - int(5*current_scale), leaf_center_y - int(3*current_scale)), leaf_radius_sub1)
        pygame.draw.circle(screen, TREE_LEAF_DARK, (tx_center + int(3*current_scale), leaf_center_y + int(10*current_scale)), leaf_radius_sub2)
        pygame.draw.circle(screen, TREE_LEAF_LIGHT, (tx_center, leaf_center_y + int(7*current_scale)), leaf_radius_sub3)


current_platforms_for_shadow = []

def main():
    global current_platforms_for_shadow

    player = Player(100, 400)
    
    platforms = [
        Platform(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60, "ground"),
        Platform(200, SCREEN_HEIGHT - 60 - 100, 150, 20, "brick"),
        Platform(400, SCREEN_HEIGHT - 60 - 200, 150, 20, "brick"),
        Platform(600, SCREEN_HEIGHT - 60 - 300, 150, 20, "brick"),
        Platform(300, SCREEN_HEIGHT - 60 - 100, 60, 100, "pipe"),
        Platform(700, SCREEN_HEIGHT - 60 - 150, 60, 150, "pipe"),
        Platform(850, SCREEN_HEIGHT - 60 - 150, 100, 20, "brick"),
        Platform(50, SCREEN_HEIGHT - 60 - 250, 100, 20, "brick"),
    ]
    current_platforms_for_shadow = platforms

    for p in platforms:
        if p.type == "pipe":
            p.rect.bottom = SCREEN_HEIGHT - 60
    
    enemies = [
        Enemy(300, SCREEN_HEIGHT - 60 - 35),
        Enemy(500, SCREEN_HEIGHT - 60 - 300 - 35),
        Enemy(750, SCREEN_HEIGHT - 60 - 35),
    ]
    
    initial_coin_count = 7
    coins = [
        Coin(250, SCREEN_HEIGHT - 60 - 100 - 40),
        Coin(450, SCREEN_HEIGHT - 60 - 200 - 40),
        Coin(650, SCREEN_HEIGHT - 60 - 300 - 40),
        Coin(880, SCREEN_HEIGHT - 60 - 150 - 40),
        Coin(100, SCREEN_HEIGHT - 60 - 250 - 40),
        Coin(350, SCREEN_HEIGHT - 60 - 100 - 100 - 10),
        Coin(550, SCREEN_HEIGHT - 60 - 40),
    ]
    
    running = True
    game_over = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    player = Player(100, 400)
                    enemies = [
                        Enemy(300, SCREEN_HEIGHT - 60 - 35),
                        Enemy(500, SCREEN_HEIGHT - 60 - 300 - 35),
                        Enemy(750, SCREEN_HEIGHT - 60 - 35),
                    ]
                    coins = [
                        Coin(250, SCREEN_HEIGHT - 60 - 100 - 40),
                        Coin(450, SCREEN_HEIGHT - 60 - 200 - 40),
                        Coin(650, SCREEN_HEIGHT - 60 - 300 - 40),
                        Coin(880, SCREEN_HEIGHT - 60 - 150 - 40),
                        Coin(100, SCREEN_HEIGHT - 60 - 250 - 40),
                        Coin(350, SCREEN_HEIGHT - 60 - 100 - 100 - 10),
                        Coin(550, SCREEN_HEIGHT - 60 - 40),
                    ]
                    game_over = False
        
        if not game_over:
            if not player.update(platforms, enemies, coins):
                game_over = True
            for enemy in enemies:
                enemy.update(platforms)
        
        screen.fill(BLACK)
        draw_background(screen)
        
        for platform in platforms:
            platform.draw(screen)
        for coin in coins:
            coin.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
            
        player.draw(screen)
        
        font = pygame.font.Font(None, 36)
        score_text = f"Coins: {initial_coin_count - len(coins)}/{initial_coin_count}"
        shadow_surface_font = font.render(score_text, True, BLACK)
        screen.blit(shadow_surface_font, (12, 12))
        score_surface = font.render(score_text, True, WHITE)
        screen.blit(score_surface, (10, 10))
        
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            game_over_text = font.render("GAME OVER! Press R to Restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (230, 230, 230), bg_rect, border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect, 3, border_radius=10)
            screen.blit(game_over_text, text_rect)
            
        elif len(coins) == 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 100))
            screen.blit(overlay, (0,0))
            win_text = font.render("YOU WIN! All Coins Collected!", True, DARK_GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (220, 255, 220), bg_rect, border_radius=10)
            pygame.draw.rect(screen, GOLD, bg_rect, 3, border_radius=10)
            screen.blit(win_text, text_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()