#main.py
import pygame as pg
import constants as c
from agents import Agent
from food import Food
import random
import threading
import time
import matplotlib.pyplot as plt
from infofunc import screen, prnt, checkmouse, envtime, createAgent,agent_fitness,inter_genome,best_fitness_genome,save_genomes,upload_gen_info,load_genomes,extract_species_info
import numpy as np
from genome import Genome
from nn import NeuralNetwork
# Initialize pygame
pg.init()

# Create a clock
clock = pg.time.Clock()

# Create game window
screen = pg.display.set_mode((c.screen_width, c.screen_height))
pg.display.set_caption("Alternative reproductive tactics (ARTs)")


# Create groups
agent_group = pg.sprite.Group()
food_group = pg.sprite.Group()
agent_group2 = pg.sprite.Group()

pop_set_num=1

# Initial food population

initial_food= c.food_population
for _ in range(initial_food):
    food = Food()
    food_group.add(food)

# Initial agent population
initial_population = 150
for _ in range(initial_population):
    gene=Genome()
    inter_genome(gene,agent_group)
 


# Population history
population_history = []
start_time = time.time()

def update_population_history():
    global run
    while run:
        current_time = time.time() - start_time
        population_history.append((current_time, len(agent_group)))
        time.sleep(1)

# Start population history thread
run = True
history_thread = threading.Thread(target=update_population_history)
history_thread.start()
conter=0
conter2=0
# Game loop
while run:
    conter=conter+1

    # print("counter: ",conter)


    # Track mouse position
    mouse_pos = pg.mouse.get_pos()
    num_agent_on_screen=len(agent_group)

    # population set number



    if num_agent_on_screen>0:
        #neural network output taken
        # input=Agent.data()
        for agent in agent_group:
            nn=NeuralNetwork()
            output=nn.forward(agent.data(),agent.genome.gene)
            conter2=conter2+1
            # print("counter2: ",conter2)

            output_0=output[0]
            output_1=output[1]
            output_2=output[2]
            output_3=output[3]
            output_4=output[4]

            # Map the outputs to a dictionary
            outputs = {
                'output_0': output_0,
                'output_1': output_1,
                'output_2': output_2,
                'output_3': output_3,
                'output_4': output_4
            }

            # Find the maximum value and the corresponding key
            max_output_key = max(outputs, key=outputs.get)
            max_output_value = outputs[max_output_key]

            # Output the result
            # print(f"The maximum value is {max_output_value} from {max_output_key}")

            if max_output_key == "output_0":
                agent.state = 'moving_to_food'
            if max_output_key == "output_1":
                agent.state = 'searching_for_food'
            if max_output_key == "output_2": 
                agent.state = 'mating as male'
            if max_output_key == "output_3":
                agent.state = 'mating as female'
            if max_output_key == "output_4":
                agent.state = 'wandering'

            c.update_agent_info(agent,output[5], output[6]) 
        

        # Updating groups
        agent_group.update(agent_group,agent_group2, food_group)
        # Drawing agents
        agent_group.draw(screen)

    else:
        c.pop_set_num +=1
        
        upload_gen_info()#uploading the genrationinfo
        sizeofagent=len(agent_group)
        agent_group.empty()
        c.clear_agents()
        c.clear_ge()


        for newagents in agent_group2:


            if len(agent_group)<100:

                choice=random.choice(["y","n"])
                if choice == "y":
                    agent_group.add(newagents)
                    c.update_ge(newagents.genome)
                

                else:

                    break   
        if len(agent_group)<100:
            agent_size=len(agent_group)
            loop=100-agent_size
            for _ in range(loop):
                gene=Genome()
                inter_genome(gene,agent_group)

        agent_group2.empty()

        checkmouse(agent_group)

    # Draw and update the food circles
    food_group.update(food_group)
    food_group.draw(screen)
    # Clock calculation
    clock_time = time.time() - start_time
    sec, min, hour = envtime(clock_time)

    checkmouse(agent_group)


    # Print the number of agents on the screen
    population = len(agent_group)
    if population > 0:
        highest_generation = max(agent.generation_no for agent in agent_group)
        font = pg.font.Font(None, 20)
        text = font.render(f"Population: {population} Highest Generation: {highest_generation}", True, c.WHITE)
    text2 = font.render(f"CLOCK : {hour} hr: {min} min: {sec} sec", True, c.WHITE)
    text4 = font.render(f"Population set number: {c.pop_set_num}", True, c.WHITE)
    text3 = font.render(f"Agents children length: {len(agent_group2)}", True, c.WHITE)
    text5 = font.render(f"No. of food: {len(food_group)}", True, c.WHITE)
    prnt(text5, 0.7)
    prnt(text3, 0.5)
    prnt(text2, 0.8)
    prnt(text4, 0.3)
    prnt(text, 0.01)

    # Event handler
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            # print("counter: ",conter)

    # Update display
    pg.display.flip()
    clock.tick(c.fps)
    screen.fill(c.BLACK)


# Stop the population history thread
history_thread.join()

# Quit pygame
pg.quit()

# Plot the population history
times, populations = zip(*population_history)
plt.plot(times, populations)
plt.xlabel('Time (seconds)')
plt.ylabel('Population')
plt.title('Population vs. Time')
plt.show()

