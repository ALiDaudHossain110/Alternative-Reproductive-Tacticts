#main.py
import pygame as pg
import constants as c
from agents import Agent
from food import Food
import random
import threading
import time
import matplotlib.pyplot as plt
from infofunc import screen, prnt, prnt1,checkmouse, envtime, createAgent,agent_fitness,inter_genome,best_fitness_genome,save_genomes,upload_gen_info,load_genomes,cloneAgent
import numpy as np
from genome import Genome
from nn import NeuralNetwork
import copy
from retrivegenome import retrivegenome, retriveselectedgenome

# Initialize pygame
pg.init()

# Create a clock
clock = pg.time.Clock()

# Create game window
screen = pg.display.set_mode((c.screen_width+100, c.screen_height+100))
pg.display.set_caption("Alternative reproductive tactics (ARTs)")


# Create groups
agent_group = pg.sprite.Group()
food_group = pg.sprite.Group()
agent_group2 = pg.sprite.Group()
agent_group3 = pg.sprite.Group()

pop_set_num=1

# Initial food population

initial_food= c.food_population
for _ in range(initial_food):
    food = Food()
    food_group.add(food)

initialization="start"
if initialization=="retrive":
    retrivegenome("dead_agents_info_todayfinalpart2.pkl",agent_group)
elif initialization=="retriveselectedgenome":
    retriveselectedgenome("dead_agents_info_todayfinalpart2.pkl",agent_group,114)
elif initialization=="start":
    # Initial agent population
    initial_population = c.totalpop
    for _ in range(initial_population):
        gene=Genome()
        inter_genome(gene,agent_group,1)#1 is the gen_num(generation number)
 

start_time = time.time()

run = True

