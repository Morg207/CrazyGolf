import pygame
import random
import sys
import math

pygame.init()
FPS = 60
clock = pygame.time.Clock()
running = True
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 681
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("Crazy Golf")
background_image = pygame.image.load("Bitmaps/background.png").convert_alpha()
barrier1_image = pygame.image.load("Bitmaps/barrier1.png").convert_alpha()
barrier2_image = pygame.image.load("Bitmaps/barrier2.png").convert_alpha()
hole_image = pygame.image.load("Bitmaps/hole.png").convert_alpha()
hole_image = pygame.transform.smoothscale_by(hole_image,0.26)
icon_image = pygame.image.load("Bitmaps/icon.ico")
icon_image = pygame.transform.smoothscale(icon_image,(32,32))
pygame.display.set_icon(icon_image)
gauge_colour = (255,255,255)
gauge_fill_colour = (212,255,93)
gauge_background_colour = (40,40,40)
pygame.mixer.music.load("Music/background music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)
level = 1
max_level = 3

#bad way to create levels but it does the job for now.
def gen_level1():
    barriers = [Barrier(80,153,barrier1_image),
            Barrier(463,80,barrier2_image)]
    hole = Hole(340,100)
    ball = Ball(WINDOW_WIDTH // 2,WINDOW_HEIGHT // 4 * 3,barriers,hole)
    shot_gauge = ShotGauge(ball)
    return (barriers,hole,ball,shot_gauge)

def gen_level2():
    barriers = [Barrier(80,455,barrier1_image),
            Barrier(463,457,barrier2_image),Barrier(310,380,barrier2_image)]
    hole = Hole(WINDOW_WIDTH // 2,WINDOW_HEIGHT // 4 * 3.5)
    ball = Ball(100,80,barriers,hole)
    shot_gauge = ShotGauge(ball)
    return (barriers,hole,ball,shot_gauge)

def gen_level3():
    barriers = [Barrier(158,230,barrier1_image),
            Barrier(541,230,barrier2_image),Barrier(387,155,barrier2_image)]
    hole = Hole(425,295)
    ball = Ball(100,80,barriers,hole)
    shot_gauge = ShotGauge(ball)
    return (barriers,hole,ball,shot_gauge)

def draw_text(text,x,y,size):
    font = pygame.font.Font("Fonts/retro.ttf",size)
    text_image = font.render(text,True,gauge_colour)
    text_rect = text_image.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    window.blit(text_image,text_rect)

class Hole():
    def __init__(self,x,y):
        self.image = hole_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
    
    def draw(self):
        window.blit(self.image,self.rect)

class Barrier():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        window.blit(self.image,self.rect)

class ShotGauge():
    def __init__(self,ball):
        self.ball = ball
        self.bar_length = 28
        self.bar_height = 100
        self.outline_rect = pygame.Rect(630,550,self.bar_length,self.bar_height)
        self.background_rect = pygame.Rect(630,550,self.bar_length,self.bar_height)
        self.fill_rect = pygame.Rect(self.outline_rect.x,self.outline_rect.top,self.outline_rect.width,0)

    def update(self):
        power_height = self.ball.vel.magnitude()
        if power_height > self.outline_rect.height:
            power_height = self.outline_rect.height
        self.fill_rect.height = power_height

    def draw(self):
        draw_text("Power",645,530,20)
        pygame.draw.rect(window,gauge_background_colour,self.background_rect,border_radius=4)
        pygame.draw.rect(window,gauge_fill_colour,self.fill_rect,border_radius=4)
        pygame.draw.rect(window,gauge_colour,self.outline_rect,border_radius=4,width=3)

class Ball():
    def __init__(self,x,y,barriers,hole):
        self.barriers = barriers
        self.hole = hole
        self.vel = pygame.Vector2(0,0)
        self.click_pos = pygame.Vector2(0,0)
        self.arrow_image = pygame.image.load("Bitmaps/arrow.png").convert_alpha()
        self.arrow_image = pygame.transform.smoothscale_by(self.arrow_image,0.32)
        self.arrow_image = pygame.transform.rotate(self.arrow_image,180)
        self.original_arrow_image = self.arrow_image.copy()
        self.ball_image = pygame.image.load("Bitmaps/ball.png").convert_alpha()
        self.ball_image = pygame.transform.smoothscale_by(self.ball_image,0.23)
        self.original_ball_image = self.ball_image.copy()
        self.ball_width = self.ball_image.get_width()
        self.ball_height = self.ball_image.get_height()
        self.ball_rect = self.ball_image.get_rect()
        self.ball_rect.centerx = x
        self.ball_rect.centery = y
        self.arrow_rect = self.arrow_image.get_rect()
        self.clicked = False
        self.in_hole = False
        self.hit = False
        self.moving = False
        self.friction = 0.05
        self.ball_offset = pygame.Vector2(0,-45)
        self.pivot = pygame.Vector2(self.ball_rect.centerx,self.ball_rect.centery)
        self.arrow_angle = 0
        self.ball_scale = 1
        self.score_radius = 20
        self.hit_sound = pygame.mixer.Sound("Sounds/hit.mp3")
        self.score_sound = pygame.mixer.Sound("Sounds/score.mp3")
        self.strokes = 0

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        if mouse_buttons[0] and not self.in_hole and not self.moving:
            self.hit = True
            self.calc_velocity()
        elif not mouse_buttons[0] and self.hit and self.vel.magnitude() > 0:
            self.strokes += 1
            self.hit_sound.play()
            self.hit = False
            self.moving = True
        else:
            self.clicked = False
            if self.moving:
               self.move()
            self.collide_with_barriers()
            self.collide_with_hole()
            self.collide_with_walls()

    def calc_velocity(self):
        if not self.clicked:
            self.vel = pygame.Vector2(0,0)
            mouse_pos = pygame.mouse.get_pos()
            self.pivot = pygame.Vector2(self.ball_rect.centerx,self.ball_rect.centery)
            self.click_pos = pygame.Vector2(mouse_pos[0],mouse_pos[1])
            self.clicked = True
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = pygame.Vector2(mouse_pos[0],mouse_pos[1])
        direction = pygame.Vector2(mouse_pos.x-self.click_pos.x,mouse_pos.y-self.click_pos.y)
        self.vel = -direction * 0.3
        self.arrow_angle = math.degrees(math.atan2(self.vel.y,self.vel.x))
        rotated_image = pygame.transform.rotate(self.original_arrow_image,-self.arrow_angle+90)
        rotated_offset = self.ball_offset.rotate(self.arrow_angle+90)
        rect = rotated_image.get_rect(center=self.pivot+rotated_offset)
        self.arrow_image = rotated_image
        self.arrow_rect = rect
        
    def move(self):
        self.vel.x -= self.friction * self.vel.x
        self.vel.y -= self.friction * self.vel.y
        if abs(self.vel.x) < 0.01:
            self.vel.x = 0
        if abs(self.vel.y) < 0.01:
            self.vel.y = 0
        if self.vel.magnitude() < 0.3:
            self.moving = False
        self.ball_rect.x += int(self.vel.x)
        self.ball_rect.y += int(self.vel.y)

    def collide_with_barriers(self):
        for barrier in self.barriers:
            new_x = self.ball_rect.x + self.vel.x
            new_y = self.ball_rect.y
            if pygame.Rect(new_x,new_y,self.ball_width,self.ball_height).colliderect(barrier.rect):
                 self.vel.x *= -1
                 if self.ball_rect.x + self.ball_width > barrier.rect.left and self.ball_rect.x + self.ball_width < barrier.rect.right:
                     self.ball_rect.x = barrier.rect.left - self.ball_width
                 if self.ball_rect.x < barrier.rect.right and self.ball_rect.x > barrier.rect.left:
                     self.ball_rect.x = barrier.rect.right
            new_x = self.ball_rect.x
            new_y = self.ball_rect.y + self.vel.y
            if pygame.Rect(new_x,new_y,self.ball_width,self.ball_height).colliderect(barrier.rect):
                 self.vel.y *= -1
                 if self.ball_rect.y < barrier.rect.bottom and self.ball_rect.y > barrier.rect.top:
                     self.ball_rect.y = barrier.rect.bottom
                 if self.ball_rect.y + self.ball_height > barrier.rect.top and self.ball_rect.y + self.ball_height < barrier.rect.bottom:
                     self.ball_rect.y = barrier.rect.top

    def collide_with_hole(self):
        if self.ball_rect.colliderect(self.hole.rect) and self.vel.magnitude() < 20:
                x_direction = self.ball_rect.centerx - self.hole.rect.centerx
                y_direction = self.ball_rect.centery - self.hole.rect.centery
                direction = pygame.Vector2(x_direction,y_direction)
                if direction.magnitude() < self.score_radius:
                    self.in_hole = True
                    self.ball_scale -= 0.02
                    self.ball_image = pygame.transform.smoothscale_by(self.original_ball_image,self.ball_scale)
                    self.ball_rect = self.ball_image.get_rect()
                    self.ball_rect.centerx = self.hole.rect.centerx
                    self.ball_rect.centery = self.hole.rect.centery
                    if self.ball_rect.width == 0 and self.ball_rect.height == 0:
                        self.score_sound.play()
                        global level
                        level += 1
                        if level > max_level:
                            level = 1
                        self.barriers.clear()
            
    def collide_with_walls(self):
        if self.ball_rect.x + self.ball_width > WINDOW_WIDTH:
            self.ball_rect.x = WINDOW_WIDTH - self.ball_width
            self.vel.x *= -1
        if self.ball_rect.x < 0:
            self.ball_rect.x = 0
            self.vel.x *= -1
        if self.ball_rect.y < 0:
            self.ball_rect.y = 0
            self.vel.y *= -1
        if self.ball_rect.y + self.ball_height > WINDOW_HEIGHT:
            self.ball_rect.y = WINDOW_HEIGHT-self.ball_height
            self.vel.y *= -1
            
    def draw(self):
        window.blit(self.ball_image,self.ball_rect)
        if self.clicked and not self.in_hole and self.vel.magnitude() > 0:
            window.blit(self.arrow_image,self.arrow_rect)

barriers,hole,ball,shot_gauge = gen_level1()

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.blit(background_image,(0,0))
    if len(barriers) == 0 and level == 1:
        barriers,hole,ball,shot_gauge = gen_level1()
    if len(barriers) == 0 and level == 2:
        barriers,hole,ball,shot_gauge = gen_level2()
    if len(barriers) == 0 and level == 3:
        barriers,hole,ball,shot_gauge = gen_level3()
    for barrier in barriers:
        barrier.draw()
    hole.draw()
    ball.update()
    ball.draw()
    shot_gauge.update()
    shot_gauge.draw()
    draw_text("Strokes: "+str(ball.strokes),90,600,20)
    pygame.display.update()
pygame.quit()
sys.exit()
