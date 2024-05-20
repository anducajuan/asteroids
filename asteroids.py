import pygame
import random
import math
from datetime import datetime, timedelta

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonte
font = pygame.font.Font(None, 36)

# Classe da Nave
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 25), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(5, 25), (15, 20), (25, 25), (15, 0)])
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.angle = 0
        self.lives = 3
        self.bullet_speed = 10
        self.bullet_count = 1
        self.multi_directions = [0]  # Inicialmente apenas uma direção
        

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            self.rect.x -= self.speed * math.sin(math.radians(self.angle))
            self.rect.y -= self.speed * math.cos(math.radians(self.angle))
        if self.angle > 360:
            self.angle = 0
        if self.angle < 0:
            self.angle = 359
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        bullets = []
        for direction in self.multi_directions:
            angle = self.angle + direction
            tip_x = self.rect.centerx - (self.rect.height / 2) * math.sin(math.radians(angle))
            tip_y = self.rect.centery - (self.rect.height / 2) * math.cos(math.radians(angle))
            bullets.append(Bullet((tip_x, tip_y), angle, self.bullet_speed))
        return bullets

    def apply_buff(self, buff_type):
        if buff_type == 'speed':
            if self.bullet_speed < 16:
                self.bullet_speed += 5
        elif buff_type == 'count':
            if self.bullet_count < 5:
                self.bullet_count += 1
        elif buff_type == 'multi_direction':
            num_directions = len(self.multi_directions)
            if num_directions < 2:
                self.multi_directions.append(180)  # Adiciona uma direção oposta (atrás)
            elif num_directions < 12:  # Limite de 12 direções
                step = 360 / (num_directions * 2)
                new_directions = [(num_directions * step), -(num_directions * step)]
                self.multi_directions.extend(new_directions)
                
# Classe Base do Asteroide
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, spaceship, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.color = color
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.speed = random.randint(1, 3)
        angle_to_ship = calculate_angle(self, spaceship)
        self.direction = angle_to_ship
        self.image = self.create_irregular_shape()
        self.rect = self.image.get_rect(center=self.rect.center)

    def create_irregular_shape(self):
        shape = pygame.Surface((40, 40), pygame.SRCALPHA)
        points = [(random.randint(10, 30), random.randint(10, 30)) for _ in range(8)]
        pygame.draw.polygon(shape, self.color, points)
        return shape

    def update(self):
        self.rect.x -= self.speed * math.sin(math.radians(self.direction))
        self.rect.y -= self.speed * math.cos(math.radians(self.direction))
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

# Classes de Asteroides Especiais
class GreenAsteroid(Asteroid):
    def __init__(self, spaceship):
        super().__init__(spaceship, GREEN)

class RedAsteroid(Asteroid):
    def __init__(self, spaceship):
        super().__init__(spaceship, RED)

class BlueAsteroid(Asteroid):
    def __init__(self, spaceship):
        super().__init__(spaceship, BLUE)

# Classe do Tiro
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, speed):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.angle = angle

    def update(self):
        self.rect.x -= self.speed * math.sin(math.radians(self.angle))
        self.rect.y -= self.speed * math.cos(math.radians(self.angle))
        if not screen.get_rect().contains(self.rect):
            self.kill()

def calculate_angle(obj_a, obj_b):
    delta_x = obj_b.rect.centerx - obj_a.rect.centerx
    delta_y = obj_b.rect.centery - obj_a.rect.centery
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return angle

def show_game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    screen.blit(overlay, (0, 0))

    game_over_text = font.render("Você perdeu todas as vidas", True, WHITE)
    restart_text = font.render("Pressione 'R' para reiniciar ou 'Q' para sair", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()

# Grupos de sprites
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Criação da nave
spaceship = Spaceship()
all_sprites.add(spaceship)

# Função para criar asteroides
def create_asteroid():
    if random.random() < 0.1:  # 10% de chance de ser um asteroide azul
        asteroid = BlueAsteroid(spaceship)
    elif random.random() < 0.2:  # 20% de chance de ser um asteroide especial (verde ou vermelho)
        asteroid = random.choice([GreenAsteroid, RedAsteroid])(spaceship)
    else:
        asteroid = Asteroid(spaceship)
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

def restart_game():
    global spaceship, asteroids_destroyed, spawn_timer, last_shoot
    all_sprites.empty()
    asteroids.empty()
    bullets.empty()

    spaceship = Spaceship()
    all_sprites.add(spaceship)

    for _ in range(5):
        create_asteroid()

    asteroids_destroyed = 0
    spawn_timer = 0
    last_shoot = datetime.now()
    

# Criação de asteroides iniciais
for _ in range(5):
    create_asteroid()

restart_game()

# Contador de asteroides destruídos
asteroids_destroyed = 0

# Loop principal
running = True
clock = pygame.time.Clock()
spawn_timer = 0
last_shoot = datetime.now() 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (datetime.now() - last_shoot) > timedelta(milliseconds=500): #Verifica se Espaço foi apertado e se o último tiro foi há mais de meio segundo
                last_shoot = datetime.now() #Reseta o tempo de contagem do último tiro
                bullets_fired = spaceship.shoot()
                for bullet in bullets_fired:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            if event.key == pygame.K_c:
                spaceship.lives = 99999

    # Atualização
    all_sprites.update()

    # Verificar colisões
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, asteroids, True)
        for hit in hits:
            bullet.kill()
            asteroids_destroyed += 1
            if isinstance(hit, GreenAsteroid):
                spaceship.apply_buff('speed')
            elif isinstance(hit, RedAsteroid):
                spaceship.apply_buff('count')
            elif isinstance(hit, BlueAsteroid):
                spaceship.apply_buff('multi_direction')
            create_asteroid()
    hits = pygame.sprite.spritecollide(spaceship, asteroids, True)
    if hits:
        spaceship.lives -= 1
        if spaceship.lives <= 0:
            show_game_over_screen()
            restart_game()
        else:
            for hit in hits:
                create_asteroid()

    # Desenhar na tela
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Mostrar contador de asteroides destruídos
    score_text = font.render(f"Asteroids Destroyed: {asteroids_destroyed}", True, WHITE)
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"Lives: {spaceship.lives}", True, WHITE)
    screen.blit(lives_text, (10, 50))

    # Mostrar níveis dos buffs
    speed_text = font.render(f"Bullet Speed: {spaceship.bullet_speed}", True, WHITE)
    screen.blit(speed_text, (10, 90))
    count_text = font.render(f"Bullet Count: {spaceship.bullet_count}", True, WHITE)
    screen.blit(count_text, (10, 130))
    multi_text = font.render(f"Multi-Directions: {len(spaceship.multi_directions)}", True, WHITE)
    screen.blit(multi_text, (10, 170))

    pygame.display.flip()

    # Aumentar a quantidade de asteroides com base no tempo
    spawn_timer += 1
    if spawn_timer > 400: 
        create_asteroid()
        spawn_timer = 0

    clock.tick(60)

pygame.quit()
