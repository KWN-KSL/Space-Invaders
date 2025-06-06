import pygame
import random
import sys
import copy
import time
import math
import asyncio
import platform
import os

# Inicjalizacja Pygame oraz modułu dźwięku
pygame.init()
pygame.mixer.init()

# Definicje kolorów w formacie RGB
WHITE, BLACK, GREEN, RED, BLUE = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255)
GRAY, HOVER = (100, 100, 100), (150, 150, 150)

# Stałe określające wymiary i prędkości obiektów w grze
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 30
PLAYER_SPEED = 6
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
BULLET_SPEED = 7
ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_DROP = 20
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 80, 40
MOTHERSHIP_FIRE_CHANCE = 0.05
MOTHERSHIP_SPEED = 3
ASTEROID_SPEED = 5
ASTEROID_SPAWN_INTERVAL = 5
ENEMY_FIRE_CHANCE = 0.002
ENEMY_SPEED = 1
ASTEROID_HP = 2
MOTHERSHIP_HP = 10

# Pobieranie informacji o rozdzielczości ekranu i ustawianie trybu pełnoekranowego
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders")

# Inicjalizacja czcionek do wyświetlania tekstu
font = pygame.font.SysFont(None, 50)
big_font = pygame.font.SysFont(None, 80)
clock = pygame.time.Clock()

# Zmienne globalne przechowujące stan gry
state = "menu"
previous_state = None
game_mode = None
state_buffer = []
can_shoot = True
score = 0
wave = 0
enemy_float_positions = []
enemy_direction = 1
last_difficulty = (0.002, 1)
life_lost_message_timer = 0
life_lost_message = False
player_lives = 0
last_asteroid_spawn = 0
game_won = False
game_over = False
respawning = False
respawn_timer = 0
volume_return_state = None
last_save = time.time()
last_restore_time = 0
win_music_played = False
game_over_music_played = False
music_volume = 0.25
effects_volume = 0.25
game_end_menu_y = HEIGHT//2 - 300

# Funkcja do ładowania zasobów (grafik, dźwięków) z uwzględnieniem ścieżki
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Ładowanie muzyki tła i ustawianie głośności
pygame.mixer.music.load(resource_path("Muzyka/glowna.ogg"))
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)

# Ładowanie efektów dźwiękowych
player_shot_sound = pygame.mixer.Sound(resource_path("Muzyka/gracz.mp3"))
enemy_shot_sound = pygame.mixer.Sound(resource_path("Muzyka/przeciwnicy.ogg"))
explosion_sound = pygame.mixer.Sound(resource_path("Muzyka/eksplozja.wav"))
player_shot_sound.set_volume(effects_volume)
enemy_shot_sound.set_volume(effects_volume)
explosion_sound.set_volume(effects_volume)

# Ładowanie i skalowanie grafik tła
menu_background = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/Tło/głowne.png")).convert(), (WIDTH, HEIGHT))
select_background = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/Tło/wybor_trudnosci.png")).convert(), (WIDTH, HEIGHT))
game_background = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/Tło/gra.png")).convert(), (WIDTH, HEIGHT))
testers_background = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/Tło/testerzy.png")).convert(), (WIDTH, HEIGHT))

# Ładowanie i skalowanie grafik pocisków
ship_bullet_images = [pygame.transform.scale_by(pygame.image.load(resource_path(f"Pociski/Gracz/{i}.png")).convert_alpha(), 0.1) for i in range(1, 7)]
enemy_bullet_images = [pygame.transform.scale_by(pygame.image.load(resource_path(f"Pociski/Przeciwnicy/{i}.png")).convert_alpha(), 0.1) for i in range(1, 7)]
boss_bullet_images = [pygame.transform.scale_by(pygame.image.load(resource_path(f"Pociski/Boss/{i}.png")).convert_alpha(), 0.1) for i in range(1, 7)]

# Ładowanie grafik testerów
tester_images = [pygame.transform.scale(pygame.image.load(resource_path(f"Statki/Testerzy/{i}.png")).convert_alpha(), (300, 300)) for i in range(1, 4)]

# Ładowanie grafiki serca (życie gracza)
heart_image = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/serce.png")).convert_alpha(), (40, 40))

# Funkcja do ładowania klatek animacji dymu
def load_white_puff_frames():
    frames = [pygame.image.load(resource_path(f"Obiekty/Zanikanie/whitePuff{str(i).zfill(2)}.png")).convert_alpha() for i in range(25)]
    return [pygame.transform.scale_by(frame, 0.333) for frame in frames]
white_puff_frames = load_white_puff_frames()

