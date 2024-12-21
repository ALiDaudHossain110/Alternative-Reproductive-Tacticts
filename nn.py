import math
import numpy as np


class NeuralNetwork():
    def __init__(self):
        pass

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    def forward(self, inputs,gene):
        # Compute the raw output by multiplying inputs with gene (weight matrix)
        raw_output = np.dot(inputs, gene)
        
        # Apply the tanh activation function
        output = np.tanh(raw_output) #soutput should be argmaxfunction
        # output = self.sigmoid(raw_output)

        return output
