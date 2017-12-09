import pygame
import random
import math

from PlayerShip import *
from Bullet import *
from Enemy import *
from Bosses import *
from Menu import *
from PowerUp import *
from Intro import *
from Constants import *

class Game():
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Ragnarok The Game')
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_highscore()
        self.alive = True
        self.pause = False
        self.background_y = 0

    def load_highscore(self):
        f = open('highscore.txt', 'r')
        temp = f.read()
        if temp != "":
            self.highscore = int(temp)
        else:
            self.highscore = 0
        f.close()

    def write_highscore(self):
        if self.score >= self.highscore:
            f = open('highscore.txt', 'w')
            f.write(str(self.score))
            f.close()

    def new_game(self):
        #List of all sprites
        self.sprites_list = pygame.sprite.Group()
        #List of bullets
        self.bullet_list = pygame.sprite.Group()
        self.boss_bullet_list = pygame.sprite.Group()
        #BOSS
        self.boss_list = pygame.sprite.Group()
        #List of all enemies
        self.enemy_list = pygame.sprite.Group()
        #List of mobs
        self.mob_list = pygame.sprite.Group()
        #List of PowerUps
        self.power_up_list = pygame.sprite.Group()
        #List of meteor
        self.meteor_list = pygame.sprite.Group()
        #Creating sprites
        self.player = PlayerShip(SCREEN_WIDTH, SCREEN_HEIGHT, [self.sprites_list])

        #Game Properties
        self.score = 0
        self.current_level = 0
        self.difficulty = 10

        #Player Properties
        self.bullet_speed = 5

        #Enemies Properties
        self.boss_speed = 1
        self.boss_bullet_speed = 5
        self.enemies_speed = math.sqrt(10 + self.current_level)
        self.boss_id = 0

        #Setting up firing bullet delay
        self.fire_bullet_event = pygame.USEREVENT + 1
        self.fire_bullet_delay = 500
        pygame.time.set_timer(self.fire_bullet_event, self.fire_bullet_delay)

        #Setting up the boss firing bullet delay
        self.boss_bullet_event = pygame.USEREVENT + 2
        self.boss_bullet_delay = 100
        self.boss_bullet_counter = 0
        pygame.time.set_timer(self.boss_bullet_event, self.boss_bullet_delay)
        self.run()

    def intro(self):
        self.intro = Intro(self.screen,SCREEN_WIDTH,SCREEN_HEIGHT, ARCADE_FUNK)
        self.intro.show_intro(self.screen)
        self.background = pygame.image.load(BACKGROUND_IMG).convert()
        self.new_game()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def draw(self):
        # Game Loop - draw
        if not self.pause and self.alive:
            relative_y = self.background_y % self.background.get_rect().height
            self.screen.blit(self.background, [0, relative_y - self.background.get_rect().height])
            if relative_y < SCREEN_HEIGHT:
                self.screen.blit(self.background, [0, relative_y])
            self.background_y += 1
        # *after* drawing everything, flip the display
        self.screen.blit(pygame.font.SysFont("'freesansbold.ttf", 60, True).render(str(self.score), 1, (91, 109, 131)), (SCREEN_WIDTH-100,50 ))
        if self.boss_list:
            self.boss.update_health_bar()
        self.sprites_list.draw(self.screen)
        pygame.display.flip()

    def events(self):
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #update highscore when you quit
                self.write_highscore()
                self.playing = False
                self.running = False

            if self.alive and event.type == self.fire_bullet_event and not self.pause:
                self.fire_bullet(self.player, self.bullet_speed, self.fire_bullet_event, self.fire_bullet_delay, [self.sprites_list, self.bullet_list])
            # update the boss bullet
            if self.alive and event.type == self.boss_bullet_event and not self.pause:
                if self.boss_list:
                    self.boss_fire_bullet(self.boss_list.sprites()[0], self.boss_bullet_speed, [self.sprites_list, self.boss_bullet_list])
                    self.boss_bullet_counter += 1
                    if self.boss_bullet_counter >= 2:
                        pygame.time.set_timer(self.boss_bullet_event, 2500)
                        self.boss_bullet_counter = 0
                    else:
                        pygame.time.set_timer(self.boss_bullet_event, self.boss_bullet_delay)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (not self.alive):
                    #update highscore when you press r
                    self.write_highscore()
                    self.alive = True
                    self.intro.show_intro(self.screen)
                    self.new_game()
                if self.pause:
                    if event.key == pygame.K_r and self.alive:
                        self.pause = False
                        self.intro.show_intro(self.screen)
                        self.new_game()
                if event.key == pygame.K_n and (not self.alive):
                    #update highscore when you press n
                    self.write_highscore()
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_ESCAPE and self.alive:
                    if not self.pause:
                        self.pause = True
                        self.temp_speed = [self.enemies_speed, self.bullet_speed, self.boss_bullet_speed]
                        for enemy in self.enemy_list:
                            enemy.pause = True
                        for bullet in self.bullet_list:
                            bullet.pause = True
                        for bullet in self.boss_bullet_list:
                            bullet.pause = True
                        for power_up in self.power_up_list:
                            power_up.pause = True
                        self.player.pause = True
                        if self.boss_list:
                            self.boss.pause = True
                    else:
                        self.pause = False
                        for enemy in self.enemy_list:
                            enemy.pause = False
                        for bullet in self.bullet_list:
                            bullet.pause = False
                        for bullet in self.boss_bullet_list:
                            bullet.pause = False
                        for power_up in self.power_up_list:
                            power_up.pause = False
                        self.player.pause = False
                        if self.boss_list:
                            self.boss.pause = False

    def update(self):
        self.sprites_list.update()

        if self.alive and not self.pause:
            # player colliding with enemy
            enemy_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_list, True)
            if enemy_hit_list:
                pygame.mixer.Channel(4).play(pygame.mixer.Sound('Sound/killed_explo.ogg'))
                self.alive = False

            #Increase speed of bullets if get power up
            power_up_hit_list = pygame.sprite.spritecollide(self.player, self.power_up_list, False)
            for hit in power_up_hit_list:
                hit.kill()
                if self.fire_bullet_delay >= 150:
                    self.fire_bullet_delay -= 50

            for bullet in self.bullet_list:
                enemies_hit_list = pygame.sprite.spritecollide(bullet, self.mob_list, False)
                for enemy in enemies_hit_list:
                    enemy.health -= 1
                    bullet.kill()
                    if enemy.health <= 0:
                        enemy.kill()
                        #Spawn power ups
                        if not self.power_up_list:
                            if random.randint(0,100) < POWERUP_PERCENTAGE:
                                self.spawn_power_ups(self.enemies_speed * 1.5, enemy.rect.x, enemy.rect.y, [self.power_up_list, self.sprites_list])
                        self.score += 1
                        pygame.mixer.Channel(3).play(pygame.mixer.Sound('Sound/explo.ogg'))
                        pygame.mixer.Channel(3).set_volume(0.5)

                #when player bullet colliding boss
                boss_hit_list = pygame.sprite.spritecollide(bullet, self.boss_list, False)
                for boss in boss_hit_list:
                     bullet.kill()
                     boss.is_hit()

                     if not boss.is_alive():
                         self.current_level += 1
                         self.score += 100
                         boss.kill()
                         # can add sound here
                         for boss_bullet in self.boss_bullet_list:
                             boss_bullet.kill()
    ##                     boss_bullet.kill()
    ##                     if boss_bullet_delay >= 500:
    ##                        boss_bullet_delay -= 100


                #if player bullet goes off screen
                if bullet.rect.y < -10:
                    bullet.kill()
            # when player colliding boss bullet
            player_hit_list = pygame.sprite.spritecollide(self.player, self.boss_bullet_list, False)
            if player_hit_list:
                    pygame.mixer.Channel(4).play(pygame.mixer.Sound('Sound/killed_explo.ogg'))
                    self.alive = False

            #Kill bullet if it hits meteors
            for meteor in self.meteor_list:
                meteor_hit_list = pygame.sprite.spritecollide(meteor, self.bullet_list, True)

           #Spawn enemies if there aren't any, levels and speeds fix later
            if not self.mob_list and not self.boss_list:
                if self.current_level % 5 != 0 or self.current_level == 0:
                    self.spawn_enemy(self.enemies_speed, self.current_level, self.difficulty, [self.enemy_list, self.mob_list, self.sprites_list])
                    self.current_level += 1
                else:
                    self.boss_id += 1
                    self.spawn_boss(self.boss_speed,self.screen, self.current_level, self.boss_id, [self.boss_list,self.boss_bullet_list, self.sprites_list])

            #Spawn meteor:
            if not self.meteor_list and not self.boss_list:
                if self.current_level % 5 == 0:
                    self.spawn_meteor(self.enemies_speed * 2,  [self.enemy_list, self.meteor_list, self.sprites_list])

            for sprite in self.sprites_list :
                #If enemies go off screen
                if sprite.rect.y > SCREEN_HEIGHT:
                    sprite.kill()
        #m = Menu(screen_width/2,screen_height/2)
        if not self.alive:
            if self.score > self.highscore:
                self.highscore = self.score
           # sprites_list.remove(player))
            Menu(SCREEN_WIDTH,SCREEN_HEIGHT).displayMenu(self.screen,"c",self.score,self.highscore)
            for sprite in self.sprites_list:
                sprite.kill()

        elif self.pause :
            Menu(SCREEN_WIDTH,SCREEN_HEIGHT).displayMenu(self.screen, "b")
            #Erm, why is pressing R doesn't make it go back to screen can someone fix

    #Spawning enemies
    def spawn_enemy(self, speed, current_level, difficulty, groups):
        health = int(current_level / difficulty) + 1
        for i in range (5):
            enemy = Enemy(speed, health, groups)
            enemy.rect.x = 10 + 100*i
            enemy.rect.y = -50

    def spawn_power_ups(self, speed, pos_x, pos_y, groups):
        power_up = PowerUp(SCREEN_WIDTH, SCREEN_HEIGHT, speed, groups)
        power_up.rect.x = pos_x
        power_up.rect.y = pos_y

    def spawn_meteor(self, speed, groups):
        pygame.mixer.Channel(2).play(pygame.mixer.Sound('Sound/comet.ogg'))
        pygame.mixer.Channel(2).set_volume(0.8)
        meteor = Meteor(speed, groups)
        meteor.rect.y = -200
        meteor.rect.x = random.randrange(0, SCREEN_WIDTH - meteor.rect.width)

    #!!!!!!!!!!!!! can add different boss images!!
    def spawn_boss(self, speed, screen, current_level, boss_id, groups):
        self.boss = Boss(boss_id,screen,SCREEN_WIDTH, speed, current_level, groups)
        self.boss.rect.x = SCREEN_WIDTH/2 - self.boss.rect.width/2
        self.boss.rect.y = 50

    def fire_bullet(self, player, bullet_speed, fire_bullet_event, fire_bullet_delay, groups):
        pygame.mixer.Channel(1).play(pygame.mixer.Sound('Sound/laser.ogg'))
        pygame.mixer.Channel(1).set_volume(0.2)
        bullet = Bullet((player.rect.x + player.image.get_rect().width/2), player.rect.y, bullet_speed, groups)
        pygame.time.set_timer(fire_bullet_event, fire_bullet_delay)

    def boss_fire_bullet(self, boss, boss_bullet_speed, groups):
        #can add music
    ##    pygame.mixer.Channel(1).play(pygame.mixer.Sound('Sound/laser.ogg'))
    ##    pygame.mixer.Channel(1).set_volume(0.2)
        # if boss.boss_id ==1 the bullet is like this, we could also add boss_id ==2 or more than that if we want different bosses with different bullets
        if boss.boss_id == 1:
            Boss_Bullet(boss,(boss.rect.x + boss.image.get_rect().width/2 - 50), boss.rect.y + boss.image.get_rect().height, boss_bullet_speed, groups)
            Boss_Bullet(boss,(boss.rect.x + boss.image.get_rect().width/2), boss.rect.y + boss.image.get_rect().height, boss_bullet_speed, groups)
            Boss_Bullet(boss,(boss.rect.x + boss.image.get_rect().width/2 + 50), boss.rect.y + boss.image.get_rect().height, boss_bullet_speed, groups)
    ##    pygame.time.set_timer(boss_bullet_event, 0)


g = Game()
g.intro()
while g.running:
    g.new_game()

pygame.quit()