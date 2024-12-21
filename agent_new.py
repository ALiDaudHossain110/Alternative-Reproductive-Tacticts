import pygame as pg
import constants as c  # Ensure this module contains required constants
import random
import math
import numpy as np
from genome import Genome
import time

class Agent(pg.sprite.Sprite):
    def __init__(self, pos,generation_no, energy_level, body_size, genome,birthtime):
        super().__init__()
        self.rect = pg.Rect(pos[0], pos[1], 2 * body_size, 2 * body_size)
        self.age = 0
        self.gender = "m"
        self.generation_no = generation_no
        self.energy_level = energy_level
        self.body_size = body_size
        self.pos=pos

        self.reproductive_success=0
        self.no_of_matings_as_female=0
        self.no_of_matings_as_male=0

        self.mating_state_timer=c.mating_state_timer_counter
        self.post_mating_state_timer=c.post_mating_state_timer_counter

        self.genome = genome
        # self.dir_selec=0

        self.color=None
        self.front_marker_color = c.BLACK
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        self.appearance(self.gender,self.body_size,self.pos)

        self.rect = self.image.get_rect(center=self.rect.center)
        self.old_timestep=0
        self.last_energy_decrease_time = pg.time.get_ticks()
        self.state = 'waiting'


        random_angle = random.uniform(0, 360)
        self.direction = pg.Vector2(math.cos(math.radians(random_angle)), math.sin(math.radians(random_angle)))
        self.direction_to_move=pg.Vector2(math.cos(math.radians(random_angle)), math.sin(math.radians(random_angle)))
        self.speed = 2
        self.sight_radius = 100
        self.vision_angle = 180
        self.vision_angle_mating = 150
        self.can_reproduce=True
        if self.gender == "f":
            self.can_reproduce = True  # Flag to track reproduction waiting period
  
        self.nearby_food = []
        self.nearby_agents = []
        self.nearby_agents_face_dist = []
        self.nearby_agents_face = []
        self.nearby_agents_back_dist = []
        self.nearby_agents_back = []

        self.state_counter_dict={
            "moving_to_food":[0]*500,
            "waiting":[0]*500,
            "mating as male":[0]*500,
            "mating as female":[0]*500,
            "searching_for_food":[0]*500,
        }

    def state_stat(self):
        i=int(self.energy_level)
        i-=1
        self.state_counter_dict[self.state][i]= int(self.state_counter_dict[self.state][i])+1


