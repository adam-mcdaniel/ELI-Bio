#! /usr/bin/python

import pygame,sys,time,random,os
import numpy as np
from pygame import *

WIN_WIDTH = 1024
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30
ELIes = []
exits = []
def main():
    global cameraX, cameraY
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Evol")
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#000000"))
    entities = pygame.sprite.Group()
    player = Player(32,32)

    platforms = []
    x = y = 0

    with open(os.path.join(os.path.dirname(sys.argv[0]),'data/level.txt')) as f:
        level = f.readlines()
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                E = ELIent(x, y,entities,ELIes,2*np.random.random((5,1))-1,2*np.random.random((1,4))-1,32)
                # E = ELIent(x, y,entities,ELIes,np.random.random((13,1000-0)),np.random.random((10000,4)),32)
            if col == "B":
                B = ELIent(x,y,entities,ELIes,np.array([[0,0,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0],[0,0,1,1,0,0,0,0,0]]),np.array([[1,1,0,0],[1,1,0,0],[1,1,0,0]]),64)
            if col == "e":
                e = ExitBlock(x, y,exits)
                exits.append(e)
                entities.add(e)
            x += 32
        y += 32
        x = 0

    total_level_width  = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(complex_camera, total_level_width, total_level_height)

    while 1:
        timer.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
                up = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_DOWN:
                down = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
                left = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
                right = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                for ELI in ELIes:
                    ELI.syn0 = 2*np.random.random((5,1))-1
                    ELI.syn1 = 2*np.random.random((1,4))-1
                    ELI.xvel = 0
                    ELI.yvel = 0
                    ELI.velocity = random.randint(1,10)
                    ELI.square = 32
                    ELI.rect.left = ELI.savex
                    ELI.rect.top = ELI.savey
            if e.type == pygame.KEYUP and e.key == pygame.K_UP:
                up = False
            if e.type == pygame.KEYUP and e.key == pygame.K_DOWN:
                down = False
            if e.type == pygame.KEYUP and e.key == pygame.K_RIGHT:
                right = False
            if e.type == pygame.KEYUP and e.key == pygame.K_LEFT:
                left = False

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        player.update(up, down, left, right, running, platforms)

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        camera.update(player)

        # update player, draw everything else
        for ELI in ELIes:
            ELI.update(up, down, left, right,platforms,exits,ELIes)
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()

