# Importing essential modules
import pygame
from pygame.locals import *
import sys
import math
from random import randint, choice
import time
import json

# initiating pygame
pygame.init()

# Creating a screen and clock
screen_width = 1250
screen_height = 750
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Defend your Cashews")
clock = pygame.time.Clock()
running_fps = 1440

# making a dictionary with all the essential images
images = {
    "weapons" : {
        
        "smg" : [
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/smg1.png").convert_alpha(),(100,100)), -90),
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/smg2.png").convert_alpha(),(100,100)), -90),
        ],
        "sniper" : [
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/sniper1.png").convert_alpha(),(250,125)), -90),
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/sniper2.png").convert_alpha(),(250,125)), -90),
        ],
        "glock" : [
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/glock2.png").convert_alpha(),(100,100)), -90),
            pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/glock1.png").convert_alpha(),(100,100)), -90),
        ]
    },
    
    "enemies" : {
        "zombie" : pygame.transform.flip(pygame.image.load("images/zombie.png").convert_alpha(), True, False),
        "big_buff" : pygame.transform.flip(pygame.image.load("images/buff_zombie.png").convert_alpha(), True, False),
        "fast_boi" : pygame.transform.flip(pygame.image.load("images/fast_zombie.png").convert_alpha(), True, False),
    },
    
    "wall" : [
        pygame.transform.scale(pygame.image.load("images/wall1.png").convert_alpha(), (int(600/3),int(1025/3))),
        pygame.transform.scale(pygame.image.load("images/wall2.png").convert_alpha(), (int(600/3),int(1025/3))),
        pygame.transform.scale(pygame.image.load("images/wall3.png").convert_alpha(), (int(600/3),int(1025/3))),
    ],
    "shop" : {
        "ammo" : pygame.transform.scale(pygame.image.load("images/ammo.png").convert_alpha(),(100,100)),
        "glock_levelup" : pygame.transform.scale(pygame.image.load("images/glock_levelup.png").convert_alpha(),(100,100)),
        "smg_levelup" : pygame.transform.scale(pygame.image.load("images/smg_levelup.png").convert_alpha(),(100,100)),
        "sniper_levelup" : pygame.transform.scale(pygame.image.load("images/sniper_levelup.png").convert_alpha(),(100,100)),
        "wall_heal" : pygame.transform.scale(pygame.image.load("images/wallheal.png").convert_alpha(),(100,100)),
    },
    "icons": {
        "smg" : pygame.image.load("images/smg_icon.png").convert_alpha(),
        "sniper" : pygame.image.load("images/sniper_icon.png").convert_alpha(),
        "glock" : pygame.image.load("images/glock_icon.png").convert_alpha(),
    },
    
    "player" : pygame.image.load("images/squirel.png"),
    "bullet" : pygame.transform.scale(pygame.image.load("images/BULLET.png").convert_alpha(),(18,18)),
    "background" : pygame.image.load("images/background.png").convert_alpha(),
    "ammodrop" : pygame.transform.scale(pygame.image.load("images/ammo.png").convert_alpha(),(75,75)),
    "coinimg" : pygame.transform.scale(pygame.image.load("images/coin.png").convert_alpha(),(75,75)),
    "coinimg2" : pygame.transform.scale(pygame.image.load("images/coin.png").convert_alpha(),(60,60)),
    "shop_bcg" : pygame.image.load("images/shop background.png").convert_alpha(),
    "scull" : pygame.transform.scale(pygame.image.load("images/scull.png").convert_alpha(), (75,75)),
    "cashew" : pygame.transform.scale(pygame.image.load("images/cashew.png").convert_alpha(), (75,75)),
    "settings_ui" : pygame.image.load("images/settings_ui.png").convert_alpha(),
    "selected" : pygame.image.load("images/selected.png").convert_alpha()
    
}