# Funkcja do rysowania tekstu z tłem
def draw_text(text, font, color, x, y, surface=screen):
    surf = font.render(text, True, color)
    padding = 10
    background = pygame.Surface((surf.get_width() + 2 * padding, surf.get_height() + 2 * padding), pygame.SRCALPHA)
    background.fill((0, 0, 0, 180))
    surface.blit(background, (x - surf.get_width() // 2 - padding, y - padding))
    surface.blit(surf, (x - surf.get_width() // 2, y))

# Klasa przycisku w menu
class Button:
    def __init__(self, text, x, y, w, h, action, key=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.key = key
        self.hovered = False
    def draw(self, surface=screen):
        color = HOVER if self.hovered else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        txt = font.render(self.text, True, WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
    def click(self):
        self.action()

# Klasa suwaka głośności
class VolumeSlider:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.dragging = False
        self.label = label
    def draw(self, volume):
        pygame.draw.rect(screen, GRAY, self.rect)
        fill_width = int(self.rect.width * volume)
        pygame.draw.rect(screen, BLUE, (self.rect.x, self.rect.y, fill_width, self.rect.height))
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        txt = font.render(f"{self.label}: {int(volume * 100)}%", True, WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.y - 30))
    def update_volume(self, mouse_pos):
        if self.dragging:
            relative_x = mouse_pos[0] - self.rect.x
            return max(0.0, min(1.0, relative_x / self.rect.width))
        return None
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self.update_volume(event.pos)
        return None

# Klasa menu głośności
class VolumeMenu:
    def __init__(self):
        self.music_slider = VolumeSlider(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 20, "Muzyka")
        self.effects_slider = VolumeSlider(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 20, "Efekty")
        self.back_button = Button("Powrót", WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60, self.return_to_previous_state, pygame.K_RETURN)
    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        draw_text("Ustawienia głośności", big_font, WHITE, WIDTH//2, HEIGHT//4)
        self.music_slider.draw(music_volume)
        self.effects_slider.draw(effects_volume)
        self.back_button.draw()
    def handle_event(self, event):
        global music_volume, effects_volume
        music_result = self.music_slider.handle_event(event)
        if music_result is not None:
            music_volume = music_result
            pygame.mixer.music.set_volume(music_volume)
        effects_result = self.effects_slider.handle_event(event)
        if effects_result is not None:
            effects_volume = effects_result
            player_shot_sound.set_volume(effects_volume)
            enemy_shot_sound.set_volume(effects_volume)
            explosion_sound.set_volume(effects_volume)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                self.back_button.click()
        if event.type == pygame.KEYDOWN:
            if event.key == self.back_button.key:
                self.back_button.click()
        if event.type == pygame.MOUSEMOTION:
            self.back_button.check_hover(event.pos)
    def return_to_previous_state(self):
        global volume_return_state
        if volume_return_state:
            switch_state(volume_return_state)
            volume_return_state = None

# Klasa menu końca gry
class GameEndMenu:
    def __init__(self, is_game_over):
        self.is_game_over = is_game_over
        self.buttons = [
            Button("Menu", WIDTH//2 - 100, HEIGHT//2 - 50, 200, 60, reset_to_menu, pygame.K_1),
            Button("Restart", WIDTH//2 - 100, HEIGHT//2 + 20, 200, 60, set_boss_game if game_mode == "boss_game" else lambda: set_difficulty(*last_difficulty), pygame.K_2),
            Button("Głośność", WIDTH//2 - 100, HEIGHT//2 + 90, 200, 60, lambda: switch_state("volume"), pygame.K_3),
            Button("Wyjście", WIDTH//2 - 100, HEIGHT//2 + 160, 200, 60, lambda: sys.exit(), pygame.K_4)]
        if is_game_over and score >= 5:
            self.buttons.insert(2, Button("Cofnij", WIDTH//2 - 100, HEIGHT//2 + 90, 200, 60, try_restore, pygame.K_3))
            self.buttons[3].rect.y = HEIGHT//2 + 160
            self.buttons[3].key = pygame.K_4
            self.buttons[4].rect.y = HEIGHT//2 + 230
            self.buttons[4].key = pygame.K_5
        title = "GAME OVER" if self.is_game_over else "Gratulacje! Wygrałeś!"
        title_surface = big_font.render(title, True, WHITE)
        title_width = title_surface.get_width() + 40
        score_surface = font.render(f"Wynik: {score}", True, WHITE)
        score_width = score_surface.get_width() + 40
        button_width = 200
        self.menu_width = max(title_width, score_width, button_width) + 20
        self.menu_height = 600 if len(self.buttons) == 4 else 670
    def draw(self):
        pygame.sprite.GroupSingle(player).draw(screen)
        bullets.draw(screen)
        enemy_bullets.draw(screen)
        enemies.draw(screen)
        for mothership in motherships:
            mothership.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        for i in range(player_lives):
            screen.blit(heart_image, (20 + i * 50, 20))
        draw_text(f"Wynik: {score}", font, WHITE, WIDTH - 150, 30)
        if life_lost_message and pygame.time.get_ticks() - life_lost_message_timer < 1000:
            draw_text("-1 Życie", font, RED, WIDTH//2, HEIGHT//2 - 50)
        menu_rect = pygame.Rect(WIDTH//2 - self.menu_width//2, HEIGHT//2 - self.menu_height//2, self.menu_width, self.menu_height)
        overlay = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (WIDTH//2 - self.menu_width//2, HEIGHT//2 - self.menu_height//2))
        pygame.draw.rect(screen, WHITE, menu_rect, 2)
        title = "GAME OVER" if self.is_game_over else "Gratulacje! Wygrałeś!"
        draw_text(title, big_font, WHITE, WIDTH//2, HEIGHT//2 - self.menu_height//2 + 50)
        draw_text(f"Wynik: {score}", font, WHITE, WIDTH//2, HEIGHT//2 - self.menu_height//2 + 120)
        for b in self.buttons:
            b.draw()
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in self.buttons:
                if b.rect.collidepoint(event.pos):
                    b.click()
        if event.type == pygame.KEYDOWN:
            for b in self.buttons:
                if b.key == event.key:
                    b.click()
        if event.type == pygame.MOUSEMOTION:
            for b in self.buttons:
                b.check_hover(mouse_pos)

# Klasa gracza
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load(resource_path("Statki/Gracz/rakieta.png")).convert_alpha(), 0.5)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
    def update(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

# Klasa pocisku
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_player, is_boss=False):
        super().__init__()
        if is_player:
            self.image = random.choice(ship_bullet_images)
            player_shot_sound.play()
        elif is_boss:
            self.image = random.choice(boss_bullet_images)
            enemy_shot_sound.play()
        else:
            self.image = random.choice(enemy_bullet_images)
            enemy_shot_sound.play()
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.is_player = is_player
    def update(self):
        self.rect.y += BULLET_SPEED * self.direction
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Klasa wroga
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load(resource_path(image_path)).convert_alpha(), 0.2)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.float_x = float(x)
        self.float_y = float(y)
    def update_position(self, dx, dy=0):
        self.float_x += dx
        self.float_y += dy
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

# Klasa statku-matki (bossa)
class Mothership(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load(resource_path("Statki/Boss/matka.png")).convert_alpha(), 0.3)
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.direction = random.choice([-1, 1])
        self.change_direction_timer = time.time()
        self.hp = MOTHERSHIP_HP
    def update(self):
        if time.time() - self.change_direction_timer > random.uniform(1, 3):
            self.direction = random.choice([-1, 1])
            self.change_direction_timer = time.time()
        self.rect.x += self.direction * MOTHERSHIP_SPEED
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            explosions.add(Explosion(self.rect.centerx, self.rect.centery, explosion_frames))
            explosion_sound.play()
            self.kill()
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        bar_width = self.rect.width + 20
        bar_height = 10
        bar_x = self.rect.left - 10
        bar_y = self.rect.top - 15
        fill_width = int(bar_width * (self.hp / MOTHERSHIP_HP))
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

# Klasa asteroidy
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(resource_path("Obiekty/asteroida.png")).convert_alpha(), (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = ASTEROID_HP
        angle = random.uniform(0, 2 * math.pi)
        self.dx = ASTEROID_SPEED * math.cos(angle)
        self.dy = ASTEROID_SPEED * math.sin(angle)
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.dx = -self.dx
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.dy = -self.dy
        for mothership in motherships:
            if self.rect.colliderect(mothership.rect):
                self.dx = -self.dx
                self.dy = -self.dy
                self.rect.x += self.dx
                self.rect.y += self.dy
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.dx = -self.dx
                self.dy = -self.dy
                self.rect.x += self.dx
                self.rect.y += self.dy
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            explosions.add(Explosion(self.rect.centerx, self.rect.centery, explosion_frames))
            explosion_sound.play()
            self.kill()
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.left
        bar_y = self.rect.top - 10
        fill_width = int(bar_width * (self.hp / ASTEROID_HP))
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

# Klasa przeszkody
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.stage = 1
        self.hp = 10
        self.x, self.y = x, y
        self.image_paths = [
            pygame.transform.scale(pygame.image.load(resource_path("Obiekty/przeszkoda1.png")).convert_alpha(), (120, 80)),
            pygame.transform.scale(pygame.image.load(resource_path("Obiekty/przeszkoda2.png")).convert_alpha(), (120, 80))]
        self.image = self.image_paths[0]
        self.rect = self.image.get_rect(center=(x, y))
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            if self.stage == 1:
                self.stage = 2
                self.image = self.image_paths[1]
                self.hp = 10
            else:
                explosions.add(Explosion(self.rect.centerx, self.rect.centery, explosion_frames))
                explosion_sound.play()
                self.kill()
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.left
        bar_y = self.rect.top - 10
        fill_width = int(bar_width * (self.hp / 10))
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

# Klasa efektu eksplozji
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_timer = 0
    def update(self):
        self.frame_timer += 1
        if self.frame_timer % 4 == 0:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.current_frame]

# Klasa efektu trafienia
class HitEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = white_puff_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_timer = 0
    def update(self):
        self.frame_timer += 1
        if self.frame_timer % 2 == 0:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.current_frame]

# Klasa animacji odradzania gracza
class PlayerRespawnAnimation(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = player_respawn_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_timer = 0
    def update(self):
        self.frame_timer += 1
        if self.frame_timer % 2 == 0:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.current_frame]

# Funkcja inicjalizująca grę
def create_game():
    global player, bullets, enemy_bullets, enemies, obstacles, enemy_direction, game_over, score, enemy_float_positions, respawning, respawn_timer, wave, motherships, asteroids, game_won, last_asteroid_spawn
    player = Player()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    motherships = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    enemy_float_positions = []
    enemy_rows = ["alien1", "alien2", "alien3", "alien4"]
    for row in range(4):
        for col in range(10):
            x, y = 80 * col + 100, 60 * row + 50
            path = f"Statki/Przeciwnicy/{enemy_rows[row]}.png"
            enemies.add(Enemy(x, y, path))
            enemy_float_positions.append([x, y])
    obstacle_y = HEIGHT - 300
    for i in range(4):
        x = (i + 1) * WIDTH // 5
        obstacles.add(Obstacle(x, obstacle_y))
    enemy_direction = 1
    respawning = False
    respawn_timer = 0
    game_over = False
    game_won = False
    state_buffer.clear()
    score = 0
    wave = 1
    last_asteroid_spawn = time.time()
    pygame.mixer.music.load(resource_path("Muzyka/glowna.ogg"))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

# Funkcja inicjalizująca tryb bossa
def create_boss_mode():
    global player, bullets, enemy_bullets, enemies, obstacles, enemy_direction, game_over, score, enemy_float_positions, respawning, respawn_timer, wave, motherships, asteroids, game_won, last_asteroid_spawn
    player = Player()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    motherships = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    enemy_float_positions = []
    obstacle_y = HEIGHT - 300
    for i in range(4):
        x = (i + 1) * WIDTH // 5
        obstacles.add(Obstacle(x, obstacle_y))
    enemy_direction = 1
    respawning = False
    respawn_timer = 0
    game_over = False
    game_won = False
    state_buffer.clear()
    score = 0
    wave = 3
    motherships.add(Mothership())
    last_asteroid_spawn = time.time()
    pygame.mixer.music.stop()
    pygame.mixer.music.load(resource_path("Muzyka/boss.wav"))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

# Funkcja inicjalizująca tryb gry z bossem
def create_boss_game():
    global player, bullets, enemy_bullets, enemies, obstacles, game_over, score, respawning, respawn_timer, motherships, asteroids, game_won, last_asteroid_spawn, enemy_float_positions
    player = Player()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    motherships = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    enemy_float_positions = []
    obstacle_y = HEIGHT - 300
    for i in range(4):
        x = (i + 1) * WIDTH // 5
        obstacles.add(Obstacle(x, obstacle_y))
    motherships.add(Mothership())
    respawning = False
    respawn_timer = 0
    game_over = False
    game_won = False
    state_buffer.clear()
    score = 0
    last_asteroid_spawn = time.time()
    pygame.mixer.music.stop()
    pygame.mixer.music.load(resource_path("Muzyka/boss.wav"))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

# Funkcja tworząca nową falę wrogów
def spawn_new_wave():
    global enemies, enemy_float_positions, wave
    enemies.empty()
    enemy_float_positions.clear()
    enemy_rows = ["alien1", "alien2", "alien3", "alien4"]
    for row in range(4):
        for col in range(10):
            x, y = 80 * col + 100, 60 * row + 50
            path = f"Statki/Przeciwnicy/{enemy_rows[row]}.png"
            enemies.add(Enemy(x, y, path))
            enemy_float_positions.append([x, y])
    wave += 1

# Funkcja tworząca statek-matkę
def create_mothership():
    global enemies, motherships, last_asteroid_spawn, wave
    enemies.empty()
    motherships.add(Mothership())
    last_asteroid_spawn = time.time()
    wave += 1
    pygame.mixer.music.stop()
    pygame.mixer.music.load(resource_path("Muzyka/boss.wav"))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

# Funkcja resetująca grę do menu głównego
def reset_to_menu():
    global bullets, enemy_bullets, enemies, obstacles, score, enemy_float_positions, can_shoot, player_lives, wave, motherships, asteroids, game_won, win_music_played, game_end_menu_y, game_over_music_played, game_mode
    bullets.empty()
    enemy_bullets.empty()
    enemies.empty()
    obstacles.empty()
    motherships.empty()
    asteroids.empty()
    enemy_float_positions.clear()
    can_shoot = False
    player_lives = 0
    wave = 0
    game_won = False
    win_music_played = False
    game_over_music_played = False
    game_end_menu_y = HEIGHT//2 - 300
    game_mode = None
    pygame.mixer.music.stop()
    pygame.mixer.music.load(resource_path("Muzyka/glowna.ogg"))
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)
    switch_state("menu")

# Funkcja zapisująca stan gry
def save_state():
    if len(state_buffer) > 10:
        state_buffer.pop(0)
    snapshot = {
        "player": player.rect.copy(),
        "bullets": [b.rect.copy() for b in bullets],
        "enemy_bullets": [b.rect.copy() for b in enemy_bullets],
        "enemies": [e.rect.copy() for e in enemies],
        "enemy_dir": enemy_direction if game_mode == "game" else None,
        "score": score,
        "player_lives": player_lives,
        "wave": wave if game_mode == "game" else None,
        "motherships": [(m.rect.copy(), m.hp, m.direction, m.change_direction_timer) for m in motherships],
        "asteroids": [(a.rect.copy(), a.hp, a.dx, a.dy) for a in asteroids],
        "obstacles": [(o.rect.copy(), o.hp, o.stage) for o in obstacles]
    }
    state_buffer.append(snapshot)

# Funkcja przywracająca zapisany stan gry
def try_restore():
    global game_over, score, game_end_menu_y, game_over_music_played, last_restore_time
    current_time = time.time()
    if current_time - last_restore_time < 5:
        return
    if score >= 5 and state_buffer:
        score -= 5
        restore_state()
        game_over = False
        game_over_music_played = False
        game_end_menu_y = HEIGHT//2 - 300
        pygame.mixer.music.stop()
        music_file = "Muzyka/boss.wav" if game_mode == "boss_game" or wave == 3 else "Muzyka/glowna.ogg"
        pygame.mixer.music.load(resource_path(music_file))
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
        switch_state(game_mode)
        last_restore_time = current_time
        pygame.event.clear()

# Funkcja przywracająca szczegóły stanu gry
def restore_state():
    global enemy_direction, enemy_float_positions, player_lives, wave, motherships, asteroids, obstacles
    s = state_buffer[max(0, len(state_buffer) - 5)]
    player.rect = s["player"].copy()
    bullets.empty()
    for r in s["bullets"]:
        b = Bullet(r.centerx, r.centery, -1, True)
        b.rect = r.copy()
        bullets.add(b)
    enemy_bullets.empty()
    for r in s["enemy_bullets"]:
        b = Bullet(r.centerx, r.centery, 1, False, is_boss=(game_mode == "boss_game" or wave == 3))
        b.rect = r.copy()
        enemy_bullets.add(b)
    if game_mode == "game" and s["enemies"]:
        enemies.empty()
        enemy_float_positions.clear()
        for r in s["enemies"]:
            if r.y < 60 + 50:
                sprite = "alien1"
            elif r.y < 120 + 50:
                sprite = "alien2"
            elif r.y < 180 + 50:
                sprite = "alien3"
            else:
                sprite = "alien4"
            image_path = f"Statki/Przeciwnicy/{sprite}.png"
            e = Enemy(r.x, r.y, image_path)
            enemies.add(e)
            enemy_float_positions.append([float(r.x), float(r.y)])
        enemy_direction = s["enemy_dir"] if s["enemy_dir"] is not None else 1
        wave = s["wave"] if s["wave"] is not None else 1
    motherships.empty()
    for m_data in s.get("motherships", []):
        m = Mothership()
        m.rect = m_data[0].copy()
        m.hp = m_data[1]
        m.direction = m_data[2]
        m.change_direction_timer = m_data[3]
        motherships.add(m)
    asteroids.empty()
    for a_data in s.get("asteroids", []):
        a = Asteroid(a_data[0].centerx, a_data[0].centery)
        a.rect = a_data[0].copy()
        a.hp = a_data[1]
        a.dx = a_data[2]
        a.dy = a_data[3]
        asteroids.add(a)
    obstacles.empty()
    for o_data in s.get("obstacles", []):
        o = Obstacle(o_data[0].centerx, o_data[0].centery)
        o.rect = o_data[0].copy()
        o.hp = o_data[1]
        o.stage = o_data[2]
        if o.stage == 2:
            o.image = o.image_paths[1]
        obstacles.add(o)
    player_lives = s["player_lives"]

# Funkcja rysująca menu pauzy
def pause_menu():
    pygame.sprite.GroupSingle(player).draw(screen)
    bullets.draw(screen)
    enemy_bullets.draw(screen)
    enemies.draw(screen)
    for mothership in motherships:
        mothership.draw(screen)
    for asteroid in asteroids:
        asteroid.draw(screen)
    for obs in obstacles:
        obs.draw(screen)
    for i in range(player_lives):
        screen.blit(heart_image, (20 + i * 50, 20))
    draw_text(f"Wynik: {score}", font, WHITE, WIDTH - 150, 30)
    if life_lost_message and pygame.time.get_ticks() - life_lost_message_timer < 1000:
        draw_text("-1 Życie", font, RED, WIDTH//2, HEIGHT//2 - 50)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    for b in pause_buttons:
        b.draw()

# Funkcja ustawiająca poziom trudności
def set_difficulty(fire_chance, speed):
    global ENEMY_FIRE_CHANCE, ENEMY_SPEED, last_difficulty, player_lives, wave, ASTEROID_HP, MOTHERSHIP_HP, game_end_menu_y, game_over_music_played, game_mode
    ENEMY_FIRE_CHANCE = fire_chance
    ENEMY_SPEED = max(0.3, speed)
    last_difficulty = (fire_chance, speed)
    if fire_chance == 0.001:
        player_lives = 3
        ASTEROID_HP = 2
        MOTHERSHIP_HP = 10
    elif fire_chance == 0.003:
        player_lives = 2
        ASTEROID_HP = 3
        MOTHERSHIP_HP = 20
    else:
        player_lives = 1
        ASTEROID_HP = 5
        MOTHERSHIP_HP = 50
    wave = 0
    game_end_menu_y = HEIGHT//2 - 300
    game_over_music_played = False
    game_mode = "game"
    create_game()
    switch_state("game")

# Funkcja ustawiająca tryb bossa
def set_boss_mode():
    global ENEMY_FIRE_CHANCE, ENEMY_SPEED, last_difficulty, player_lives, wave, ASTEROID_HP, MOTHERSHIP_HP, game_end_menu_y, game_over_music_played, game_mode
    ENEMY_FIRE_CHANCE = 0.005
    ENEMY_SPEED = 2
    last_difficulty = (0.005, 2)
    player_lives = 1
    ASTEROID_HP = 5
    MOTHERSHIP_HP = 50
    wave = 2
    game_end_menu_y = HEIGHT//2 - 300
    game_over_music_played = False
    game_mode = "game"
    create_boss_mode()
    switch_state("game")

# Funkcja ustawiająca tryb gry z bossem
def set_boss_game():
    global player_lives, ASTEROID_HP, MOTHERSHIP_HP, game_end_menu_y, game_over_music_played, game_mode
    player_lives = 1
    ASTEROID_HP = 5
    MOTHERSHIP_HP = 50
    game_end_menu_y = HEIGHT//2 - 300
    game_over_music_played = False
    game_mode = "boss_game"
    create_boss_game()
    switch_state("boss_game")

# Funkcja restartująca grę
def restart_game():
    if game_mode == "boss_game":
        set_boss_game()
    else:
        set_difficulty(*last_difficulty)

# Funkcja przełączająca stan gry
def switch_state(s):
    global state, previous_state, can_shoot, volume_return_state
    if s == "volume":
        volume_return_state = state
    elif s == "pause":
        if previous_state not in ["game", "boss_game"]:
            previous_state = "game" if game_mode == "game" else "boss_game"
    elif s in ["game", "boss_game"]:
        previous_state = None
        volume_return_state = None
    state = s
    can_shoot = (s in ["game", "boss_game"])
    pygame.event.clear(pygame.MOUSEBUTTONDOWN)

# Funkcja ładująca klatki animacji eksplozji
def load_explosion_frames(sheet_path, num_frames):
    frame_width, frame_height = 128, 128
    sheet = pygame.image.load(resource_path(sheet_path)).convert_alpha()
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frame = sheet.subsurface(rect)
        frames.append(frame)
    return frames

# Funkcja ładująca klatki animacji odradzania gracza
def load_player_respawn_frames(sheet_path, frame_w=128, frame_h=128, cols=8, rows=8):
    sheet = pygame.image.load(resource_path(sheet_path)).convert_alpha()
    frames = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frame = sheet.subsurface(rect)
            frames.append(frame)
    return frames

# Definicja przycisków menu
play_button = Button("GRAJ", WIDTH//2 - 100, HEIGHT//2 + 120, 200, 60, lambda: switch_state("select"))
volume_button = Button("GŁOŚNOŚĆ", WIDTH//2 - 100, HEIGHT//2 + 200, 200, 60, lambda: switch_state("volume"))
testers_button = Button("TESTERZY", WIDTH//2 - 100, HEIGHT//2 + 280, 200, 60, lambda: switch_state("testers"))
exit_button = Button("ZAMKNIJ", WIDTH//2 - 100, HEIGHT//2 + 360, 200, 60, lambda: sys.exit())
easy = Button("Łatwy", WIDTH//2 - 90, HEIGHT//2 - 150, 180, 60, lambda: set_difficulty(0.001, 0.3))
medium = Button("Średni", WIDTH//2 - 90, HEIGHT//2 - 50, 180, 60, lambda: set_difficulty(0.003, 1))
hard = Button("Trudny", WIDTH//2 - 90, HEIGHT//2 + 50, 180, 60, lambda: set_difficulty(0.005, 2))
boss = Button("Boss", WIDTH//2 - 90, HEIGHT//2 + 150, 180, 60, set_boss_game)
back_button_select = Button("Powrót", WIDTH//2 - 90, HEIGHT//2 + 250, 180, 60, reset_to_menu, pygame.K_RETURN)
back_button_testers = Button("Powrót", WIDTH//2 - 100, 0, 200, 60, reset_to_menu, pygame.K_RETURN)
pause_buttons = [
    Button("1. Wznów", WIDTH//2 - 100, HEIGHT//2 - 175, 200, 60, lambda: switch_state(previous_state), pygame.K_1),
    Button("2. Restart", WIDTH//2 - 100, HEIGHT//2 - 105, 200, 60, restart_game, pygame.K_2),
    Button("3. Menu", WIDTH//2 - 100, HEIGHT//2 - 35, 200, 60, reset_to_menu, pygame.K_3),
    Button("4. Cofnij", WIDTH//2 - 100, HEIGHT//2 + 35, 200, 60, try_restore, pygame.K_4),
    Button("5. Głośność", WIDTH//2 - 100, HEIGHT//2 + 105, 200, 60, lambda: switch_state("volume"), pygame.K_5),
    Button("6. Wyjście", WIDTH//2 - 100, HEIGHT//2 + 175, 200, 60, lambda: sys.exit(), pygame.K_6)]
volume_menu = VolumeMenu()

# Inicjalizacja gry
create_game()
explosion_frames = load_explosion_frames("Obiekty/eksplozja.png", 12)
explosions = pygame.sprite.Group()
hit_effects = pygame.sprite.Group()
player_respawn_effects = pygame.sprite.Group()
motherships = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
player_respawn_frames = load_player_respawn_frames("Obiekty/animacja_gracza.png")

# Główna pętla gry
async def main():
    global can_shoot, game_over, game_won, respawning, respawn_timer, enemy_direction, score, player_lives, life_lost_message, life_lost_message_timer, last_save, last_asteroid_spawn, win_music_played, game_end_menu_y, game_over_music_played
    game_end_menu = None
    testers = ["1glotta", "Gmblr", "BillyChappo"]
    while True:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if state in ["game", "boss_game"] and not game_over and not game_won:
                    if can_shoot and e.button in [1, 3]:
                        bullets.add(Bullet(player.rect.centerx, player.rect.top, -1, True))
                        can_shoot = True
                elif state == "volume":
                    volume_menu.handle_event(e)
                elif state == "game_end" and game_end_menu:
                    game_end_menu.handle_event(e, mouse_pos)
                elif state == "testers":
                    if back_button_testers.rect.collidepoint(e.pos):
                        back_button_testers.click()
                else:
                    all_buttons = []
                    if state == "menu":
                        all_buttons = [play_button, volume_button, testers_button, exit_button]
                    elif state == "select":
                        all_buttons = [easy, medium, hard, boss, back_button_select]
                    elif state == "pause":
                        all_buttons = pause_buttons
                    for b in all_buttons:
                        if b.rect.collidepoint(e.pos):
                            b.click()
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button in [1, 3]:
                    can_shoot = True
                if state == "volume":
                    volume_menu.handle_event(e)
            if e.type == pygame.MOUSEMOTION:
                if state == "volume":
                    volume_menu.handle_event(e)
                elif state == "game_end" and game_end_menu:
                    for b in game_end_menu.buttons:
                        b.check_hover(mouse_pos)
                elif state == "testers":
                    back_button_testers.check_hover(mouse_pos)
                else:
                    all_buttons = []
                    if state == "menu":
                        all_buttons = [play_button, volume_button, testers_button, exit_button]
                    elif state == "select":
                        all_buttons = [easy, medium, hard, boss, back_button_select]
                    elif state == "pause":
                        all_buttons = pause_buttons
                    for b in all_buttons:
                        b.check_hover(mouse_pos)
            if e.type == pygame.KEYDOWN:
                if state == "pause":
                    for b in pause_buttons:
                        if b.key == e.key:
                            b.click()
                if state == "select":
                    if e.key == back_button_select.key:
                        back_button_select.click()
                if state == "testers":
                    if e.key == back_button_testers.key:
                        back_button_testers.click()
                if e.key == pygame.K_SPACE:
                    if state in ["game", "boss_game"] and not game_over and not game_won and can_shoot:
                        bullets.add(Bullet(player.rect.centerx, player.rect.top, -1, True))
                        can_shoot = False
                if e.key == pygame.K_ESCAPE:
                    if state in ["game", "boss_game"]:
                        switch_state("pause")
                    elif state == "pause":
                        switch_state(previous_state)
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_SPACE:
                    can_shoot = True
        if state == "menu":
            screen.blit(menu_background, (0, 0))
            draw_text("Space Invaders", big_font, WHITE, WIDTH//2, HEIGHT//6)
            draw_text("Autorzy projektu:", font, WHITE, WIDTH//2, HEIGHT//3)
            draw_text("Kewin Kisiel 197866", font, WHITE, WIDTH//2, HEIGHT//3 + 50)
            draw_text("Mateusz Kuczerowski 197900", font, WHITE, WIDTH//2, HEIGHT//3 + 100)
            for b in [play_button, volume_button, testers_button, exit_button]:
                b.check_hover(mouse_pos)
                b.draw()
        elif state == "select":
            screen.blit(select_background, (0, 0))
            draw_text("Wybierz poziom trudności", big_font, WHITE, WIDTH//2, HEIGHT//4)
            for b in [easy, medium, hard, boss, back_button_select]:
                b.check_hover(mouse_pos)
                b.draw()
        elif state == "testers":
            screen.blit(testers_background, (0, 0))
            draw_text("W projekcie pomogli testerzy:", big_font, WHITE, WIDTH//2, 100)
            y_base = HEIGHT // 2 - 250
            y_image = y_base + 50
            draw_text("1glotta", font, WHITE, WIDTH // 4, y_base)
            img_rect1 = tester_images[0].get_rect(center=(WIDTH // 4, y_image + 150))
            screen.blit(tester_images[0], img_rect1)
            draw_text("Gmblr", font, WHITE, 3 * WIDTH // 4, y_base)
            img_rect2 = tester_images[1].get_rect(center=(3 * WIDTH // 4, y_image + 150))
            screen.blit(tester_images[1], img_rect2)
            draw_text("BillyChappo", font, WHITE, WIDTH // 2, y_base)
            img_rect3 = tester_images[2].get_rect(center=(WIDTH // 2, y_image + 150))
            screen.blit(tester_images[2], img_rect3)
            back_button_testers.rect.center = (WIDTH // 2, y_image + 150 + 250)
            back_button_testers.draw()
            back_button_testers.check_hover(mouse_pos)
        elif state == "pause":
            screen.blit(game_background, (0, 0))
            pause_menu()
            for b in pause_buttons:
                b.check_hover(mouse_pos)
        elif state == "volume":
            screen.blit(game_background, (0, 0))
            volume_menu.draw()
        elif state == "game" or state == "boss_game" or state == "game_end":
            screen.blit(game_background, (0, 0))
            explosions.update()
            explosions.draw(screen)
            player_respawn_effects.update()
            player_respawn_effects.draw(screen)
            hit_effects.update()
            hit_effects.draw(screen)
            if state == "game" and not game_over and not game_won:
                player.update(keys)
                if respawning:
                    now = pygame.time.get_ticks()
                    if now - respawn_timer < 2000:
                        offset = 5 if (now // 100) % 2 == 0 else -5
                        player.rect.x += offset
                    else:
                        respawning = False
                bullets.update()
                enemy_bullets.update()
                enemies.update()
                motherships.update()
                asteroids.update()
                if len(enemies) == 0 and len(motherships) == 0:
                    if wave == 1:
                        spawn_new_wave()
                    elif wave == 2:
                        create_mothership()
                move_down = False
                for i, enemy in enumerate(enemies):
                    enemy.update_position(ENEMY_SPEED * enemy_direction)
                    if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                        move_down = True
                    if random.random() < ENEMY_FIRE_CHANCE:
                        bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, 1, False)
                        enemy_bullets.add(bullet)
                if move_down:
                    enemy_direction *= -1
                    for enemy in enemies:
                        enemy.update_position(0, ENEMY_DROP)
                for mothership in motherships:
                    if random.random() < MOTHERSHIP_FIRE_CHANCE:
                        bullet = Bullet(mothership.rect.centerx, mothership.rect.bottom, 1, False, is_boss=True)
                        enemy_bullets.add(bullet)
                    if time.time() - last_asteroid_spawn > ASTEROID_SPAWN_INTERVAL:
                        asteroids.add(Asteroid(mothership.rect.centerx, mothership.rect.bottom))
                        last_asteroid_spawn = time.time()
                hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
                for enemy_list in hits.values():
                    for enemy in enemy_list:
                        explosions.add(Explosion(enemy.rect.centerx, enemy.rect.centery, explosion_frames))
                        explosion_sound.play()
                score += len(hits)
                for bullet in pygame.sprite.groupcollide(bullets, motherships, True, False):
                    for mothership in pygame.sprite.spritecollide(bullet, motherships, False):
                        mothership.hit()
                        score += 1
                for bullet in pygame.sprite.groupcollide(bullets, asteroids, True, False):
                    for asteroid in pygame.sprite.spritecollide(bullet, asteroids, False):
                        asteroid.hit()
                        score += 1
                for bullet in pygame.sprite.groupcollide(bullets, obstacles, True, False):
                    for obs in pygame.sprite.spritecollide(bullet, obstacles, False):
                        obs.hit()
                for bullet in pygame.sprite.groupcollide(enemy_bullets, obstacles, True, False):
                    for obs in pygame.sprite.spritecollide(bullet, obstacles, False):
                        obs.hit()
                if not respawning and pygame.sprite.spritecollide(player, enemy_bullets, True):
                    player_lives -= 1
                    life_lost_message = True
                    life_lost_message_timer = pygame.time.get_ticks()
                    if player_lives > 0:
                        hit_effects.add(HitEffect(player.rect.centerx, player.rect.centery))
                    player_respawn_effects.add(PlayerRespawnAnimation(player.rect.centerx, player.rect.centery))
                    if player_lives <= 0:
                        game_over = True
                        game_end_menu = GameEndMenu(True)
                        game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                        if not game_over_music_played:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(resource_path("Muzyka/przegrana.mp3"))
                            pygame.mixer.music.set_volume(music_volume)
                            pygame.mixer.music.play(-1)
                            game_over_music_played = True
                        switch_state("game_end")
                    else:
                        respawning = True
                        respawn_timer = pygame.time.get_ticks()
                if not respawning and pygame.sprite.spritecollide(player, asteroids, True):
                    player_lives -= 1
                    life_lost_message = True
                    life_lost_message_timer = pygame.time.get_ticks()
                    if player_lives > 0:
                        hit_effects.add(HitEffect(player.rect.centerx, player.rect.centery))
                    player_respawn_effects.add(PlayerRespawnAnimation(player.rect.centerx, player.rect.centery))
                    if player_lives <= 0:
                        game_over = True
                        game_end_menu = GameEndMenu(True)
                        game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                        if not game_over_music_played:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(resource_path("Muzyka/przegrana.mp3"))
                            pygame.mixer.music.set_volume(music_volume)
                            pygame.mixer.music.play(-1)
                            game_over_music_played = True
                        switch_state("game_end")
                    else:
                        respawning = True
                        respawn_timer = pygame.time.get_ticks()
                if any(enemy.rect.bottom >= player.rect.top for enemy in enemies):
                    game_over = True
                    game_end_menu = GameEndMenu(True)
                    game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                    if not game_over_music_played:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(resource_path("Muzyka/przegrana.mp3"))
                        pygame.mixer.music.set_volume(music_volume)
                        pygame.mixer.music.play(-1)
                        game_over_music_played = True
                    switch_state("game_end")
                if len(motherships) == 0 and wave == 3:
                    game_won = True
                    game_end_menu = GameEndMenu(False)
                    game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                    switch_state("game_end")
                if time.time() - last_save >= 1:
                    save_state()
                    last_save = time.time()
            elif state == "boss_game" and not game_over and not game_won:
                player.update(keys)
                if respawning:
                    now = pygame.time.get_ticks()
                    if now - respawn_timer < 2000:
                        offset = 5 if (now // 100) % 2 == 0 else -5
                        player.rect.x += offset
                    else:
                        respawning = False
                bullets.update()
                enemy_bullets.update()
                motherships.update()
                asteroids.update()
                for mothership in motherships:
                    if random.random() < MOTHERSHIP_FIRE_CHANCE:
                        bullet = Bullet(mothership.rect.centerx, mothership.rect.bottom, 1, False, is_boss=True)
                        enemy_bullets.add(bullet)
                    if time.time() - last_asteroid_spawn > ASTEROID_SPAWN_INTERVAL:
                        asteroids.add(Asteroid(mothership.rect.centerx, mothership.rect.bottom))
                        last_asteroid_spawn = time.time()
                for bullet in pygame.sprite.groupcollide(bullets, motherships, True, False):
                    for mothership in pygame.sprite.spritecollide(bullet, motherships, False):
                        mothership.hit()
                        score += 1
                for bullet in pygame.sprite.groupcollide(bullets, asteroids, True, False):
                    for asteroid in pygame.sprite.spritecollide(bullet, asteroids, False):
                        asteroid.hit()
                        score += 1
                for bullet in pygame.sprite.groupcollide(bullets, obstacles, True, False):
                    for obs in pygame.sprite.spritecollide(bullet, obstacles, False):
                        obs.hit()
                for bullet in pygame.sprite.groupcollide(enemy_bullets, obstacles, True, False):
                    for obs in pygame.sprite.spritecollide(bullet, obstacles, False):
                        obs.hit()
                if not respawning and pygame.sprite.spritecollide(player, enemy_bullets, True):
                    player_lives -= 1
                    life_lost_message = True
                    life_lost_message_timer = pygame.time.get_ticks()
                    if player_lives > 0:
                        hit_effects.add(HitEffect(player.rect.centerx, player.rect.centery))
                    player_respawn_effects.add(PlayerRespawnAnimation(player.rect.centerx, player.rect.centery))
                    if player_lives <= 0:
                        game_over = True
                        game_end_menu = GameEndMenu(True)
                        game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                        if not game_over_music_played:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(resource_path("Muzyka/przegrana.mp3"))
                            pygame.mixer.music.set_volume(music_volume)
                            pygame.mixer.music.play(-1)
                            game_over_music_played = True
                        switch_state("game_end")
                    else:
                        respawning = True
                        respawn_timer = pygame.time.get_ticks()
                if not respawning and pygame.sprite.spritecollide(player, asteroids, True):
                    player_lives -= 1
                    life_lost_message = True
                    life_lost_message_timer = pygame.time.get_ticks()
                    if player_lives > 0:
                        hit_effects.add(HitEffect(player.rect.centerx, player.rect.centery))
                    player_respawn_effects.add(PlayerRespawnAnimation(player.rect.centerx, player.rect.centery))
                    if player_lives <= 0:
                        game_over = True
                        game_end_menu = GameEndMenu(True)
                        game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                        if not game_over_music_played:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(resource_path("Muzyka/przegrana.mp3"))
                            pygame.mixer.music.set_volume(music_volume)
                            pygame.mixer.music.play(-1)
                            game_over_music_played = True
                        switch_state("game_end")
                    else:
                        respawning = True
                        respawn_timer = pygame.time.get_ticks()
                if len(motherships) == 0:
                    game_won = True
                    game_end_menu = GameEndMenu(False)
                    game_end_menu_y = HEIGHT//2 - game_end_menu.menu_height//2
                    switch_state("game_end")
                if time.time() - last_save >= 1:
                    save_state()
                    last_save = time.time()
            if game_won and not win_music_played:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(resource_path("Muzyka/wygrana.ogg"))
                pygame.mixer.music.set_volume(music_volume)
                pygame.mixer.music.play(-1)
                win_music_played = True
            pygame.sprite.GroupSingle(player).draw(screen)
            bullets.draw(screen)
            enemy_bullets.draw(screen)
            enemies.draw(screen)
            for mothership in motherships:
                mothership.draw(screen)
            for asteroid in asteroids:
                asteroid.draw(screen)
            for obs in obstacles:
                obs.draw(screen)
            for i in range(player_lives):
                screen.blit(heart_image, (20 + i * 50, 20))
            draw_text(f"Wynik: {score}", font, WHITE, WIDTH - 150, 30)
            if life_lost_message and pygame.time.get_ticks() - life_lost_message_timer < 1000:
                draw_text("-1 Życie", font, RED, WIDTH//2, HEIGHT//2 - 50)
            if state == "game_end" and game_end_menu:
                game_end_menu.draw()
        pygame.display.flip()
        await asyncio.sleep(1.0 / 60)

# Uruchomienie gry w zależności od platformy
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())