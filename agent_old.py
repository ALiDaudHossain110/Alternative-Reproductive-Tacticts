#agents.py
import pygame as pg
import constants as c  # Ensure this module contains required constants
import random
import math
import neat

import time

class Agent(pg.sprite.Sprite):
    def __init__(self, pos, age, gender, generation_no, energy_level, body_size, genome,birthtime):
        super().__init__()
        self.rect = pg.Rect(pos[0], pos[1], 2 * body_size, 2 * body_size)
        self.age = age
        self.gender = gender
        self.generation_no = generation_no
        self.energy_level = energy_level
        self.body_size = body_size
        self.last_age_increment_time = pg.time.get_ticks()
        
        self.birth_time=birthtime
        self.reproductive_success=0
        
        self.reproductive_success_weight=0.1
        self.servival_time_weight=0.1
        self.energy_weight=0.1
        
        self.genome = genome
       # self.childfitness=0
        self.color = c.WHITE if gender == "m" else c.RED
        self.front_marker_color = c.BLACK

        # Initialize wheel parameters
        self.wheel_radius = body_size // 2
        self.wheel_distance = body_size
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

        self.original_image = pg.Surface((2 * body_size, 2 * body_size), pg.SRCALPHA)
        self.original_image.fill((0, 0, 0, 0))
        pg.draw.circle(self.original_image, self.color, (body_size, body_size), body_size)
        pg.draw.circle(self.original_image, self.front_marker_color, (body_size + body_size // 2, body_size), body_size // 5)
        pg.draw.circle(self.original_image, c.YELLOW, (body_size, body_size + body_size // 2), body_size // 5)  # Left wheel
        pg.draw.circle(self.original_image, c.YELLOW, (body_size, body_size - body_size // 2), body_size // 5)  # Right wheel

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.rect.center)

        self.last_energy_decrease_time = pg.time.get_ticks()
        self.state = 'searching'

        random_angle = random.uniform(0, 360)
        self.direction = pg.Vector2(math.cos(math.radians(random_angle)), math.sin(math.radians(random_angle)))
      
        self.speed = 2
        self.sight_radius = 75
        self.vision_angle = 180
        if self.gender == "f":
            self.can_reproduce = True  # Flag to track reproduction waiting period
  
        self.nearby_food = []
        self.nearby_agents = []

    def update(self, agents, agent_group2, food_group, configg):
        self.perceive(agents, food_group)
        #self.decide()
        self.act(agents)
        self.interact(agents,agent_group2,configg)
        self.eat(food_group)

        current_time = pg.time.get_ticks()
        if current_time - self.last_energy_decrease_time > c.energy_decrease_interval * 1000:
            self.energy_level -= 1
            self.last_energy_decrease_time = current_time

        if self.energy_level <= 0:
            self.kill()

        if current_time - self.last_age_increment_time > c.age_increment_interval * 1000:
            self.increment_age()
            self.last_age_increment_time = current_time

        self.update_position(agents)
        # print("Movement Direction:", self.calculate_movement_direction())
        # print("Left Wheel Speed:", self.left_wheel_speed)
        # print("Right Wheel Speed:", self.right_wheel_speed)
 

    def perceive(self, agents, food_group):

        for food in food_group:
            if self.energy_level < 26:
                direction_to_food = pg.Vector2(food.rect.centerx - self.rect.centerx, food.rect.centery - self.rect.centery)
                if direction_to_food.length() <= self.sight_radius:
                    angle_to_food = self.direction.angle_to(direction_to_food)
                    if abs(angle_to_food) <= self.vision_angle / 2:
                        self.nearby_food.append(food)

        for agent in agents:
            if agent is not self:
                if self.age > 7 and self.energy_level > 3:
                    direction_to_agent = pg.Vector2(agent.rect.centerx - self.rect.centerx, agent.rect.centery - self.rect.centery)
                    if direction_to_agent.length() <= self.sight_radius:
                        angle_to_agent = self.direction.angle_to(direction_to_agent)
                        if abs(angle_to_agent) <= self.vision_angle / 2:
                            self.nearby_agents.append(agent)

    # def decide(self):
    #     if self.nearby_food and self.energy_level < 26:
    #         self.state = 'moving_to_food'
    #     elif self.energy_level < 8:
    #         self.state = 'searching_for_food'
    #     elif self.nearby_agents and self.age > 7 and self.energy_level > 3:
    #         self.state = 'mating'
    #     else:
    #         self.state = 'wandering'

    def act(self,agents):
        if self.state == 'moving_to_food' and self.nearby_food:
            self.move_to(self.nearby_food[0].rect.center,agents)
        elif self.state == 'searching_for_food':
            self.search_for_food()
        elif self.state == 'mating':
            self.find_mate(agents)
        elif self.state == 'wandering':
            self.wander()

    def data(self):
        input = [0, 0, 0, 0]
        agent_center = pg.Vector2(self.rect.centerx, self.rect.centery)

        # Get the center coordinates of the first nearby food item,agent center,other center.
        if self.nearby_food is not None and len(self.nearby_food) >0:
            food_center = pg.Vector2(self.nearby_food[0].rect.centerx, self.nearby_food[0].rect.centery)
            dist_to_food = food_center.distance_to(agent_center)

        else:
            # If there is no nearby food, set default values
            dist_to_food = -1

        # Get the center coordinates of the first nearby food item,agent center,other center.
        if len(self.nearby_agents) > 0:
            other_center = pg.Vector2(self.nearby_agents[0].rect.centerx, self.nearby_agents[0].rect.centery)
            dist_to_other = other_center.distance_to(agent_center)

        else:
            # If there is no nearby food, set default values
            dist_to_other = -1

    
        # Calculate the distance between the agent and the food

        input[0] = dist_to_food  # Add this distance to the input list      
        input[1] = dist_to_other  # Add this distance to the input list      
        input[2] = self.energy_level  # Add energy level
        input[3] = self.age #add age   
        
        return input

    
    def move_to(self, target,agents):

        self.check_Collision(agents)

        # Calculate the vector pointing to the target
        direction = pg.Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery)

        # Calculate the angle to the target
        angle_to_target = self.direction.angle_to(direction)
        
        # Adjust wheel speeds based on the angle to the target using proportional control
        kp = 0.1  # Proportional gain
        rotation_speed = kp * angle_to_target

        self.left_wheel_speed = self.speed - rotation_speed
        self.right_wheel_speed = self.speed + rotation_speed

        # Ensure wheel speeds are within acceptable limits
        max_wheel_speed = self.speed
        self.left_wheel_speed =int( max(-max_wheel_speed, min(self.left_wheel_speed, max_wheel_speed)))
        self.right_wheel_speed = int(max(-max_wheel_speed, min(self.right_wheel_speed, max_wheel_speed)))

        # self.check_Collision()        
        self.update_position(agents)

    def update_position(self,agents):
        # Update the agent's position based on the left and right wheel speeds
        velocity = (self.left_wheel_speed + self.right_wheel_speed) / 2
        rotation = (self.right_wheel_speed - self.left_wheel_speed) / self.wheel_distance

        # Update direction based on rotation
        if rotation != 0:
            angle = rotation * 180 / math.pi
            self.direction.rotate_ip(angle)  # Adjusted sign for correct rotation direction
        
        # Move agent in the direction it's facing
        self.rect.center += self.direction * velocity

        # Check for collision with screen boundaries and adjust position
        self.check_boundaries()
        self.check_Collision(agents)
        # Rotate agent's image to match its orientation
        self.rotate_image()


    def check_Collision(self,agents):
        # collided_agent = pg.sprite.spritecollideany(self, self.nearby_agents)
        # if collided_agent:

        #     self.handle_elastic_collision(collided_agent)
        for agent in agents:
            if agent is not self:
                distance = pg.math.Vector2(self.rect.center).distance_to(agent.rect.center)
                if distance <= self.body_size * 2:
                    self.handle_elastic_collision(agent)
                    break
        


    def handle_elastic_collision(self, other):
        # # Calculate the normal vector (collision axis) and its unit vector
        collision_vector = pg.Vector2(self.rect.center) - pg.Vector2(other.rect.center)

        # Check if collision_vector is zero
        if collision_vector.length() == 0:
            # Move the agents slightly apart to avoid zero-length vector
            collision_vector = pg.Vector2(1, 0)

        collision_normal = collision_vector.normalize()

        # Calculate the relative velocity of the agents
        relative_velocity = self.direction * self.speed - other.direction * other.speed

        # Calculate the velocity components along the collision axis
        velocity_along_normal = relative_velocity.dot(collision_normal)

        # If the velocities are separating, no need to resolve the collision
        if velocity_along_normal > 0:
            return

        # Calculate the impulse scalar
        restitution = 1  # Elastic collision
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= 2  # Dividing by the sum of inverse masses (both masses are considered equal and 1)

        # Apply the impulse to the agents' velocities
        impulse = impulse_scalar * collision_normal
        self.direction += impulse
        other.direction -= impulse

        # Normalize directions and update speeds
        self.direction = self.direction.normalize() * self.speed
        other.direction = other.direction.normalize() * other.speed

        # Adjust positions to avoid overlap
        overlap = (self.rect.width + other.rect.width) / 2 - collision_vector.length()
        displacement = overlap / 2 * collision_normal
        self.rect.center += displacement
        other.rect.center -= displacement

        # Ensure agents move away from each other
        self.direction.x *= -1
        self.direction.y *= -1
        other.direction.x *= -1
        other.direction.y *= -1
    # Calculate the normal and tangential components of the velocities
        # normal = pg.math.Vector2(self.rect.center) - pg.math.Vector2(other.rect.center)
        # distance = normal.length()
        # normal /= distance

        # tangent = pg.math.Vector2(-normal.y, normal.x)

        # v1n = normal*self.velocity
        # v1t = tangent*self.velocity
        # v2n = normal*other.velocity
        # v2t = tangent*other.velocity

        # # Swap the normal components (perfectly elastic collision)
        # self.velocity = v2n * normal + v1t * tangent
        # other.velocity = v1n * normal + v2t * tangent


    def interact(self, agents,agent_group2,configg):
        for agent in agents:
            if agent is not self and self.rect.colliderect(agent.rect):
                if self.gender != agent.gender:
                    self.mate(agent,agent_group2,configg)

 
    def find_mate(self,agents):
        for agent in self.nearby_agents:
            if agent is not self and agent.gender != self.gender:
                self.move_to(agent.rect.center,agents)
                break

    def mate(self, other,agent_group2,configg):
        if (self.gender == "m" and other.gender == "f") or (self.gender == "f" and other.gender == "m"):
            male = self if self.gender == "m" else other
            female = self if self.gender == "f" else other

            male_genome = male.genome    # Get the genome of the male agent
            female_genome = female.genome # Get the genome of the female agent
            male_age=male.age
            female_age=female.age

            

            if male.energy_level > 3 and female.energy_level > 3:
                if male.age > 7 and female.age > 7 and female.can_reproduce:
                    num_children = random.randint(1, 3)  # Random number of children between 1 and 3
                    self.reproductive_success+=num_children

                    for _ in range(num_children):
                        c.genomeid+= 1
                        #child_genome = neat.DefaultGenome(c.genomeid)  # Create a new genome for the child
                        male.genome.fitness += 10
                        female.genome.fitness += 10
                        #child_genome.configure_new(configg)
                        child_genome=configg.genome_type(c.genomeid)
                        
                        c.female_parent.append(female_genome)
                        c.male_parent.append(male_genome)

                        # Perform crossover using NEAT's method, based on the config
                        child_genome.configure_crossover(male_genome, female_genome,configg.genome_config)  
                        # Apply mutation based on the probabilities defined in config.txt
                        child_genome.mutate(configg.genome_config)
                        new_pos_x = (self.rect.x + other.rect.x) // 2
                        new_pos_y = (self.rect.y + other.rect.y) // 2
                        new_pos = (new_pos_x, new_pos_y)
                        # c.agent_pos.append(new_pos)
                        if male_genome.fitness>female_genome.fitness:
                            new_age = male_age
                        else:
                            new_age = female_age
                        new_gender = random.choice(["m", "f"])
                        new_generation_no = max(self.generation_no, other.generation_no) + 1
                        new_energy_level =  random.randint(6, 9)
                        new_body_size = 6 
                        new_agent = Agent(new_pos, new_age, new_gender, new_generation_no, new_energy_level, new_body_size,child_genome,time.time())
                        agent_group2.add(new_agent)
                        c.agents2.append(new_agent)
                        c.ge2.append(child_genome)
                        # net = neat.nn.FeedForwardNetwork.create(child_genome, configg)
                        # c.nets2.append(net)
                        child_genome.fitness = (male_genome.fitness + female_genome.fitness) / 2  # Average, for example
                        fitness = (male_genome.fitness + female_genome.fitness) / 2  # Average, for example
                        fitness=max(1.0,fitness)
                        c.fitness.append(fitness)  # Store the child's fitness 
                        c.genome_id.append(c.genomeid)
                        # c.generation_num.append(new_generation_no)
                        

                    male.energy_level -= 2
                    female.energy_level -= 2
                    female.can_reproduce = False  # Female needs to wait until aging to reproduce again
                    male.state = 'wandering'
                    female.state = 'wandering'
                    male.nearby_agents.clear()
                    female.nearby_agents.clear()
                    # male.direction.x *= -1
                    # male.direction.y *= -1
                    # female.direction.x *= -1
                    # female.direction.y *= -1                    
    # def get_fitness(self):
    #     return self.childfitness
    

    def eat(self, food_group):
        collided_food = pg.sprite.spritecollideany(self, food_group)
        if collided_food:
            if self.energy_level < 26:
                self.energy_level += collided_food.energy
            collided_food.kill()

    def wander(self):
        # Randomly adjust the left and right wheel speeds for wandering behavior
        # self.left_wheel_speed = random.randint(-self.speed, self.speed)
        # self.right_wheel_speed = random.randint(-self.speed, self.speed)


        choice=random.choice(["s","l","r"])
        if choice=="s":
            self.left_wheel_speed = self.speed
            self.right_wheel_speed = self.speed
        if choice=="l":
            self.left_wheel_speed = -self.speed
            self.right_wheel_speed = self.speed
        if choice=="r":
            self.left_wheel_speed = self.speed
            self.right_wheel_speed = -self.speed
    def search_for_food(self):
        # Randomly adjust the left and right wheel speeds for wandering behavior
        # self.left_wheel_speed1 = 2 * self.left_wheel_speed 
        # self.right_wheel_speed1 = 2 * self.right_wheel_speed 
        # self.left_wheel_speed = random.randint(self.left_wheel_speed1, self.left_wheel_speed)
        # self.right_wheel_speed = random.randint(self.right_wheel_speed1, self.left_wheel_speed)
        choice=random.choice(["s","l","r"])
        if choice=="s":
            self.left_wheel_speed = self.speed*2
            self.right_wheel_speed = self.speed*2
        if choice=="l":
            self.left_wheel_speed = -self.speed*2
            self.right_wheel_speed = self.speed*2
        if choice=="r":
            self.left_wheel_speed = self.speed*2
            self.right_wheel_speed = -self.speed*2

    def rotate_image(self):
        # Calculate the angle of rotation based on the direction vector
        angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))

        # Rotate the agent's image
        self.image = pg.transform.rotate(self.original_image, angle)

        # Update the agent's rectangle to match the rotated image
        self.rect = self.image.get_rect(center=self.rect.center)


    def check_boundaries(self):
        screen_width, screen_height = c.screen_width, c.screen_height
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction.x *= -1
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.direction.x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y *= -1
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.direction.y *= -1


            
    def increment_age(self):
        self.age += 1
        if self.age<18:
            self.body_size += 0.75

        self.original_image = pg.Surface((2 * self.body_size, 2 * self.body_size), pg.SRCALPHA)
        self.original_image.fill((0, 0, 0, 0))
        pg.draw.circle(self.original_image, self.color, (self.body_size, self.body_size), self.body_size)
        pg.draw.circle(self.original_image, self.front_marker_color, (self.body_size + self.body_size // 2, self.body_size), self.body_size // 5)
        pg.draw.circle(self.original_image, c.YELLOW, (self.body_size , self.body_size + self.body_size // 2), self.body_size // 5)  # Left wheel
        pg.draw.circle(self.original_image, c.YELLOW, (self.body_size , self.body_size - self.body_size // 2), self.body_size // 5)  # Right wheel

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.gender == "f":
            self.can_reproduce = True  # Allow reproduction again after aging
        if self.age > 12:
            self.kill()



   
    def calculate_movement_direction(self):
        if self.left_wheel_speed == 0 and self.right_wheel_speed == 0:
            return "Stationary"
        elif self.left_wheel_speed == self.right_wheel_speed:
            return "Straight" if self.left_wheel_speed > 0 else "Backward"
        elif self.left_wheel_speed == -self.right_wheel_speed:
            return "Rotating right on fixed position" if self.left_wheel_speed > 0 else "Rotating left on fixed position"
        elif self.left_wheel_speed < self.right_wheel_speed:
            return "Turning left"
        else:
            return "Turning right"