sounds = {
    "guns" : {
      "smg" : pygame.mixer.Sound("sounds/smg.mp3")  ,
      "glock" : pygame.mixer.Sound("sounds/glock_shot.mp3")  ,
      "sniper" : pygame.mixer.Sound("sounds/sniper.mp3"),
    },
    "switch_gun" : pygame.mixer.Sound("sounds/change_gun.mp3"),
    "collect_coins" : pygame.mixer.Sound("sounds/pickupsound.wav"),
    "healwall" : pygame.mixer.Sound("sounds/healwall.wav"),
    "enemyded" : pygame.mixer.Sound("sounds/enemyded.wav"),
    
}

class SaveManager():
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        
    def save(self):
        with open(str(filename)+".txt", "w") as file:
            for data in self.data:
                file.write(data+",")
        print("Data Saved!")
    def load(self):
        with open(str(filename)+".txt" "r") as file:
            text = file.read()
            text = text.split(",")
            for num,data in enumerate(text):
            
                self.data[num] = int(data)      
        print("Data Loaded!")

# Creating the Gun class (essentially the player)
class Gun(pygame.sprite.Sprite):
    def __init__(self, weapon, speed, rate, ammo,damage,canholddown):
        
        # unnecesary big line of code to set standart variables
        self.weapon,self.speed,self.rate,self.ammo,self.damage,self.hold = weapon, speed, rate,ammo,damage ,canholddown
        self.maxx,self.maxy = 250 ,230
        self.x,self.y = 250 ,230
        
        # creating variables essential for the shooting mechanism
        self.clicked = False
        self.timer = 0
        self.pew = 0
        
        # Setting the image and rect
        self.image = images["weapons"][self.weapon][self.pew]
        self.icon = images["icons"][self.weapon]

        self.rect = self.image.get_rect(center = (self.x,self.y))
        
        self.sound = sounds["guns"][self.weapon]
        
    # Update() function used for drawing the image and calling other functions
    def update(self):
        self.checkShoot()
        self.image = images["weapons"][self.weapon][self.pew]
        self.rotate()
        screen.blit(self.image, (self.rect.x,self.rect.y))   

    # Unnecesaraly long function to shoot , made as less dynamic as possible for
    # further customizabillity without the need of extra weird code
    
    def checkShoot(self):
        self.timer += 1 * dt
        
        # check if mouse is clicked
        mouse_pressed = pygame.mouse.get_pressed()

        # checking if the gun has full auto
        if not self.hold:
            
            # checking if mouse is pressed
            # and if pressed, creates a bullet and adds a cooldown
            
            if mouse_pressed[0] and not self.clicked and not pause:
                if self.ammo > 0:
                
                    newBullet = Bullet(self)
                    self.pew = 1
                    self.ammo -= 1
                    bulletGroup.add(newBullet)
                    self.sound.play()
                    self.clicked = True
                else:
                    print("no ammo")
                
            # resets cooldown when time is right
            if not mouse_pressed[0] and self.timer >= self.rate:
                self.clicked = False
                self.timer = 0
                self.pew = 0

        else:
            
            # checks if pressed but allows holding down left click and adds a small
            # cooldown so the game doesnt bug out a lot
            if mouse_pressed[0] and self.timer >= self.rate and not pause:
                if self.ammo >0:
                    
                    newBullet = Bullet(self)
                    bulletGroup.add(newBullet)
                    self.sound.play()
                    self.ammo -= 1
                    self.timer = 0
                    self.pew = 1
                    self.countdown = True
                else:
                    print("no ammo")

            else:
                self.pew = 0
                
    def rotate(self):
        self.pos = pygame.math.Vector2(self.rect.x,self.rect.y)
        rel_x,rel_y = pygame.mouse.get_pos() - self.pos
        self.angle = round(math.degrees(math.atan2(rel_x, rel_y)))
        self.image = pygame.transform.rotozoom(self.image, self.angle, 1)     
           
