#food.py
import pygame as pg
import constants
import random
class Food(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.color = constants.GREEN
        x="yn"
        choose=random.choice(x)
        if choose=="y":
            self.energy = 100  # Random energy level for the food
            self.radius = 6  # Random radius for the food
            # Load and scale the food image
            image_path = 'images/food1.png'
            self.original_image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.original_image, (self.radius * 3, self.radius * 3))  # Scale the image

            # Set up the position of the food
            self.rect = self.image.get_rect(
                center=(
                    random.randint(0 + self.radius, constants.screen_width - self.radius),
                    random.randint(0 + self.radius, constants.screen_height - self.radius)
                )
            )

        if choose=="n":
            # self.energy = random.randint(5, 7)  # Random energy level for the foody
            self.energy = 100  # Random energy level for the food
            self.radius = 6  # Random radius for the food
            # Load and scale the food image
            image_path = 'images/food2.png'
            self.original_image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.original_image, (self.radius * 2, self.radius * 2))  # Scale the image

            # Set up the position of the food
            self.rect = self.image.get_rect(
                center=(
                    random.randint(0 + self.radius, constants.screen_width - self.radius),
                    random.randint(0 + self.radius, constants.screen_height - self.radius)
                )
            )

        self.timer = 20 * constants.fps  # 20 seconds (converted to frames)

    def update(self, food_group):
        # Decrement the timer
        self.timer -= 1

        # Add new food if the food population is lower than the threshold
        if len(food_group) < constants.food_population:
            food = Food()
            food_group.add(food)

        # Check if the timer has reached zero
        if self.timer <= 0:
            # Remove the food from both the screen and memory
            self.kill()