def nonlin(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    return Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Tentacle(Entity):
    def __init__(self, x, y,leftdif,topdif,width,height):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.square = 32
        self.image = Surface((width,height))
        self.image.fill(Color("#00FFFF"))
        self.image.convert()
        self.rect = Rect(x, y, width, height)
        self.leftdif = leftdif
        self.topdif = topdif

    def update(self,ELI):
        self.rect.left = ELI.rect.left+self.leftdif
        self.rect.top = ELI.rect.top+self.topdif


class ELIent(Entity):
    def __init__(self, x, y,entities,ELIes,X,Y,square):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0

        self.savex = x
        self.savey = y

        self.velocity = random.randint(1,10)
        self.square = square
        self.image = Surface((self.square,self.square))
        self.image.fill(Color("#FF0000"))
        self.image.convert()

        self.rect = Rect(x, y, self.square, self.square)
        self.onGround = False
        self.L1 = Tentacle(self.rect.left,self.rect.top,0,-2,32,2)
        self.L2 = Tentacle(self.rect.left,self.rect.top,self.square+2,0,2,32)
        self.L3 = Tentacle(self.rect.left,self.rect.top,0,self.square+2,32,2)
        self.L4 = Tentacle(self.rect.left,self.rect.top,-2,0,2,32)
        self.L5 = Tentacle(self.rect.left,self.rect.top,16,-32,5,5)
        self.L6 = Tentacle(self.rect.left,self.rect.top,self.square+32,16,5,5)
        self.L7 = Tentacle(self.rect.left,self.rect.top,16,self.square+32,5,5)
        self.L8 = Tentacle(self.rect.left,self.rect.top,-32,16,5,5)
        self.L9 = Tentacle(self.rect.left,self.rect.top,16,-64,5,5)
        self.L10 = Tentacle(self.rect.left,self.rect.top,self.square+64,16,5,5)
        self.L11 = Tentacle(self.rect.left,self.rect.top,16,self.square+64,5,5)
        self.L12 = Tentacle(self.rect.left,self.rect.top,-64,16,5,5)

        self.tentacles = [self.L1,self.L2,self.L3,self.L4,self.L5,self.L6,self.L7,self.L8,self.L9,self.L10,self.L11,self.L12]
        entities.add(self)
        # entities.add(self.L1)
        # entities.add(self.L2)
        # entities.add(self.L3)
        # entities.add(self.L4)
        entities.add(self.L5)
        entities.add(self.L6)
        entities.add(self.L7)
        entities.add(self.L8)
        # entities.add(self.L9)
        # entities.add(self.L10)
        # entities.add(self.L11)
        # entities.add(self.L12)
        print(self)
        ELIes.append(self)
        # randomly initialize our weights with mean 0
        try:
            # self.syn0 = np.random.random((13,10000)) - 1
            self.syn0 = X
            self.syn1 = Y

        except Exception as e:
                print (e)

    def update(self, up, down, left, right,platforms,exits,ELIes):

        self.image = Surface((self.square,self.square))
        self.image.fill(Color("#FF0000"))
        self.image.convert()
        self.rect = Rect(self.rect.left, self.rect.top, self.square, self.square)

        for tent in self.tentacles:
            tent.update(self)
        self.arrayinput = np.array([0,0,0,0,1])

        # self.arrayinput = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])

        for tentacle in range(len(self.arrayinput)):
            if tentacle >= len(self.tentacles)-1:
                break
            for p in platforms:
                if pygame.sprite.collide_rect(self.tentacles[tentacle],p):
                    self.arrayinput[tentacle] = 1
                    break
                else:
                    self.arrayinput[tentacle] = 0

            # for ELI in ELIes:
            #     if self.testing == True:
            #         if pygame.sprite.collide_rect(self.tentacles[tentacle],ELI):
            #             self.arrayinput[tentacle] = 0.5
            #             self.testing = False
            #             break
            #         else:
            #             self.arrayinput[tentacle] = 0

        self.l0 = self.arrayinput
        self.l1 = nonlin(np.dot(self.l0,self.syn0))
        self.l2 = nonlin(np.dot(self.l1,self.syn1))

        for x in range(len(self.l2)):

            self.l2[x] = round(self.l2[x])
            
        self.xvel = 0

        for x in range(len(self.l2)):
            if int(self.l2[x]) == 1:
                if x == 0:
                    if self.onGround:
                        self.yvel -= 9
                if x == 1:
                    self.xvel = self.velocity
                if x == 3:
                    self.xvel = -self.velocity
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.4
            # max falling speed
            if self.yvel > 100: self.yvel = 100

        print("in: "+str(self.arrayinput))
        print("out: "+str(self.l2))

        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms,exits,ELIes)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, platforms,exits,ELIes)

    def collide(self, xvel, yvel, platforms,exits,ELIes):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                if xvel < 0:
                    self.rect.left = p.rect.right
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.yvel = 0
                    self.onGround = True
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.yvel = 0

        for e in exits:
            if pygame.sprite.collide_rect(self,e):
                for ELI in ELIes:
                    ELI.syn0 = self.syn0
                    ELI.syn1 = self.syn1
                    for row in ELI.syn0:
                        for col in row:
                            col = col * random.uniform(-0.5,0.5)
                    for row in ELI.syn1:
                        for col in row:
                            col = col * random.uniform(-0.5,0.5)
                    ELI.rect.left = ELI.savex
                    ELI.rect.top = ELI.savey
                    ELI.velocity = self.velocity + random.randint(-1,1)
                    width_height = random.randint(-4,4)
                    while self.square + width_height < 1:
                        width_height = random.randint(0,4)
                    ELI.square = self.square + width_height

    def image_change(self,square):
        self.square = square
        self.image = Surface((self.square,self.square))
        self.image.fill(Color("#0000FF"))
        self.image.convert()
        self.rect = Rect(self.rect.left, self.rect.top, self.square, self.square)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.lastdir = 'right'
        self.xvel = 0
        self.yvel = 0
        self.image = pygame.Surface((1,1))
        self.image.fill(pygame.Color("#000000"))
        self.image.convert()
        self.rect = pygame.Rect(x, y, 1, 1)

    def update(self, up, down, left, right, running, platforms):
        if up:
            self.yvel = -24
        if down:
            self.yvel = 24
        if left:
            self.xvel = -24
        if right:
            self.xvel = 24

        if not(left or right):
            self.xvel = 0
        if not(up or down):
            self.yvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        self.rect.top += self.yvel


class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#DDDDDD"))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Entity):
    def __init__(self, x, y,exits):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#DDDDDD"))
        self.rect = Rect(x, y, 32, 32)
        self.image.fill(pygame.Color("#00FF00"))
        exits.append(self)


if __name__ == "__main__":
    main()
