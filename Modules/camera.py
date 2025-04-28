# camera.py
from Objects.player import Player

class Camera:
    def __init__(self, level_width, screen_width):
        self.speed = 2
        self.offset = 0
        self.level_width = level_width
        self.screen_width = screen_width

    def movecamera(self, obj):
        obj.x -= self.speed
        if isinstance(obj, Player):
            self.offset += self.speed

    def check(self, player, w, h):
        # Scroll right if player near right edge and not at end of level
        if (player.x + player.w > w - 200) and (self.offset < self.level_width - self.screen_width):
            self.speed = abs(self.speed)
            return True
        # Scroll left if player near left edge and not at start of level
        elif player.x < 200 and self.offset > 0:
            self.speed = -abs(self.speed)
            return True
        return False
