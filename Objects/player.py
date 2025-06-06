import pygame
from Modules.spriteSheet import SpriteSheet


class Player:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.delay = 2  # Animation
        self.currDelay = 0

        # Horizontal Movement
        self.speed = 0
        self.maxSpeed = 5
        self.acc = 0.4
        
        # Controller deadzone
        self.deadzone = 0.2

        # Vertical Movement
        self.maxG = 100
        self.currG = 0
        self.gAcc = 0.5
        self.isOnGround = False

        self.jumpVel = 0
        self.jumpMax = 13.5

        # Collision Stuff
        self.last_y = y
        self.gs = 0

        # Sprites
        self.state = "IDLE_RIGHT"
        self.pastState = "RUN_RIGHT"

        self.idle_state = 0
        self.idle_length = 11
        player_idle = SpriteSheet(pygame.image.load("./Assets/Player/player_idle.png"))
        self.idle = [player_idle.getimage(32*x, 0, 32, 32) for x in range(self.idle_length)]

        for x in range(len(self.idle)):
            self.idle[x] = pygame.transform.scale(self.idle[x], (64, 64))

        self.run_state = 0
        self.run_length = 12
        player_run = SpriteSheet(pygame.image.load("./Assets/Player/player_run.png"))
        self.run = [player_run.getimage(32 * x, 0, 32, 32) for x in range(self.run_length)]

        for x in range(len(self.run)):
            self.run[x] = pygame.transform.scale(self.run[x], (64, 64))

        self.player_jump = pygame.transform.scale(pygame.image.load("./Assets/Player/player_jump.png"), (64, 64))
        self.player_fall = pygame.transform.scale(pygame.image.load("./Assets/Player/player_fall.png"), (64, 64))

    def draw(self, display):
        if not self.isOnGround and self.jumpVel > self.currG:
            if self.pastState == "RUN_RIGHT":
                display.blit(self.player_jump, (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.player_jump, 1, 0), (self.x, self.y))
        elif not self.isOnGround:
            if self.pastState == "RUN_RIGHT":
                display.blit(self.player_fall, (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.player_fall, 1, 0), (self.x, self.y))
        elif self.state == "IDLE_RIGHT":
            display.blit(self.idle[self.idle_state % self.idle_length], (self.x, self.y))
            if self.currDelay == self.delay:
                self.idle_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "IDLE_LEFT":
            display.blit(pygame.transform.flip(self.idle[self.idle_state % self.idle_length], 1, 0), (self.x, self.y))
            if self.currDelay == self.delay:
                self.idle_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "RUN_RIGHT":
            display.blit(self.run[self.run_state % self.run_length], (self.x, self.y))
            if self.currDelay == self.delay:
                self.run_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "RUN_LEFT":
            display.blit(pygame.transform.flip(self.run[self.run_state % self.run_length], 1, 0), (self.x, self.y))
            if self.currDelay == self.delay:
                self.run_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1

        # Collision Stuff
        self.last_y = self.y
        if self.gs != 0:
            self.isOnGround = True
        else:
            self.isOnGround = False
        self.gs = 0

    def update(self, keys, controller_input=None):
        if controller_input is None:
            controller_input = {'left_stick_x': 0.0, 'a_button': False}

        # Horizontal Movement
        stall = self.x
        
        # Check for controller input first, then keyboard if no controller input
        moving_left = False
        moving_right = False
        
        # Controller left stick
        if abs(controller_input['left_stick_x']) > self.deadzone:
            if controller_input['left_stick_x'] < -self.deadzone:  # Left on stick
                moving_left = True
            elif controller_input['left_stick_x'] > self.deadzone:  # Right on stick
                moving_right = True
        
        # If no controller input, check keyboard
        if not moving_left and not moving_right:
            moving_right = keys[pygame.K_d]
            moving_left = keys[pygame.K_a]
        
        # Cancel out if both directions pressed
        if moving_left and moving_right:
            self.speed = 0
        else:
            if moving_right:
                if self.speed <= self.maxSpeed:
                    self.speed += self.acc
                self.x += self.speed
                self.state = "RUN_RIGHT"
                self.pastState = "RUN_RIGHT"
            elif moving_left:
                if self.speed <= self.maxSpeed:
                    self.speed += self.acc
                self.x -= self.speed
                self.state = "RUN_LEFT"
                self.pastState = "RUN_LEFT"
            else:
                if self.pastState == "RUN_RIGHT" or self.pastState == "JUMP_RIGHT":
                    self.state = "IDLE_RIGHT"
                elif self.pastState == "RUN_LEFT" or self.pastState == "JUMP_LEFT":
                    self.state = "IDLE_LEFT"
                    
        if stall == self.x:
            self.speed = 0

        # Jumping - check controller A button or keyboard
        jump_pressed = controller_input['a_button'] or keys[pygame.K_SPACE] or keys[pygame.K_w]
        
        if self.isOnGround and jump_pressed:
            self.jumpVel = self.jumpMax
            self.isOnGround = False
        
        if self.isOnGround:
            self.jumpVel = 0
            
        if not self.isOnGround and self.jumpVel > self.currG:
            self.state = "JUMP"

        self.y -= self.jumpVel

        # Gravity
        if not self.isOnGround:
            if self.currG <= self.maxG:
                self.currG += self.gAcc
            self.y += self.currG
        else:
            self.currG = 0