#agents.py
import pygame as pg
import constants as c  # Ensure this module contains required constants
import random
import math
import numpy as np
from genome import Genome
import time
screen = pg.display.set_mode((c.screen_width, c.screen_height))

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
        self.birth_time=birthtime
        self.reproductive_success=0

        self.no_of_matings_as_female=0
        self.no_of_matings_as_male=0

        self.mating_state_timer=c.mating_state_timer_counter
        self.post_mating_state_timer=c.post_mating_state_timer_counter
        
        self.reproductive_success_weight=0.1
        self.servival_time_weight=0.1
        self.energy_weight=0.1
        
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
        self.state = 'wandering'


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
        self.font = pg.font.Font(None, 30)

        self.state_counter_dict={
            "moving_to_food":[0]*550,
            "waiting":[0]*550,
            "wandering":[0]*550,
            "mating as male":[0]*550,
            "mating as female":[0]*550,
            "searching_for_food":[0]*550,
            "Aproach_towards_nearest":[0]*550,
        }

    def state_stat(self):
        i=int(self.energy_level)
        i-=1
        self.state_counter_dict[self.state][i]= int(self.state_counter_dict[self.state][i])+1

    def update(self, agents, agent_group2, food_group):
        self.age = c.loop_counter
        self.state_stat()

        self.perceive(agents, food_group)
        self.act(agents,agent_group2)
        self.interact(agents,agent_group2)
        self.eat(food_group)

        self.age=c.loop_counter
        if c.loop_counter%5==0 and c.loop_counter>self.old_timestep:
            
            self.energy_level -= 2
            self.old_timestep = c.loop_counter


        if self.energy_level <= 0:
            self.kill()

        if c.loop_counter%250==0:
            self.increment_age()


        if self.post_mating_state_timer <c.post_mating_state_timer_counter:
            if self.post_mating_state_timer > 0:
                self.post_mating_state_timer -= 1
                # print("self.post_mating_state_timer",self.post_mating_state_timer)
                # print("deducted")
            elif self.post_mating_state_timer == 0:
                # print("self.post_mating_state_timer",self.post_mating_state_timer)
                # print("value set")
                self.post_mating_state_timer=c.post_mating_state_timer_counter
                self.can_reproduce = True  # Allow reproduction again after aging


                # Do not reset the timer here. It should be reset after mating.

        self.update_position(agents)

        self.rect = self.image.get_rect(center=self.rect.center)

    def check_edge_in_vision(self, other, vision_angle):
        """
        Checks if any edge point of the target `other` is within the agent's vision cone.
        :param other: The target object to check (with a `rect` attribute for position and size).
        :param vision_angle: The agent's field of view (FOV) in degrees.
        :return: True if any edge point is within the vision cone, False otherwise.
        """


        # Vector from the agent to the target's center
        to_other_center = pg.Vector2(other.rect.center) - pg.Vector2(self.rect.center)
        if to_other_center.length() > self.sight_radius:
            return False  # Skip if the center is out of sight

        # Get the radius of the target (assuming circular or square shape)
        radius = other.rect.width / 2  # Half the width of the rect is the "radius"

        # Define the edge points to check (e.g., top, bottom, left, right, diagonals)
        edge_points = [
            pg.Vector2(
                other.rect.centerx + math.cos(math.radians(angle)) * radius,
                other.rect.centery + math.sin(math.radians(angle)) * radius,
            )
            for angle in range(0, 360, 90)  # Adjust angle intervals for precision
        ]

        # Precompute normalized agent direction for efficiency
        if self.direction.length() == 0:
            return False  # If the direction vector has zero length, the agent can't "see"
        self_dir = self.direction.normalize()

        # Helper function for safe normalization
        def safe_normalize(vector):
            if vector.length() == 0:
                return vector  # Return the zero vector as-is
            return vector.normalize()

        # Check each edge point
        for edge_point in edge_points:
            to_edge = edge_point - pg.Vector2(self.rect.center)
            if to_edge.length() <= self.sight_radius:  # Within sight radius
                # Safely normalize the vector to the edge point
                to_edge_normalized = safe_normalize(to_edge)
                # Calculate the cosine of the angle between the agent's direction and vector to edge
                cos_angle = self_dir.dot(to_edge_normalized)
                if cos_angle >= math.cos(math.radians(vision_angle / 2)):  # Within vision cone
                    return True

        return False


    def perceive(self, agents, food_group):

        self.nearby_food = []  # Clear the previous list of food
        self.nearby_agents = []  # Clear the previous list of agents 
        self.nearby_agents_face_dist=[]
        self.nearby_agents_back_dist=[]
        self.nearby_agents_back=[]
        self.nearby_agents_face=[]

        for food in food_group:
            if self.energy_level < 500:
                # if self.check_edge_in_vision(food,self.vision_angle):
                direction_to_food = pg.Vector2(food.rect.centerx - self.rect.centerx, food.rect.centery - self.rect.centery)
                if direction_to_food.length() <= self.sight_radius:
                        self.nearby_food.append(food)


        # First, calculate the distances and store the agents with their distances in a temporary list
        temp_nearby_agents = []
        temp_nearby_agents_front = []
        temp_nearby_agents_front = []
        temp_nearby_agents_back = []

        for agent in agents:
            if agent is not self:
                if self.age > 0 and self.energy_level > 3:
                    # if self.check_edge_in_vision(agent,self.vision_angle_mating):

                    direction_to_agent = pg.Vector2(agent.rect.centerx - self.rect.centerx, agent.rect.centery - self.rect.centery)
                    if direction_to_agent.length() <= self.sight_radius:
                            # Add the agent and its distance to a temporary list
                            temp_nearby_agents.append((agent, direction_to_agent.length()))
                            dist_to_front,dist_to_back=self.dist_face_back(agent)
                            check_face=self.check_faceing_or_not(agent)
                            if check_face:
                                temp_nearby_agents_front.append((agent,dist_to_front))
                            else:
                                temp_nearby_agents_back.append((agent,dist_to_back))


        # Sort the temporary list by the distance (ascending order)
        temp_nearby_agents.sort(key=lambda x: x[1])
        temp_nearby_agents_front.sort(key=lambda x: x[1])
        temp_nearby_agents_back.sort(key=lambda x: x[1])

        # Extract only the agent objects, sorted by distance
        self.nearby_agents = [agent for agent, _ in temp_nearby_agents]
        self.nearby_agents_face_dist = [dist_to_front for _, dist_to_front in temp_nearby_agents_front]
        self.nearby_agents_face = [agent for agent, _ in temp_nearby_agents_front]
        self.nearby_agents_back_dist = [dist_to_back for _, dist_to_back in temp_nearby_agents_back]
        self.nearby_agents_back = [agent for agent, _ in temp_nearby_agents_back]

    def check_faceing_or_not(self, agent):   
        vector_to_agent = pg.Vector2(agent.rect.centerx - self.rect.centerx, agent.rect.centery - self.rect.centery)
        if vector_to_agent.length()!=0:
            vector_to_agent = vector_to_agent.normalize()  # Normalize to unit vector
        else:
            vector_to_agent = pg.Vector2(0, 0) # Replace with a default vector, if needed

        # Normalize Agent 2's direction
        if agent.direction.length()>0:
            agent.direction = agent.direction.normalize()  # Normalize Agent 2's direction vector
        else:
            agent.direction = pg.Vector2(1, 0)  # Default to moving right
        # Calculate the dot product between Agent 2's direction and the vector to Agent 1
        dot_product = agent.direction.dot(vector_to_agent)
        dot_product = max(min(dot_product, 1.0), -1.0)  # Clamp to avoid numerical errors

        # Compute the angle in radians and convert it to degrees
        angle = math.degrees(math.acos(dot_product))

        # Check if the angle is within the threshold (Agent 1 is looking at Agent 2's face)
        return angle <= self.vision_angle_mating/2

    def waiting(self):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

    def dist_face_back(self, agent):
        # Extract the direction vector components(other agent)
        direction_x, direction_y = agent.direction
        
        # Calculate the length of the direction vector(other agent)
        length = math.sqrt(direction_x**2 + direction_y**2)
        
        # Normalize the direction vector(other agent)
        if length!=0:
            norm_x = direction_x / length
            norm_y = direction_y / length
        else:
            norm_x = 1
            norm_y = 0
        
        # Calculate the offset length for the front marker(other agent)
        offset_len = agent.body_size // 2 + 2
        
        # Get the agent's and self's center position
        center_x, center_y = agent.rect.center
        self_center_x, self_center_y = self.rect.center

        # Extract the direction vector components(self)
        self_direction_x, self_direction_y = self.direction
        # Calculate the length of the direction vector(self)
        self_length = math.sqrt(self_direction_x**2 + self_direction_y**2)

        # Normalize the direction vector(self)
        if self_length != 0:
            self_norm_x = self_direction_x / self_length
            self_norm_y = self_direction_y / self_length
        else:
            self_norm_x = 1  # Or some default value
            self_norm_y = 0  # Or some default value
        #the offset len of the front(self)
        self_offset_len_front=self.body_size

        # Calculate the front  coordinates(self)
        self_front_x = self_center_x + self_norm_x * self_offset_len_front
        self_front_y = self_center_y + self_norm_y * self_offset_len_front

        # Calculate the front marker coordinates(other agent)
        front_x = center_x + norm_x * offset_len
        front_y = center_y + norm_y * offset_len

        #the offset len of the back
        offset_len_back=agent.body_size
        # Calculate the back coordinates
        back_x = center_x - norm_x * offset_len_back
        back_y = center_y - norm_y * offset_len_back

        len_to_front=self.distance_cordinate(front_x,front_y,self_front_x,self_front_y)
        len_to_back=self.distance_cordinate(back_x,back_y,self_front_x,self_front_y)

        return len_to_front,len_to_back

    def distance_cordinate(self, x1, y1, x2, y2):
        # Correct Euclidean distance
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def norm_direction(self, x,y):

        max_val=max(x,y)
        if max_val==0:
            return [0,0]
        else:
            x=x/max_val
            y=y/max_val
            list=[x,y]
            return list

    def data(self):
        input = [0, 0,0,0,0,1]
        agent_center = pg.Vector2(self.rect.centerx, self.rect.centery)

        # Get the center coordinates of the first nearby food item,agent center,other center.
        if len(self.nearby_food) >0:
            food_center = pg.Vector2(self.nearby_food[0].rect.centerx, self.nearby_food[0].rect.centery)
            dist_to_food = food_center.distance_to(agent_center)

        else:
            # If there is no nearby food, set default values
            dist_to_food = -1

        # Get the distance of the face of other agent.
        if len(self.nearby_agents_face_dist) > 0:
            dist_to_other_face = self.nearby_agents_face_dist[0]

        else:
            # If there is no nearby food, set default values
            dist_to_other_face = 0

        if len(self.nearby_agents_back_dist) > 0:
            dist_to_other_back = self.nearby_agents_back_dist[0]

        else:
            # If there is no nearby food, set default values
            dist_to_other_back = 0

        direction=self.norm_direction(self.direction_to_move[0],self.direction_to_move[1])#normalizing the direction

        dist_to_food=dist_to_food/self.sight_radius
        dist_to_other_face=dist_to_other_face/self.sight_radius
        dist_to_other_back=dist_to_other_back/self.sight_radius
        input[0] = dist_to_food  # Add this distance to the food to the input list      
        input[1] = dist_to_other_face  # Add this distance to the dist_to_other_face to the input list    
        input[2] = dist_to_other_back  # Add this distance to the dist_to_other_back to the input list          
        input[3] = self.energy_level/400  # Add normalized energy level
        input[4] = self.age/5000 #add age 
        return input

    def act(self,agents,agent_group2):

        if self.state == 'moving_to_food':
            self.mating_state_timer=c.mating_state_timer_counter
            if self.nearby_food:
                self.move_to(self.nearby_food[0].rect.center,agents)
            else:
                self.state=='searching_for_food'
                self.search_for_food(agents,self.nearby_food)


        if self.state == 'Aproach_towards_nearest':
            self.mating_state_timer=c.mating_state_timer_counter
            self.aproaching(agents)
        

        if self.state == 'mating as male':
            if self.nearby_agents:
                self.find_mate_as_male(agents,agent_group2)
            else:
                self.waiting()

        if self.state == 'mating as female'and self.nearby_agents:
            self.find_mate_as_female(agents,agent_group2)
        
        else:
            self.waiting()

        # if self.state == 'wandering':
        #     self.wander()

    def appearance(self, gender, body_size, pos):
        # Load the image and scale it to the size of the body
        try:
            if gender == "m":
                image_path = 'images/male.png'
            if gender == "f":
                image_path = 'images/female.png'

            self.original_image = pg.image.load(image_path).convert_alpha()
        except pg.error as e:
            print(f"Unable to load image: {e}")
            self.original_image = pg.Surface((2 * body_size, 2 * body_size), pg.SRCALPHA)
        # Initialize wheel parameters
        self.wheel_radius = body_size // 2
        self.wheel_distance = body_size

        # Scale the image
        self.original_image = pg.transform.scale(self.original_image, (2 * body_size, 2 * body_size))

        # Add wheels or markers (optional)
        pg.draw.circle(self.original_image, c.YELLOW, (body_size+1, body_size + body_size // 2), body_size // 5)  # Left wheel
        pg.draw.circle(self.original_image, c.YELLOW, (body_size+1, body_size - body_size // 2), body_size // 5)  # Right wheel
        pg.draw.circle(self.original_image, self.front_marker_color, ((body_size + body_size // 2)+2, body_size), body_size // 5)

        # Set the image to be used for the agent
        self.image = self.original_image.copy()

        # Set the rect and position it based on the given `pos`
        self.rect = self.image.get_rect()  # Get the rect for the image
        self.rect.center = pos  # Set the rect’s center to the agent’s position

    def aproaching(self,agents):
        if self.nearby_agents:
            agent=self.nearby_agents[0]
            self.move_to(agent.rect.center,agents)
        else:
            self.state='waiting'
            self.wander()

    def move_to(self, target,agents):

        self.check_Collision(agents)
        self.direction_to_move= pg.Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery)

        # Calculate the vector pointing to the target
        self.direction = pg.Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery)

        # Normalize the direction vector
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pg.Vector2(1, 0)  # Default to moving right

        # Calculate the angle to the target
        angle_to_target = self.direction.angle_to(self.direction)
        
        # Adjust wheel speeds based on the angle to the target using proportional control
        kp = 0.1  # Proportional gain
        rotation_speed = kp * angle_to_target

        self.left_wheel_speed = self.speed - rotation_speed
        self.right_wheel_speed = self.speed + rotation_speed

        self.clamp_speed()
        # self.check_Collision()        
        self.update_position(agents)

    def update_position(self, agents):

        # Update the agent's position based on the left and right wheel speeds
        velocity = (self.left_wheel_speed + self.right_wheel_speed) / 2
        rotation = (self.right_wheel_speed - self.left_wheel_speed) / self.wheel_distance

        # Update direction based on rotation
        if rotation != 0:
            angle = rotation * 180 / math.pi
            self.direction.rotate_ip(angle)  # Adjusted sign for correct rotation direction
        # Normalize direction
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pg.Vector2(1, 0)  # Default to moving right

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
        if self.direction.length() > 0:
            self.direction = self.direction.normalize() * self.speed
        else:
            # Handle the zero vector case (e.g., assign a default direction)
            self.direction = pg.Vector2(1, 0) * self.speed  # Default to moving right
        if other.direction.length() > 0:
            other.direction = other.direction.normalize() * other.speed
        else:
            self.direction = pg.Vector2(1, 0)  # Default to moving right


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

    def clamp_speed(self):
        max_speed = 4  # Set a reasonable max speed limit
        self.left_wheel_speed = max(-max_speed, min(self.left_wheel_speed, max_speed))
        self.right_wheel_speed = max(-max_speed, min(self.right_wheel_speed, max_speed))

    def interact(self, agents,agent_group2):
        if self.state == 'mating as female' or self.state == 'mating as male':
            for agent in self.nearby_agents:
                distance = math.sqrt((self.rect.centerx - agent.rect.centerx) ** 2 + (self.rect.centery - agent.rect.centery) ** 2)
                if agent is not self and distance<18:#6 bodysize +6 body size of othe +5 mating zone
                    if self.gender != agent.gender:
                        self.mate(agent,agents,agent_group2)

    def find_mate_as_male(self,agents,agent_group2):
        self.gender="m"
        self.appearance(self.gender,self.body_size,self.rect.center)

        if self.nearby_agents:
                self.interact(agents,agent_group2)
        else:
            return
                    
        # if self.nearby_agents:
        #     if self.nearby_agents_face_dist and self.nearby_agents_back_dist:
        #         if self.nearby_agents_face_dist[0]<self.nearby_agents_back_dist[0]:
        #             agent= self.nearby_agents_face[0]
        #             if agent is not self and agent.gender != self.gender:
        #                 # self.move_to(agent.rect.center,agents)
        #                 self.interact(agents,agent_group2)
        #         else:
        #             agent= self.nearby_agents_back[0]
        #             if agent is not self and agent.gender != self.gender:
        #                 # self.move_to(agent.rect.center,agents)
        #                 self.interact(agents,agent_group2) 

    def find_mate_as_female(self,agents,agent_group2):

        self.gender="f"
        self.appearance(self.gender,self.body_size,self.rect.center)


        if self.nearby_agents:
                        self.interact(agents,agent_group2)


    def mate(self, other,agents,agent_group2):
        # print("reproduced 1st line")

        if (self.gender == "m" and other.gender == "f") or (self.gender == "f" and other.gender == "m"):
            male = self if self.gender == "m" else other
            female = self if self.gender == "f" else other

            male_genome = male.genome    # Get the genome of the male agent
            female_genome = female.genome # Get the genome of the female agent
            # print("==================================")
            # print("male.post_mating_state_timer",male.post_mating_state_timer)
            # print("male.post_mating_state_timer",male.post_mating_state_timer)
            # print("==================================")

            # print("reproduced 2nd line")
            prob_of_female_mating=female.energy_level/500
            random_num=random.random()
            # print("prob_of_female_mating",prob_of_female_mating)
            # print("random_num",random_num)
            # print("----------------------")
            if random_num<prob_of_female_mating:
                # print("reproduced 3rd line")

                # if male.age > 0 and female.age > 0 and female.can_reproduce and male.state == 'mating as male' and female.state == 'mating as female':
                if female.can_reproduce and male.state == 'mating as male' and female.state == 'mating as female':
                    # print("reproduced 4th line")
                    # print("female.mating_state_timer",female.mating_state_timer)
                    # print("female.post_mating_state_timer",female.post_mating_state_timer)
                    # print("male.mating_state_timer",male.mating_state_timer)
                    # print("male.post_mating_state_timer",male.post_mating_state_timer)

                    if female.mating_state_timer==0 and female.post_mating_state_timer==c.post_mating_state_timer_counter and male.mating_state_timer==0 and male.post_mating_state_timer==c.post_mating_state_timer_counter:
                        # print("reproduced 5th line")

                        num_children = 2 
                       
                        if self.gender=="f":
                            # print("reproduced 6th line")
                            self.reproductive_success=self.reproductive_success+2

                            self.no_of_matings_as_female=self.no_of_matings_as_female+2
                            male.no_of_matings_as_male=self.no_of_matings_as_male+2
                            for i in range(num_children):
                                # print("prob_of_female_mating-success",prob_of_female_mating)
                                # print("random_num-success",random_num)
                                # print("++++++++++++++++")
                                child_genome1=Genome()
                                child_genome2=Genome()
                                if i==0:
                                    child_genome1.gene=child_genome1.reproduce(child_genome1.gene, male_genome.gene, female_genome.gene,"m")
                                if i==1:
                                    child_genome2.gene=child_genome2.reproduce(child_genome2.gene, male_genome.gene, female_genome.gene,"f")

                                c.female_parent.append(female_genome)
                                c.male_parent.append(male_genome)

                                new_pos_x = (self.rect.x + other.rect.x) // 2
                                new_pos_y = (self.rect.y + other.rect.y) // 2
                                new_pos = (new_pos_x, new_pos_y)

                                new_generation_no = max(self.generation_no, other.generation_no) + 1
                                new_energy_level =  100
                                new_body_size = 6 
                                if i==0:
                                    new_agent = Agent(new_pos, new_generation_no, new_energy_level, new_body_size,child_genome1,time.time())
                                    agent_group2.add(new_agent)
                                    c.agents2.append(new_agent)
                                # c.ge2.append(child_genome)
                                # print("reproduced")
                                    c.genome_id.append(c.genomeid)
                                if i==1:
                                    new_agent = Agent(new_pos, new_generation_no, new_energy_level, new_body_size,child_genome2,time.time())
                                    agent_group2.add(new_agent)
                                    c.agents2.append(new_agent)
                                # c.ge2.append(child_genome)
                                # print("reproduced")
                                    c.genome_id.append(c.genomeid)                                

                            female.energy_level -= 50
                            female.can_reproduce = False  # Female needs to wait until aging to reproduce again
                            male.post_mating_state_timer-=2
                            female.post_mating_state_timer-=1

                            male.state = 'waiting'
                            female.state = 'waiting'
                            male.nearby_agents.clear()
                            female.nearby_agents.clear()
                            male.direction.x = random.choice([-1, 1]) * abs(male.direction.x)
                            male.direction.y = random.choice([-1, 1]) * abs(male.direction.y)
                            female.direction.x = random.choice([-1, 1]) * abs(female.direction.x)
                            female.direction.y = random.choice([-1, 1]) * abs(female.direction.y)
                            self.act(agents,agent_group2)
                        
                        # screen.blit(self.font.render(f"....", True, c.WHITE), (self.rect.x, self.rect.y))
                        # screen.blit(self.font.render(f"........", True, c.WHITE), (self.rect.x, self.rect.y))
                    # print("female.post_mating_state_timer",female.post_mating_state_timer)
                    # print("male.post_mating_state_timer",male.post_mating_state_timer)
                    if self.mating_state_timer<=0:
                        self.mating_state_timer=c.mating_state_timer_counter
                    else:
                        self.mating_state_timer-=1


    def eat(self, food_group):
        collided_food = pg.sprite.spritecollideany(self, food_group)
        if collided_food:
            if self.energy_level < 450:
                self.energy_level += collided_food.energy

            collided_food.kill()

    def wander(self):

        choice=random.choice(["s","l","r"])
        if choice=="s":
            self.left_wheel_speed = 2
            self.right_wheel_speed = 2
        if choice=="l":
            self.left_wheel_speed = -2
            self.right_wheel_speed = 2
        if choice=="r":
            self.left_wheel_speed = 2
            self.right_wheel_speed = -2

        if self.left_wheel_speed>4.5:
            print("self.left_wheel_speed in wander",self.left_wheel_speed)

        if self.right_wheel_speed>4.5:
            print("self.right_wheel_speed in wander",self.right_wheel_speed)

    def search_for_food(self, agents, food_group):
        # Adjust the left and right wheel speeds
        self.left_wheel_speed
        self.right_wheel_speed

        # Random choice for direction or speed changes
        choice = random.choice(["s", "l", "r"])

        # Increase speeds based on choice
        if choice == "s":
            if self.left_wheel_speed<0:
                self.left_wheel_speed *= -2
            else:
                self.left_wheel_speed*=2
            if self.right_wheel_speed<0:
                self.right_wheel_speed *= -2
            else:
                self.right_wheel_speed*=2    
        elif choice == "l":
            if self.left_wheel_speed<0:
                self.left_wheel_speed *= -2
            else:
                self.left_wheel_speed*=2
            if self.right_wheel_speed<0:
                self.right_wheel_speed *= -2
            else:
                self.right_wheel_speed*=2    

            self.left_wheel_speed = -self.left_wheel_speed  # Reverse one side for turning
        elif choice == "r":
            if self.left_wheel_speed<0:
                self.left_wheel_speed *= -2
            else:
                self.left_wheel_speed*=2
            if self.right_wheel_speed<0:
                self.right_wheel_speed *= -2
            else:
                self.right_wheel_speed*=2    

            self.right_wheel_speed = -self.right_wheel_speed  # Reverse the other side for turning

        self.clamp_speed()
        self.left_wheel_speed = round(self.left_wheel_speed, 2)
        self.right_wheel_speed = round(self.right_wheel_speed, 2)
        self.energy_level-=0.05
        # Debugging prints to ensure clamping works
        if self.left_wheel_speed >6 or self.right_wheel_speed > 6:
            print(f"Warning: Wheel speeds exceeded limit! Left: {self.left_wheel_speed}, Right: {self.right_wheel_speed}")

        # Continue with food perception and movement
        self.perceive(agents, food_group)

        if self.nearby_food:
            self.move_to(self.nearby_food[0].rect.center, agents)

        self.eat(food_group)

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
        
        # self.age += 1
        self.appearance(self.gender,self.body_size,self.rect.center)

        if self.age > 4750:
            self.kill()
   
    def calculate_movement_direction(self):
        if self.left_wheel_speed == 0 and self.right_wheel_speed == 0:
            if self.left_wheel_speed>4.5:
                print("self.left_wheel_speed in search_for_food",self.left_wheel_speed)
            

            if self.right_wheel_speed>4.5:
                print("self.right_wheel_speed in search_for_food",self.right_wheel_speed)
            return "Stationary"
        elif self.left_wheel_speed == self.right_wheel_speed:
            if self.left_wheel_speed>4.5:
                print("self.left_wheel_speed in search_for_food",self.left_wheel_speed)
            

            if self.right_wheel_speed>4.5:
                print("self.right_wheel_speed in search_for_food",self.right_wheel_speed)
            return "Straight" if self.left_wheel_speed > 0 else "Backward"
        elif self.left_wheel_speed == -self.right_wheel_speed:
            if self.left_wheel_speed>4.5:
                print("self.left_wheel_speed in search_for_food",self.left_wheel_speed)
            

            if self.right_wheel_speed>4.5:
                print("self.right_wheel_speed in search_for_food",self.right_wheel_speed)
            return "Rotating right on fixed position" if self.left_wheel_speed > 0 else "Rotating left on fixed position"
        elif self.left_wheel_speed < self.right_wheel_speed:
            if self.left_wheel_speed>4.5:
                print("self.left_wheel_speed in search_for_food",self.left_wheel_speed)
            

            if self.right_wheel_speed>4.5:
                print("self.right_wheel_speed in search_for_food",self.right_wheel_speed)
            return "Turning left"
        else:
            return "Turning right"
        