# Game loop
while run:
    c.update_loop_counter(c.loop_counter + 1)

    # Track mouse position
    mouse_pos = pg.mouse.get_pos()
    num_agent_on_screen=len(agent_group)
    # population set number
    if num_agent_on_screen>0:
        #neural network output taken
        # input=Agent.data()
        
        for i,agent in enumerate(agent_group):
            # if i <20:
            #     print(f"Inputs for agent  {agent.data()}")
            # else:
            #     print("=====================================")    
            if agent.mating_state_timer==c.mating_state_timer_counter:#not in mating period
                nn=NeuralNetwork()
                # print("agent : ", i)
                # print("agent data: ", agent.data())
                output=nn.forward(agent.data(),agent.genome.gene)

                # if i <20:
                #     print(f"output for agent  {output}")
                # else:
                #     print("=====================================")    
                output_0=output[0]
                output_1=output[1]
                output_2=output[2]
                output_3=output[3]

                # Map the outputs to a dictionary
                outputs = {
                    'output_0': output_0,
                    'output_1': output_1,
                    'output_2': output_2,
                    'output_3': output_3,
                }

                # Find the maximum value and the corresponding key
                max_output_key = max(outputs, key=outputs.get)
                max_output_value = outputs[max_output_key]

                # Output the result
                # print(f"The maximum value is {max_output_value} from {max_output_key}")
            
                if agent.post_mating_state_timer==c.post_mating_state_timer_counter:#not in post mating period
                    
                    if max_output_key == "output_0":
                        agent.state = 'moving_to_food'
                    if max_output_key == "output_1":
                        agent.state = 'Aproach_towards_nearest'
                    if max_output_key == "output_2": 
                        agent.state = 'mating as male'
                    if max_output_key == "output_3":
                        agent.state = 'mating as female'


                    # c.update_agent_info(agent,output[5], output[6],output[7]) 
                    # c.update_agent_info(agent,output[5]) 
                
                else:

                    if max_output_key == "output_2" or max_output_key == "output_3":
                        # Sort the dictionary by values in descending order and get the second item
                        second_best_output = sorted(outputs.items(), key=lambda x: x[1], reverse=True)
                        # Get the second-best key (this will be the second item in the sorted list)
                        second_best_key = second_best_output[1][0]
                        if second_best_key == "output_2" or second_best_key == "output_3":
                            third_best_key = second_best_output[2][0]
                            if third_best_key == "output_0":
                                agent.state = 'moving_to_food'
                            if third_best_key == "output_1":
                                agent.state = 'Aproach_towards_nearest'

                        else:
                            if second_best_output == "output_0":
                                agent.state = 'moving_to_food'
                            if second_best_output == "output_1":
                                agent.state = 'Aproach_towards_nearest'


                        # c.update_agent_info(agent,output[5]) 

            
            if agent.mating_state_timer<4:#checks if in mating state.
                agent.state = agent.state

        

        # Updating groups
        agent_group.update(agent_group,agent_group2, food_group)
        # Drawing agents
        agent_group.draw(screen)

    else:
        c.update_loop_counter(0)


        upload_gen_info()#uploading the genrationinfo
        c.pop_set_num +=1
        print("generation number:",  c.pop_set_num)
        
        sizeofagent=len(agent_group)
        c.clear_dead_agent_bucket_list()
        agent_group.empty()
        c.clear_agents()
        c.clear_ge()

        print("size of children list:",agent_group2)

        # Randomly select agents from `agent_group2` until `agent_group` reaches 100 agents
        # if len(agent_group2)>120:
        totl=c.totalpop
        fsttotl=0.5*c.totalpop
        if len(agent_group2)>=totl:
            for new_agent in agent_group2:
                if len(agent_group)<c.totalpop:
                    choice=random.choice(["y","n"])
                    if choice == "y":
                        agent_group.add(new_agent)
                        c.dead_agent_bucket_list.append(new_agent)
                        c.update_ge(new_agent.genome)  # Remove from agent_group2 to avoid duplicates
        
        #if less offsprings...
        else:
            # print("1")
            if len(agent_group2)==0:
                # print("2")

                # agent_group = pg.sprite.Group(copy.deepcopy(agent) for agent in agent_group3)
                for agent in agent_group3:
                    # print("1,,")
                    if len(agent_group)<fsttotl:
                        inter_genome(agent.genome,agent_group,agent.generation_no)


            if len(agent_group2)<=fsttotl and len(agent_group2)>0:
                # print("2")

                while len(agent_group) < fsttotl:
                    # print("111")

                    for new_agent in agent_group2:
                        if len(agent_group)<fsttotl:
                            # print("add")
                            inter_genome(new_agent.genome,agent_group,new_agent.generation_no)
                        else:
                            # print("length",len(agent_group))
                            break

            if len(agent_group2)>=fsttotl and len(agent_group2)<totl and len(agent_group2)>0:
                # print("2")

                    # print("111")

                for new_agent in agent_group2:
                    if len(agent_group)<totl:
                        # print("add")
                        inter_genome(new_agent.genome,agent_group,new_agent.generation_no)
                    else:
                        # print("length",len(agent_group))
                        break

            # else:

            #     for new_agent in agent_group2:
            #         if len(agent_group)<=c.totalpop:
            #             agent_group.add(new_agent)
            #             c.dead_agent_bucket_list.append(new_agent)
            #             c.update_ge(new_agent.genome)  # Remove from agent_group2 to avoid duplicates

        loop=c.totalpop-len(agent_group)
        if loop>0:
            for _ in range(loop):
                gene=Genome() 
                inter_genome(gene,agent_group,1)#1 because new genome creation
        agent_group3.empty()
        # agent_group3 = pg.sprite.Group(copy.deepcopy(agent) for agent in agent_group)
        #making a copy of the agents list going into the next generation, if the generation fails to make any offspring this will used to repopulate the next genso tht evolution is not lost.
        for agent in agent_group:
            agent_group3.add(createAgent(agent.genome,agent.birth_time,agent.generation_no))
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
        font = pg.font.Font(None, 12)
        text = font.render(f"Population: {population} Highest Generation: {highest_generation}", True, c.WHITE)
    text2 = font.render(f": {hour} hr: {min} min: {sec} sec", True, c.WHITE)
    text4 = font.render(f"Population number: {c.pop_set_num}", True, c.WHITE)
    text3 = font.render(f"children length: {len(agent_group2)}", True, c.WHITE)
    text5 = font.render(f"No. of food: {len(food_group)}", True, c.WHITE)
    # prnt1(text5, 0.7)
    prnt1(text3, 0.5)
    prnt1(text2, 0.01)
    prnt(text4, 0.6)
    prnt(text, 0.01)

    # Event handler
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    # Check if 10 seconds have passed
    # if time.time() - start_time >= 10:
    #     print("Iterations in 10 seconds:", iteration_count)
    #     break  # Stop after 10 seconds if you only want to measure this part
    # Update display
    pg.display.flip()
    clock.tick_busy_loop(c.fps)
    screen.fill(c.BLACK)



# Quit pygame
pg.quit()


