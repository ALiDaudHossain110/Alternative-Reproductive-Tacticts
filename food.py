#food.py
import pygame as pg
import constants
import random

class Food(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.energy = 50  # Random energy level for the food
        self.radius = 2  # Random radius for the food
        self.color = constants.GREEN
        self.rect = pg.Rect(random.randint(0, constants.screen_width - self.radius),
                            random.randint(0, constants.screen_height - self.radius),
                            self.radius * 2, self.radius * 2)
        self.timer = 20 * constants.fps  # 20 seconds (converted to frames)

        self.image = pg.Surface((self.radius * 2, self.radius * 2))
        self.image.fill(constants.BLACK)
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

    def update(self, food_group):
        # Decrement the timer
        self.timer -= 1


        if len(food_group)<constants.food_population:
                food = Food()
                food_group.add(food)

        # Check if the timer has reached zero
        if self.timer <= 0:
            # Remove the food from both the screen and memory
            self.kill()
