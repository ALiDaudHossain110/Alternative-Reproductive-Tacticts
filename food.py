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

        self.image = pg.Surface((self.radius * 2, self.radius * 2))
        self.image.fill(constants.BLACK)
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

    def update(self, food_group):
        # Decrement the timer


        if len(food_group)<constants.food_population:
                food = Food()
                food_group.add(food)


        if constants.loop_counter%25==0 and constants.loop_counter!=0:
             self.kill()
             