# Creating a the Bullet() class      
class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun):
        # this weird line of code i still dont know what it does
        pygame.sprite.Sprite.__init__(self)
        
        # taking some data from the assigned gun
        self.speed = gun.speed
        self.damage = gun.damage
        
        # coordinates with an offset
        self.x,self.y = gun.x + 50 ,gun.y +5
        
        # image stuff
        self.image = images["bullet"]
        self.rect = self.image.get_rect(center=(self.x,self.y))
        
        # very confusing line of code using math (im too stupid to explain
        # what it does)
        self.go_x,self.go_y = pygame.mouse.get_pos()
        self.angle = math.atan2(self.rect.y-self.go_y, self.rect.x-self.go_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

    def update(self):
        # moving to where the mouse was when the bullet was created
        self.rect.x -= self.x_vel  * dt 
        self.rect.y -= self.y_vel  * dt 
        
        # calling another function to check if the bullet is offscreen
        if self.offborder():
            self.kill()
        
        # function to check if the bullet is offscreen
    def offborder(self):
        if self.rect.x < -100:
            return True
        if self.rect.x > screen_width:
            return True
        if self.rect.y < -100:
            return True
        if self.rect.y > screen_height:
            return True
        return False
   
# Creating a class for the enemy 
class Enemy(pygame.sprite.Sprite):
    def __init__(self,hp,speed, damage, enemy):
        # same line of code that i have no idea what it does
        pygame.sprite.Sprite.__init__(self)
        # Creating a list with 3 positions that enemies can spawn in
        rows = [(screen_width, 650),(screen_width, 600),(screen_width, 500),]
        
        # assigning the image
        self.imageselect = images["enemies"][enemy]
        self.image = self.imageselect
        self.rotation = 0 
        self.multi = 1
        self.turn = False
        self.id = enemy
        
        # creating the coordinates we need to spawn enemies
        pos_x,pos_y = rows[randint(0, 2)]
        pos_x += prefix
        
        # creating the rect based on the image with the cords in the previous lines
        self.rect = self.image.get_rect(center = (pos_x,pos_y))
        
        # variable we need later to limit how often the enemy damages the wall
        self.attack_interval = 0
        
        # smaller but still big line of code that sets some typical variables
        self.hp,self.speed, self.damage = hp, speed, damage
    
    def update(self):
        global cashews, kills
        
        self.moving = self.rect.x <= end_of_run or wallup
        
        # checking if the enemy is past the end of run variable and if so starts attacking the wall
        if self.rect.x <= end_of_run and wallup :

            # damages the wall with a delay
            self.attack_interval += 1  * dt 
            if self.attack_interval >= 1:
                wall.hp -= self.damage * 3
                print("damaged")
                self.attack_interval = 0
                    
        if self.rect.x <= end_of_run and not wallup:
            # checks if enemy is offscreen and if so removes a life 
            # and kills the enemy
            self.rect.x -= self.speed  * dt
            if self.rect.x <= -50:
                cashews -= 1
                self.kill()
        
        if self.rect.x >= end_of_run:
            self.rect.x -= self.speed * dt
            
        # kills the enemy if its hp is smaller or equal to 0 and
        # creates an instance of the Drop() class 
        if self.hp <= 0:
            self.kill()
            kills += 1
            newDrop = Drop(self)
            dropList.append(newDrop)
        
        self.wobble()
            
    def wobble(self):
        self.rotation += self.speed/250 * self.multi
        
        if self.moving:
            if self.rotation >= 20:
                self.multi = -1
            elif self.rotation <= -10:
                self.multi = 1
        else:
            if self.rotation >= 30:
                self.multi = 0.1
            elif self.rotation <= -40:
                self.multi = -4
            
        
        self.image = pygame.transform.rotate(self.imageselect,self.rotation)
            
# Creates the class for the wall
class Wall():
    def __init__(self, x,y, hp, level):
        # assigning the image, coordinates, hp and level
        self.image = images["wall"][1]
        self.x,self.y = x,y
        
        self.hp = hp
        self.level = 0
    
    def update(self):
        
        global wallup
        
        # changes color based on the hp
        
        if self.hp > 1000:
            self.level = 0
        if self.hp <= 1000 >= 500:
            self.level = 1
        
        if self.hp < 500 :
            self.level = 2
        
        if self.hp < 0:
            wallup = False
            
        # draws the image and updates it
        if wallup:
            screen.blit(self.image, (self.x,self.y))
        self.image = images["wall"][self.level]
     
# Creates the drop class   
class Drop():
    def __init__(self, enemy):
        
        # takes the enemy that instantiated it 
        self.enemy = enemy
        
        # getting a random drop (ammo or money) and assigning it
        self.drops = ["ammodrop", "coinimg"]
        self.drop = self.drops[randint(0,1)]
    
        # assigns the image and creates the rect
        self.image = images[self.drop]
        self.rect = self.image.get_rect(center=(enemy.rect.x,enemy.rect.y))
    
        # variable needed later for a movie animation later
        self.starty = self.enemy.rect.y
        
    def update(self):
        global coins
        
        # getting the mouse position
        pos = pygame.mouse.get_pos()
        
        # checks if the mouse collides with the drop
        if self.rect.collidepoint(pos)and not pause:
            # applies a buff depending on the drop
            if self.drop == "ammodrop":
                selectedGun.ammo += randint(18,25)
                print("Gun ammo:", selectedGun.ammo)
                last_event = "Got Ammo+"
                print(last_event)
            if self.drop == "coinimg":
                coins += randint(18,25)
                print("Coins:", coins)
                last_event = "Got Coins+"
                print(last_event)
            
            # killing the instance if collided
            dropList.remove(self)
            sounds["collect_coins"].play()
            
        # moving it down for a nice animation
        if not self.rect.y > self.starty + 75:
            self.rect.y += 1
        
        # drawing the image
        screen.blit(self.image, (self.rect.x,self.rect.y))

class shopItem():
    def __init__(self, x,y, price_range,action):
        if action == "buyammo":
            self.image = images["shop"]["ammo"]
        if action == "glock":
            self.image = images["shop"]["glock_levelup"]
        if action == "smg":
            self.image = images["shop"]["smg_levelup"]
        if action == "sniper":
            self.image = images["shop"]["sniper_levelup"]
        if action == "healwall":
            self.image = images["shop"]["wall_heal"]
            
        self.rect = self.image.get_rect(center=(x,y))
        self.price_range = price_range
        self.price_level = 0
        self.price = self.price_range[self.price_level]
        self.action = action
        self.pressed = False
    
    def update(self):
        global coins
        self.price = self.price_range[self.price_level]
        
        maxwallhp = 2125
        
        self.max_level = self.price_level < len(self.price_range)-1
        
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            
            if pygame.mouse.get_pressed()[0] and coins >= self.price and not self.pressed:
                if self.action == "buyammo":
                    
                    selectedGun.ammo += 25
                    print("bought for ", selectedGun.weapon, f"/ Gun Ammo: {selectedGun.ammo}")
                    last_event = "Bought Ammo+"
                    sounds["collect_coins"].play()
                    #print(last_event)
                    
                        
                    self.price_level += 1 
                if self.action == "healwall" and self.max_level and wall.hp < maxwallhp :
                    wall.hp += 50
                    print(wall.hp)
                    #coins -= self.price
                    self.price_level += 1
                    last_event = "Healed Wall+"
                    sounds["healwall"].play()
                    print(last_event)
                    
                if self.action == "glock" and self.max_level:
                    if self.price_level % 2 == 0:
                        glock.rate -= 0.0375
                    else:
                        glock.damage += 2.4
                        
                    print("glock level += 1")
                    last_event = "Upgraded Glock"
                    print(last_event)
                    sounds["collect_coins"].play()
                    
                    self.price_level += 1
                    
                if self.action == "smg" and self.max_level:
                    if self.price_level % 2 == 0:
                        smg.rate -= 0.015
                    else:
                        smg.damage += 1.1
                        
                    print("glock level += 1")
                    last_event = "Upgraded SMG"
                    sounds["collect_coins"].play()
                    print(last_event)
                    
                    self.price_level += 1
                    
                if self.action == "sniper" and self.max_level:
                    if self.price_level % 2 == 0:
                        sniper.rate -= 0.275
                    else:
                        sniper.damage += 10
                        
                    print("glock level += 1")
                    last_event = "Upgraded Sniper"
                    print(last_event)
                    sounds["collect_coins"].play()
                    
                    self.price_level += 1
                    
                if self.price_level < len(self.price_range)-1:
                    if self.action == "buyammo" and selectedGun.ammo > 999 or self.action == "healwall" and wall.hp >= 2150:
                        coins += self.price
                    coins -= self.price
                self.pressed = True
            
        if not pygame.mouse.get_pressed()[0]:
            self.pressed = False
                
        if self.max_level:
            new_text("Cost: " + str(self.price), (self.rect.x + 150, self.rect.y + 10), 105)
        else:
            new_text("MAX!", (self.rect.x + 150, self.rect.y + 10), 105)
        screen.blit(self.image, (self.rect.x,self.rect.y))      
    
class Text():
    def __init__(self,text, size,place, color,font="font.ttf"):
        self.pos = place
        self.text = str(text)
        self.font_name = font
        self.size = 0
        self.font = pygame.font.SysFont(self.font_name, size)
        self.color = color
        
    def update(self, text):
        self.text = text
        screen.blit(self.font.render(self.text, True, self.color),self.pos)
        
class HealthPercent():
    def __init__(self, pos, var_display, var_max):
        self.pos = pos
        self.hp = var_display
        self.hp_max = var_max
        self.percentage = self.hp/self.hp_max*100

    def update(self, hp):
        self.hp = hp
        
        if self.hp > self.hp_max:
            self.hp = self.hp_max
        
        self.percentage = self.hp/self.hp_max*100
        new_text(str(round(self.percentage))+"%",self.pos, 100)

texts = []

def new_text(text, place,size):
    font = pygame.font.SysFont("font.ttf", size)
    ste = font.render(text, True, (255,255,255))
    screen.blit(ste, place)

cashews = 3   
        
wall = Wall(200,400, 2150, 2)

wallup = True

prefix = 0  

enemyGroup = pygame.sprite.Group()
enemyList = []

dropList = []

common_price_range = []
wallheal_price = []
for i in range(1000000):
    common_price_range.append(6)
for i in range(1000001):
    if i == 0:
        continue
    wallheal_price.append(i * 6)

shop_items = [
    shopItem(120,176,common_price_range, "buyammo"),
    shopItem(120,276,[16,32,48,48+16,48+32,48+32], "glock"),
    shopItem(120,376,[25,50,75,100,100], "smg"),
    shopItem(120,476,[40,80,120,160,200,200], "sniper"),
    shopItem(120,576,wallheal_price, "healwall"),
]

wave = 1 

pause = False

showfps = True

coins =000#0000

#               GUN/  SPEED/RATE/AMMO/DMG/FULLAUTO
glock = Gun( "glock", 3500 ,0.3 ,75 , 12 ,False)
smg = Gun(   "smg",   3500 ,0.1 ,100, 5  ,True)
sniper = Gun("sniper",3500 ,1.5 ,24 , 50 ,False)
         
gun_list = [glock]

selectedGun = glock

bulletGroup = pygame.sprite.Group()

kills = 0

events = ""

wave_reqs = [5,10,20,40,100,150,180,200,215,230,260,290,320,350,380,400, 450, 500, 600, 750]  

wave_Text = Text("Wave: "+str(wave), 100, (20,660),(255,255,255))
nextWave = Text(f"Next Wave: {kills}/{wave_reqs[wave]} Kills", 60,(20,20),(255,255,255))
Event = Text(events, 60, (500,500),(255,255,255))
wall_hp = HealthPercent((250,500),wall.hp, 2150)

def blitIcons():
    gun_x = 780   
    for gun in gun_list:
        screen.blit(images["icons"][gun.weapon], (gun_x,30))
        gun_x += 110
        if gun.ammo > 999:
            gun.ammo = 999
    gun_x = 0
    
    if selectedGun.weapon == "smg":
        screen.blit(images["selected"], (890,140))
        new_text(str(selectedGun.ammo), (890,150), 40)
    if selectedGun.weapon == "sniper":
        screen.blit(images["selected"], (1000,140))
        
    if selectedGun.weapon == "glock":
        screen.blit(images["selected"], (780,140))
        
    new_text(str(glock.ammo), (780,150), 40)
    if smg in gun_list:
        new_text(str(smg.ammo), (890,150), 40)
    if sniper in gun_list:
        new_text(str(sniper.ammo), (1000,150), 40)
    Event.update(events)
        
    if not pause:
        screen.blit(images["coinimg2"], (20,55))
        screen.blit(images["scull"], (10, 140))
    else:
        screen.blit(images["coinimg2"], (770,180))

def render():
    global last_event
    
    screen.blit(images["background"], (0,0))
    if not pause:
        enemyGroup.update()
        bulletGroup.update()
    
    if wallup:
        wall.update()  
    bulletGroup.draw(screen) 
    enemyGroup.draw(screen)
    
    for drop in dropList:
        drop.update()

    screen.blit(images["player"], (150,140))
    selectedGun.update()
    blitIcons()
    if not pause: 
        new_text(str(round(coins,0)), (100,50),105)
        new_text(str(kills), (105,150), 105)
    else:
        new_text(str(round(coins,0)), (840,175),105)
        
    wave_Text.update("Wave: "+str(wave)+"/20")
    nextWave.update(f"Next Wave: {kills}/{wave_reqs[wave]} Kills")
    
    if pause:
        screen.blit(images["shop_bcg"], (10,10))
        # screen.blit(images["settings_ui"], (765,120))
    
        for item in shop_items:
            if item.action == "healwall" and not wallup:
                continue
            if item.action == "smg" and smg not in gun_list:
                continue
            if item.action == "sniper" and sniper not in gun_list:
                continue
                
            item.update()
            
    cash_x = 450
    if not pause:
        for i in range(cashews):
            screen.blit(images["cashew"], (cash_x,30))
            cash_x += 100
            
        wall_hp.update(wall.hp)
        
    if showfps:
        new_text(str(int(clock.get_fps())), (1100,700), 50)
    
spawn_delay = 0
spawn_goal = 3
end_of_run = 350
enemies = []
for i in images["enemies"]:
    enemies.append(i)
        
def spawn_enemies():
    global spawn_delay,spawn_goal, prefix, end_of_run
    
    spawn_delay += 1 * dt
    if spawn_delay >= spawn_goal and not pause:
        spawn_delay = 0 
        for i in range(randint(1,2)):
            e = randint(1,9)
            if e  == 4 and wave  > 1:
                newenemy = Enemy(randint(usebuffhp1,usebuffhp2),150, randint(usebuffdmg1,usebuffdmg2),"big_buff")
                enemyList.append(newenemy)
                enemyGroup.add(newenemy)
                continue
                print(f"""
New Big Buff
HP -- {newenemy.hp}
DMG -- {newenemy.damage}
                      """)
            else:
                if e >= 3:
                    newenemy = Enemy(randint(usebasehp1,usebasehp2),225, randint(usebasedmg1,usebasedmg2), "zombie") 
                    enemyList.append(newenemy)
                    enemyGroup.add(newenemy)
                    print(f"""
New Normal Zombie
HP -- {newenemy.hp}
DMG -- {newenemy.damage}
                      """)
                if e >= 8 and wave > 1:
                    newenemy = Enemy(randint(usefasthp1,usefasthp2),325, randint(usefastdmg1,usefastdmg2), "fast_boi") 
                    enemyList.append(newenemy)
                    enemyGroup.add(newenemy)
                    print(f"""
New Fast Zombie
HP -- {newenemy.hp}
DMG -- {newenemy.damage}
                      """)
            
            #print("spawned enemy")
            
            prefix += 150
            if len(enemyGroup) % 5 == 0:
                end_of_run += 25
            if len(enemyGroup) < 3:
                end_of_run = 350
        prefix = 0

enemys = 0 

def collisions():
    global enemys, kills
    enemys += 1
    
    for enemy in enemyList:
        
        if len(enemyList) > 10:
            if enemys % 2 == 0:
                continue
                enemys = 0 
        
        hits = pygame.sprite.spritecollide(enemy, bulletGroup, False, pygame.sprite.collide_mask)
        if hits:
            
            hits[0].kill()
            enemy.hp -= hits[0].damage
            if hits[0].rect.y > enemy.rect.y + 50:
                enemy.hp -= hits[0].damage
            sounds["enemyded"].play()
            if enemy.hp <= 0:
                enemy.kill()
                enemyList.remove(enemy)
                kills += 1
                e = randint(0,2)
                if e == 2:   
                    newDrop = Drop(enemy)
                    dropList.append(newDrop)
                if enemy.id == "big_buff":
                    for i in range(5):
                        newDrop = Drop(enemy)
                        dropList.append(newDrop)
                #print(e)
    
        if enemy.hp <= 0:
            enemy.kill()

basehp1, basehp2 = 42,49
basedmg1,basedmg2 = 18,22
usebasehp1, usebasehp2 = basehp1, basehp2
usebasedmg1, usebasedmg2 = basedmg1, basedmg2
baseadderhp = 0
baseadderdmg = 0
       
fasthp1, fasthp2 = 18,23
fastdmg1,fastdmg2 = 13,17
usefasthp1, usefasthp2 = basehp1, basehp2
usefastdmg1, usefastdmg2 = fastdmg1, fastdmg2
fastadderhp = 0
fastadderdmg = 0

buffhp1, buffhp2 = 100,160
buffdmg1,buffdmg2 = 40,60
usebuffhp1, usebuffhp2 = buffhp1, buffhp2
usebuffdmg1, usebuffdmg2 = buffdmg1, buffdmg2
buffadderhp = 0
buffadderdmg = 0

spawn_max = 4
use_spawn_max = 4
add_spawn = 2

pygame.display.set_caption(f"Defend your Cashews")
    
def check_wave():
    global wave, baseadderdmg, fastadderdmg, buffadderdmg, baseadderhp,fastadderhp, buffadderhp, add_spawn
    for i,x in enumerate(wave_reqs):
        if kills == x:\
            wave = i + 1
            #print(wave)
            
    
    if wave % 4 == 0:
        add_spawn += 1
            
    elif wave % 2 == 0:
        baseadderhp += 15*2
        fastadderhp += 13*1.5
        buffadderhp += 18*2.2

    else:
        baseadderdmg += 13*1.5
        fastadderdmg += 12*1.2
        buffadderdmg += 15*1.8
        
    if wave == 3 and not smg in gun_list:
        gun_list.append(smg)
        sounds["switch_gun"].play()
        
        
    if wave == 5 and not sniper in gun_list:
        gun_list.append(sniper)    
        sounds["switch_gun"].play()  
        
    usebasehp1, usebasehp2 = basehp1 + baseadderhp, basehp2 + baseadderhp
    usebasedmg1, usebasedmg2 = basedmg1 + baseadderdmg, basedmg2 + baseadderdmg
    
    usefasthp1, usefasthp2 = fasthp1 + fastadderhp, fasthp2 + fastadderhp
    usefastdmg1, usefastdmg2 = fastdmg1 + fastadderdmg, fastdmg2 + fastadderdmg
    
    usebuffhp1, usebuffhp2 = buffhp1 + buffadderhp, buffhp2 + buffadderhp
    usebuffdmg1, usebuffdmg2 = buffdmg1 + buffadderdmg, buffdmg2 + buffadderdmg
    
    use_spawn_max = spawn_max + add_spawn 
    
filehandler = SaveManager("savedata", [wave, kills, coins]) 
            
prev_time = time.time()
dt = 0

run = True
while run:
    clock.tick(running_fps)
    
    now = time.time()
    dt = now-prev_time
    prev_time = now
    
    render()
    spawn_enemies()
    collisions()
    check_wave()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                print("pressed esc")
                pause = not pause
                
            if event.key == K_DELETE:
                run = False
                sys.exit()
                
            if event.key == K_1 and not selectedGun == glock:
                selectedGun = glock
                sounds["switch_gun"].play()
            try:
                if event.key == K_2 and not selectedGun == smg:
                    selectedGun = gun_list[1]
                    sounds["switch_gun"].play()
            except IndexError:
                print("gun isnt unlocked yet")
            try:
                if event.key == K_3 and not selectedGun == sniper:
                    selectedGun = gun_list[2]
                    sounds["switch_gun"].play()
            except IndexError:
                print("gun isnt unlocked yet")
                
    
            
    pygame.display.update()
    
sys.exit()