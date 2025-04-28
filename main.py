import pygame
from pytmx.util_pygame import load_pygame
from Objects.player import Player
from Objects.kiwi import Kiwi
from Objects.ground import Ground
from Objects.background import Background
from Objects.box import Box
from Objects.ui import *
from Modules.collision import *
from Modules.camera import Camera

pygame.init()

# Initialize joystick
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_COLS = SCREEN_WIDTH // TILE_SIZE
SCREEN_ROWS = SCREEN_HEIGHT // TILE_SIZE

display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Project Kiwi")
pygame.display.set_icon(pygame.image.load("./Assets/UI/icon.png"))

# Music
pygame.mixer.init()
pygame.mixer.music.load('./Assets/Music/BackgroundMusic.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
done = False
gameState = 1

# UI elements
elements = [StartButton(100, 100, 64, 64, pygame.image.load("./Assets/UI/play.png"))]

# Load map
tiled_map = load_pygame('./Assets/Levels/BasicLevel.tmx')
level_width = tiled_map.width * tiled_map.tilewidth
level_height = tiled_map.height * tiled_map.tileheight

# Initialize game
def init_game():
    global objects, player, camera, collected_count, total_kiwis

    objects = []
    player = Player(0, 0, 64, 64)
    objects.append(player)

    collected_count = 0
    total_kiwis = 0

    for layer in tiled_map.visible_layers:
        for x, y, image in layer.tiles():
            pos_x = x * tiled_map.tilewidth
            pos_y = y * tiled_map.tileheight
            width = tiled_map.tilewidth
            height = tiled_map.tileheight

            if layer.name == "Background":
                objects.append(Background(pos_x, pos_y, width, height, image))
            elif layer.name == "Terrain":
                objects.append(Ground(pos_x, pos_y, width, height, image))
            elif layer.name == "Collectibles":
                objects.append(Kiwi(pos_x, pos_y, width, height, image))
                total_kiwis += 1

    # Map boundaries
    objects.append(Box(-10, 0, 10, level_height))
    objects.append(Box(level_width, 0, 10, level_height))

    camera = Camera(level_width, SCREEN_WIDTH)

init_game()

coin_logo = pygame.transform.scale(pygame.image.load('./Assets/Collectables/coins.png'), (32, 32))

# Define controller button mappings (Xbox 360)
XBOX_A_BUTTON = 0

# Game loop
while not done:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    
    # Controller inputs
    controller_input = {
        'left_stick_x': 0.0,
        'a_button': False
    }
    
    if joystick:
        controller_input['left_stick_x'] = joystick.get_axis(0)  # Left stick X axis
        
    event = pygame.event.get()
    for e in event:
        if e.type == pygame.QUIT:
            done = True
        elif e.type == pygame.JOYBUTTONDOWN:
            if e.button == XBOX_A_BUTTON:  # A button pressed
                controller_input['a_button'] = True

    if gameState == 2:
        display.fill((0, 0, 0))

        # Update with controller input
        for obj in objects:
            if isinstance(obj, Player):
                obj.update(keys, controller_input)
            else:
                obj.update(keys)

        # Camera
        while camera.check(player, SCREEN_WIDTH, SCREEN_HEIGHT):
            for obj in objects:
                camera.movecamera(obj)

        # Collision
        for obj in objects[:]:
            if not isinstance(obj, Player) and obj.collide:
                if player_check(player, obj):
                    if isinstance(obj, Kiwi):
                        collected_count += 1
                    objects.remove(obj)

        # Fall check
        if player.y > SCREEN_HEIGHT + 100:
            gameState = 1
            init_game()

        # Draw
        for obj in objects:
            if not isinstance(obj, Player):
                obj.draw(display)
        player.draw(display)

        # UI - Keep kiwi counter
        display.blit(coin_logo, (10, 10))
        font = pygame.font.Font(None, 36)
        counter_text = font.render(f"{collected_count}/{total_kiwis}", True, (255, 255, 255))
        display.blit(counter_text, (50, 10))

    elif gameState == 1:
        display.fill((0, 0, 0))
        for ele in elements:
            ele.draw(display)
        for e in event:
            if e.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                for u in elements:
                    if u.clicked(pos):
                        if u.activate() == "start game":
                            gameState = 2
                            init_game()
            elif e.type == pygame.JOYBUTTONDOWN and e.button == XBOX_A_BUTTON:
                # Allow A button to start game from menu too
                for u in elements:
                    if u.activate() == "start game":
                        gameState = 2
                        init_game()

    pygame.display.flip()